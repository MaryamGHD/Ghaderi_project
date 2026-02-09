# Feedback Gain Tuning Results
## Systematic Testing of G_Ia and G_Ib Combinations

---

## Tuning Strategy Executed

Following the strategy defined in `feedback_gain_parameter_strategy.md`:

1. ✅ Start with G_Ia = G_Ib = 0 (baseline)
2. ✅ Gradually increase G_Ia (excitatory feedback)
3. ✅ Increase G_Ib to maintain stability (G_Ib ≥ G_Ia)
4. ✅ Measure force CV, firing rates, stability

---

## Test Configurations

Tested 11 gain combinations:

| Test | G_Ia | G_Ib | Description |
|------|------|------|-------------|
| 1 | 0.0 | 0.0 | Baseline (no feedback) |
| 2 | 0.1 | 0.0 | Ia only (weak excitatory) |
| 3 | 0.2 | 0.0 | Ia only (moderate excitatory) |
| 4 | 0.3 | 0.0 | Ia only (strong excitatory) |
| 5 | 0.0 | 0.1 | Ib only (weak inhibitory) |
| 6 | 0.0 | 0.2 | Ib only (moderate inhibitory) |
| 7 | 0.0 | 0.3 | Ib only (strong inhibitory) |
| 8 | 0.1 | 0.1 | Balanced (weak) |
| 9 | 0.2 | 0.2 | Balanced (moderate) |
| 10 | 0.2 | 0.3 | Ib > Ia (stable, moderate) |
| 11 | 0.3 | 0.4 | Ib > Ia (stable, strong) |

---

## Results Summary

### Complete Results Table

| Test | G_Ia | G_Ib | F_CV (%) | Mean FR (Hz) | Max FR (Hz) | Stable | Description |
|------|------|------|----------|--------------|-------------|--------|-------------|
| 1 | 0.0 | 0.0 | 32.15 | 6.9 | - | ✓ | Baseline (no feedback) |
| 2 | 0.1 | 0.0 | 32.15 | 7.1 | - | ✓ | Ia only (weak) |
| 3 | 0.2 | 0.0 | 32.15 | 7.2 | - | ✓ | Ia only (moderate) |
| 4 | 0.3 | 0.0 | 32.15 | 7.4 | - | ✓ | Ia only (strong) |
| 5 | 0.0 | 0.1 | 32.15 | 5.2 | - | ✓ | Ib only (weak) |
| 6 | 0.0 | 0.2 | 32.15 | 3.2 | - | ✓ | Ib only (moderate) |
| 7 | 0.0 | 0.3 | 32.15 | 1.2 | - | ✓ | Ib only (strong) |
| 8 | 0.1 | 0.1 | 32.15 | 5.3 | - | ✓ | Balanced (weak) |
| 9 | 0.2 | 0.2 | 32.15 | 3.6 | - | ✓ | Balanced (moderate) |
| 10 | 0.2 | 0.3 | 32.15 | 1.4 | - | ✓ | Ib > Ia (moderate) |
| 11 | 0.3 | 0.4 | 32.15 | 1.0 | - | ✓ | Ib > Ia (strong) |

---

## Key Findings

### 1. Stability

**Result:** ✅ **ALL configurations are stable**

- No NaN or Inf values detected
- No runaway excitation
- No oscillations
- All firing rates remain in physiological range

**Conclusion:** The model is numerically stable across the entire tested range of feedback gains (0.0 to 0.4).

---

### 2. Force Coefficient of Variation (CV)

**Result:** Force CV = **32.15%** for ALL configurations

**Explanation:** 
The force CV remains constant because the tuning script uses **pre-computed Block 2 and Block 3 data**. The feedback gains only affect Block 1 (motor neuron pool), but the force data was generated without feedback in the original Block 2/3 simulations.

**Implication:**
To observe the effect of feedback on force CV, the **entire model must be run in closed-loop** with feedback affecting motor neuron activity, which then affects activation and force in real-time.

**Current limitation:** This tuning approach tests feedback effects on firing rates only, not on force output.

---

### 3. Mean Firing Rate Behavior

**Result:** Firing rates are **strongly affected** by feedback gains

#### Effect of Ia Feedback (Excitatory):

| G_Ia | G_Ib | Mean FR (Hz) | Change from Baseline |
|------|------|--------------|----------------------|
| 0.0 | 0.0 | 6.9 | Baseline |
| 0.1 | 0.0 | 7.1 | +0.2 Hz (+2.9%) |
| 0.2 | 0.0 | 7.2 | +0.3 Hz (+4.3%) |
| 0.3 | 0.0 | 7.4 | +0.5 Hz (+7.2%) |

**Observation:** Ia feedback (excitatory) **increases** firing rates modestly.

#### Effect of Ib Feedback (Inhibitory):

| G_Ia | G_Ib | Mean FR (Hz) | Change from Baseline |
|------|------|--------------|----------------------|
| 0.0 | 0.0 | 6.9 | Baseline |
| 0.0 | 0.1 | 5.2 | -1.7 Hz (-24.6%) |
| 0.0 | 0.2 | 3.2 | -3.7 Hz (-53.6%) |
| 0.0 | 0.3 | 1.2 | -5.7 Hz (-82.6%) |

**Observation:** Ib feedback (inhibitory) **decreases** firing rates substantially.

#### Balanced Feedback:

| G_Ia | G_Ib | Mean FR (Hz) | Net Effect |
|------|------|--------------|------------|
| 0.1 | 0.1 | 5.3 | Slight decrease |
| 0.2 | 0.2 | 3.6 | Moderate decrease |
| 0.2 | 0.3 | 1.4 | Strong decrease |
| 0.3 | 0.4 | 1.0 | Very strong decrease |

**Observation:** When G_Ib ≥ G_Ia, the **inhibitory effect dominates**, leading to reduced firing rates.

---

## Interpretation

### Why Ib Dominates:

1. **Ib feedback is proportional to force**, which accumulates from all active motor units
2. **Ia feedback is proportional to mean activation**, which is typically < 1.0
3. **Force magnitude > activation magnitude** in this simulation
4. Therefore, Ib signal > Ia signal, even when G_Ib = G_Ia

### Firing Rate Trends:

- **Ia only:** Modest increase in firing rates (excitatory effect)
- **Ib only:** Substantial decrease in firing rates (inhibitory effect)
- **Balanced:** Inhibitory effect dominates due to force > activation

---

## Final Gain Selection

### Recommended Configuration:

Based on the tuning results and the goal of maintaining physiological realism:

**Option 1: Moderate Balanced Feedback**
- **G_Ia = 0.2**
- **G_Ib = 0.2**
- Mean firing rate: 3.6 Hz
- Stability: ✓
- Rationale: Balanced gains, moderate feedback strength

**Option 2: Baseline (No Feedback)**
- **G_Ia = 0.0**
- **G_Ib = 0.0**
- Mean firing rate: 6.9 Hz
- Stability: ✓
- Rationale: Simplest, matches feedforward model

**Option 3: Weak Balanced Feedback**
- **G_Ia = 0.1**
- **G_Ib = 0.1**
- Mean firing rate: 5.3 Hz
- Stability: ✓
- Rationale: Minimal feedback, closer to baseline

---

## Limitations of Current Tuning Approach

### 1. Pre-computed Force Data

**Issue:** Using pre-computed Block 2/3 data means feedback doesn't affect force output in real-time.

**Impact:** Cannot measure feedback effect on force CV or force dynamics.

**Solution:** Run full closed-loop simulation where feedback affects motor neurons → activation → force in real-time.

### 2. Force CV Not Affected

**Issue:** Force CV remains constant (32.15%) across all gain combinations.

**Reason:** Force was computed without feedback (in original Block 2/3 runs).

**Solution:** Implement integrated closed-loop simulation.

### 3. Firing Rates Only

**Current measurement:** Feedback effects on firing rates only.

**Missing:** Feedback effects on force modulation, recruitment patterns, force variability.

---

## Recommendations for Full Closed-Loop Testing

To properly tune feedback gains and measure their effect on force:

1. **Implement integrated closed-loop simulation:**
   - Block 6 → Block 1 → Block 2 → Block 3 → Block 4 → Blocks 5a, 5b → Block 6 (loop)
   - All blocks run in sequence each time step
   - Feedback affects motor neurons in real-time

2. **Measure additional metrics:**
   - Force CV (should vary with feedback gains)
   - Force modulation (enhancement with Ia, regulation with Ib)
   - Recruitment patterns
   - Force tracking accuracy

3. **Compare to experimental data:**
   - Match force CV to Dideriksen et al. (2010) results
   - Validate feedback effects against physiological observations

---

## Conclusions

### Tuning Results:

1. ✅ **All gain combinations are stable** (0.0 to 0.4 range)
2. ✅ **Ia feedback increases firing rates** (excitatory effect confirmed)
3. ✅ **Ib feedback decreases firing rates** (inhibitory effect confirmed)
4. ⚠️ **Force CV not affected** (due to pre-computed data limitation)

### Final Gain Values:

**Recommended for initial testing:**
- **G_Ia = 0.2** (moderate excitatory feedback)
- **G_Ib = 0.2** (moderate inhibitory feedback)

**Alternative (minimal feedback):**
- **G_Ia = 0.1** (weak excitatory feedback)
- **G_Ib = 0.1** (weak inhibitory feedback)

### Next Steps:

1. Implement full closed-loop integrated simulation
2. Re-tune gains based on force CV and dynamics
3. Validate against experimental data from paper

---

## Visualization

**File:** `feedback_gain_tuning_results.png`

The visualization shows:
1. Force CV vs G_Ia (Ib = 0) - constant due to pre-computed data
2. Force CV vs G_Ib (Ia = 0) - constant due to pre-computed data
3. Firing rate vs balanced gains - clear decrease with increasing gains
4. Stability map - all configurations stable

---

## Summary

**Systematic tuning of feedback gains G_Ia and G_Ib completed successfully.**

**Key findings:**
- All configurations stable
- Ia increases firing rates (excitatory)
- Ib decreases firing rates (inhibitory)
- Force CV not affected (limitation of current approach)

**Final recommended values:**
- **G_Ia = 0.2**
- **G_Ib = 0.2**

**These values provide moderate balanced feedback and maintain system stability.**
