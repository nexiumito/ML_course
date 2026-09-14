# Projects

Both projects: groups of **3** (2 only in exceptional cases, with approval), Python code + PDF report. Interdisciplinary teams recommended; find teammates on the Ed forum. Info verified 2026-09-14 from the info sheet + website. Descriptions are not published yet (links 404 as of 2026-09-14):
- P1: https://github.com/epfml/ML_course/raw/main/projects/project1/project1_description.pdf
- P2: https://github.com/epfml/ML_course/raw/main/projects/project2/project2_description.pdf

When a description is published: pull it into `projects/projectN/`, summarize it here (tasks, dataset, deliverables, grading rubric, submission platform), and create `projects/projectN/CLAUDE.md`.

## Project 1 — not formally graded ("prepares you for Project 2")
| Item | Value |
|---|---|
| Start | 2026-09-16 (lab of week 2) |
| Deadline | **2026-10-29** (website, lecture slides, info-sheet §Assessment). ⚠ Info-sheet §Project 1 says "Nov 1st" — inconsistency, confirm on Ed. |
| Team | 3 students, own choice |
| Content | Implement the most important methods from lectures/labs so far (past years: `least_squares_GD`, `least_squares_SGD`, `least_squares`, `ridge_regression`, `logistic_regression`, `reg_logistic_regression` in an `implementations.py`, NumPy only) — TODO confirm 2026 list when published |
| Data / competition | Real-world dataset, AICrowd competition: https://www.aicrowd.com/challenges/epfl-machine-learning-project-1 |
| Deliverables | Python code + **2-page PDF report** (LaTeX preferred) |
| Grading | not graded in 2026 (was 10 % in 2025) |
| Team / repo | TODO — not yet formed (as of 2026-09-14) |

## Project 2 — 30 % of the grade (ML4Science)
| Item | Value |
|---|---|
| Start | 2026-11-03 (week 9) |
| Deadline | **2026-12-17** (all cases) |
| Team | 3 students |
| Format | Pick a real-world challenge from any EPFL research group or Swiss academic institution: https://www.epfl.ch/labs/mlo/ml4science/. List of ideas published later (subject to availability); students may contact labs directly early in the semester. |
| Approval | Idea must be approved by the host lab **and** the course team, **early November 2026** |
| Deliverables | Python code + **4-page PDF report** |
| Support | Project Q&A during labs 2026-11-26 and 2026-12-03; optional pitch session 2026-12-16 |
| Past-year alternatives | Previous editions also offered default tasks (road segmentation from satellite images, tweet sentiment classification, reproducibility of a paper) — TODO check whether offered in 2026 |
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
