# Projects

Both projects: groups of **3** (2 only in exceptional cases, with approval), Python code + PDF report. Interdisciplinary teams recommended; find teammates on the Ed forum. Info verified 2026-09-14 from the info sheet + website. Descriptions are not published yet (links 404 as of 2026-09-14):
- P1: https://github.com/epfml/ML_course/raw/main/projects/project1/project1_description.pdf
- P2: https://github.com/epfml/ML_course/raw/main/projects/project2/project2_description.pdf

When a description is published: pull it into `projects/projectN/`, summarize it here (tasks, dataset, deliverables, grading rubric, submission platform), and create `projects/projectN/CLAUDE.md`.

## Project 1 — not formally graded ("prepares you for Project 2")
2026 description not yet published. Everything below marked *(2025)* comes from the 2025 description recovered from git history (see `docs/history-2025.md`); the format has been stable 2023–2025, expect the same.

| Item | Value |
|---|---|
| Start | 2026-09-16 (lab of week 2; 2025: launched 09-18) |
| Deadline | **2026-10-29** (website, slides, info-sheet §Assessment). ⚠ Info-sheet §Project 1 says "Nov 1st" — confirm on Ed. 2025 deadline was Fri 16:00 sharp. |
| Team | 3 students, own choice (Ed forum to find teammates) |
| Grading | not graded in 2026 (2025: 10 %, code 40 % / report 60 %). Still: it is the toolbox for P2 and the exam. |
| Allowed libs *(2025)* | **Python stdlib + NumPy only**; matplotlib/seaborn for plots only. No pandas, sklearn, torch. No external data/code. |
| Task *(2025)* | Binary classification: predict coronary heart disease (MICHD) from BRFSS 2015 lifestyle survey (>300k people). Data: `x_train.csv`, `y_train.csv` (labels −1/1), `x_test.csv`; load with `helpers.load_csv_data`, submit with `create_csv_submission`. |
| Competition | AICrowd https://www.aicrowd.com/challenges/epfl-machine-learning-project-1 — max 5 submissions/day, rank not graded; always use local validation/CV. |
| Deliverables *(2025)* | GitHub Classroom repo with `README.md`, `implementations.py`, `run.py` (or `run.ipynb`) reproducing the best submission exactly; **2-page LaTeX report** (refs on a 3rd page, no appendix). Submission via http://mlcourse.epfl.ch. Plagiarism check. |
| Public tests *(2025)* | `projects/project1/grading_tests/`: `pytest --github_link <repo-url> .` (or a local path). Format code with `black`. |

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

| Team / repo | TODO — not yet formed (as of 2026-09-14) |
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
| Topic / lab / team | TODO — not yet decided (as of 2026-09-14) |

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
| Fallback (no lab) | course-provided default tasks (if offered in 2026) | AIcrowd road segmentation, tweet text classification, recommender system; reproducibility challenge |
