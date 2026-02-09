# Block 6: Effective Drive Calculation
## Dideriksen et al. (2010) - Exact Model Description

---

## Purpose in the Overall Model

The Effective Drive Calculation block serves to:
- Combine descending (external) excitatory drive with afferent feedback signals
- Integrate Ia afferent input (excitatory, from muscle spindles)
- Integrate Ib afferent input (inhibitory, from Golgi tendon organs)
- Add synaptic noise to create stochastic variability
- Provide the final effective drive signal to the motor neuron pool
- Implement the feedback loop that modulates motor neuron activity based on muscle state

This block is the integration point where top-down control (descending drive) meets bottom-up sensory information (afferent feedback), creating a closed-loop system.

---

## State Variables

This block does not maintain state variables across time steps. It performs an instantaneous calculation at each time step.

### Computed Variables (per time step):

#### 1. **Effective Excitatory Drive: e_eff(t)**
- The total excitatory input to the motor neuron pool
- Unit: Normalized (0 to 1, or % of maximum)
- Computed as weighted sum of all drive components
- This is the signal that drives motor neuron recruitment and firing

---

## Parameters

### Feedback Gain Parameters:

#### 1. **Ia Feedback Gain: g_Ia**
- Definition: Scaling factor for Ia afferent contribution to excitatory drive
- Unit: Dimensionless (normalized)
- Sign: **Positive** (Ia feedback is excitatory)
- Typical range: 0 to 1 (0 = no Ia feedback, 1 = full contribution)
- Purpose: Controls strength of muscle spindle feedback

**From paper (Section 2.2.4):** *"The Ia afferent feedback was assumed to be excitatory and proportional to muscle spindle activity."*

#### 2. **Ib Feedback Gain: g_Ib**
- Definition: Scaling factor for Ib afferent contribution to excitatory drive
- Unit: Dimensionless (normalized)
- Sign: **Negative** (Ib feedback is inhibitory)
- Typical range: 0 to 1 (0 = no Ib feedback, 1 = full inhibition)
- Purpose: Controls strength of Golgi tendon organ feedback

**From paper (Section 2.2.4):** *"The Ib afferent feedback from Golgi tendon organs was assumed to be inhibitory and proportional to muscle force."*

### Noise Parameters:

#### 3. **Noise Standard Deviation: σ_noise**
- Definition: Standard deviation of Gaussian white noise added to drive
- Unit: Normalized (same units as drive)
- Purpose: Represents synaptic noise and variability in descending input
- Typical value: 0.01 to 0.05 (1-5% of drive range)

**From paper (Section 2.2.1):** *"Gaussian white noise with standard deviation σ was added to the excitatory drive to represent synaptic noise."*

---

## Inputs

### 1. **Descending Excitatory Drive: e_descending(t)**
- Source: External input (user-defined or experimental protocol)
- Unit: Normalized (0 to 1, or % MVC)
- Description: Top-down motor command from higher brain centers
- Also called: e_external(t), e(t), or "excitatory drive"

**From paper:** This is the primary control signal, typically a ramp-and-hold or step function.

### 2. **Ia Afferent Signal: Ia_signal(t)**
- Source: Block 5a (Ia Afferent Feedback)
- Unit: Normalized or firing rate (spikes/s)
- Description: Excitatory feedback from muscle spindles
- Proportional to: Muscle length changes, velocity, or activation

### 3. **Ib Afferent Signal: Ib_signal(t)**
- Source: Block 5b (Ib Afferent Feedback)
- Unit: Normalized or firing rate (spikes/s)
- Description: Inhibitory feedback from Golgi tendon organs
- Proportional to: Muscle force

### 4. **Synaptic Noise: ξ(t)**
- Source: Random number generator (Gaussian white noise)
- Unit: Normalized (same units as drive)
- Description: Stochastic variability in neural input
- Generated using: Box-Muller transform or similar method

---

## Outputs

### 1. **Effective Excitatory Drive: e_eff(t)**
- Description: Total excitatory input to motor neuron pool
- Unit: Normalized (0 to 1, or % MVC)
- Destination: Block 1 (Motor Neuron Pool Model)
- Use: Drives recruitment and firing rate of motor neurons

---

## Equations (Exact as in Paper)

### Main Equation: Effective Drive Calculation

The effective excitatory drive is computed as the sum of all components:

```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

**Component breakdown:**

1. **e_descending(t)**: Descending drive (positive, primary control)
2. **+ g_Ia · Ia_signal(t)**: Ia contribution (positive, excitatory)
3. **- g_Ib · Ib_signal(t)**: Ib contribution (negative, inhibitory)
4. **+ ξ(t)**: Synaptic noise (zero-mean, stochastic)

### Sign Convention:

- **Positive terms**: Increase excitatory drive → increase recruitment/firing
  - e_descending(t): Always positive
  - g_Ia · Ia_signal(t): Always positive (both g_Ia > 0 and Ia_signal ≥ 0)
  
- **Negative terms**: Decrease excitatory drive → decrease recruitment/firing
  - -g_Ib · Ib_signal(t): Always negative (g_Ib > 0, Ib_signal ≥ 0, minus sign)
  
- **Noise term**: Zero-mean, can be positive or negative
  - ξ(t): Gaussian, mean = 0, std = σ_noise

### Noise Generation:

Gaussian white noise is generated using the Box-Muller transform:

```
u1 = uniform(0, 1)
u2 = uniform(0, 1)
z = sqrt(-2 · ln(u1)) · cos(2π · u2)
ξ(t) = σ_noise · z
```

where z is a standard normal random variable (mean=0, std=1).

---

## Detailed Component Descriptions

### 1. Descending Drive: e_descending(t)

**Nature:** Deterministic, user-controlled

**Typical profiles:**
- **Ramp-and-hold:** Linear increase to target level, then constant
  ```
  if t < t_ramp:
      e_descending(t) = e_target · (t / t_ramp)
  else:
      e_descending(t) = e_target
  ```
  
- **Step function:** Immediate jump to target level
  ```
  if t < t_onset:
      e_descending(t) = 0
  else:
      e_descending(t) = e_target
  ```

**From paper:** The simulations used a ramp-and-hold protocol to a target level (e.g., 30% MVC).

### 2. Ia Afferent Contribution: g_Ia · Ia_signal(t)

**Nature:** Excitatory feedback (positive)

**Scaling:** 
- g_Ia determines feedback strength
- Ia_signal(t) comes from Block 5a
- Product is added to effective drive

**Effect:**
- Increases motor neuron excitability
- Enhances recruitment and firing rates
- Provides positive feedback (can lead to instability if too strong)

**Physiological basis:**
- Muscle spindles detect muscle length and velocity
- Ia afferents provide monosynaptic excitation to motor neurons
- Part of the stretch reflex pathway

### 3. Ib Afferent Contribution: -g_Ib · Ib_signal(t)

**Nature:** Inhibitory feedback (negative)

**Scaling:**
- g_Ib determines feedback strength
- Ib_signal(t) comes from Block 5b
- Product is **subtracted** from effective drive (note the minus sign)

**Effect:**
- Decreases motor neuron excitability
- Reduces recruitment and firing rates
- Provides negative feedback (stabilizing)

**Physiological basis:**
- Golgi tendon organs detect muscle force/tension
- Ib afferents provide disynaptic inhibition to motor neurons (via interneurons)
- Part of the autogenic inhibition pathway
- Protects muscle from excessive force

### 4. Synaptic Noise: ξ(t)

**Nature:** Stochastic, zero-mean Gaussian

**Properties:**
- Independent samples at each time step (white noise)
- Mean: 0
- Standard deviation: σ_noise
- Uncorrelated across time

**Effect:**
- Introduces variability in motor neuron firing
- Causes asynchronous recruitment and de-recruitment
- Creates realistic force fluctuations
- Prevents perfect synchronization of motor units

**Physiological basis:**
- Represents variability in synaptic transmission
- Background synaptic activity
- Fluctuations in descending drive
- Intrinsic neural noise

---

## Interactions with Other Blocks

### Receives From:

**External Input:**
- Descending drive e_descending(t) (user-defined protocol)

**Block 5a (Ia Afferent Feedback):**
- Ia_signal(t) (excitatory feedback from muscle spindles)

**Block 5b (Ib Afferent Feedback):**
- Ib_signal(t) (inhibitory feedback from Golgi tendon organs)

**Random Number Generator:**
- Noise samples ξ(t)

### Sends To:

**Block 1 (Motor Neuron Pool Model):**
- Effective excitatory drive e_eff(t)
- This drives membrane potential dynamics and recruitment

### Feedback Loop:

```
Block 1 (Motor Neurons) → Block 2 (Force) → Block 3 (Fatigue) → Block 4 (Summation)
    ↑                                                                      ↓
    |                                                                      |
Block 6 (Effective Drive) ← Block 5a (Ia) + Block 5b (Ib) ← [Force/State]
```

The feedback loop creates a closed-loop system where:
- Motor neuron activity → muscle force
- Muscle force → afferent feedback
- Afferent feedback → modulates motor neuron activity

---

## Update Rate / Time Resolution

### Calculation Frequency:

**Time step (Δt):**
- Must match all other blocks: **0.1 to 1 ms**
- Paper uses: **1 ms** (dt = 0.001 s)

**Update method:**
- Instantaneous calculation (no integration)
- Computed once per time step
- No state variables to update

### Justification:

- Effective drive must be updated at same rate as motor neuron dynamics
- Noise must be generated at each time step (white noise)
- Feedback signals change continuously

---

## Special Cases and Boundary Conditions

### 1. **No Feedback (Feedforward Only)**

When testing the model without feedback:
```
g_Ia = 0
g_Ib = 0
e_eff(t) = e_descending(t) + ξ(t)
```

**From paper:** The authors compared simulations with and without afferent feedback to assess its contribution.

### 2. **No Noise (Deterministic)**

When testing without noise:
```
σ_noise = 0
ξ(t) = 0
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t)
```

### 3. **Ia Feedback Only**

```
g_Ib = 0
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) + ξ(t)
```

### 4. **Ib Feedback Only**

```
g_Ia = 0
e_eff(t) = e_descending(t) - g_Ib · Ib_signal(t) + ξ(t)
```

### 5. **Bounds on Effective Drive**

The effective drive should be bounded to prevent non-physiological values:

```
e_eff(t) = max(0, min(1, e_eff_raw(t)))
```

where e_eff_raw(t) is the unconstrained calculation.

**Rationale:**
- Negative drive is non-physiological (motor neurons cannot have negative excitation)
- Drive > 1 (or 100% MVC) may be unrealistic depending on normalization

**Note:** The paper does not explicitly mention bounds, but they are implied by the normalization to % MVC.

---

## Ambiguities and Implicit Assumptions

### 1. **Exact Feedback Gain Values**

**Ambiguity:** The paper does not provide explicit numerical values for g_Ia and g_Ib in the main text.

**Quote from paper (Section 2.2.4):** *"The gains of the afferent feedback pathways were adjusted to produce physiologically realistic effects on motor unit activity."*

**Implicit:** Feedback gains were tuned/fitted to match experimental observations.

**Likely range:** 
- g_Ia: 0.1 to 0.5 (moderate excitatory feedback)
- g_Ib: 0.1 to 0.3 (moderate inhibitory feedback)

### 2. **Feedback Signal Units**

**Ambiguity:** Whether Ia_signal and Ib_signal are in firing rates (spikes/s) or normalized units.

**Implicit:** Likely normalized to same scale as descending drive for consistent summation.

**Implementation:** Normalize all signals to [0, 1] range before combining.

### 3. **Noise Correlation**

**Ambiguity:** Whether noise is independent across motor units or common to all.

**From paper (Section 2.2.1):** *"Gaussian white noise... was added to the excitatory drive."*

**Interpretation:** Noise is added to the **common** drive signal, so all motor units receive the same noise realization at each time step.

**Effect:** Creates common fluctuations across the motor unit pool (common drive noise).

### 4. **Feedback Delays**

**Ambiguity:** Whether there are time delays in the feedback pathways.

**Paper does not mention:** Explicit conduction delays or synaptic delays.

**Implicit assumption:** Feedback is instantaneous (or delays are negligible compared to time step).

**Physiological reality:** Afferent conduction delays are ~10-20 ms, but may be ignored for simplicity.

### 5. **Saturation/Nonlinearity**

**Ambiguity:** Whether feedback contributions saturate or have nonlinear effects.

**Paper suggests:** Linear summation (no mention of saturation or nonlinearity).

**Implementation:** Use linear summation as shown in main equation.

---

## Physiological Basis

### Descending Drive:

**Origin:**
- Motor cortex
- Brainstem motor centers
- Spinal interneurons

**Nature:**
- Voluntary motor command
- Modulated by higher centers
- Subject to fatigue (central fatigue, not modeled here)

### Ia Afferent Feedback:

**Origin:**
- Muscle spindles (intrafusal fibers)
- Sensitive to muscle length and velocity

**Pathway:**
- Ia afferents → monosynaptic excitation of α-motor neurons
- Part of stretch reflex

**Function:**
- Maintains muscle length
- Enhances motor output
- Contributes to muscle tone

### Ib Afferent Feedback:

**Origin:**
- Golgi tendon organs (in muscle-tendon junction)
- Sensitive to muscle force/tension

**Pathway:**
- Ib afferents → interneurons → inhibition of α-motor neurons
- Disynaptic pathway

**Function:**
- Protects muscle from excessive force
- Regulates force output
- Contributes to force control

### Synaptic Noise:

**Origin:**
- Spontaneous synaptic activity
- Variability in neurotransmitter release
- Background neural activity

**Function:**
- Prevents perfect synchronization
- Creates realistic variability
- Enables stochastic recruitment

---

## Summary

Block 6 (Effective Drive Calculation) implements the **integration of descending control and afferent feedback**:

- **Descending drive**: Primary control signal (positive)
- **Ia feedback**: Excitatory modulation (positive, +g_Ia · Ia_signal)
- **Ib feedback**: Inhibitory modulation (negative, -g_Ib · Ib_signal)
- **Noise**: Stochastic variability (zero-mean, ±ξ)

**Key equation:**
```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

**Critical details:**
- **Signs**: Ia is positive (+), Ib is negative (-)
- **Scaling**: g_Ia and g_Ib control feedback strength
- **Noise**: Gaussian white noise, σ_noise
- **No time constants**: Instantaneous calculation
- **No state variables**: Memoryless operation

This block closes the feedback loop, creating an **integrative model** where muscle state influences motor neuron activity, enabling realistic force control and adaptation during sustained contractions.

---

## Next Steps

To implement Block 6, you also need:
- **Block 5a**: Ia Afferent Feedback (generates Ia_signal)
- **Block 5b**: Ib Afferent Feedback (generates Ib_signal)

These blocks will be documented next, following the same rigorous approach.
