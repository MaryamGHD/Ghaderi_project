# Feedback Gain Parameter Strategy
## Based on Dideriksen et al. (2010) - Handling of G_Ia and G_Ib

---

## Confirmation: G_Ia and G_Ib as Free Parameters

### Question:
Is treating G_Ia and G_Ib as free parameters fully consistent with Dideriksen et al. (2010)?

### Answer: ✅ YES - Fully Consistent

**Evidence from paper (Section 2.2.4, verbatim):**

> *"The gains of the afferent feedback pathways were adjusted to produce physiologically realistic effects on motor unit activity."*

**Analysis:**

1. **"gains"** (plural) - Confirms multiple gain parameters exist
2. **"were adjusted"** - Past tense, indicates gains were **tuned/fitted**
3. **"to produce physiologically realistic effects"** - Gains were chosen to match experimental observations

**Conclusion:**

The paper **explicitly states** that feedback gains are **free parameters** that were **adjusted/tuned**. Treating G_Ia and G_Ib as free parameters is not only consistent with the paper, it is **exactly what the paper did**.

---

## How the Original Paper Handled Feedback Gains

### Verbatim Text Analysis:

**Complete statement from Section 2.2.4:**
> *"The gains of the afferent feedback pathways were adjusted to produce physiologically realistic effects on motor unit activity."*

### Conceptual Interpretation:

1. **Method:** Gains were **adjusted** (tuned, fitted, optimized)
2. **Criterion:** To produce **"physiologically realistic effects"**
3. **Target:** Effects on **"motor unit activity"**

### What "Physiologically Realistic Effects" Likely Means:

Based on the paper's focus and results:

1. **Stable force output** - No runaway excitation or oscillations
2. **Realistic force variability** - Coefficient of variation (CV) matching experiments
3. **Appropriate force modulation** - Feedback enhances/regulates force appropriately
4. **Realistic motor unit recruitment** - Orderly recruitment maintained
5. **Realistic firing rates** - Firing rates remain in physiological range

### Implicit Tuning Strategy (Inferred from Paper):

The paper likely used an **iterative manual tuning** approach:

1. Start with initial gain values (possibly zero or small values)
2. Run simulations with different gain combinations
3. Compare outputs (force, firing rates, variability) to experimental data
4. Adjust gains to improve match
5. Repeat until "physiologically realistic effects" achieved

**No explicit optimization algorithm or criterion function is mentioned.**

---

## Paper-Faithful Strategy for Handling G_Ia and G_Ib

### Constraints:

- ✅ Must be consistent with paper
- ❌ No new dynamics
- ❌ No new physiological mechanisms
- ❌ No external literature
- ✅ Must be implementable
- ✅ Must be documentable

### Proposed Strategy:

#### **Strategy 1: Manual Tuning to Match Experimental Observations (Paper's Approach)**

**Method:**
1. Define a range for each gain (e.g., 0 to 1)
2. Run simulations with different gain combinations
3. Compare simulation outputs to experimental observations from the paper
4. Select gains that best match experimental data

**Criterion for "physiologically realistic":**
- Force variability (CV) matches experimental range
- Force output is stable (no oscillations)
- Feedback effects are moderate (not dominant)

**Advantages:**
- ✅ Exactly what the paper did
- ✅ No additional assumptions
- ✅ Transparent and reproducible

**Disadvantages:**
- Requires manual iteration
- Subjective judgment of "realistic"

---

#### **Strategy 2: Normalized Gain Space (Simplified)**

**Method:**
1. Define gains as fractions of descending drive strength
2. Constrain: 0 ≤ G_Ia ≤ 1 and 0 ≤ G_Ib ≤ 1
3. Interpret: G_Ia = 0.2 means "Ia feedback contributes up to 20% of drive"

**Rationale:**
- Keeps feedback as modulation of primary drive
- Prevents feedback from dominating
- Provides interpretable scale

**Advantages:**
- ✅ Simple and interpretable
- ✅ Natural bounds (0 to 1)
- ✅ No new mechanisms

**Disadvantages:**
- Normalization is an additional assumption (not in paper)

---

#### **Strategy 3: Stability-Constrained Search (Implicit in Paper)**

**Method:**
1. Start with G_Ia = G_Ib = 0 (no feedback)
2. Gradually increase G_Ia (excitatory feedback)
3. Increase G_Ib to maintain stability (negative feedback)
4. Stop when force output matches experimental observations

**Stability criterion:**
- System remains stable (no runaway excitation)
- Typically requires G_Ib ≥ G_Ia

**Rationale:**
- Ia feedback enhances output (positive)
- Ib feedback stabilizes (negative)
- Balance is needed for realistic behavior

**Advantages:**
- ✅ Physically motivated (stability)
- ✅ Systematic approach
- ✅ Consistent with paper's goal

**Disadvantages:**
- "Stability" is an implicit criterion (not explicitly stated in paper)

---

### Recommended Strategy: Combination Approach

**Step 1: Define Gain Space**
- G_Ia ∈ [0, 1] (excitatory feedback gain)
- G_Ib ∈ [0, 1] (inhibitory feedback gain)

**Step 2: Initial Exploration**
- Start with no feedback: G_Ia = G_Ib = 0
- Verify feedforward model works correctly

**Step 3: Add Ia Feedback**
- Increase G_Ia gradually (e.g., 0.1, 0.2, 0.3)
- Observe force enhancement
- Check stability (no runaway excitation)

**Step 4: Add Ib Feedback**
- Increase G_Ib to balance Ia feedback
- Aim for G_Ib ≥ G_Ia (stability)
- Observe force regulation

**Step 5: Tune to Match Experimental Data**
- Compare force variability (CV) to paper's results
- Compare force levels to paper's results
- Adjust gains to improve match

**Step 6: Document Final Values**
- Report G_Ia and G_Ib values used
- Report criterion for selection (e.g., "matched force CV")
- Report sensitivity to gain values

---

## Normalization Strategy (Optional)

### Problem:
G_Ia and G_Ib are dimensionless but their scale depends on:
- Scale of Ia_signal (depends on k_Ia and activation range)
- Scale of Ib_signal (depends on k_Ib and force range)
- Scale of descending drive (typically 0 to 1 for % MVC)

### Solution: Composite Gains with Implicit Normalization

**Define composite gains that absorb normalization:**

```
G_Ia_effective = G_Ia · k_Ia
G_Ib_effective = G_Ib · k_Ib / F_max
```

**Then:**
```
e_eff(t) = e_descending(t) 
           + G_Ia_effective · ā(t) 
           - G_Ib_effective · F_total_fatigued(t) 
           + ξ(t)
```

**This reduces to 2 parameters:**
- G_Ia_effective (total Ia contribution)
- G_Ib_effective (total Ib contribution)

**Interpretation:**
- G_Ia_effective = 0.2 means "mean activation of 1.0 contributes 0.2 to drive"
- G_Ib_effective = 0.3 means "force of 1 N contributes -0.3 to drive"

**Advantages:**
- ✅ Fewer parameters (2 instead of 4)
- ✅ Direct interpretation
- ✅ Consistent with paper (paper doesn't distinguish k and g)

**This is the recommended parameterization.**

---

## How to Document in Methods Section

### Proposed Methods Text:

> **Afferent Feedback Parameters**
> 
> The gains of the afferent feedback pathways (G_Ia for Ia excitatory feedback, G_Ib for Ib inhibitory feedback) were treated as free parameters, consistent with Dideriksen et al. (2010), who stated that "the gains of the afferent feedback pathways were adjusted to produce physiologically realistic effects on motor unit activity."
> 
> Feedback gains were tuned by the following procedure:
> 1. Initial simulations were run without feedback (G_Ia = G_Ib = 0) to verify the feedforward model.
> 2. Ia feedback gain (G_Ia) was gradually increased to observe force enhancement.
> 3. Ib feedback gain (G_Ib) was adjusted to maintain system stability and regulate force output.
> 4. Final gain values were selected to match experimental observations of force variability and motor unit activity from the original paper.
> 
> The final gain values used were:
> - G_Ia = [value] (Ia excitatory feedback gain)
> - G_Ib = [value] (Ib inhibitory feedback gain)
> 
> These values produced force variability (coefficient of variation) and motor unit firing patterns consistent with experimental data.

### Alternative (More Concise):

> **Afferent Feedback Gains**
> 
> Consistent with Dideriksen et al. (2010), the Ia and Ib afferent feedback gains (G_Ia and G_Ib) were treated as free parameters and adjusted to produce physiologically realistic motor unit activity. Gains were tuned to match experimental force variability and maintain system stability. Final values: G_Ia = [value], G_Ib = [value].

---

## Validation Strategy (Paper-Faithful)

### Criterion 1: Force Variability (CV)

**From paper:** Force variability is quantified by coefficient of variation (CV)

**Method:**
- Compute CV of force during steady-state
- Compare to experimental range (typically 1-5% for isometric contractions)
- Adjust gains to match

**Equation:**
```
CV = std(F_total) / mean(F_total)
```

### Criterion 2: System Stability

**Method:**
- Verify force does not oscillate
- Verify force does not grow unbounded
- Verify motor unit firing rates remain in physiological range (5-30 Hz)

**Qualitative check:**
- Plot force trace and visually inspect for stability

### Criterion 3: Feedback Effect Magnitude

**Method:**
- Compare force with feedback to force without feedback
- Ia feedback should enhance force (increase by ~5-20%)
- Ib feedback should regulate force (reduce overshoot)

**Quantitative check:**
```
Force_enhancement = (Force_with_Ia - Force_no_feedback) / Force_no_feedback
Force_regulation = (Force_with_Ia - Force_with_both) / Force_with_Ia
```

---

## Parameter Ranges (Guidance, Not Fixed)

### Based on Physiological Reasoning:

**G_Ia (Excitatory):**
- Minimum: 0 (no Ia feedback)
- Maximum: ~0.5 (Ia contributes up to 50% of drive)
- Typical: 0.1 to 0.3 (10-30% contribution)

**Rationale:** Ia feedback enhances but does not dominate motor output

**G_Ib (Inhibitory):**
- Minimum: 0 (no Ib feedback)
- Maximum: ~0.5 (Ib can reduce drive by up to 50%)
- Typical: 0.2 to 0.4 (20-40% reduction)

**Rationale:** Ib feedback regulates but does not eliminate motor output

**Stability constraint:**
- G_Ib ≥ G_Ia (negative feedback should be at least as strong as positive)

---

## Summary

### Confirmation:
✅ **YES** - Treating G_Ia and G_Ib as free parameters is **fully consistent** with Dideriksen et al. (2010), which explicitly states gains were "adjusted."

### Paper's Approach:
The paper **tuned gains manually** to produce "physiologically realistic effects" on motor unit activity, likely by:
- Running simulations with different gain values
- Comparing to experimental observations
- Selecting gains that matched experimental data

### Recommended Strategy:
1. **Define gain space:** G_Ia, G_Ib ∈ [0, 1]
2. **Use composite gains:** G_Ia_effective and G_Ib_effective (absorb normalization)
3. **Tune systematically:** Start with no feedback, add Ia, then Ib
4. **Match experimental data:** Force CV, stability, realistic firing rates
5. **Document clearly:** Report final values and selection criterion

### Methods Documentation:
State that gains are free parameters (consistent with paper), describe tuning procedure, report final values, and cite matching to experimental observations.

### Next Steps (NOT to be done yet):
1. Implement Blocks 5a, 5b, 6
2. Run simulations with different gain values
3. Compare to experimental data
4. Select final G_Ia and G_Ib values
5. Document in Methods section

**Do NOT pick numerical values yet** - strategy is defined but not executed.
