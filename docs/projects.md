# Projects

Both projects: groups of **3** (2 only in exceptional cases, with approval), Python code + PDF report. Interdisciplinary teams recommended; find teammates on the Ed forum. Info verified 2026-09-14 from the info sheet + website. Descriptions are not published yet (links 404 as of 2026-09-14):
- P1: https://github.com/epfml/ML_course/raw/main/projects/project1/project1_description.pdf
- P2: https://github.com/epfml/ML_course/raw/main/projects/project2/project2_description.pdf

When a description is published: pull it into `projects/projectN/`, summarize it here (tasks, dataset, deliverables, grading rubric, submission platform), and create `projects/projectN/CLAUDE.md`.

## Project 1 — not formally graded ("prepares you for Project 2")
**2026 description published 2026-09-17** (`projects/project1/project1_description.pdf`) — identical to 2025 except: deadline Thu 2026-10-29 16:00, not graded, code in a **public GitHub repo** of the team (no GitHub Classroom). Rows marked *(2025)* were verified identical in the 2026 text.

| Item | Value |
|---|---|
| Start | 2026-09-16 (lab of week 2; 2025: launched 09-18) |
| Deadline | **Thursday 2026-10-29, 16:00** (official description; the info sheet's "Nov 1st" was a typo). |
| Team | 3 students, own choice (Ed forum to find teammates) |
| Grading | not graded in 2026 (2025: 10 %, code 40 % / report 60 %). Still: it is the toolbox for P2 and the exam. |
| Allowed libs *(2025)* | **Python stdlib + NumPy only**; matplotlib/seaborn for plots only. No pandas, sklearn, torch. No external data/code. |
| Task *(2025)* | Binary classification: predict coronary heart disease (MICHD) from BRFSS 2015 lifestyle survey (>300k people). Data: `x_train.csv`, `y_train.csv` (labels −1/1), `x_test.csv`; load with `helpers.load_csv_data`, submit with `create_csv_submission`. |
| Competition | AICrowd https://www.aicrowd.com/challenges/epfl-machine-learning-project-1 — max 5 submissions/day, rank not graded; always use local validation/CV. |
| Deliverables | **Public GitHub repo** of the team with `README.md`, `implementations.py`, `run.py` (or `run.ipynb`) reproducing the best submission exactly; **2-page LaTeX report** (refs on a 3rd page, no appendix). Submission via http://mlcourse.epfl.ch. Plagiarism check (MOSS). |
| Public tests | `projects/project1/grading_tests/`: `pytest --github_link <repo-url-or-local-path> .` — checks the 6 signatures/return types. Conda env in `environment.yml` (python 3.9, numpy 1.23). Format code with `black`. |
| Starter files | Pushed upstream 2026-09-21/22, in repo since 2026-09-24: `helpers.py` (`load_csv_data`, `create_csv_submission`), `data/dataset_to_release.zip`, `latex-example-paper/` (IEEE template for the report). |
| Leaked grading material (2026-09-17, resolved 2026-09-18) | Upstream had accidentally pushed `solutions.py`, `test_project1_private.py`, `moss.pl`, an internal `README.md` and two scripts into `grading_tests/`. Elie reported it; the prof rewrote upstream history (force-push, commit `22f74fa` "project 1 released") and the files were removed from this repo on 2026-09-18 (they remain in this fork's history before that date — do not use them). |

Required functions *(2025 Table 1; all in `implementations.py`, all return `(w, loss)` with `w` the **last** iterate; loss of regularized methods **excludes** the penalty; vectors are 1-D `(D,)`; MSE has the ½ factor; SGD uses batch size 1; `numpy.linalg` allowed except `lstsq`)*:
| Function | Method |
|---|---|
| `mean_squared_error_gd(y, tx, initial_w, max_iters, gamma)` | linear regression, GD |
| `mean_squared_error_sgd(y, tx, initial_w, max_iters, gamma)` | linear regression, SGD (batch 1) |
| `least_squares(y, tx)` | normal equations |
| `ridge_regression(y, tx, lambda_)` | normal equations |
| `logistic_regression(y, tx, initial_w, max_iters, gamma)` | y ∈ {0,1}, GD |
| `reg_logistic_regression(y, tx, lambda_, initial_w, max_iters, gamma)` | y ∈ {0,1}, GD, penalty λ‖w‖² |

Report grading criteria *(2025)*: correct implementation + explanation (half), then scientific contribution: novelty, creativity, reproducibility (all hyperparameters, folds, transformations), solid baselines + **ablation study**, write-up quality. Target reader: ML beginner. Advice in description: EDA, feature processing, over/underfitting diagnosis, error analysis, CV.

| Team | **Elie, Gabin, Antoine** (formed 2026-09-15). Team registered on AICrowd (2026-09-24). Repo (public, owned by Antoine): https://github.com/antoinemdly/ML_2026_Project_1 |
|---|---|

## Project 2 — 30 % of the grade
2026 description not yet published; 2025 version (recovered from git, published 2025-10-09) is the reference below.

| Item | Value |
|---|---|
| Start | 2026-11-03 (week 9) |
| Deadline | **2026-12-17** (2025: 16:00 sharp) |
| Team | 3 students (may differ from P1). 2025: if no team by 11-18, contact staff. |
| Two options *(2025)* | **A — ML4Science**: project with any lab of the (extended) EPFL campus or Swiss academic institution (EPFL, UniL, CERN, CHUV, Idiap…); the **lab's professor must confirm via the registration form by early Nov** (2025: 11-04); the lab co-grades domain merit. **B — predefined AICrowd challenge**: text classification (tweets) https://www.aicrowd.com/challenges/epfl-ml-text-classification or road segmentation (aerial images) https://www.aicrowd.com/challenges/epfl-ml-road-segmentation; leaderboard rank mapped linearly to 4–6 for the competitive part; 5 submissions/person/day. |
| Allowed | External libraries, models, datasets **allowed if cited** (PyTorch etc.). LauzHack PyTorch project template recommended (Hydra, pre-commit). |
| Deliverables | **4-page LaTeX report** (+ refs, acknowledgements, optional appendix) with a **meaningful title**; GitHub Classroom repo with README, reproducible code (`run.py` reproducing the AICrowd submission for option B; pretrained weights when possible). Submission via http://mlcourse.epfl.ch. |
| **Ethical risks section** *(2025, mandatory, graded)* | 200–400 words, outside the 4-page limit, using the Digital Ethics Canvas. Either describe one identified risk (stakeholders, impact, severity/likelihood, how evaluated, how mitigated or why not) or justify ruling risks out (≥ 2 stakeholder categories incl. indirect/environment, evidence). |
| Grading criteria | solid baselines (start from a trivial baseline, quantify each addition), reproducibility, scientific novelty/creativity (what specific problem, why, how, results before/after), ethics component, write-up quality (clear story, labeled plots, proofread). Task difficulty is accounted for. |
| Support | Project Q&A during labs 2026-11-26 and 12-03; optional pitch session 2026-12-16 |
| Team | Elie, Gabin, Antoine (same as P1, to confirm) |
| Topic / lab | **In progress with SIP lab, UNIGE** (S. Voloshynovskiy + V. Kinakh). Contact email sent 2026-09-21; Slava replied the same day: "we will think — we might have a couple of ideas". No news as of 2026-09-30. Gentle follow-up (relays the staff answer, offers to draft title/description) **sent 2026-10-07**; no reply as of 2026-10-08. Second short follow-up 2026-10-14 (offering to meet at Battelle on Friday) → Slava asked Elie to call him; **phone call 2026-10-14**: Slava wants to make sure the project does **not need daily or weekly supervision** (the lab has little time for supervision). **Meeting in Slava's office at Battelle, Fri 2026-10-16 16:00**, to discuss the topic and fill in the form together. Elie to prepare: project type, approximate workload, how many contacts with the lab are needed and whether they go through Elie or the course staff. Plan: gentle follow-up ~2026-10-06 if silent, firmer one ~2026-10-17; form (filled by the lab) due 2026-10-24; confirmation 2026-11-04. Backup if it falls through: another lab from the list below or option B (AICrowd). |
| **2026 lab-hosting form** (Ed #78, M. Jaggi, 2026-09-20) | "Interest in hosting AI4Science projects, Fall 2026": https://docs.google.com/forms/d/e/1FAIpQLScSzxMRFDncTJ9CRgUmIh6aDCMyDpgSbM5KzH31Uq8iJUyKuQ/viewform — **filled by the lab**, not the students. Fields: organization, lab, website, head of lab, contact person + email, project title, description/objectives, data availability, data description + evaluation metrics, number of groups wanted. Deadlines: **2026-10-24** expression of interest; **2026-11-04** lab head confirms; 2026-12-17 submission; Jan 2027 lab suggests domain grade. Eligible: any academic lab in Switzerland or beyond; international institutions, NGOs, companies if in collaboration with academia (contact staff). Jaggi (Ed, 2026-09-23): P2 "not officially released yet", so no PDF; the form "has all the info that we give to the hosting labs". The form has no field naming a student team. Open question (asked on Ed 2026-09-24, unanswered; then by email to the course staff): is a lab project proposed on a team's initiative reserved for that team? Answer (email, ~2026-10): "this is up to the lab, as they prefer. if they are ready to confirm you already, that's fine too. note they are also allowed to host more than one group if they like". Says nothing about skipping the form: assume the lab still fills it in by 2026-10-24 and names the team in the description. |

**Form intro re-read 2026-10-16** (facts usable with a host lab): AI4Science initiative, ~600 MSc students; students work **part-time** in groups of 3 from early Nov to 2026-12-17; **≈ 2 ECTS per student** (course = 8 ECTS, project = 30 %), i.e. roughly 50–60 h per student (Bologna 25–30 h/ECTS; estimate, not stated by the course); students contact the lab directly; no detailed proposal needed at the expression-of-interest stage (think dataset, question/prediction task, evaluation metric); expressing interest does not commit the lab; submissions are visible to students as they arrive; lab head confirms the hosted group(s) by 2026-11-04 via a separate form; January 2027: lab head suggests a grade for domain-specific merit, the teaching team grades the technical part. Nothing in the form or on the ML4Science page specifies a meeting frequency (only "reachable for occasional questions"). 2025 description: code in a **private** GitHub Classroom repo (lab data need not be public), lab "will help us grading the domain-specific merit". Course contacts: Martin Jaggi, Simin Fan, Gizem Yüce.

**SIP public CDP resources (checked 2026-10-16):** `github.com/sip-group/snf-it-dis` lists public, academic-use-only datasets — IndigoMobile (300 DataMatrix templates, 300 originals printed on HP Indigo 5500, 1,200 fakes from 2 copiers × 2 papers, iPhone XS captures; paper Taran et al. arXiv 2110.01864, WIFS 2021 / EURASIP JIS 2023), Indigo1x1_base (2 Indigo printers, scanner captures), Indigo1x1_variability — downloads on `sipcloud.unige.ch`; code for 10 papers on `gitlab.unige.ch/sip-group` (mobile CDP auth, ML attacks on CDP, supervised auth under ML attacks ICIP 2022, anomaly localization WIFS 2022, digital twin WIFS 2022, adversarial defenses). Candidate P2 angle: authentication against **unseen** fakes (leave-one-fake-type-out), classical baselines (logistic/SVM/k-NN on template-correlation features) vs one-class vs CNN, ML-based fakes (stated future work of the paper).

**Meeting with Slava + Vitaliy, Battelle, 2026-10-16 16:00 — outcome:** Slava **filled in the expression-of-interest form**. Watermarking topics were discussed but judged too deep-learning-heavy; agreed direction = **copy detection patterns (CDP)**, building on **Joakim Tutt's PhD thesis** (UNIGE, Dec 2025, advisor Voloshynovskiy; "Un modèle mathématique d'impression et d'imagerie pour l'authentification des codes de détection de copie", doi 10.13097/archive-ouverte/unige:192628, CC BY 4.0, PDF in English; local copy in Elie's Downloads). Reference paper + **reference code (on request)** + data (public links exist, see below). Supervision must stay light (no weekly meetings).
**Thesis in brief:** ch. 3 deep encoder–decoder "digital twin" of the printing–imaging channel (Indigo mobile; unstable across seeds); ch. 4 **BPC model** (Binary Pattern-based Channel): bit-flip probability of each symbol depends on its 3×3 neighbourhood pattern ω (512 patterns) → **codebook** Pb(ω) estimated from (template t, Otsu-binarized capture t̃) pairs; **PLL** score = Σ log πᵢⱼ; ch. 5 authentication with PLL and **masked metrics** (keep only reliable patterns Pb(ω) ≤ µ = 0.01): Hamming error drops from ~21 % to ~0.9 % (iPhone), cross-device slightly worse; **SVM baseline on 512-d codebook features**: 1-class 21.9 % → 2.3 % masked (iPhone), 2-class 0 % (but needs fakes; ⚠ hyperparameters tuned on the test set); ch. 6 Hamming test as binomial hypothesis test, Neyman–Pearson bounds, aggregation strategies (S1 average, S2 reliable patterns, S3 min-Perr, S4 linear 2C-SVM coefficients), multi-shot fusion of the 6 captures. Future work stated: other datasets/devices, **cross-device**, unseen fakes ("2C-SVM should be prone to errors against unseen fakes" — conjecture), relax independence (Ising-like correlations), non-stationarity, template design.
**Dataset of the thesis = Indigo 1x1 base:** 1,440 templates 228×228; printers HP Indigo 5500 & 7600; captures iPhone 12 Pro + Samsung Note 20 Ultra (6 runs each, originals + ML-based fakes on HPI55) and Epson scanner 2400 dpi (720 templates, originals from both printers + 4 fake combos f^{mm/nn}). Thesis link https://sipcloud.unige.ch/index.php/s/tYKffnKNRgSwBAN (snf-it-dis README gives …/TBzWKaCS77tcYPa); sipcloud did not answer from Claude's network on 2026-10-17 — test from EPFL/UNIGE network or ask the lab.
**Data/code check 2026-10-19:** `github.com/sip-group/snf-it-dis-code` (updated 2026-02) holds code for ~10 SIP papers incl. **`pattern-reliability/`** = code of the BPC/pattern-reliability work (WIFS 2022 / TIFS 2024, thesis ch. 4–5): `predictor_functions.py` (train_codebook, predict, Otsu + majority voting), `cdp_metrics.py` (MSE, PCOR, L1, Hamming, LLS…), PyTorch `Dataset_cdp*.py` for 'scanner'/'iphone'/'samsung', notebooks measure_codebook / measure_weighted_metrics; data paths point to the lab's internal server (gallager.unige.ch, SSH key needed). `datasets/indigo1x1base/` contains **only a README** (no data): public release = **scanner only** (720 templates × 5 densities, 7,200 originals HPI55/76 at 6400 dpi, 2,880 ML-based fakes at 2400 dpi, density 50 %), download on sipcloud (…/TBzWKaCS77tcYPa). The smartphone captures used in thesis ch. 5–6 (1,440 templates, iPhone/Samsung) are behind the thesis link (…/tYKffnKNRgSwBAN). Both sipcloud links and sip.unige.ch time out from Claude's network (www.unige.ch answers) → ask Vitaliy for access / confirm whether the phone data are public.
**Project angle (draft, 2026-10-17):** reproduce codebook features + masked Hamming/PLL baselines; then course-ML on the 512-d codebook vectors with proper CV (logistic, L1-logistic for pattern selection vs S2/S4, SVM 1C/2C, k-NN); protocols for **unseen fakes** (scanner subset: leave-one-fake-combo-out), **cross-device** (iPhone ↔ Samsung) and **cross-printer**; optional CNN baseline on raw images.

Lecture 01a slides list hundreds of past ML4Science project titles (2020–2024) — useful for inspiration; grep `lectures/01/lecture01a_intro.pdf` text if needed.

## Candidate host labs for Project 2 (research done 2026-09-14)
Official 2026 list not yet published. Labs below hosted ML4Science groups in 2021–2025 (sources: student repos on GitHub `CS-433/ml-project-2-*`, MLO ML4Science archive https://www.epfl.ch/labs/mlo/?p=1027, lecture 01a project titles). Recurring hosts (several years) marked ★. Contact early (Sept–Oct); approval deadline early November.

| Domain | Lab (EPFL unless noted) | Past project examples |
|---|---|---|
| LLMs / NLP | ★ Swiss AI Initiative (`swiss-ai`, Apertus LLM) | Apertus RAG evaluation, output-embedding/vocab optimization, image+audio→text instruction data, OCR benchmarking (2025) |
| LLMs / NLP | ★ Data Science Lab (DLAB, R. West) | Homepage2Vec multilingual website classification with LLM-generated data |
| LLMs / NLP | ML4ED (T. Käser) — has a public student-projects page | learner modeling with LLMs, knowledge tracing |
| LLMs / NLP | LSIR | argument quality / stance detection with LLMs |
| LLMs / NLP | Meditron / LiGHT (M. Jaggi, A. Bosselut) | medical LLM instruction tuning, Meditron-V, MiniMeditron reward models |
| Computer vision | ★ VITA (A. Alahi) | pose estimation (goalkeeping), trajectory prediction, camera localization |
| Computer vision | ★ EPFL Center for Imaging | image filtering/denoising, generalist microscopy segmentation (MEDIAR) |
| Computer vision | ★ LESO-PB | rooftop PV area detection from aerial images (many years) |
| Computer vision | LTS4 (P. Frossard) | whole-slide image resolution vs foundation models (pathology) |
| Computer vision / digital humanities | DHLAB, MetaMedia Center, CAI (HES-SO) | illustration descriptors, concert recordings, handwritten chess-notation recognition ★ |
| Neuro / medical | ★ TNE (S. Micera) | vagus-nerve histology segmentation, EEG/intracortical decoding |
| Neuro / medical | ★ UPHummel (F. Hummel), MIP:Lab (D. Van De Ville), CIBM | stroke prediction from neuronal avalanches, brain age, fMRI decoding, MRSI |
| Neuro / medical | CHUV / HUG / iGH (M. Hartley, MLO) | clinical decision support (MoDN), COVID prognosis, respiratory disease from lung sounds |
| Neuro / medical | ETH Sensory-Motor Systems Lab | depression from passive phone data |
| Biology | ★ LPBS (S. Rahi), ★ Oates lab (UPOATES) | yeast cell segmentation, C. elegans lifespan/optogenetics, zebrafish PSM segmentation |
| Biology | LCSB, MACE, Galland & Quack group, Chemical-ML | protein/lipid prediction, flow-cytometry classifiers, neuron growth segmentation |
| Biology / chemistry | COSMO (M. Ceriotti), LCMD | NMR shift prediction, ML force fields, SMILES/SELFIES property prediction |
| Physics | ★ Swiss Plasma Center (TCV tokamak) | H-mode regime classification, MHD spectrogram pattern recognition, disruption detection |
| Physics / space | LASTRO, CASBI, ESA collaboration | reionisation, chemical-abundance simulation-based inference, CME detection on Venus Express |
| Engineering | ★ ICE lab, LIPID, LESO (ENAC) | sensible heat flux from chair sensors, glare detection, daylight/view-out |
| Engineering | SCI-SB-SD (hemodynamics), LMS/structures, LAPD (photonics) | POD-DL-ROM for hemodynamics, GNN FEM stress prediction, AAR crack detection, photonic devices |
| Engineering | Laboratory of Sensing and Networking (SENS) | Radar4K super-resolution on SLAM-RF |
| Environment | ECOL, WSL, LCH, ML for lake/plume | traffic generation, Rhône plume shape, plankton detection, Greenland landscape classification |
| Economics / transport | TRANSP-OR (M. Bierlaire), CDM labs | mode-choice prediction, discrete choice models, volatility forecasting |
| Security / imaging (UNIGE) | **SIP — Stochastic Information Processing, Univ. de Genève (Prof. S. Voloshynovskiy, svolos@unige.ch)** — Elie's idea 2026-09-21. Topics: anti-counterfeiting with copy detection patterns (CDP) + diffusion models, adversarial robustness, privacy of DL, information-theoretic view of foundation models, generative models for radio astronomy (Sinergia "Astro Signals" with Obs. de Genève), high-energy physics (RODEM). ~13 PhD students, ~300 papers. No trace of a previous CS-433 hosting found (as of 2026-09-21). | — |
| Fallback (no lab) | course-provided default tasks (if offered in 2026) | AIcrowd road segmentation, tweet text classification, recommender system; reproducibility challenge |
