# Feedback Blocks Summary: Blocks 5a, 5b, and 6
## Dideriksen et al. (2010) - Complete Feedback System

---

## Overview

This document summarizes the complete afferent feedback system as documented from Dideriksen et al. (2010), consisting of three interconnected blocks that create closed-loop sensory-motor control.

---

## Block Architecture

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │  Block 1: Motor Neuron Pool        │
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │ Spike trains
                                   ↓
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │  Block 2: Muscle Force Generation   │
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │ Activation, Force
                                   ↓
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │  Block 3: Fatigue                   │
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │ Fatigued Force
                                   ↓
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │  Block 4: Force Summation           │
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │ Total Force
                    ┌──────────────┴──────────────┐
                    │                             │
                    ↓                             ↓
         ┌──────────────────────┐    ┌──────────────────────┐
         │                      │    │                      │
         │  Block 5a: Ia        │    │  Block 5b: Ib        │
         │  Afferent Feedback   │    │  Afferent Feedback   │
         │  (Excitatory)        │    │  (Inhibitory)        │
         │                      │    │                      │
         └──────────┬───────────┘    └──────────┬───────────┘
                    │ Ia_signal              │ Ib_signal
                    │                        │
                    └────────┬───────────────┘
                             ↓
                  ┌──────────────────────────┐
                  │                          │
                  │  Block 6: Effective      │
                  │  Drive Calculation       │
                  │                          │
                  └──────────┬───────────────┘
                             │ e_eff(t)
                             │
                             └──→ Back to Block 1
```

---

## Complete Feedback Equation

### Master Equation (Block 6):

```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

### Component Equations:

**Block 5a (Ia Afferent Feedback):**
```
Ia_signal(t) = k_Ia · ā(t)
```
where `ā(t) = mean(a_i(t))` is mean activation across active motor units.

**Block 5b (Ib Afferent Feedback):**
```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```
where `F_total_fatigued(t)` is total muscle force from Block 3.

**Block 6 (Effective Drive):**
```
e_eff(t) = e_descending(t) + g_Ia · k_Ia · ā(t) - g_Ib · k_Ib · (F_total_fatigued(t) / F_max) + ξ(t)
```

---

## Parameters Summary

| Parameter | Block | Description | Typical Range | Sign |
|-----------|-------|-------------|---------------|------|
| k_Ia | 5a | Ia sensitivity to activation | 0.2 - 0.5 | Positive |
| g_Ia | 6 | Ia feedback gain | 0.1 - 0.3 | Positive |
| k_Ib | 5b | Ib sensitivity to force | 0.2 - 0.5 | Positive |
| g_Ib | 6 | Ib feedback gain | 0.2 - 0.4 | Positive (but subtracted) |
| σ_noise | 6 | Noise standard deviation | 0.01 - 0.05 | ± |
| F_max | 5b | Force normalization constant | Model-dependent | Positive |

---

## Signal Flow (One Time Step)

### Step 1: Compute Feedback Signals

**From Block 2 (activation):**
```
ā(t) = (1/n_active) · Σ a_i(t)
```

**From Block 3 (force):**
```
F_total_fatigued(t) = Σ F_i_fatigued(t)
```

**Block 5a (Ia feedback):**
```
Ia_signal(t) = k_Ia · ā(t)
```

**Block 5b (Ib feedback):**
```
Ib_signal(t) = k_Ib · (F_total_fatigued(t) / F_max)
```

### Step 2: Generate Noise

**Box-Muller transform:**
```
u1 = uniform(0, 1)
u2 = uniform(0, 1)
z = sqrt(-2 · ln(u1)) · cos(2π · u2)
ξ(t) = σ_noise · z
```

### Step 3: Compute Effective Drive

**Block 6:**
```
e_eff(t) = e_descending(t) + g_Ia · Ia_signal(t) - g_Ib · Ib_signal(t) + ξ(t)
```

### Step 4: Send to Motor Neuron Pool

**Block 1 uses e_eff(t) for:**
- Recruitment decisions
- Membrane potential dynamics
- Firing rate modulation

---

## Feedback Effects

### Ia Feedback (Positive/Excitatory):

**Mechanism:**
- Muscle activation → Ia afferent firing
- Ia firing → increased motor neuron excitation
- Increased excitation → more activation

**Effect:**
- Enhances motor output
- Amplifies voluntary commands
- Can lead to instability if too strong

**Physiological basis:**
- Muscle spindles detect muscle state
- Monosynaptic excitation (stretch reflex)
- Contributes to muscle tone

### Ib Feedback (Negative/Inhibitory):

**Mechanism:**
- Muscle force → Ib afferent firing
- Ib firing → decreased motor neuron excitation
- Decreased excitation → less force

**Effect:**
- Regulates force output
- Stabilizes motor control
- Protects muscle from excessive force

**Physiological basis:**
- Golgi tendon organs detect force
- Disynaptic inhibition (autogenic inhibition)
- Force regulation and protection

### Combined Effect:

**Balance:**
- Ia provides positive feedback (enhancement)
- Ib provides negative feedback (regulation)
- Net effect depends on relative gains (g_Ia vs g_Ib)

**Stability:**
- System is stable when g_Ib ≥ g_Ia
- Typical ratio: g_Ib/g_Ia ≈ 1.0 to 2.0

---

## Implementation Checklist

### Block 5a: Ia Afferent Feedback

- [ ] Compute mean activation: `ā(t) = mean(a_i(t))`
- [ ] Calculate Ia signal: `Ia_signal(t) = k_Ia · ā(t)`
- [ ] Set parameter: k_Ia (typical 0.2-0.5)

### Block 5b: Ib Afferent Feedback

- [ ] Get total fatigued force: `F_total_fatigued(t)` from Block 3
- [ ] Normalize force: `F_normalized(t) = F_total_fatigued(t) / F_max`
- [ ] Calculate Ib signal: `Ib_signal(t) = k_Ib · F_normalized(t)`
- [ ] Set parameter: k_Ib (typical 0.2-0.5)

### Block 6: Effective Drive Calculation

- [ ] Get descending drive: `e_descending(t)` (user-defined)
- [ ] Get Ia signal from Block 5a
- [ ] Get Ib signal from Block 5b
- [ ] Generate noise: `ξ(t)` using Box-Muller
- [ ] Compute effective drive: `e_eff(t) = e_descending + g_Ia·Ia - g_Ib·Ib + ξ`
- [ ] Set parameters: g_Ia (0.1-0.3), g_Ib (0.2-0.4), σ_noise (0.01-0.05)
- [ ] Send e_eff(t) to Block 1

---

## Integration with Existing Blocks

### Modifications to Block 1 (Motor Neuron Pool):

**Current implementation:**
```python
e_eff = e_descending + xi_t
```

**With feedback:**
```python
# Get feedback signals
Ia_signal = compute_Ia_feedback(activation_levels)  # From Block 5a
Ib_signal = compute_Ib_feedback(total_force)        # From Block 5b

# Compute effective drive
e_eff = e_descending + g_Ia * Ia_signal - g_Ib * Ib_signal + xi_t
```

### Data Flow:

**Forward path (already implemented):**
```
Block 1 → Block 2 → Block 3 → Block 4
```

**Feedback path (to be added):**
```
Block 4 → Block 5a, 5b → Block 6 → Block 1
```

---

## Parameter Tuning Guidelines

### Starting Values:

```python
# Ia feedback (excitatory)
k_Ia = 0.3        # Ia sensitivity
g_Ia = 0.2        # Ia feedback gain

# Ib feedback (inhibitory)
k_Ib = 0.3        # Ib sensitivity
g_Ib = 0.3        # Ib feedback gain

# Noise
sigma_noise = 0.02  # 2% noise

# Normalization
F_max = 1.0       # Maximum force (adjust based on simulation)
```

### Tuning Strategy:

1. **Start with no feedback** (g_Ia = g_Ib = 0)
   - Verify feedforward model works correctly
   
2. **Add Ia feedback only** (g_Ia > 0, g_Ib = 0)
   - Observe force enhancement
   - Increase g_Ia until force increases by ~10-20%
   
3. **Add Ib feedback** (g_Ib > 0)
   - Observe force regulation
   - Increase g_Ib until force is regulated
   - Ensure g_Ib ≥ g_Ia for stability
   
4. **Fine-tune both** to match experimental data
   - Adjust k_Ia, k_Ib for sensitivity
   - Adjust g_Ia, g_Ib for feedback strength

### Validation:

- Force should increase with Ia feedback (compared to no feedback)
- Force should be regulated with Ib feedback (less overshoot)
- System should remain stable (no oscillations)
- Compare with experimental force traces from paper

---

## Expected Behavior

### Without Feedback (Feedforward Only):

- Force follows descending drive directly
- No adaptation to muscle state
- Force variability only from noise

### With Ia Feedback Only:

- Force is enhanced (positive feedback)
- Faster rise to target force
- Potential instability if g_Ia too high

### With Ib Feedback Only:

- Force is regulated (negative feedback)
- Slower rise to target force
- More stable force output
- Lower peak force

### With Both Ia and Ib Feedback:

- Balanced enhancement and regulation
- Faster initial rise (Ia effect)
- Regulated steady-state (Ib effect)
- Stable force control
- Realistic force dynamics

---

## Files Created

1. **[block5a_ia_feedback.md](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block5a_ia_feedback.md)** - Complete Ia feedback documentation
2. **[block5b_ib_feedback.md](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block5b_ib_feedback.md)** - Complete Ib feedback documentation
3. **[block6_effective_drive.md](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block6_effective_drive.md)** - Complete effective drive documentation
4. **[feedback_blocks_summary.md](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/feedback_blocks_summary.md)** - This summary document

---

## Next Steps

1. **Create pseudocode** for Blocks 5a, 5b, and 6
2. **Implement in Python** following pseudocode line-by-line
3. **Integrate with existing blocks** (modify Block 1 to use e_eff with feedback)
4. **Test feedback system** with different gain values
5. **Validate against experimental data** from Dideriksen et al. (2010)
6. **Create integrated simulation** combining all blocks

---

## Summary

The complete feedback system consists of:

- **Block 5a**: Ia afferent feedback (excitatory, from muscle activation)
- **Block 5b**: Ib afferent feedback (inhibitory, from muscle force)
- **Block 6**: Effective drive calculation (combines all inputs)

**Master equation:**
```
e_eff(t) = e_descending(t) + g_Ia · k_Ia · ā(t) - g_Ib · k_Ib · (F_total/F_max) + ξ(t)
```

This creates a **closed-loop sensory-motor system** where muscle state modulates motor neuron activity, enabling realistic force control and adaptation during sustained contractions.

All blocks are now fully documented with exact equations, parameters, and connections as specified in Dideriksen et al. (2010).
