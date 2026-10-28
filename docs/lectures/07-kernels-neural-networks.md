# Lecture 07 — Kernel Ridge Regression & the Kernel Trick; Neural Networks: Basic Structure, Representation Power

Sources (lecturer **Nicolas Flammarion**; pulled 2026-10-28):
- §A `lectures/07/lecture07a.pdf` (23 p., Tue 2026-10-27) — Kernel ridge regression and the kernel trick
- §B `lectures/07/lecture07b.pdf` (46 p., Wed 2026-10-28) — Neural networks: basic structure, representation power

⚠ Course **week 8** (10-27/28) = lecture folder **07** (week 7 was the break).

**Slide numbering:** no printed numbers → **"slide N" = PDF page N** (title = p. 1). Render with `pdftoppm -f N -l N`.
**Annotated version:** Flammarion lecture → **none expected**. **Proxy:** the 2025 decks (taught by R. West, slide credits Flammarion) are the same content but with extra build-up pages: `git show '48f3822^:lectures/07/lecture07a_annotated.pdf'` (25 p.) and `…/lecture07b_annotated.pdf` (54 p.). Notes from them are marked *(2025 ann.)*.
- Page map 07a: 2026 p. 1–10 = 2025 p. 1–10; 2026 p. 11 = 2025 p. 12; **2026 p. N = 2025 p. N+2 for N ≥ 12** (2025 p. 11 and p. 14 were build-ups).
- Page map 07b: 2026 p. 1–27 = 2025 p. 1–27; p. 28 = 29; p. 29 = 30–31; p. 30 = 32–33; p. 31–35 = 34–38; p. 36 = 39–40; p. 37–39 = 41–43; p. 40 = 44–45; p. 41 = 46–48; p. 42 = 49–50; **p. 43–46 = 51–54**.
- **Only content change vs 2025:** 07a p. 15 polynomial kernel is now **(1 + xᵀx′)²** with ϕ ∈ ℝ¹⁰ (2025: homogeneous (xᵀx′)² with ϕ ∈ ℝ⁶).

Formulas below come from the PDF text layer (real text in these decks), checked against renders where √ signs were lost.

## §A Kernel ridge regression and the kernel trick (07a)
- **Two forms of the ridge solution (p. 2):** objective min_w 1/(2N) Σₙ (yₙ − wᵀxₙ)² + (λ/2)‖w‖² (squared loss + ℓ₂ regularizer, 2025 ann.).
  **w\* = (1/N)((1/N)XᵀX + λI_d)⁻¹Xᵀy** (inverts a **d × d** matrix) **= (1/N)Xᵀ((1/N)XXᵀ + λI_N)⁻¹y** (inverts an **N × N** matrix — the kernel matrix, 2025 ann.).
- **Proof (p. 3) — "push-through" identity:** P ∈ ℝᵐˣⁿ, Q ∈ ℝⁿˣᵐ: P(QP + Iₙ) = PQP + P = (PQ + Iₘ)P ⇒ **(PQ + Iₘ)⁻¹P = P(QP + Iₙ)⁻¹** (if both invertible). Apply with P = Xᵀ, Q = X/(λN).
- **Usefulness (p. 4):** (1) **cost**: original O(d³ + Nd²), new O(N³ + dN²) → pick the cheaper one depending on d vs N. (2) **structure**: **w\* = Xᵀα\***, α\* = (1/N)((1/N)XXᵀ + λI_N)⁻¹y ∈ ℝᴺ ⇒ **w\* ∈ span{x₁, …, x_N}**. These two insights are the basis of the kernel trick.
- **Representer theorem (p. 5):** for **any loss ℓ** and any minimizer w\* ∈ argmin (1/N) Σₙ ℓ(xₙᵀw, yₙ) + (λ/2)‖w‖², **∃α\* ∈ ℝᴺ: w\* = Xᵀα\*** (every minimizer lies in the span of the data). Consequence: kernel trick for kernel SVM, kernel LS, kernel PCA. (Wahba 1990; Schölkopf–Herbrich–Smola 2001.) *(2025 ann.: ℓ can be (y − xᵀw)², |y − xᵀw|, …)*
- **Proof (p. 6):** write w\* = Σₙ αₙxₙ + u with uᵀxₙ = 0 ∀n (orthogonal decomposition). Let w = w\* − u. Pythagoras: ‖w\*‖² = ‖w‖² + ‖u‖² ⇒ ‖w‖ ≤ ‖w\*‖. Same predictions: wᵀxₙ = w\*ᵀxₙ ⇒ same loss. So objective(w) ≤ objective(w\*), and by optimality ≥ ⇒ ‖w\*‖² = ‖w‖² ⇒ **u = 0**. (Needs λ > 0.)
- **Kernelized ridge (p. 7):** primal in w: argmin 1/(2N)‖y − Xw‖² + (λ/2)‖w‖². **Dual-like form in α: α\* = argmin_α ½ αᵀ((1/N)XXᵀ + λI_N)α − (1/N)αᵀy.** Gradient = 0 ⇒ α\* = (1/N)((1/N)XXᵀ + λI_N)⁻¹y, w\* = Xᵀα\*. Takeaways: complexity depends on d, N; **the α-form uses X only through K = XXᵀ**.
- **Kernel matrix (p. 8):** **K = XXᵀ = (xᵢᵀxⱼ)ᵢⱼ ∈ ℝᴺˣᴺ**, symmetric. Inner product = similarity (uᵀv = ‖u‖‖v‖cos α, 2025 ann.).
- **Feature spaces (p. 9–10):** ϕ(x) = (x, x²): 1-D data not separable by a threshold becomes **separable by a half-space** after embedding. p. 10: 2-D picture lifted onto a paraboloid.
- **Kernel matrix with features (p. 11):** ϕ: ℝᵈ → ℝᵈ̃, **K = ΦΦᵀ = (ϕ(xᵢ)ᵀϕ(xⱼ))ᵢⱼ**. Problem: if d ≪ d̃, computing ϕ(x)ᵀϕ(x′) costs O(d̃) — too expensive.
- **Kernel trick (p. 12):** a **kernel function κ(x, x′) = ϕ(x)ᵀϕ(x′)** (similarity realised as an inner product in feature space). Compute κ directly instead of mapping then taking the inner product ⇒ **linear methods in a high- (even infinite-) dimensional space without ever computing there**.
- **Prediction (p. 13):** **y = ϕ(x)ᵀw\* = ϕ(x)ᵀΦᵀα\* = Σₙ κ(x, xₙ)α\*ₙ** → only the kernel is needed, but **with every training point**. Linear in feature space, **non-linear in input space 𝒳**.
- **Examples (p. 14–17):**
  1. linear κ = xᵀx′, ϕ(x) = x;
  2. quadratic (1-D) κ = (xx′)², ϕ(x) = x²;
  3. **polynomial (p. 15)**, x ∈ ℝ³: **κ = (1 + xᵀx′)²**, ϕ(x) = [1, √2x₁, √2x₂, √2x₃, x₁², x₂², x₃², √2x₁x₂, √2x₁x₃, √2x₂x₃] ∈ ℝ¹⁰ — expand the square and identify the terms. (Homogeneous (xᵀx′)² on ℝ³ → ℝ⁶, without the 1 and the √2xᵢ.)
  4. **RBF (p. 16)**: **κ(x, x′) = exp(−‖x − x′‖²)**; in 1-D ϕ(x) = e^{−x²}(…, 2^{k/2}xᵏ/√(k!), …) — **infinite-dimensional** (proof: e^{−x²}e^{−x′²}e^{2xx′} + Taylor series of exp). **Cannot be an inner product in a finite-dimensional space.**
  5. string kernels (p. 17): features = weighted counts of substrings u in a string s (DNA, text); picture only.
- **Building kernels (p. 18–20):** κ₁, κ₂ valid with maps ϕ₁ ∈ ℝ^{d₁}, ϕ₂ ∈ ℝ^{d₂}:
  - **ακ₁ + βκ₂, α, β ≥ 0** is a kernel: ϕ = [√α ϕ₁; √β ϕ₂] ∈ ℝ^{d₁+d₂};
  - **κ₁κ₂** is a kernel: ϕ(x) = ((ϕ₁(x))ᵢ(ϕ₂(x))ⱼ)ᵢⱼ ∈ ℝ^{d₁d₂} (all pairwise products; Σᵢⱼ … = (ϕ₁ᵀϕ₁′)(ϕ₂ᵀϕ₂′)).
- **Mercer's condition (p. 21):** ∃ϕ with κ(x, x′) = ϕ(x)ᵀϕ(x′) **⇔ (i) κ symmetric and (ii) for every N and every set (xₙ)ₙ₌₁ᴺ, K = (κ(xᵢ, xⱼ))ᵢⱼ ⪰ 0 (PSD)**.
- **Recap (p. 22):** many algorithms (SVM, LS, PCA) rely only on inner products XXᵀ → replace by kernels to get non-linear models; avoids computing ϕ; **prediction needs κ(x, xᵢ) for every training point**; new kernels from closure rules.
- **Bonus (p. 23):** Mercer proof. ⇒ direction: vᵀKv = Σᵢⱼ vᵢvⱼϕ(xᵢ)ᵀϕ(xⱼ) = ‖Σᵢ vᵢϕ(xᵢ)‖² ≥ 0. ⇐ direction: ϕ(x) = κ(·, x), function space of Σ αᵢκ(·, xᵢ) with inner product ⟨κ(·, x), κ(·, x′)⟩ = κ(x, x′) (RKHS construction).

## §B Neural networks: basic structure, representation power (07b)
- **Motivation (p. 2–4):** state of the art in detection, translation, speech, image generation, chess, protein folding. Linear: **y = ϕ(x)ᵀw with ϕ fixed** (handcrafted features); NN: **y = f(x)ᵀw with f learned** — first layers learn a representation, **the last layer is a linear predictor**. Deep learning needs lots of data + compute; quality keeps improving with more data and bigger models.
- **Logistic regression recap (p. 6):** f_LR(x) = p(1|x) = σ(xᵀw + b), σ(z) = 1/(1 + e^{−z}) ("squish", 2025 ann.). Pattern-matching view: **a single template w** (very restrictive).
- **Two-layer NN (p. 7):** stack logistic units in a hidden layer, ϕ(x)ⱼ = σ(Σᵢ xᵢw⁽¹⁾ᵢⱼ + bⱼ), output ϕ(x)ᵀw⁽²⁾. Each hidden unit learns **a different pattern** (not necessarily interpretable) → much more flexible.
- **Multi-layer NN (p. 8–14):** L hidden layers of K neurons each + output layer with a single node. Parameters W⁽ˡ⁾, b⁽ˡ⁾ for 1 ≤ l ≤ L + 1; each **column of W⁽ˡ⁾ = weights of one neuron**. Layer output **x⁽ˡ⁾ = f⁽ˡ⁾(x⁽ˡ⁻¹⁾) := ϕ((W⁽ˡ⁾)ᵀx⁽ˡ⁻¹⁾ + b⁽ˡ⁾)**, single neuron x⁽ˡ⁾ⱼ = ϕ(Σᵢ x⁽ˡ⁻¹⁾ᵢ w⁽ˡ⁾ᵢⱼ + b⁽ˡ⁾ⱼ). **w⁽ˡ⁾ᵢⱼ = weight of the edge from node i in layer l−1 to node j in layer l.** x⁽⁰⁾ = input. **Fully connected**: every node is connected to every node of the previous layer. **ϕ must be non-linear**, otherwise the network is a linear function.
- **Feature extractor view (p. 15):** NN = feature extractor f: ℝᵈ → ℝᴷ (input + L hidden layers) + output layer. Defined by learned {W⁽ˡ⁾, b⁽ˡ⁾} and the chosen ϕ. **#parameters O(dK + K²L) ≈ O(K²L)**. In practice L and K are large → **overparametrized**.
- **Inference (p. 16):** h(x) = f(x)ᵀw⁽ᴸ⁺¹⁾ + b⁽ᴸ⁺¹⁾. Regression: h(x); binary y ∈ {−1, 1}: sign(h(x)); multiclass y ∈ {1, …, K}: argmax_c h(x)_c.
- **Training (p. 17):** losses on h: square (h(x) − y)²; **logistic log(1 + exp(−y h(x)))** for y ∈ {−1, 1}; **cross-entropy −log(e^{h(x)_y} / Σᵢ e^{h(x)ᵢ})** for multiclass (lab 7 Problem 2).
- **Activations (p. 18):** **sigmoid σ(x) = 1/(1 + e^{−x})**; **ReLU (x)₊ = max{0, x}** (rectified linear unit); **GELU x·Φ(x) ≈ x·σ(1.702x)** (Φ = standard Gaussian CDF). ReLU and GELU are the most used.
- **Three theoretical questions (p. 19):** expressive power (why can NNs approximate the functions we care about?), success of naive optimization (why does GD find good minima?), generalization "miracle" (why no overfitting despite so many parameters?). This lecture = **expressive power** only.
- **Barron's theorem (p. 21–23):** f: ℝᵈ → ℝ with Fourier transform f̂(ω) = ∫ f(x)e^{−iωᵀx}dx; smoothness assumption **∫ |ω||f̂(ω)| dω ≤ C**. Then ∀n ≥ 1, r > 0, ∃ **fₙ(x) = Σⱼ₌₁ⁿ cⱼϕ(xᵀwⱼ + bⱼ) + c₀ = cᵀϕ(Wᵀx + b) + c₀** (one hidden layer, n nodes) with
  **∫_{‖x‖≤r} (f(x) − fₙ(x))² dx ≤ (2Cr)²/n.**
  Reading: more neurons ⇒ smaller error (rate **1/n**); smoother f (smaller C) ⇒ smaller error; larger domain (larger r) ⇒ larger error; approximation **in average (ℓ₂ / L²)**, not pointwise; works for any **"sigmoid-like"** activation. (Barron 1993.)
- **Intuitive ℓ₁ proof (p. 24–31), 1-D:** claim proved: "a NN with sigmoid activation and **at most two hidden layers** approximates a smooth function well in ℓ₁". (1) Riemann: approximate f by a sum of **rectangles** (lower/upper sums), ℓ₁ error = ∫f − Σ areas. (2) **rectangle = difference of two steps**: h𝟙_{[a,b]} = h𝟙_{x≥a} − h𝟙_{x≥b}. (3) **step ≈ steep sigmoid** ϕ(w(x − b)): b = location, w = steepness, slope at b is ϕ̃′(b) = w/4 ⇒ transition width O(4/w). (4) rectangle ≈ **h(ϕ(w(x − a)) − ϕ(w(x − b)))** = 2 hidden nodes. ⇒ **k rectangles → 2k hidden nodes, one hidden layer.** Remarks: works for any sigmoid-like ϕ; intuition, not a rate; **weights must be large**.
- **d = 2 (p. 32–38):** ϕ(w(x₁ − a₁)) − ϕ(w(x₁ − b₁)) = **infinite band** in x₂; adding the x₂ band gives a **cross** (4 sigmoids, value 2 in the centre, 1 on the arms). **Threshold with an output sigmoid** (≈ 𝟙_{y≥c}, c ∈ (1, 2], e.g. bias −3w/2) removes the arms ⇒ one 2-D rectangle. Many rectangles ⇒ sum them ⇒ **2 hidden layers**. Example sin(πx₁)sin(πx₂) with 9 rectangles on [0, 1]².
- **ℓ₂ vs ℓ∞ (p. 39):** ℓ₂ = average deviation (large errors at few points can be compensated); ℓ∞ = maximum pointwise error (uniform control). Barron is ℓ₂; next: ℓ∞.
- **ℓ∞ via piecewise linear (p. 40):** (Shektman 1982) f continuous on [c, d] ⇒ ∀ε > 0 ∃ **PWL q with sup |f − q| ≤ ε**. PWL: q(x) = Σᵢ₌₁ᵐ (aᵢx + bᵢ)𝟙_{rᵢ₋₁ ≤ x < rᵢ}, continuity aᵢrᵢ + bᵢ = aᵢ₊₁rᵢ + bᵢ₊₁.
- **ReLU ↔ PWL (p. 41–43):** in (ax + b)₊ the **bias sets the kink position**, the **weight the slope**; a linear combination Σ ãᵢ(x − b̃ᵢ)₊ is PWL. **Claim 1:** any PWL q = ã₁x + b̃₁ + Σᵢ₌₂ᵐ ãᵢ(x − b̃ᵢ)₊ with ã₁ = a₁, b̃₁ = b₁, **b̃ᵢ = rᵢ₋₁ (kinks)**, **aᵢ = Σⱼ≤ᵢ ãⱼ ⇔ ãᵢ = aᵢ − aᵢ₋₁ (change of slope)**. **Claim 2:** this is a **one-hidden-layer ReLU NN**: each term = one node (input weight 1, bias −b̃ᵢ, output weight ãᵢ); ã₁x = ã₁(x)₊ since x ∈ [0, 1]; b̃₁ = output bias ⇒ **m hidden nodes**.
- **Proof (p. 44–45):** induction on the pieces — on [rᵢ₋₁, rᵢ] the active ReLUs give slope Σⱼ≤ᵢ ãⱼ = aᵢ and r(rᵢ₋₁) = q(rᵢ₋₁); two affine functions with the same slope and same starting point are equal.
- **Recap (p. 46):** NN = linear layers + non-linearities; learned feature extractor + linear predictor; needs lots of data/compute; **very high representational power (universal approximation)** unlike linear regression.

## Notation (new)
| Symbol | Meaning |
|---|---|
| α\* ∈ ℝᴺ | coefficients of w\* = Xᵀα\* in the span of the data (representer theorem) |
| K = XXᵀ, K = ΦΦᵀ | kernel (Gram) matrix N × N; with feature map Φ ∈ ℝᴺˣᵈ̃ has rows ϕ(xₙ)ᵀ |
| ϕ: ℝᵈ → ℝᵈ̃ | feature map (07a); **⚠ in 07b ϕ is the activation function** |
| κ(x, x′) | kernel function = ϕ(x)ᵀϕ(x′) |
| L, K (07b) | number of hidden layers, neurons per hidden layer (⚠ K ≠ kernel matrix) |
| W⁽ˡ⁾, b⁽ˡ⁾, w⁽ˡ⁾ᵢⱼ | weight matrix, bias of layer l; edge i (layer l−1) → j (layer l) |
| x⁽ˡ⁾ | output of layer l, x⁽⁰⁾ = input |
| f(x), h(x) | learned representation ∈ ℝᴷ; output h = f(x)ᵀw⁽ᴸ⁺¹⁾ + b⁽ᴸ⁺¹⁾ |
| (x)₊, Φ | ReLU max{0, x}; standard Gaussian CDF (GELU) |
| f̂, C, r, n | Fourier transform, Barron smoothness constant, domain radius, #hidden neurons |

## Exam-relevant points / pitfalls
- **Valid kernel = symmetric + PSD Gram matrix for every finite point set** (2024 Q42 — state the definition). Quick invalidity tests: **κ(x, x) = ‖ϕ(x)‖² must be ≥ 0** (2022 Q28: cos(x + x′) invalid since cos 2x < 0); 2×2 Gram matrix with negative determinant or eigenvalue (2024 Q43–44: (xᵀx′ + c)ᵈ with c < 0 invalid, use x₁ = 1, x₂ = −1; 2025 Q26: |xᵀy| invalid with x, −x).
- **Pick the valid one** (2025 Q26): (1 + xᵀy)² valid (= 1 + 2xᵀy + (xᵀy)², non-negative sum); −‖x − y‖², |xᵀy|, −xᵀy, 1 − xᵀy invalid.
- **All valid** (2020 Q9): constant 2 (= √2·√2), (xᵀx′)², cos(x − x′) = ⟨(cos x, sin x), (cos x′, sin x′)⟩, 2^{x+x′} = 2ˣ·2^{x′}, xᵀAx′ with A PSD (= (Bx)ᵀ(Bx′), B² = A).
- **Closure rules** (2018 Problem 19, open): aκ₁ + bκ₂ (a, b ≥ 0), κ₁κ₂, κ₁(f(x), f(x′)), f(x)f(x′) — prove by exhibiting ϕ. Graders: if you exhibit ϕ, no need to check Mercer. **Difference κ₁ − κ₂ is NOT guaranteed valid** (2025 Q35 False). Lab 7: polynomial with positive coefficients of a kernel, exp(κ₁) are valid; 1/(1 − xᵀx′) on the unit ball is valid (2021 Q25 True, geometric series).
- **Feature map ↔ kernel identification** (2019 Q5): x̃ = (x₁², x₂², √2x₁x₂) ⇒ K̃ᵢⱼ = (xᵢᵀxⱼ)², i.e. f(z) = z² applied entrywise.
- **Kernel trick ⇒ inner products in infinite-dimensional spaces** (RBF) (2023 Q21 True). Kernel methods make non-separable data linearly separable in feature space; a regularizer does not (2023 Q20).
- **Kernel prediction needs all training points** (or all support vectors for SVM): cost of kernel SVM scales with N / #support vectors, **not** with the input dimension (2025 Q34 False).
- **Primal vs kernel ridge cost**: O(d³ + Nd²) vs O(N³ + dN²) — choose by d vs N. Kernel matrix is N × N, XᵀX is d × d.
- **Kernel PCA** open problem (2020): K = ΦΦᵀ, size n × n; only κ is computable.
- **ReLU nets implementing PWL functions** (2025 Q27): **output weight of each ReLU = change of slope at its kink**: slopes 0 → 3 at x = 2, 3 → −1 at x = 5 ⇒ 3(x − 2)₊ − 4(x − 5)₊.
- **ReLU constructions without skip connections** (2024 Q45–46, open, 4 + 6 pts): identity **x = (x)₊ − (−x)₊** (2 units); **max{x₁, x₂} = (x₁ − x₂)₊ + (x₂)₊ − (−x₂)₊** (3 units, W = [[1, −1], [0, 1], [0, −1]], v = (1, 1, −1)).
- Without a non-linear activation a deep network computes a linear function of x — **but its MSE is still non-convex in the parameters** (2021 Q34 False: output w₁w₂x).
- Barron: error **(2Cr)²/n**, one hidden layer, **ℓ₂ (average)** sense — know how each of n, C, r affects the bound.

## Not exam material / lower priority
- Proof of Mercer's theorem (p. 23, "Bonus").
- String kernels (p. 17, picture only).
- The quantitative proof of Barron's theorem (not given; only the ℓ₁ "proof by picture").

## Exercises mentioned
- Lab 7 (`labs/ex07/`, Thu 2026-10-29; notebook identical to 2025): theory **Problem 1** kernels (f(κ₁) with positive-coefficient polynomial f is valid; exp(κ₁) valid via limit of valid kernels), **Problem 2** softmax cross-entropy (stable softmax with maxⱼ xⱼ, ∂H/∂xⱼ = zⱼ − yⱼ, label smoothing), **Problem 3** PyTorch intro + approximate a 2-D function with a ReLU MLP (`get_model_weights`, `predict`, `train_network` with Adam) + MNIST classifier. Details in `docs/labs.md`.
