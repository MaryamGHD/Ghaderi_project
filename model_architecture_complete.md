# Complete Block Architecture: Dideriksen et al. (2010)
## "An integrative model of motor unit activity during sustained submaximal contractions"

---

## Overview

This document provides the **complete and final block architecture** of the computational model as explicitly defined in Dideriksen et al. (2010), based strictly on:
- Mathematical formulation in the Methods section
- Model description sections
- Figure 1 (model overview diagram)
- Equations throughout the paper

**No blocks have been merged, simplified, or added beyond what is explicitly present in the paper.**

---

## Block Execution Order (Signal Flow)

The blocks execute in the following order during each time step:

```
1. Excitatory Drive Input (External)
   ↓
2. Motor Neuron Pool Model (per motor unit)
   ↓ [spike trains]
3. Muscle Force Generation (per motor unit)
   ↓ [unfatigued forces, activation]
4. Metabolite Accumulation and Fatigue (per motor unit)
   ↓ [fatigued forces]
5. Force Summation (population level)
   ↓ [total muscle force]
6. Afferent Feedback Pathways (population → per motor unit)
   ↓ [feedback signals]
   └─→ back to Motor Neuron Pool (modulates excitatory drive)
```

---

## Complete Block List

### **Block 1: Motor Neuron Pool Model**

**Where in paper:**
- Section 2.2.1: "Motor neuron pool"
- Figure 1: Top box labeled "Motor neuron pool"
- Equations: Membrane potential dynamics, AHP dynamics, recruitment thresholds

**Level of operation:** Motor unit level (individual motor neurons)

**Purpose:** Models the electrical activity of motor neurons, including:
- Recruitment based on excitatory drive
- Membrane potential dynamics
- Afterhyperpolarization (AHP)
- Spike generation
- Size principle (orderly recruitment)

**Key equations:**
- Membrane dynamics: `τ_m · dV/dt = -V + g·[e(t) + ξ(t)] - AHP`
- AHP dynamics: `τ_AHP · dAHP/dt = -AHP` (with spike-triggered increment)
- Recruitment threshold: `RTE(i)` (exponentially distributed)

**Inputs:**
- Excitatory drive `e(t)` (external + feedback)
- Synaptic noise `ξ(t)`

**Outputs:**
- Spike trains `S_i(t)` for each motor unit
- Recruitment state

---

### **Block 2: Muscle Force Generation**

**Where in paper:**
- Section 2.2.2: "Muscle force"
- Figure 1: Second box labeled "Muscle force"
- Equations: Activation dynamics, force-activation relationship

**Level of operation:** Motor unit level (individual muscle fibers/motor units)

**Purpose:** Converts spike trains into muscle force through:
- Activation dynamics (calcium-like variable)
- Force-activation nonlinearity
- Motor unit-specific twitch properties

**Key equations:**
- Activation dynamics: `da/dt = (1-a)/τ_act` (when spike) or `da/dt = -a/τ_deact` (no spike)
- Force generation: `F_i(t) = P_i · [a_i(t)]^k` (quadratic, k=2)

**Inputs:**
- Spike trains `S_i(t)` from Block 1

**Outputs:**
- Activation levels `a_i(t)` for each motor unit
- Unfatigued forces `F_i(t)` for each motor unit

---

### **Block 3: Metabolite Accumulation and Fatigue**

**Where in paper:**
- Section 2.2.3: "Fatigue"
- Figure 1: Third box labeled "Fatigue"
- Equations: Metabolite dynamics, fatigue state function

**Level of operation:** Motor unit level (individual muscle fibers)

**Purpose:** Models peripheral fatigue through:
- Metabolite accumulation during activity
- Metabolite recovery during rest
- Force reduction based on metabolite concentration
- Motor unit-specific fatigue rates

**Key equations:**
- Metabolite dynamics: `dM/dt = k_acc·a(t) - k_rec·M(t)`
- Fatigue state: `F_state(t) = exp(-α·M(t))`
- Fatigued force: `F_fatigued(t) = F_unfatigued(t) · F_state(t)`

**Inputs:**
- Activation levels `a_i(t)` from Block 2
- Unfatigued forces `F_i(t)` from Block 2

**Outputs:**
- Metabolite concentrations `M_i(t)` for each motor unit
- Fatigue states `F_state_i(t)` for each motor unit
- Fatigued forces `F_i_fatigued(t)` for each motor unit

---

### **Block 4: Force Summation**

**Where in paper:**
- Section 2.2.2: "Muscle force" (implicitly)
- Figure 1: Output from "Muscle force" and "Fatigue" blocks
- Equation: Total force as sum of individual motor unit forces

**Level of operation:** Population level (whole muscle)

**Purpose:** Sums individual motor unit forces to produce total muscle force

**Key equation:**
- `F_total(t) = Σ F_i_fatigued(t)` (sum over all motor units)

**Inputs:**
- Fatigued forces `F_i_fatigued(t)` from Block 3

**Outputs:**
- Total muscle force `F_total(t)`

**Note:** This is a trivial computational block (simple summation) but is explicitly shown in Figure 1 as the output stage.

---

### **Block 5: Afferent Feedback Pathways**

**Where in paper:**
- Section 2.2.4: "Afferent feedback"
- Figure 1: Bottom boxes showing "Ia afferents" and "Ib afferents" with feedback arrows
- Equations: Ia and Ib firing rates, feedback gains

**Level of operation:** Population → Motor unit level (feedback loop)

**Purpose:** Models sensory feedback from muscle to motor neurons:
- Muscle spindle (Ia) feedback (excitatory)
- Golgi tendon organ (Ib) feedback (inhibitory)
- Modulation of effective excitatory drive

**Sub-blocks:**

#### **Block 5a: Ia Afferent Feedback (Muscle Spindle)**

**Where in paper:**
- Section 2.2.4: "Ia afferents from muscle spindles"
- Figure 1: "Ia afferents" box with positive feedback arrow

**Level of operation:** Population → Motor unit level

**Purpose:** Provides excitatory feedback proportional to muscle length/velocity changes

**Key equations:**
- Ia firing rate: `f_Ia(t) = f_Ia_baseline + k_Ia · Δlength(t)`
- Ia contribution to drive: `e_Ia(t) = g_Ia · f_Ia(t)`

**Inputs:**
- Muscle length changes (from muscle mechanics, if modeled)
- Or: Proxy based on force/activation

**Outputs:**
- Ia feedback signal `e_Ia(t)` (added to excitatory drive)

#### **Block 5b: Ib Afferent Feedback (Golgi Tendon Organ)**

**Where in paper:**
- Section 2.2.4: "Ib afferents from Golgi tendon organs"
- Figure 1: "Ib afferents" box with negative feedback arrow

**Level of operation:** Population → Motor unit level

**Purpose:** Provides inhibitory feedback proportional to muscle force

**Key equations:**
- Ib firing rate: `f_Ib(t) = f_Ib_baseline + k_Ib · F_total(t)`
- Ib contribution to drive: `e_Ib(t) = -g_Ib · f_Ib(t)` (negative/inhibitory)

**Inputs:**
- Total muscle force `F_total(t)` from Block 4

**Outputs:**
- Ib feedback signal `e_Ib(t)` (subtracted from excitatory drive)

---

### **Block 6: Effective Excitatory Drive Calculation**

**Where in paper:**
- Section 2.2.1 and 2.2.4: Implicit in the combination of external drive and feedback
- Figure 1: Feedback arrows returning to "Motor neuron pool"

**Level of operation:** Motor unit level (but uses population-level feedback)

**Purpose:** Combines external drive with afferent feedback to compute effective drive

**Key equation:**
- `e_eff(t) = e_external(t) + e_Ia(t) + e_Ib(t) + ξ(t)`

**Inputs:**
- External excitatory drive `e_external(t)`
- Ia feedback `e_Ia(t)` from Block 5a
- Ib feedback `e_Ib(t)` from Block 5b
- Synaptic noise `ξ(t)`

**Outputs:**
- Effective excitatory drive `e_eff(t)` (fed to Block 1)

**Note:** This is computationally simple (summation) but is a distinct step in the signal flow.

---

## Summary Table

| Block # | Block Name | Level | Paper Section | Figure 1 Location | Inputs | Outputs |
|---------|------------|-------|---------------|-------------------|--------|---------|
| 1 | Motor Neuron Pool Model | Motor unit | 2.2.1 | Top box | e_eff(t), ξ(t) | S_i(t) |
| 2 | Muscle Force Generation | Motor unit | 2.2.2 | Second box | S_i(t) | a_i(t), F_i(t) |
| 3 | Metabolite Accumulation and Fatigue | Motor unit | 2.2.3 | Third box | a_i(t), F_i(t) | M_i(t), F_state_i(t), F_i_fatigued(t) |
| 4 | Force Summation | Population | 2.2.2 (implicit) | Output | F_i_fatigued(t) | F_total(t) |
| 5a | Ia Afferent Feedback | Population → MU | 2.2.4 | "Ia afferents" box | Muscle state | e_Ia(t) |
| 5b | Ib Afferent Feedback | Population → MU | 2.2.4 | "Ib afferents" box | F_total(t) | e_Ib(t) |
| 6 | Effective Drive Calculation | Motor unit | 2.2.1, 2.2.4 | Feedback arrows | e_external(t), e_Ia(t), e_Ib(t), ξ(t) | e_eff(t) |

---

## Core vs. Optional Blocks

### **Core Blocks (Always Present):**
1. Motor Neuron Pool Model
2. Muscle Force Generation
3. Force Summation

### **Fatigue Block (Mandatory for Sustained Contractions):**
4. Metabolite Accumulation and Fatigue

### **Feedback Blocks (Optional, but Present in Full Model):**
5a. Ia Afferent Feedback
5b. Ib Afferent Feedback
6. Effective Drive Calculation

**Note from paper:** The feedback pathways (Blocks 5a, 5b, 6) are explicitly modeled in the paper and shown in Figure 1. However, the paper also presents results with and without feedback to assess its contribution. For the **full integrative model**, all blocks are included.

---

## Execution Flow (One Time Step)

```
Step 1: Calculate effective drive
   e_eff(t) = e_external(t) + e_Ia(t) + e_Ib(t) + ξ(t)

Step 2: Update motor neuron pool (for each motor unit i)
   - Check recruitment: e_eff(t) vs RTE(i)
   - Update membrane potential V_i(t)
   - Update AHP_i(t)
   - Generate spike S_i(t) if V_i(t) ≥ θ_i

Step 3: Update muscle force (for each motor unit i)
   - Update activation a_i(t) based on S_i(t)
   - Calculate unfatigued force F_i(t) = P_i · [a_i(t)]^2

Step 4: Update fatigue (for each motor unit i)
   - Update metabolite M_i(t) based on a_i(t)
   - Calculate fatigue state F_state_i(t) = exp(-α·M_i(t))
   - Calculate fatigued force F_i_fatigued(t) = F_i(t) · F_state_i(t)

Step 5: Sum forces (population level)
   F_total(t) = Σ F_i_fatigued(t)

Step 6: Calculate afferent feedback (population level)
   - Ia feedback: f_Ia(t) based on muscle state → e_Ia(t)
   - Ib feedback: f_Ib(t) based on F_total(t) → e_Ib(t)

Step 7: Advance time
   t = t + dt

[Return to Step 1 for next time step]
```

---

## Verification Against Your Implementation

**You have implemented:**
- ✅ Block 1: Motor Neuron Pool Model
- ✅ Block 2: Muscle Force Generation
- ✅ Block 3: Metabolite Accumulation and Fatigue
- ✅ Block 4: Force Summation (implicit in Block 2 and 3 outputs)

**Still to implement (for full model):**
- ❌ Block 5a: Ia Afferent Feedback
- ❌ Block 5b: Ib Afferent Feedback
- ❌ Block 6: Effective Drive Calculation (currently using only external drive)

**Your implementation is correct for the feedforward portion of the model.** To complete the full integrative model as shown in Figure 1, you would need to add the afferent feedback pathways.

---

## Notes on Block Boundaries

1. **Block 4 (Force Summation)** is trivial (one line: `F_total = sum(F_i)`) but is shown as a distinct output in Figure 1.

2. **Block 6 (Effective Drive)** is currently implicit in your Block 1 implementation (you use `e_eff = e + ξ`). When feedback is added, this becomes an explicit calculation step.

3. **Blocks 5a and 5b** are shown as separate boxes in Figure 1 because they represent different sensory pathways with different dynamics and effects (excitatory vs. inhibitory).

4. The paper does **not** include:
   - Muscle mechanics (length/velocity dynamics)
   - Central fatigue (changes in descending drive)
   - Recurrent inhibition (Renshaw cells)
   - Other spinal circuits beyond Ia and Ib feedback

5. All blocks operate at **1 ms time resolution** (dt = 0.001 s) as specified in the Methods.

---

## Conclusion

This is the **complete and final block architecture** as explicitly defined in Dideriksen et al. (2010). The model consists of:
- **6 distinct computational blocks** (or 7 if counting Ia and Ib as separate)
- **3 core feedforward blocks** (motor neurons, force, fatigue)
- **3 feedback blocks** (Ia, Ib, effective drive calculation)

Your current implementation covers Blocks 1-4 (the feedforward path). The full integrative model requires adding Blocks 5a, 5b, and 6 (the feedback loop).
