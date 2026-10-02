"""`uv run revision …` command line."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import typer

from revision.config import DEFAULT_PORT, load_config

app = typer.Typer(help="CS-433 revision app (spaced repetition).", no_args_is_help=True, pretty_exceptions_enable=False)
content_app = typer.Typer(help="Card content commands.", no_args_is_help=True)
reports_app = typer.Typer(help="Card reports (flags raised from the app).", no_args_is_help=True)
app.add_typer(content_app, name="content")
app.add_typer(reports_app, name="reports")


def _now() -> datetime:
    return datetime.now(UTC)


def _load_or_exit():
    from revision.content import ContentError, load_content

    cfg = load_config()
    try:
        content = load_content(cfg.content_dir, cfg.repo_root)
    except ContentError as e:
        for w in e.warnings:
            typer.secho(f"warning: {w}", fg="yellow", err=True)
        for msg in e.errors:
            typer.secho(f"error: {msg}", fg="red", err=True)
        typer.secho(f"{len(e.errors)} error(s)", fg="red", err=True)
        sys.exit(1)
    return cfg, content


@content_app.command("check")
def content_check(
    db: bool = typer.Option(False, "--db", help="Also list DB items whose card/cloze disappeared (orphans)."),
) -> None:
    """Validate all content (SPEC §4.2). Exit code 1 on error."""
    cfg, content = _load_or_exit()
    for w in content.warnings:
        typer.secho(f"warning: {w}", fg="yellow", err=True)
    by_origin: dict[str, int] = {}
    for lc in content.cards:
        by_origin[lc.card.origin] = by_origin.get(lc.card.origin, 0) + 1
    detail = ", ".join(f"{k} {v}" for k, v in sorted(by_origin.items()))
    typer.secho(
        f"OK — {len(content.cards)} cards ({detail}), {len(content.items)} review items, "
        f"{len(content.course.lectures)} lectures",
        fg="green",
    )
    if db:
        from revision.db import open_db, orphan_items

        if not cfg.db_path.exists():
            typer.echo("no database yet")
            return
        conn = open_db(cfg.db_path)
        orphans = orphan_items(conn, content)
        conn.close()
        typer.echo(f"{len(orphans)} orphan item(s)")
        for r in orphans:
            typer.echo(f"  {r['item_id']} (reps {r['reps']})")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Bind address (keep localhost; expose with `tailscale serve`)."),
    port: int = typer.Option(DEFAULT_PORT),
    reload: bool = typer.Option(False, help="Dev: restart on backend or content changes."),
) -> None:
    """Run the web app (API + built frontend)."""
    import uvicorn

    _load_or_exit()  # fail fast with readable errors
    app_root = Path(__file__).resolve().parents[2]
    uvicorn.run(
        "revision.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(app_root / "backend" / "revision"), str(app_root / "content")] if reload else None,
        reload_includes=["*.py", "*.yaml"] if reload else None,
    )


@app.command()
def backup(keep: int = typer.Option(30, help="Number of backups to keep.")) -> None:
    """Online SQLite backup into DATA_DIR/backups/."""
    from revision.db import backup as do_backup
    from revision.db import open_db

    cfg = load_config()
    cfg.ensure_dirs()
    conn = open_db(cfg.db_path)
    try:
        out = do_backup(conn, cfg.backup_dir, _now(), keep)
    finally:
        conn.close()
    typer.echo(str(out))


@app.command()
def export(out: Path | None = typer.Option(None, "--out", "-o", help="Output file (default: stdout).")) -> None:
    """Full JSON dump of the database (items, review log, reports, settings)."""
    from revision.db import export_all, iso, open_db

    cfg = load_config()
    conn = open_db(cfg.db_path)
    try:
        data = export_all(conn)
    finally:
        conn.close()
    data["exported_utc"] = iso(_now())
    text = json.dumps(data, ensure_ascii=False, indent=1)
    if out:
        out.write_text(text, encoding="utf-8")
        typer.echo(f"wrote {out}")
    else:
        typer.echo(text)


@reports_app.command("list")
def reports_list(
    open_only: bool = typer.Option(True, "--open/--all", help="Only open reports (default) or all."),
) -> None:
    """Markdown list of reports (start of every content session)."""
    from revision.content import ContentError, load_content
    from revision.db import open_db
    from revision.reports import list_reports, reports_markdown

    cfg = load_config()
    try:
        content = load_content(cfg.content_dir, cfg.repo_root)
    except ContentError:
        content = None
    conn = open_db(cfg.db_path)
    try:
        reports = list_reports(conn, "open" if open_only else None)
    finally:
        conn.close()
    typer.echo(reports_markdown(reports, content))


@reports_app.command("resolve")
def reports_resolve(report_id: int, note: str = typer.Option(..., "--note", help="What was done.")) -> None:
    """Mark a report as resolved."""
    from revision.db import open_db
    from revision.reports import ReportError, resolve_report

    cfg = load_config()
    conn = open_db(cfg.db_path)
    try:
        resolve_report(conn, report_id, note, _now())
    except ReportError as e:
        typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    finally:
        conn.close()
    typer.echo(f"report #{report_id} resolved")
