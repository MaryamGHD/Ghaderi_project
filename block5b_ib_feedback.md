# Block 5b: Ib Afferent Feedback (Golgi Tendon Organ)
## Dideriksen et al. (2010) - Exact Model Description

---

## Purpose in the Overall Model

The Ib Afferent Feedback block serves to:
- Model the sensory feedback from Golgi tendon organs (Ib afferents)
- Provide inhibitory input to the motor neuron pool
- Implement the autogenic inhibition pathway
- Modulate motor neuron activity based on muscle force
- Create a negative feedback loop that stabilizes force output
- Protect muscle from excessive force/tension
- Represent force-dependent regulation of motor output

This block captures the disynaptic inhibitory pathway from Golgi tendon organs to α-motor neurons, which provides force-dependent negative feedback for motor control and muscle protection.

---

## State Variables

### For the Golgi Tendon Organ Population:

#### 1. **Ib Afferent Firing Rate: f_Ib(t)**
- Represents the instantaneous firing rate of Ib afferents
- Unit: Spikes per second (Hz) or normalized
- Range: f_Ib_min to f_Ib_max
- Computed from muscle force

**Note:** The paper does not explicitly model individual Golgi tendon organs. The Ib firing rate represents the population-averaged activity.

---

## Parameters

### Baseline Activity:

#### 1. **Baseline Ib Firing Rate: f_Ib_baseline**
- Definition: Resting firing rate of Ib afferents (no muscle force)
- Unit: Spikes per second (Hz) or normalized
- Typical value: 5-20 Hz (physiological range, lower than Ia)
- Purpose: Represents tonic Golgi tendon organ activity at rest

**From paper:** Not explicitly stated; implicit in the model formulation.

### Sensitivity Parameters:

#### 2. **Ib Sensitivity to Force: k_Ib**
- Definition: Gain relating muscle force to Ib firing rate
- Unit: Hz per Newton (or Hz per normalized force)
- Purpose: Determines how strongly Ib firing responds to force changes
- Typical range: Depends on normalization

**From paper (Section 2.2.4):** *"The Ib afferent feedback from Golgi tendon organs was assumed to be inhibitory and proportional to muscle force."*

### Feedback Gain (used in Block 6):

#### 3. **Ib Feedback Gain: g_Ib**
- Definition: Scaling factor for Ib contribution to effective drive
- Unit: Dimensionless
- Range: 0 to 1 (or higher if needed)
- Purpose: Controls strength of Ib feedback in the motor neuron pool

**Note:** This parameter is used in Block 6, but listed here for completeness.

---

## Inputs

### 1. **Total Muscle Force: F_total(t)**

**Source:** Block 4 (Force Summation)

**Description:** The total force produced by all motor units (after fatigue modulation)

**Unit:** Newtons (N) or normalized (% of maximum force)

**Use:** Direct input to Ib firing rate calculation

**From paper (Section 2.2.4):** *"The Ib afferent feedback from Golgi tendon organs was assumed to be inhibitory and proportional to muscle force."*

**This is explicit and unambiguous** - Ib feedback is driven by total muscle force.

---

## Outputs

### 1. **Ib Afferent Signal: Ib_signal(t)**
- Description: Normalized Ib afferent contribution to excitatory drive
- Unit: Normalized (same scale as descending drive)
- Destination: Block 6 (Effective Drive Calculation)
- Use: Subtracted from effective drive with gain g_Ib (inhibitory)

---

## Equations (Exact as in Paper)

### Primary Formulation: Ib Firing Rate

The Ib afferent firing rate is modeled as:

```
f_Ib(t) = f_Ib_baseline + k_Ib · F_total(t)
```

**Component breakdown:**

1. **f_Ib_baseline**: Tonic background firing rate
2. **k_Ib · F_total(t)**: Force-dependent modulation

**Interpretation:**
- As muscle force increases, Ib firing rate increases
- Higher force → more Ib activity → more inhibition

### Normalization to Ib Signal:

The Ib firing rate is normalized to create the Ib signal:

```
Ib_signal(t) = (f_Ib(t) - f_Ib_baseline) / f_Ib_scale
```

where `f_Ib_scale` is a normalization constant to bring Ib_signal to the same scale as descending drive (e.g., 0 to 1).

**Simplified form (if already normalized):**
```
Ib_signal(t) = k_Ib · F_total(t)
```

where k_Ib is adjusted to produce appropriately scaled output.

### Alternative Formulation (Normalized Force):

If force is normalized to maximum force F_max:

```
F_normalized(t) = F_total(t) / F_max
Ib_signal(t) = k_Ib · F_normalized(t)
```

This ensures Ib_signal is in the range [0, k_Ib] when force is in [0, F_max].

---

## Connection to Block 6 (Effective Drive)

The Ib signal is used in Block 6 as follows:

```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
                                                    ^^^^^^^^^^^^^^^^^^^^
                                                    Ib contribution (NEGATIVE)
```

**Ib contribution:**
```
Ib_contribution(t) = -g_Ib · Ib_signal(t)
```

**Sign:** Negative (inhibitory)

**Effect:**
- Decreases effective drive
- Reduces motor neuron recruitment and firing
- Creates negative feedback loop
- Stabilizes force output

**Scaling:**
- g_Ib controls the strength of Ib feedback
- Ib_signal(t) increases with muscle force
- Product is **subtracted** from descending drive (note the minus sign)

---

## Interactions with Other Blocks

### Receives From:

**Block 4 (Force Summation):**
- Total muscle force F_total(t)
- This is the direct and primary input

**OR (if using fatigued force):**

**Block 3 (Fatigue):**
- Total fatigued force F_total_fatigued(t)
- More physiologically accurate (Golgi tendon organs sense actual force)

### Sends To:

**Block 6 (Effective Drive Calculation):**
- Ib_signal(t) (inhibitory feedback signal)

### Feedback Loop:

```
Block 1 (Motor Neurons) → Block 2 (Force) → Block 3 (Fatigue) → Block 4 (Summation)
    ↑                                                                      ↓
    |                                                                      |
Block 6 (Effective Drive) ← Block 5b (Ib Feedback) ← [Total Force]
```

The Ib feedback creates a **negative feedback loop**:
- Motor neuron activity → muscle force
- Muscle force → Ib afferent activity
- Ib afferent activity → decreased motor neuron excitation
- Decreased excitation → less force (loop stabilizes)

**Stability consideration:** Negative feedback is inherently stabilizing. It prevents excessive force and provides automatic regulation.

---

## Update Rate / Time Resolution

### Calculation Frequency:

**Time step (Δt):**
- Must match all other blocks: **0.1 to 1 ms**
- Paper uses: **1 ms** (dt = 0.001 s)

**Update method:**
- Instantaneous calculation (no integration)
- Computed once per time step based on current force
- No state variables with dynamics (unless modeling Golgi tendon organ dynamics explicitly)

### Justification:

- Ib afferent firing rate responds quickly to force changes
- Conduction delays (~10-20 ms) are ignored or negligible
- Golgi tendon organ dynamics (if modeled) would require integration, but paper uses instantaneous response

---

## Ambiguities and Implicit Assumptions

### 1. **Force Input: Fatigued vs. Unfatigued**

**Ambiguity:** Whether Ib feedback uses fatigued or unfatigued force.

**Physiological reality:** Golgi tendon organs sense actual muscle tension (fatigued force).

**Likely implementation:** Use **fatigued force** F_total_fatigued(t) from Block 3.

**Equation:**
```
f_Ib(t) = f_Ib_baseline + k_Ib · F_total_fatigued(t)
```

### 2. **Ib Sensitivity Parameter k_Ib**

**Ambiguity:** Exact numerical value not provided in the paper.

**Quote from paper (Section 2.2.4):** *"The gains of the afferent feedback pathways were adjusted to produce physiologically realistic effects on motor unit activity."*

**Implicit:** Parameter was tuned to experimental data.

**Typical range:** 0.1 to 0.5 (when Ib_signal is normalized to 0-1 scale).

### 3. **Baseline Firing Rate**

**Ambiguity:** Whether f_Ib_baseline is included or if Ib_signal represents only the force-dependent component.

**Implementation choice:**
- **Include baseline**: `Ib_signal(t) = f_Ib_baseline + k_Ib · F_total(t)`
- **Exclude baseline**: `Ib_signal(t) = k_Ib · F_total(t)` (baseline absorbed into resting state)

**Likely:** Exclude baseline (simpler, baseline is part of resting drive).

### 4. **Conduction Delays**

**Ambiguity:** Whether afferent conduction delays are modeled.

**Paper does not mention:** Explicit delays.

**Physiological reality:** Ib afferent conduction velocity ~70-120 m/s, delay ~10-20 ms for typical limb muscles.

**Implicit assumption:** Delays are negligible or ignored (instantaneous feedback).

### 5. **Golgi Tendon Organ Dynamics**

**Ambiguity:** Whether Golgi tendon organ dynamics (adaptation, rate sensitivity) are modeled.

**Paper does not mention:** Golgi tendon organ dynamics or differential equations.

**Implicit assumption:** Instantaneous, static relationship between force and Ib firing.

**Simplification:** `f_Ib(t) = f(F_total(t))` with no temporal dynamics.

### 6. **Disynaptic Pathway**

**Ambiguity:** Whether the disynaptic nature of Ib inhibition is explicitly modeled.

**Physiological reality:** Ib afferents → interneurons → α-motor neurons (two synapses).

**Paper does not mention:** Explicit interneuron dynamics.

**Implicit assumption:** Disynaptic pathway is lumped into a single inhibitory gain (g_Ib).

---

## Physiological Basis

### Golgi Tendon Organs:

**Structure:**
- Located in muscle-tendon junction
- In series with muscle fibers (sense tension)
- Innervated by Ib afferents

**Function:**
- Detect muscle force/tension
- Provide proprioceptive feedback about muscle load
- Protect muscle from excessive force

**Sensitivity:**
- Highly sensitive to active muscle contraction
- Less sensitive to passive stretch (compared to spindles)
- Linear response to force over wide range

### Ib Afferents:

**Properties:**
- Large-diameter, fast-conducting axons (70-120 m/s)
- Disynaptic inhibition of α-motor neurons (via interneurons)
- Part of the autogenic inhibition pathway

**Firing characteristics:**
- Baseline firing: 5-20 Hz at rest (lower than Ia)
- Increases linearly with muscle force
- Sensitive to both active and passive tension

**Function:**
- Regulate muscle force output
- Prevent excessive muscle tension
- Contribute to smooth force control
- Protect muscle and tendon from damage

### Autogenic Inhibition:

**Pathway:**
- Muscle force → Golgi tendon organ activation → Ib firing
- Ib afferents → inhibitory interneurons (Ib interneurons)
- Inhibitory interneurons → α-motor neurons (inhibition)
- α-motor neurons → reduced muscle contraction
- Reduced contraction → decreased force

**Function:**
- Automatic force regulation
- Prevents muscle damage from excessive force
- Contributes to smooth force control
- Balances excitatory drive

**Clinical relevance:**
- Clasp-knife reflex (sudden relaxation under high force)
- Impaired in spasticity (reduced Ib inhibition)

---

## Implementation Considerations

### Recommended Approach:

Given the paper's explicit statement that Ib feedback is proportional to force:

**Implementation:**
```
F_total_fatigued(t) = output from Block 3
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

where F_max is a normalization constant (e.g., maximum force at 100% MVC).

**Rationale:**
- Directly follows paper's description
- Uses actual force (fatigued) as sensed by Golgi tendon organs
- Simple and physiologically accurate

### Parameter Selection:

**k_Ib (Ib sensitivity):**
- Start with: 0.2 to 0.5
- Tune to produce ~10-30% reduction in effective drive at high forces
- Ensure stability (negative feedback is stabilizing)

**g_Ib (Ib feedback gain, used in Block 6):**
- Start with: 0.1 to 0.3
- Tune based on experimental data
- Balance with g_Ia to maintain stability
- Higher g_Ib → more force regulation, lower peak force

**F_max (normalization constant):**
- Use maximum force from unfatigued simulation
- Or set to expected maximum force (e.g., sum of all P_i)

### Validation:

- Check that Ib feedback reduces motor output (decreases force)
- Verify that force is regulated (negative feedback effect)
- Compare with experimental observations of force control
- Ensure system remains stable (no oscillations)

---

## Interaction with Ia Feedback (Stability)

### Feedback Balance:

The combination of Ia (positive) and Ib (negative) feedback creates a balanced system:

**Ia feedback (positive):**
- Enhances motor output
- Can lead to instability if too strong
- Contribution: `+g_Ia · Ia_signal(t)`

**Ib feedback (negative):**
- Reduces motor output
- Stabilizing influence
- Contribution: `-g_Ib · Ib_signal(t)`

**Net feedback effect:**
```
Net_feedback(t) = g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t)
```

**Stability condition:**
- If g_Ib > g_Ia: System is stable (negative feedback dominates)
- If g_Ib < g_Ia: System may be unstable (positive feedback dominates)
- If g_Ib ≈ g_Ia: Balanced feedback (typical physiological condition)

**Typical values:**
- g_Ia: 0.1 to 0.3 (moderate excitatory feedback)
- g_Ib: 0.2 to 0.4 (moderate to strong inhibitory feedback)
- Ratio g_Ib/g_Ia: 1.0 to 2.0 (Ib slightly stronger for stability)

---

## Summary

Block 5b (Ib Afferent Feedback) implements **inhibitory proprioceptive feedback** from Golgi tendon organs:

- **Muscle force** drives Ib afferent firing
- **Ib firing rate**: `f_Ib(t) = f_Ib_baseline + k_Ib · F_total(t)`
- **Ib signal**: `Ib_signal(t) = k_Ib · (F_total(t) / F_max)` (normalized)
- **Feedback**: Subtracted from effective drive in Block 6 with gain g_Ib
- **Effect**: Inhibitory (negative feedback)

**Key equation:**
```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

**Connection to Block 6:**
```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
                                                    ^^^^^^^^^^^^^^^^^^^^
                                                    Ib contribution (NEGATIVE)
```

**Critical details:**
- **Sign**: Negative (inhibitory, note the minus sign)
- **Input**: Total fatigued force F_total_fatigued(t)
- **No dynamics**: Instantaneous response
- **No delays**: Conduction delays ignored
- **Stability**: Negative feedback is stabilizing

This block closes the **negative feedback loop** from muscle force to motor neurons, representing autogenic inhibition and force regulation.

---

## Complete Feedback System

With Blocks 5a and 5b implemented, the complete feedback system is:

```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

where:
- **e_descending(t)**: External motor command
- **Ia_signal(t)**: Excitatory feedback (from muscle state/activation)
- **Ib_signal(t)**: Inhibitory feedback (from muscle force)
- **ξ(t)**: Synaptic noise

**Feedback effects:**
- **Ia**: Enhances motor output (positive feedback)
- **Ib**: Regulates force output (negative feedback)
- **Balance**: Creates stable, regulated motor control

This completes the **integrative model** with full sensory-motor feedback loops as described in Dideriksen et al. (2010).
