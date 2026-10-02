"""API tests: full review sessions through TestClient for every card type and mode (M2 'done when')."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from revision.app import create_app
from revision.content import ContentError

from .conftest import write_content


@pytest.fixture
def client(cfg, clock):
    return TestClient(create_app(cfg, clock=clock))


def answer_payload(card_detail: dict, correct: bool = True) -> dict:
    c = card_detail["card"]
    if c["type"] == "tf":
        return {"answer": c["answer"] if correct else not c["answer"]}
    if c["type"] == "mcq":
        wrong = [i for i in range(len(c["choices"])) if i not in c["answer"]][:1]
        return {"answer": c["answer"] if correct else wrong}
    return {"rating": 3 if correct else 1}


def run_session(client, clock, max_steps=200, **params) -> list[dict]:
    """Drive a session like the frontend: queue -> (reveal|answer) -> review, until done/waiting."""
    reviewed = []
    last = None
    for _ in range(max_steps):
        q = client.get("/api/queue", params={**params, **({"exclude": last} if last else {})})
        assert q.status_code == 200, q.text
        body = q.json()
        if body["item"] is None:
            if body["waiting_until"]:
                clock.advance(minutes=11)
                continue
            return reviewed
        item = body["item"]
        assert item["front"] and item["sources"]
        if item["type"] in ("tf", "mcq"):
            assert item["answer"] is None and item["explanation"] is None  # withheld until graded
        else:
            assert item["back"]
        detail = client.get(f"/api/cards/{item['card_id']}").json()
        r = client.post(
            "/api/review",
            json={
                "item_id": item["item_id"],
                "mode": params.get("mode", "study"),
                "session_id": params.get("session_id"),
                "duration_ms": 1234,
                **answer_payload(detail),
            },
        )
        assert r.status_code == 200, r.text
        res = r.json()
        if item["type"] in ("tf", "mcq"):
            assert res["auto_graded"] and res["correct"] is True and res["rating"] == 3
            assert res["correct_answer"] == detail["card"]["answer"]
            assert res["explanation"] == detail["card"]["explanation"]
        reviewed.append({"item": item, "result": res})
        last = item["item_id"]
    raise AssertionError("session did not finish")


def test_health_and_meta(client):
    h = client.get("/api/health").json()
    assert h == {"status": "ok", "version": "0.1.0", "cards": 10, "items": 11, "orphans": 0}
    meta = client.get("/api/meta").json()
    assert [lec["id"] for lec in meta["lectures"]] == ["04a", "04b", "05a"]
    assert meta["lectures"][0]["counts"]["exam_official"] == 2
    assert meta["settings"]["desired_retention"] == 0.9
    assert "wrong" in meta["report_reasons"]


def test_full_study_session_every_card_type(client, clock):
    reviews = run_session(client, clock, session_id="s1")
    types = {r["item"]["type"] for r in reviews}
    assert types == {"basic", "cloze", "tf", "mcq"}
    items = {r["item"]["item_id"] for r in reviews}
    assert "04a-cloze::c1" in items and "04a-cloze::c2" not in items  # sibling buried until tomorrow
    # learning steps: each new item rated Good comes back once after 10 min, then graduates
    assert all(r["result"]["state"] in ("learning", "review") for r in reviews)
    s = client.get("/api/session/s1/summary").json()
    assert s["reviews"] == len(reviews) and s["auto_graded"] == s["auto_correct"] > 0
    assert s["duration_ms"] == 1234 * len(reviews)
    ov = client.get("/api/stats/overview").json()
    assert ov["today"]["reviews"] == len(reviews) and ov["streak"] == 1


def test_cloze_item_rendering(client):
    q = client.get("/api/queue", params={"types": "cloze"}).json()
    item = q["item"]
    assert item["item_id"] == "04a-cloze::c1"
    assert "\ue000[…]\ue001" in item["front"] and "$O(1/\\sqrt{N})$" in item["front"]
    assert "\ue000$\\sqrt{" in item["back"]
    assert set(item["previews"]) == {"1", "2", "3", "4"}


@pytest.mark.parametrize(
    "params",
    [
        {"mode": "exam"},
        {"mode": "exam", "include_not_due": "true", "session_id": "e"},
        {"mode": "drill", "session_id": "d", "limit": 4},
        {"mode": "study", "lectures": "04b"},
        {"mode": "study", "weeks": "4", "core": "true", "origins": "concept,exam_style"},
    ],
)
def test_every_mode_runs_to_completion(client, clock, params):
    reviews = run_session(client, clock, **params)
    assert reviews
    if params["mode"] == "exam":
        assert {r["item"]["origin"] for r in reviews} <= {"exam_official", "exam_style"}
        assert all(r["item"]["type"] in ("tf", "mcq") for r in reviews)
    if params.get("limit"):
        assert len(reviews) == params["limit"]


def test_weak_mode_session(client, clock):
    run_session(client, clock, session_id="first")
    clock.advance(days=30)
    detail = client.get("/api/cards/exam-2023-q30").json()
    r = client.post("/api/review", json={"item_id": "exam-2023-q30", **answer_payload(detail, correct=False)}).json()
    assert r["rating"] == 1 and r["correct"] is False
    q = client.get("/api/queue", params={"mode": "weak", "session_id": "w"}).json()
    assert q["item"]["item_id"] == "exam-2023-q30"
    weakest = client.get("/api/stats/weakest").json()["items"]
    assert weakest[0]["item_id"] == "exam-2023-q30"


def test_guessed_and_too_easy(client):
    g = client.post("/api/review", json={"item_id": "04a-tf", "answer": True, "guessed": True}).json()
    assert g["rating"] == 2
    e = client.post("/api/review", json={"item_id": "exam-2023-q30", "answer": False, "too_easy": True}).json()
    assert e["rating"] == 4 and e["state"] == "review"


def test_review_validation_errors(client):
    assert client.post("/api/review", json={"item_id": "nope", "rating": 3}).status_code == 404
    assert client.post("/api/review", json={"item_id": "04a-basic"}).status_code == 400  # missing rating
    assert client.post("/api/review", json={"item_id": "04a-tf", "rating": 3}).status_code == 400  # needs answer
    assert client.post("/api/review", json={"item_id": "04a-basic", "rating": 7}).status_code == 422
    assert client.post("/api/review", json={"item_id": "05a-x", "rating": 3}).status_code == 200  # inactive allowed
    assert client.get("/api/queue", params={"mode": "nope"}).status_code == 422
    assert client.get("/api/queue", params={"weeks": "x"}).status_code == 400


def test_undo_restores_previous_state(client, conn):
    before = dict(conn.execute("SELECT * FROM items WHERE item_id = '04a-basic'").fetchone())
    client.post("/api/review", json={"item_id": "04a-basic", "rating": 4, "session_id": "u"})
    assert conn.execute("SELECT state FROM items WHERE item_id = '04a-basic'").fetchone()[0] == "review"
    u = client.post("/api/undo", json={"session_id": "u"}).json()
    assert u["item_id"] == "04a-basic"
    view = client.get("/api/items/04a-basic").json()
    assert view["item_id"] == "04a-basic" and view["state"] == "new"
    assert client.get("/api/items/exam-2023-q30").json()["answer"] is None
    assert client.get("/api/items/nope").status_code == 404
    after = dict(conn.execute("SELECT * FROM items WHERE item_id = '04a-basic'").fetchone())
    assert after == before
    assert conn.execute("SELECT COUNT(*) FROM review_log").fetchone()[0] == 0
    assert client.post("/api/undo", json={}).status_code == 404


def test_suspend_unsuspend(client):
    assert client.post("/api/items/04a-basic/suspend").json()["suspended"] is True
    assert client.get("/api/queue").json()["item"]["item_id"] != "04a-basic"
    assert client.post("/api/review", json={"item_id": "04a-basic", "rating": 3}).status_code == 400
    client.post("/api/items/04a-basic/unsuspend")
    assert client.get("/api/queue").json()["item"]["item_id"] == "04a-basic"
    assert client.post("/api/items/nope/suspend").status_code == 404


def test_reports_round_trip(client, cli_env):
    r = client.post(
        "/api/reports",
        json={"card_id": "04a-cloze", "item_id": "04a-cloze::c2", "reason": "unclear", "comment": "rate is ambiguous"},
    )
    assert r.status_code == 200
    rid = r.json()["id"]
    assert client.post("/api/reports", json={"card_id": "04a-cloze", "reason": "meh"}).status_code == 400
    assert client.post("/api/reports", json={"card_id": "zzz", "reason": "typo"}).status_code == 400
    assert (
        client.post(
            "/api/reports", json={"card_id": "04a-tf", "item_id": "04a-cloze::c1", "reason": "typo"}
        ).status_code
        == 400
    )
    assert [x["id"] for x in client.get("/api/reports", params={"status": "open"}).json()["reports"]] == [rid]
    # CLI listing (what Claude reads at the start of a content session)
    out = CliRunner().invoke(cli_env, ["reports", "list"])
    assert out.exit_code == 0 and "unclear" in out.output and "cards/04a.yaml" in out.output
    res = client.post(f"/api/reports/{rid}/resolve", json={"note": "reworded"}).json()
    assert res["status"] == "resolved" and res["resolution_note"] == "reworded"
    assert client.post(f"/api/reports/{rid}/resolve", json={"note": "again"}).status_code == 400
    assert client.get("/api/reports", params={"status": "open"}).json()["reports"] == []


def test_browse_and_card_detail(client):
    all_cards = client.get("/api/cards").json()
    assert all_cards["total"] == 10
    assert client.get("/api/cards", params={"include_inactive": "false"}).json()["total"] == 8
    hits = client.get("/api/cards", params={"q": "true risk"}).json()["cards"]
    assert [c["id"] for c in hits] == ["04a-basic"]
    assert client.get("/api/cards", params={"origins": "exam_official"}).json()["total"] == 2
    d = client.get("/api/cards/04a-cloze").json()
    assert len(d["items"]) == 2 and d["items"][0]["state"]["retrievability"] is None
    d = client.get("/api/cards/exam-2025-q24").json()
    assert d["exam_label"] == "Final 2025 Q24" and d["items"][0]["view"]["answer"] == [0]
    assert d["card"]["sources"][0]["page_url"].startswith("/api/source/page?pdf=exam/")
    assert d["card"]["sources"][0]["page_count"] == 3
    assert client.get("/api/cards/nope").status_code == 404


def test_source_page_and_files_whitelist(client):
    r = client.get("/api/source/page", params={"pdf": "lectures/04/lecture04a.pdf", "page": 2, "scale": 1})
    assert r.status_code == 200 and r.headers["content-type"] == "image/png" and r.content[:4] == b"\x89PNG"
    again = client.get("/api/source/page", params={"pdf": "lectures/04/lecture04a.pdf", "page": 2, "scale": 1})
    assert again.content == r.content  # served from cache
    for bad in [
        ("lectures/04/lecture04a.pdf", 9),
        ("lectures/../secret.txt", 1),
        ("secret.txt", 1),
        ("/etc/passwd", 1),
        ("lectures/04/missing.pdf", 1),
    ]:
        assert client.get("/api/source/page", params={"pdf": bad[0], "page": bad[1]}).status_code == 404, bad
    assert client.get("/files/lectures/04/lecture04a.pdf").status_code == 200
    assert client.get("/files/labs/ex04/exercise04.pdf").status_code == 200
    assert client.get("/files/secret.txt").status_code == 404
    assert client.get("/files/lectures/%2e%2e/secret.txt").status_code == 404
    assert client.get("/content-img/img/exam-2025-q24.png").status_code == 200
    assert client.get("/content-img/course.yaml").status_code == 404
    assert client.get("/content-img/img/../course.yaml").status_code == 404


def test_settings(client):
    s = client.put("/api/settings", json={"desired_retention": 0.85, "new_per_day": 5}).json()
    assert s["desired_retention"] == 0.85 and s["new_per_day"] == 5
    assert client.get("/api/settings").json()["new_per_day"] == 5
    assert client.put("/api/settings", json={"desired_retention": 0.5}).status_code == 422
    assert client.put("/api/settings", json={"unknown": 1}).status_code == 422
    assert client.get("/api/queue").json()["counts"]["new"] == 5


def test_stats_endpoints(client, clock):
    run_session(client, clock, session_id="s")
    clock.advance(days=3)
    for path in ("overview", "calendar", "forecast", "by-lecture", "by-theme", "exam", "weakest"):
        r = client.get(f"/api/stats/{path}")
        assert r.status_code == 200, path
    lec = {x["key"]: x for x in client.get("/api/stats/by-lecture").json()["lectures"]}
    assert lec["04a"]["seen"] > 0 and "05a" not in lec
    exam = client.get("/api/stats/exam").json()
    assert {x["key"] for x in exam["by_origin"]} == {"exam_official", "exam_style"}
    assert {x["key"] for x in exam["by_year"]} == {"2023", "2025"}
    cal = client.get("/api/stats/calendar", params={"days": 7}).json()
    assert len(cal["days"]) == 7 and cal["days"][-4]["reviews"] > 0
    fc = client.get("/api/stats/forecast").json()["days"]
    assert sum(d["due"] for d in fc) > 0


def test_export_and_backup(client, cfg, conn, clock):
    client.post("/api/review", json={"item_id": "04a-basic", "rating": 3})
    data = client.get("/api/export").json()
    assert len(data["review_log"]) == 1 and len(data["items"]) == 11 and data["schema_version"] == 1
    from revision.db import backup

    out = backup(conn, cfg.backup_dir, clock(), keep=2)
    assert out.exists()
    for _ in range(3):
        clock.advance(minutes=1)
        backup(conn, cfg.backup_dir, clock(), keep=2)
    assert len(list(cfg.backup_dir.glob("revision-*.db"))) == 2


def test_reload_content(client, cfg, tree):
    tree["files"]["cards/04b.yaml"].append({**tree["files"]["cards/04b.yaml"][0], "id": "04b-bias", "front": "Bias?"})
    write_content(cfg.content_dir, tree)
    r = client.post("/api/admin/reload").json()
    assert r["added"] == 1 and r["cards"] == 11
    tree["files"]["cards/04b.yaml"][0]["themes"] = ["nope"]
    write_content(cfg.content_dir, tree)
    bad = client.post("/api/admin/reload")
    assert bad.status_code == 422 and "unknown theme" in bad.json()["detail"]["errors"][0]
    assert client.get("/api/health").json()["cards"] == 11  # old content kept


def test_app_refuses_to_start_on_bad_content(cfg, tree, clock):
    tree["files"]["cards/04a.yaml"][0]["back"] = "TODO"
    write_content(cfg.content_dir, tree)
    with pytest.raises(ContentError):
        create_app(cfg, clock=clock)


def test_spa_fallback(cfg, clock, tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>app</html>")
    (dist / "assets" / "a.js").write_text("js")
    from dataclasses import replace

    c = TestClient(create_app(replace(cfg, frontend_dist=dist), clock=clock))
    assert c.get("/").text == "<html>app</html>"
    assert c.get("/review").text == "<html>app</html>"
    assert c.get("/assets/a.js").text == "js"
    assert c.get("/api/unknown").status_code == 404
    no_dist = TestClient(create_app(cfg, clock=clock))
    assert no_dist.get("/").status_code == 503


# --------------------------------------------------------------------------- CLI


@pytest.fixture
def cli_env(cfg, monkeypatch):
    monkeypatch.setenv("REVISION_REPO_ROOT", str(cfg.repo_root))
    monkeypatch.setenv("REVISION_CONTENT_DIR", str(cfg.content_dir))
    monkeypatch.setenv("REVISION_DATA_DIR", str(cfg.data_dir))
    from revision.cli import app

    return app


def test_cli_content_check(cli_env, cfg, tree):
    ok = CliRunner().invoke(cli_env, ["content", "check"])
    assert ok.exit_code == 0 and "OK — 10 cards" in ok.output
    tree["files"]["cards/04a.yaml"][0]["themes"] = ["nope"]
    write_content(cfg.content_dir, tree)
    bad = CliRunner().invoke(cli_env, ["content", "check"])
    assert bad.exit_code == 1 and "unknown theme 'nope'" in bad.output


def test_cli_backup_export_resolve(cli_env, cfg, tmp_path):
    runner = CliRunner()
    assert runner.invoke(cli_env, ["backup"]).exit_code == 0
    out = tmp_path / "dump.json"
    assert runner.invoke(cli_env, ["export", "-o", str(out)]).exit_code == 0 and out.exists()
    assert runner.invoke(cli_env, ["reports", "resolve", "99", "--note", "x"]).exit_code == 1
    assert "No reports" in runner.invoke(cli_env, ["reports", "list"]).output
