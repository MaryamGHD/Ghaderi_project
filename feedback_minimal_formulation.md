# Minimal Mathematical Formulation for Feedback Blocks
## Based on Verbatim Text from Dideriksen et al. (2010)

---

## Methodology

This document:
1. Extracts **verbatim text** from the paper constraining feedback blocks
2. Identifies what is **explicit** vs **implicit**
3. Proposes **minimal mathematical formulations** consistent with the paper
4. Labels all **assumptions** clearly
5. Introduces **no additional dynamics, delays, or filtering**

---

## Section 2.2.4: Afferent Feedback (Verbatim Extraction)

### Complete Verbatim Text from Paper:

> **"Afferent feedback"**
> 
> *"The Ia afferent feedback was assumed to be excitatory and proportional to muscle spindle activity. The Ib afferent feedback from Golgi tendon organs was assumed to be inhibitory and proportional to muscle force. The gains of the afferent feedback pathways were adjusted to produce physiologically realistic effects on motor unit activity."*

**That is the complete text** from Section 2.2.4. No other equations or descriptions are provided.

---

## Analysis of Verbatim Text

### What is EXPLICIT:

1. **Ia feedback:**
   - ✅ "excitatory" (positive sign)
   - ✅ "proportional to muscle spindle activity"

2. **Ib feedback:**
   - ✅ "inhibitory" (negative sign)
   - ✅ "proportional to muscle force"

3. **Feedback gains:**
   - ✅ Exist (plural: "gains")
   - ✅ Were "adjusted" (tuned/fitted)
   - ✅ Purpose: "produce physiologically realistic effects"

### What is IMPLICIT:

1. **Ia feedback:**
   - ❌ No equation for "muscle spindle activity"
   - ❌ No equation for Ia firing rate
   - ❌ No numerical value for gain
   - ❌ No specification of proportionality constant

2. **Ib feedback:**
   - ❌ No equation for Ib firing rate
   - ❌ No numerical value for gain
   - ❌ No specification of proportionality constant
   - ❌ No clarification of which force (fatigued vs unfatigued)

3. **Effective drive:**
   - ❌ No explicit equation combining descending drive and feedback
   - ❌ No specification of how feedback is added/subtracted

---

## Additional Relevant Text from Paper

### Section 2.2.1: Motor Neuron Pool (Verbatim)

> *"Gaussian white noise with standard deviation σ was added to the excitatory drive to represent synaptic noise."*

**Interpretation:** Noise is added to "the excitatory drive" (singular), suggesting a common drive signal.

### Figure 1 Caption (Verbatim)

> *"Schematic diagram of the model. The motor neuron pool receives excitatory drive and afferent feedback from Ia and Ib afferents."*

**Interpretation:** Motor neuron pool receives both drive and feedback.

### No Other Relevant Text

The paper contains **no other explicit equations or descriptions** for the feedback pathways.

---

## Minimal Mathematical Formulation

### Constraints from Paper:

1. Ia feedback is **proportional** to muscle spindle activity
2. Ib feedback is **proportional** to muscle force
3. Ia feedback is **excitatory** (positive)
4. Ib feedback is **inhibitory** (negative)
5. Feedback has **gains** (scaling factors)
6. No dynamics, delays, or filtering mentioned

---

## Block 5a: Ia Afferent Feedback

### Verbatim Constraint:

> *"The Ia afferent feedback was assumed to be excitatory and proportional to muscle spindle activity."*

### Explicit Components:

1. **Sign:** Excitatory (positive)
2. **Relationship:** Proportional (linear)
3. **Input:** "Muscle spindle activity"

### Implicit Components:

1. **What is "muscle spindle activity"?**
   - Paper does not define this
   - Paper does not model muscle length or velocity
   - Paper does not model fusimotor drive

2. **What is the proportionality constant?**
   - Paper does not specify
   - Paper states it was "adjusted"

### Minimal Mathematical Formulation:

```
Ia_signal(t) = k_Ia · spindle_activity(t)
```

where:
- `k_Ia` = proportionality constant (gain)
- `spindle_activity(t)` = proxy for muscle spindle activity

### Required Assumption #1: Spindle Activity Proxy

**Assumption (Implicit but necessary for implementation):**

Since the paper does not model muscle mechanics (length/velocity), muscle spindle activity must be approximated using available state variables.

**Options consistent with the model:**

**Option A: Mean activation**
```
spindle_activity(t) = ā(t) = (1/n_active) · Σ a_i(t)
```

**Rationale:**
- Activation is available from Block 2
- Activation correlates with muscle state during isometric contraction
- No additional variables needed

**Option B: Constant baseline**
```
spindle_activity(t) = constant
```

**Rationale:**
- Simplest approximation
- Represents tonic spindle firing
- No modulation with muscle state

**Option C: Normalized force**
```
spindle_activity(t) = F_total(t) / F_max
```

**Rationale:**
- Force is available from Block 3/4
- Force correlates with muscle state
- Alternative proxy

**Recommended:** Option A (mean activation) as it uses muscle state without requiring additional modeling.

### Final Equation for Block 5a:

```
Ia_signal(t) = k_Ia · ā(t)
```

where:
```
ā(t) = (1/n_active) · Σ a_i(t)
```

**Labeled Assumptions:**

1. **[Implicit but necessary for implementation]:** Muscle spindle activity is approximated by mean activation level, since the paper does not model muscle length/velocity dynamics.

2. **[Implicit but necessary for implementation]:** The proportionality is linear (no saturation or nonlinearity), consistent with "proportional to" in the paper.

3. **[Implicit but necessary for implementation]:** No temporal dynamics (no time constants or delays), as none are mentioned in the paper.

---

## Block 5b: Ib Afferent Feedback

### Verbatim Constraint:

> *"The Ib afferent feedback from Golgi tendon organs was assumed to be inhibitory and proportional to muscle force."*

### Explicit Components:

1. **Sign:** Inhibitory (negative)
2. **Relationship:** Proportional (linear)
3. **Input:** "Muscle force"

### Implicit Components:

1. **Which force?**
   - Fatigued or unfatigued?
   - Paper does not specify

2. **What is the proportionality constant?**
   - Paper does not specify
   - Paper states it was "adjusted"

### Minimal Mathematical Formulation:

```
Ib_signal(t) = k_Ib · force(t)
```

where:
- `k_Ib` = proportionality constant (gain)
- `force(t)` = muscle force

### Required Assumption #2: Which Force

**Assumption (Implicit but necessary for implementation):**

Since Golgi tendon organs sense actual muscle tension, the **fatigued force** should be used (output of Block 3).

**Equation:**
```
force(t) = F_total_fatigued(t)
```

**Rationale:**
- Golgi tendon organs are in series with muscle fibers
- They sense actual tension (fatigued force)
- Physiologically accurate
- Consistent with model structure (feedback from Block 3 output)

### Normalization:

To ensure Ib_signal is on the same scale as other drive components:

```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

where `F_max` is a normalization constant.

### Final Equation for Block 5b:

```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

**Labeled Assumptions:**

1. **[Implicit but necessary for implementation]:** Ib feedback uses fatigued force (output of Block 3), as Golgi tendon organs sense actual muscle tension.

2. **[Implicit but necessary for implementation]:** Force is normalized by F_max to ensure Ib_signal is on the same scale as descending drive.

3. **[Implicit but necessary for implementation]:** The proportionality is linear (no saturation or nonlinearity), consistent with "proportional to" in the paper.

4. **[Implicit but necessary for implementation]:** No temporal dynamics (no time constants or delays), as none are mentioned in the paper.

---

## Block 6: Effective Drive Calculation

### Verbatim Constraints:

**From Section 2.2.1:**
> *"Gaussian white noise with standard deviation σ was added to the excitatory drive to represent synaptic noise."*

**From Section 2.2.4:**
> *"The Ia afferent feedback was assumed to be excitatory..."*
> *"The Ib afferent feedback from Golgi tendon organs was assumed to be inhibitory..."*

**From Figure 1:**
> *"The motor neuron pool receives excitatory drive and afferent feedback from Ia and Ib afferents."*

### Explicit Components:

1. **Descending drive:** Exists (called "excitatory drive")
2. **Noise:** Added to drive (Gaussian, std = σ)
3. **Ia feedback:** Excitatory (added)
4. **Ib feedback:** Inhibitory (subtracted)

### Implicit Components:

1. **How are components combined?**
   - Paper does not provide explicit equation
   - Linear summation is implied

2. **What are the feedback gains?**
   - Paper mentions "gains" (plural)
   - Paper does not specify values
   - Paper states they were "adjusted"

### Minimal Mathematical Formulation:

The effective drive is the sum of all excitatory and inhibitory components:

```
e_eff(t) = e_descending(t) + Ia_contribution(t) - Ib_contribution(t) + ξ(t)
```

where:
- `e_descending(t)` = descending excitatory drive (external input)
- `Ia_contribution(t)` = excitatory feedback from Ia afferents
- `Ib_contribution(t)` = inhibitory feedback from Ib afferents (note: subtracted)
- `ξ(t)` = Gaussian white noise

### Feedback Contributions with Gains:

```
Ia_contribution(t) = g_Ia · Ia_signal(t)
Ib_contribution(t) = g_Ib · Ib_signal(t)
```

where:
- `g_Ia` = Ia feedback gain (positive)
- `g_Ib` = Ib feedback gain (positive, but contribution is subtracted)

### Final Equation for Block 6:

```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

**Expanded form (substituting Blocks 5a and 5b):**

```
e_eff(t) = e_descending(t) + g_Ia · k_Ia · ā(t) - g_Ib · k_Ib · (F_total_fatigued(t) / F_max) + ξ(t)
```

### Noise Generation:

From Section 2.2.1, noise is Gaussian white noise:

```
ξ(t) ~ N(0, σ²)
```

Implementation using Box-Muller transform (already used in Block 1):

```
u1 = uniform(0, 1)
u2 = uniform(0, 1)
z = sqrt(-2 · ln(u1)) · cos(2π · u2)
ξ(t) = σ · z
```

**Labeled Assumptions:**

1. **[Implicit but necessary for implementation]:** Components are combined by linear summation, as no other combination method is mentioned in the paper.

2. **[Implicit but necessary for implementation]:** Ia feedback is added (positive sign) because it is "excitatory".

3. **[Implicit but necessary for implementation]:** Ib feedback is subtracted (negative sign) because it is "inhibitory".

4. **[Implicit but necessary for implementation]:** Feedback signals are scaled by gains g_Ia and g_Ib, consistent with "gains of the afferent feedback pathways" mentioned in the paper.

5. **[Implicit but necessary for implementation]:** Noise is added to the total effective drive (not to individual components), consistent with "added to the excitatory drive" in Section 2.2.1.

6. **[Implicit but necessary for implementation]:** No temporal dynamics, delays, or filtering are applied, as none are mentioned in the paper.

---

## Summary of Minimal Formulations

### Block 5a: Ia Afferent Feedback

**Equation:**
```
Ia_signal(t) = k_Ia · ā(t)
```

where:
```
ā(t) = (1/n_active) · Σ a_i(t)  [mean activation over active motor units]
```

**Parameters:**
- `k_Ia` = Ia sensitivity/gain (to be tuned)

**Assumptions:**
- [Implicit] Spindle activity approximated by mean activation
- [Implicit] Linear proportionality
- [Implicit] No dynamics or delays

---

### Block 5b: Ib Afferent Feedback

**Equation:**
```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

**Parameters:**
- `k_Ib` = Ib sensitivity/gain (to be tuned)
- `F_max` = normalization constant (e.g., maximum force)

**Assumptions:**
- [Implicit] Uses fatigued force (actual tension)
- [Implicit] Force normalized to same scale as drive
- [Implicit] Linear proportionality
- [Implicit] No dynamics or delays

---

### Block 6: Effective Drive Calculation

**Equation:**
```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

**Expanded:**
```
e_eff(t) = e_descending(t) + g_Ia · k_Ia · ā(t) - g_Ib · k_Ib · (F_total_fatigued(t) / F_max) + ξ(t)
```

**Parameters:**
- `g_Ia` = Ia feedback gain (to be tuned)
- `g_Ib` = Ib feedback gain (to be tuned)
- `σ` = noise standard deviation (already defined in Block 1)

**Assumptions:**
- [Implicit] Linear summation of components
- [Implicit] Ia added (excitatory)
- [Implicit] Ib subtracted (inhibitory)
- [Implicit] Gains scale feedback contributions
- [Implicit] Noise added to total drive
- [Implicit] No dynamics, delays, or filtering

---

## Parameter Consolidation

The feedback system introduces **4 new parameters** (all mentioned but not valued in paper):

1. **k_Ia** - Ia sensitivity (proportionality constant)
2. **g_Ia** - Ia feedback gain
3. **k_Ib** - Ib sensitivity (proportionality constant)
4. **g_Ib** - Ib feedback gain

**Note:** The paper mentions "gains" (plural) but does not distinguish between sensitivity (k) and feedback gain (g). These could be combined:

**Simplified parameterization:**
```
Ia_contribution = G_Ia · ā(t)
Ib_contribution = G_Ib · (F_total_fatigued(t) / F_max)
```

where `G_Ia = g_Ia · k_Ia` and `G_Ib = g_Ib · k_Ib` are composite gains.

**This reduces to 2 parameters:**
1. **G_Ia** - Total Ia feedback gain
2. **G_Ib** - Total Ib feedback gain

---

## What is NOT Included (Not in Paper)

The following are **NOT** included because they are **NOT mentioned** in the paper:

1. ❌ Conduction delays (afferent pathway delays)
2. ❌ Synaptic delays (transmission delays)
3. ❌ Temporal filtering (low-pass, high-pass, etc.)
4. ❌ Nonlinear relationships (saturation, thresholds)
5. ❌ Spindle dynamics (differential equations for spindle response)
6. ❌ Golgi tendon organ dynamics
7. ❌ Fusimotor drive (γ-motor neuron activity)
8. ❌ Interneuron dynamics (for Ib pathway)
9. ❌ Muscle length/velocity dynamics
10. ❌ Rate-dependent effects (velocity sensitivity)

---

## Consistency Check

### With Paper's Explicit Statements:

✅ Ia feedback is excitatory (positive sign)  
✅ Ia feedback is proportional to muscle spindle activity (linear)  
✅ Ib feedback is inhibitory (negative sign)  
✅ Ib feedback is proportional to muscle force (linear)  
✅ Feedback has gains (scaling factors)  
✅ Noise is added to drive (Gaussian)  

### With Paper's Implicit Structure:

✅ No dynamics mentioned → no dynamics added  
✅ No delays mentioned → no delays added  
✅ No filtering mentioned → no filtering added  
✅ No nonlinearities mentioned → linear relationships used  
✅ No muscle mechanics modeled → proxy variables used  

### With Existing Blocks:

✅ Uses activation from Block 2 (for Ia)  
✅ Uses fatigued force from Block 3 (for Ib)  
✅ Uses noise generation from Block 1 (for ξ)  
✅ Outputs effective drive for Block 1 (e_eff)  

---

## Final Equations Summary

### Block 5a:
```
Ia_signal(t) = k_Ia · ā(t)
ā(t) = (1/n_active) · Σ a_i(t)
```

### Block 5b:
```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

### Block 6:
```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

### Composite (all blocks combined):
```
e_eff(t) = e_descending(t) 
           + g_Ia · k_Ia · ā(t) 
           - g_Ib · k_Ib · (F_total_fatigued(t) / F_max) 
           + ξ(t)
```

**These are the minimal formulations consistent with the paper, with all assumptions explicitly labeled.**

---

## Next Steps (NOT to be done yet)

1. Create pseudocode for Blocks 5a, 5b, 6
2. Implement in Python
3. Integrate with Block 1 (modify to use e_eff from Block 6)
4. Tune parameters (G_Ia, G_Ib) to match experimental data
5. Validate against paper's results

**Do NOT close the feedback loop yet** - equations are defined but not integrated.
