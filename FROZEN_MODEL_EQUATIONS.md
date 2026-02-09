# FROZEN MODEL EQUATIONS
## Complete Mathematical Formulation - Dideriksen et al. (2010)
## **NO FURTHER MODIFICATIONS WILL BE MADE TO THESE EQUATIONS**

---

## Declaration

**This document contains the FINAL, FROZEN mathematical formulation of the complete model.**

✅ **All equations are finalized**  
✅ **All parameters are defined**  
✅ **All inputs/outputs are specified**  
✅ **No further modifications will be made in subsequent implementation steps**

Any implementation (pseudocode, Python) must follow these equations **exactly as written**.

---

## Model Overview

The model consists of **6 computational blocks** executed in the following order:

```
Block 6 (Effective Drive) → Block 1 (Motor Neurons) → Block 2 (Force) 
→ Block 3 (Fatigue) → Block 4 (Summation) → Block 5a,5b (Feedback) → [loop back to Block 6]
```

**Time resolution:** dt = 0.001 s (1 ms)  
**Motor unit pool size:** n = 120

---

## BLOCK 1: Motor Neuron Pool Model

### Purpose:
Models motor neuron electrical activity, recruitment, and spike generation.

### State Variables:
- `V[i]` - Membrane potential of motor unit i (mV)
- `AHP[i]` - Afterhyperpolarization of motor unit i (mV)
- `is_recruited[i]` - Recruitment status (boolean)

### Inputs:
- `e_eff(t)` - Effective excitatory drive **from Block 6** (includes descending drive + feedback + noise)

**CRITICAL:** Block 1 uses `e_eff(t)` from Block 6, NOT `e_descending(t)` directly. This closes the feedback loop.

### Outputs:
- `S[i](t)` - Spike train (binary: 0 or 1)

### Parameters:

**Fixed parameters:**
- `n = 120` - Number of motor units
- `RTE_1 = 0.01` - Recruitment threshold of first motor unit
- `RR = 50` - Range of recruitment thresholds
- `theta_1 = 10` mV - Firing threshold of first motor unit
- `theta_n = 10` mV - Firing threshold of last motor unit
- `tau_m_1 = 0.020` s - Membrane time constant of first motor unit
- `tau_m_n = 0.005` s - Membrane time constant of last motor unit
- `tau_AHP_1 = 0.100` s - AHP time constant of first motor unit
- `tau_AHP_n = 0.010` s - AHP time constant of last motor unit
- `A_AHP_1 = 5` mV - AHP amplitude of first motor unit
- `A_AHP_n = 50` mV - AHP amplitude of last motor unit
- `g = 40.0` - Gain factor (mV per normalized drive)
- `Delta_H = 0.05` - Recruitment hysteresis
- `sigma_noise = 0.02` - **[FREE]** Noise standard deviation

### Equations:

**Motor unit parameter distributions:**
```
RTE[i] = RTE_1 · exp((i-1) · ln(RR) / (n-1))
theta[i] = theta_1 + (theta_n - theta_1) · (i-1) / (n-1)
tau_m[i] = tau_m_1 + (tau_m_n - tau_m_1) · (i-1) / (n-1)
tau_AHP[i] = tau_AHP_1 + (tau_AHP_n - tau_AHP_1) · (i-1) / (n-1)
A_AHP[i] = A_AHP_1 · exp((i-1) · ln(A_AHP_n / A_AHP_1) / (n-1))
```

**Recruitment dynamics:**
```
if not is_recruited[i]:
    if e_eff(t) >= RTE[i]:
        is_recruited[i] = True
else:
    if e_eff(t) < RTE[i] - Delta_H:
        is_recruited[i] = False
```

**Membrane potential dynamics (if recruited):**
```
dV/dt = (-V[i] + g · e_eff(t) - AHP[i]) / tau_m[i]
```

**AHP dynamics:**
```
dAHP/dt = -AHP[i] / tau_AHP[i]
```

**Spike generation:**
```
if V[i] >= theta[i]:
    S[i] = 1
    AHP[i] = AHP[i] + A_AHP[i]
else:
    S[i] = 0
```

**If not recruited:**
```
S[i] = 0
V[i] = 0
```

---

## BLOCK 2: Muscle Force Generation

### Purpose:
Converts spike trains to muscle force via activation dynamics.

### State Variables:
- `a[i]` - Activation level of motor unit i (0 to 1)

### Inputs:
- `S[i](t)` - Spike trains from Block 1

### Outputs:
- `a[i](t)` - Activation levels
- `F[i](t)` - Unfatigued force per motor unit

### Parameters:

**Fixed parameters:**
- `T_c = 0.020` s - Contraction time of first motor unit
- `T_r = 0.090` s - Contraction time of last motor unit
- `P_1 = 0.001` N - Peak twitch force of first motor unit
- `RP = 100` - Range of peak twitch forces
- `k = 2` - Force-activation exponent (quadratic)

### Equations:

**Motor unit parameter distributions:**
```
tau_act[i] = T_c + (T_r - T_c) · (i-1) / (n-1)
tau_deact[i] = tau_act[i]
P[i] = P_1 · exp((i-1) · ln(RP) / (n-1))
```

**Activation dynamics:**
```
if S[i] = 1:
    da/dt = (1 - a[i]) / tau_act[i]
else:
    da/dt = -a[i] / tau_deact[i]
```

**Force generation:**
```
F[i](t) = P[i] · [a[i](t)]^k
```

---

## BLOCK 3: Metabolite Accumulation and Fatigue

### Purpose:
Models peripheral fatigue via metabolite accumulation.

### State Variables:
- `M[i]` - Metabolite concentration (arbitrary units)
- `F_state[i]` - Fatigue state (0 to 1)

### Inputs:
- `a[i](t)` - Activation levels from Block 2
- `F[i](t)` - Unfatigued forces from Block 2

### Outputs:
- `F_fatigued[i](t)` - Fatigued force per motor unit

### Parameters:

**Fixed parameters:**
- `k_acc_1 = 0.01` 1/s - Accumulation rate of first motor unit
- `k_acc_n = 0.10` 1/s - Accumulation rate of last motor unit
- `k_rec_1 = 0.005` 1/s - Recovery rate of first motor unit
- `k_rec_n = 0.02` 1/s - Recovery rate of last motor unit
- `alpha = 1.0` 1/AU - Fatigue sensitivity
- `M_max = 10.0` AU - Maximum metabolite concentration

### Equations:

**Motor unit parameter distributions:**
```
k_acc[i] = k_acc_1 + (k_acc_n - k_acc_1) · (i-1) / (n-1)
k_rec[i] = k_rec_1 + (k_rec_n - k_rec_1) · (i-1) / (n-1)
```

**Metabolite dynamics:**
```
if a[i](t) > 0:
    dM/dt = k_acc[i] · a[i](t) - k_rec[i] · M[i]
else:
    dM/dt = -k_rec[i] · M[i]
```

**Bounds:**
```
M[i] = max(0, min(M_max, M[i]))
```

**Fatigue state:**
```
F_state[i](t) = exp(-alpha · M[i](t))
```

**Fatigued force:**
```
F_fatigued[i](t) = F[i](t) · F_state[i](t)
```

---

## BLOCK 4: Force Summation

### Purpose:
Sums individual motor unit forces to produce total muscle force.

### Inputs:
- `F_fatigued[i](t)` - Fatigued forces from Block 3

### Outputs:
- `F_total(t)` - Total muscle force

### Equations:

**Force summation:**
```
F_total(t) = Σ F_fatigued[i](t)  [sum over i = 1 to n]
```

---

## BLOCK 5a: Ia Afferent Feedback

### Purpose:
Provides excitatory feedback proportional to muscle activation.

### Inputs:
- `a[i](t)` - Activation levels from Block 2

### Outputs:
- `Ia_signal(t)` - Ia afferent feedback signal

### Parameters:

**Free parameters:**
- `G_Ia` - **[FREE]** Total Ia feedback gain

### Equations:

**Mean activation:**
```
ā(t) = (1/n_active) · Σ a[i](t)  [sum over active motor units]
```

where `n_active` = number of motor units with `a[i] > 0.01`

**Ia signal:**
```
Ia_signal(t) = G_Ia · ā(t)
```

---

## BLOCK 5b: Ib Afferent Feedback

### Purpose:
Provides inhibitory feedback proportional to muscle force.

### Inputs:
- `F_total(t)` - Total muscle force from Block 4

### Outputs:
- `Ib_signal(t)` - Ib afferent feedback signal

### Parameters:

**Free parameters:**
- `G_Ib` - **[FREE]** Total Ib feedback gain
- `F_max` - Force normalization constant (set to maximum expected force)

### Equations:

**Ib signal:**
```
Ib_signal(t) = G_Ib · (F_total(t) / F_max)
```

---

## BLOCK 6: Effective Drive Calculation

### Purpose:
Combines descending drive with afferent feedback and noise.

### Inputs:
- `e_descending(t)` - Descending excitatory drive (external input)
- `Ia_signal(t)` - Ia feedback from Block 5a
- `Ib_signal(t)` - Ib feedback from Block 5b

### Outputs:
- `e_eff(t)` - Effective excitatory drive (to Block 1)

### Parameters:

**Fixed parameters:**
- `sigma_noise = 0.02` - Noise standard deviation (same as Block 1)

**Free parameters:**
- `G_Ia` - **[FREE]** Ia feedback gain (used in Block 5a)
- `G_Ib` - **[FREE]** Ib feedback gain (used in Block 5b)

### Equations:

**Noise generation (Box-Muller transform):**
```
u1 = uniform(0, 1)
u2 = uniform(0, 1)
z = sqrt(-2 · ln(u1)) · cos(2π · u2)
xi(t) = sigma_noise · z
```

**Effective drive:**
```
e_eff(t) = e_descending(t) + Ia_signal(t) - Ib_signal(t) + xi(t)
```

**Expanded form:**
```
e_eff(t) = e_descending(t) + G_Ia · ā(t) - G_Ib · (F_total(t) / F_max) + xi(t)
```

---

## Complete Parameter List

### Fixed Parameters (Values from Paper or Standard):

**Block 1:**
- `n = 120` - Motor unit pool size
- `RTE_1 = 0.01` - First recruitment threshold
- `RR = 50` - Recruitment range
- `theta_1 = 10` mV, `theta_n = 10` mV - Firing thresholds
- `tau_m_1 = 0.020` s, `tau_m_n = 0.005` s - Membrane time constants
- `tau_AHP_1 = 0.100` s, `tau_AHP_n = 0.010` s - AHP time constants
- `A_AHP_1 = 5` mV, `A_AHP_n = 50` mV - AHP amplitudes
- `g = 40.0` - Gain factor
- `Delta_H = 0.05` - Recruitment hysteresis

**Block 2:**
- `T_c = 0.020` s, `T_r = 0.090` s - Contraction times
- `P_1 = 0.001` N - First peak twitch force
- `RP = 100` - Peak force range
- `k = 2` - Force-activation exponent

**Block 3:**
- `k_acc_1 = 0.01` 1/s, `k_acc_n = 0.10` 1/s - Accumulation rates
- `k_rec_1 = 0.005` 1/s, `k_rec_n = 0.02` 1/s - Recovery rates
- `alpha = 1.0` 1/AU - Fatigue sensitivity
- `M_max = 10.0` AU - Max metabolite concentration

**Block 6:**
- `dt = 0.001` s - Time step

### Free Parameters (To Be Tuned):

1. **`sigma_noise`** - Noise standard deviation (typical: 0.01-0.05)
2. **`G_Ia`** - Ia feedback gain (typical: 0.1-0.3)
3. **`G_Ib`** - Ib feedback gain (typical: 0.2-0.4)
4. **`F_max`** - Force normalization (set to max expected force)

**Note:** Paper states these were "adjusted to produce physiologically realistic effects."

---

## Execution Order (One Time Step)

```
1. Block 6: Compute e_eff(t) from e_descending(t), Ia_signal(t-dt), Ib_signal(t-dt), xi(t)
2. Block 1: Update V[i], AHP[i], generate S[i] using e_eff(t)
3. Block 2: Update a[i], compute F[i] using S[i]
4. Block 3: Update M[i], compute F_state[i], compute F_fatigued[i] using a[i], F[i]
5. Block 4: Compute F_total using F_fatigued[i]
6. Block 5a: Compute Ia_signal using a[i]
7. Block 5b: Compute Ib_signal using F_total
8. Advance time: t = t + dt
9. Return to step 1
```

**Note:** Feedback signals computed at step t are used in step t+dt (one time step delay implicit in discrete implementation).

---

## Initial Conditions

**Block 1:**
```
V[i] = 0 mV
AHP[i] = 0 mV
is_recruited[i] = False
```

**Block 2:**
```
a[i] = 0
```

**Block 3:**
```
M[i] = 0 AU
F_state[i] = 1.0
```

**Block 5a, 5b:**
```
Ia_signal = 0
Ib_signal = 0
```

---

## Descending Drive Profile (Example)

**Ramp-and-hold to 30% MVC:**
```
if t < 5.0 s:
    e_descending(t) = 0.30 · (t / 5.0)
else:
    e_descending(t) = 0.30
```

---

## CONFIRMATION

### ✅ **EQUATIONS ARE FROZEN**

**All equations above are FINAL and will NOT be modified in:**
- Pseudocode generation
- Python implementation
- Parameter tuning
- Validation
- Any subsequent steps

**Any implementation must follow these equations EXACTLY.**

### ✅ **FEEDBACK LOOP IS CLOSED**

**The feedback loop is now explicitly closed:**

```
Block 6 (e_eff) → Block 1 (spikes) → Block 2 (activation, force) 
→ Block 3 (fatigued force) → Block 4 (total force) 
→ Block 5a (Ia feedback) + Block 5b (Ib feedback) → Block 6 (e_eff) → [loop]
```

**Key connection:**
- Block 1 receives `e_eff(t)` **from Block 6**
- Block 6 computes `e_eff(t) = e_descending(t) + Ia_signal(t) - Ib_signal(t) + ξ(t)`
- Ia_signal depends on activation (Block 2)
- Ib_signal depends on force (Block 4)
- Therefore: **muscle state feeds back to motor neurons**

**Confirmation:**
- ✅ Block 1 uses `e_eff(t)` from Block 6 (NOT `e_descending(t)` directly)
- ✅ Feedback signals (Ia, Ib) are computed from muscle state
- ✅ Feedback signals modulate effective drive
- ✅ Loop is closed: motor neurons → muscle → feedback → motor neurons

### ✅ **PARAMETERS ARE DEFINED**

**All parameters are listed with:**
- Fixed values (from paper or standard)
- Free parameters marked **[FREE]**
- Typical ranges for free parameters

### ✅ **INPUTS/OUTPUTS ARE SPECIFIED**

**All blocks have:**
- Clearly defined inputs
- Clearly defined outputs
- Specified data flow

### ✅ **MODEL IS COMPLETE**

**All 6 blocks are defined:**
- Block 1: Motor Neuron Pool ✅
- Block 2: Muscle Force Generation ✅
- Block 3: Fatigue ✅
- Block 4: Force Summation ✅
- Block 5a: Ia Feedback ✅
- Block 5b: Ib Feedback ✅
- Block 6: Effective Drive ✅

---

## Next Steps (Implementation Only)

1. **Pseudocode:** Translate frozen equations to algorithmic form
2. **Python:** Implement pseudocode line-by-line
3. **Integration:** Connect all blocks
4. **Tuning:** Adjust free parameters (G_Ia, G_Ib, sigma_noise)
5. **Validation:** Compare to experimental data

**NO EQUATION MODIFICATIONS** will occur during these steps.

---

**END OF FROZEN MODEL EQUATIONS**
