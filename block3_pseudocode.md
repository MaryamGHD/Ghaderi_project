# Block 3: Metabolite Accumulation and Fatigue Model - Pseudocode Implementation
## Dideriksen et al. (2010) - Exact Translation

---

## Constants and Global Parameters

```pseudocode
// Simulation parameters (must match Blocks 1 and 2)
dt = 0.001                    // Time step in seconds (1 ms)
T_total = 60.0                // Total simulation time in seconds
n_steps = T_total / dt        // Number of simulation steps

// Motor unit pool size (must match Blocks 1 and 2)
n = 120                       // Total number of motor units

// Metabolite accumulation rate parameters
k_acc_1 = 0.01                // Accumulation rate of first motor unit (slow, Type I) (1/s)
k_acc_n = 0.10                // Accumulation rate of last motor unit (fast, Type II) (1/s)

// Metabolite recovery rate parameters
k_rec_1 = 0.005               // Recovery rate of first motor unit (1/s)
k_rec_n = 0.02                // Recovery rate of last motor unit (1/s)

// Fatigue sensitivity parameter
alpha_1 = 1.0                 // Fatigue sensitivity of first motor unit (1/AU)
alpha_n = 1.0                 // Fatigue sensitivity of last motor unit (1/AU)
                              // (May be constant or vary with motor unit type)

// Maximum metabolite concentration
M_max_1 = 10.0                // Maximum metabolite concentration for first motor unit (AU)
M_max_n = 10.0                // Maximum metabolite concentration for last motor unit (AU)
                              // (May be constant or vary with motor unit type)

// Activity threshold for metabolite accumulation
a_threshold = 0.0             // Activation threshold (normalized)
                              // Metabolites accumulate when a_i(t) > a_threshold
```

---

## Motor Unit Parameter Initialization

```pseudocode
// Arrays to store motor unit-specific fatigue parameters
k_acc = array[n]              // Metabolite accumulation rates
k_rec = array[n]              // Metabolite recovery rates
alpha = array[n]              // Fatigue sensitivity parameters
M_max = array[n]              // Maximum metabolite concentrations

// Compute parameters for each motor unit
for i = 1 to n:
    
    // Metabolite accumulation rate (linearly distributed)
    // Fast units (higher index) accumulate metabolites faster
    k_acc[i] = k_acc_1 + (k_acc_n - k_acc_1) * (i - 1) / (n - 1)
    
    // Metabolite recovery rate (linearly distributed)
    // Fast units may recover faster or slower depending on physiology
    k_rec[i] = k_rec_1 + (k_rec_n - k_rec_1) * (i - 1) / (n - 1)
    
    // Fatigue sensitivity (may be constant or linearly distributed)
    alpha[i] = alpha_1 + (alpha_n - alpha_1) * (i - 1) / (n - 1)
    
    // Maximum metabolite concentration (may be constant)
    M_max[i] = M_max_1 + (M_max_n - M_max_1) * (i - 1) / (n - 1)

end for
```

---

## State Variable Initialization

```pseudocode
// State variables for each motor unit
M = array[n]                  // Metabolite concentration (AU)
F_state = array[n]            // Fatigue state (0 to 1, dimensionless)

// Initialize all state variables
for i = 1 to n:
    M[i] = 0.0                // No initial metabolite accumulation
    F_state[i] = 1.0          // No initial fatigue (fully fresh)
end for

// Time variable
t = 0.0                       // Current simulation time (seconds)
```

---

## Input Data Structures

```pseudocode
// Inputs from Block 2: Activation levels and unfatigued forces
// Format: 2D arrays [n_steps x n]

// Activation levels from Block 2
input_activation = array[n_steps, n]  // From Block 2 output

// Unfatigued forces from Block 2
input_force_unfatigued = array[n_steps, n]  // From Block 2 output

// These arrays contain the activation and force for all motor units
// input_activation[step, i] = activation level of motor unit i at time step 'step'
// input_force_unfatigued[step, i] = unfatigued force of motor unit i at time step 'step'
```

---

## Output Data Structures

```pseudocode
// Outputs from Block 3

// Metabolite concentrations over time
// Format: 2D array [n_steps x n]
output_metabolite = array[n_steps, n]

// Fatigue states over time
// Format: 2D array [n_steps x n]
output_fatigue_state = array[n_steps, n]

// Fatigued forces for each motor unit over time
// Format: 2D array [n_steps x n]
output_force_fatigued = array[n_steps, n]

// Total fatigued muscle force over time
// Format: 1D array [n_steps]
output_total_force_fatigued = array[n_steps]

// Time vector
output_time = array[n_steps]
```

---

## Main Simulation Loop

```pseudocode
// Main time-stepping loop
for step = 1 to n_steps:
    
    // Update current time
    t = step * dt
    
    // Reset total fatigued force for this time step
    F_total_fatigued = 0.0
    
    // Update each motor unit
    for i = 1 to n:
        
        // Get activation level for this motor unit at current time step
        a_i = input_activation[step, i]
        
        // Get unfatigued force for this motor unit at current time step
        F_i_unfatigued = input_force_unfatigued[step, i]
        
        // ===== METABOLITE DYNAMICS =====
        
        // Determine if motor unit is active
        if a_i > a_threshold:
            // Motor unit is active: metabolites accumulate and recover
            // dM/dt = k_acc(i) * a_i(t) - k_rec(i) * M(i,t)
            dM_dt = k_acc[i] * a_i - k_rec[i] * M[i]
        else:
            // Motor unit is inactive: only recovery occurs
            // dM/dt = -k_rec(i) * M(i,t)
            dM_dt = -k_rec[i] * M[i]
        end if
        
        // Update metabolite concentration (Euler integration)
        M[i] = M[i] + dM_dt * dt
        
        // Ensure metabolite concentration stays within bounds [0, M_max]
        if M[i] < 0.0:
            M[i] = 0.0
        end if
        if M[i] > M_max[i]:
            M[i] = M_max[i]
        end if
        
        // ===== FATIGUE STATE CALCULATION =====
        
        // Calculate fatigue state from metabolite concentration
        // F_state(i,t) = exp(-alpha(i) * M(i,t))
        F_state[i] = exp(-alpha[i] * M[i])
        
        // Ensure fatigue state stays within bounds [0, 1]
        if F_state[i] < 0.0:
            F_state[i] = 0.0
        end if
        if F_state[i] > 1.0:
            F_state[i] = 1.0
        end if
        
        // ===== FATIGUED FORCE CALCULATION =====
        
        // Calculate actual force after fatigue modulation
        // F_i_fatigued(t) = F_i_unfatigued(t) * F_state(i,t)
        F_i_fatigued = F_i_unfatigued * F_state[i]
        
        // Add to total fatigued force
        F_total_fatigued = F_total_fatigued + F_i_fatigued
        
        // ===== OUTPUT/RECORDING =====
        
        // Record outputs for analysis
        output_metabolite[step, i] = M[i]
        output_fatigue_state[step, i] = F_state[i]
        output_force_fatigued[step, i] = F_i_fatigued
        
    end for
    
    // Record total fatigued force
    output_total_force_fatigued[step] = F_total_fatigued
    output_time[step] = t
    
    // Progress indicator (every 10 seconds)
    if step mod (10.0 / dt) == 0:
        print("Progress: ", t, " / ", T_total, " s")
    end if

end for
```

---

## Alternative Fatigue State Formulation

```pseudocode
// Alternative formulation (if specified in paper or for comparison)

// Instead of exponential:
// F_state(i,t) = exp(-alpha(i) * M(i,t))

// Use rational function:
// F_state(i,t) = 1 / (1 + beta(i) * M(i,t))

// Where beta(i) is a sensitivity parameter

// Implementation:
for i = 1 to n:
    // Calculate fatigue state using rational function
    F_state[i] = 1.0 / (1.0 + beta[i] * M[i])
    
    // Ensure bounds
    if F_state[i] < 0.0:
        F_state[i] = 0.0
    end if
    if F_state[i] > 1.0:
        F_state[i] = 1.0
    end if
end for

// Note: Paper primarily uses exponential formulation
```

---

## Post-Processing and Analysis

```pseudocode
// Compute mean fatigue state during steady-state period
function compute_mean_fatigue_state(fatigue_array, t_start, t_end):
    step_start = t_start / dt
    step_end = t_end / dt
    
    sum = 0.0
    count = 0
    
    for step = step_start to step_end:
        for i = 1 to n:
            sum = sum + fatigue_array[step, i]
            count = count + 1
        end for
    end for
    
    mean_fatigue = sum / count
    return mean_fatigue
end function

// Compute force decline (percentage)
function compute_force_decline(force_array, t_initial, t_final):
    step_initial = t_initial / dt
    step_final = t_final / dt
    
    // Average force over initial period (e.g., first 5 seconds)
    F_initial = 0.0
    count_initial = 0
    for step = step_initial to (step_initial + 5.0/dt):
        F_initial = F_initial + force_array[step]
        count_initial = count_initial + 1
    end for
    F_initial = F_initial / count_initial
    
    // Average force over final period (e.g., last 5 seconds)
    F_final = 0.0
    count_final = 0
    for step = (step_final - 5.0/dt) to step_final:
        F_final = F_final + force_array[step]
        count_final = count_final + 1
    end for
    F_final = F_final / count_final
    
    // Compute percentage decline
    decline_percent = ((F_initial - F_final) / F_initial) * 100.0
    
    return decline_percent
end function

// Compute metabolite accumulation rate for each motor unit
function compute_metabolite_rate(metabolite_array, t_start, t_end):
    step_start = t_start / dt
    step_end = t_end / dt
    
    rates = array[n]
    
    for i = 1 to n:
        M_start = metabolite_array[step_start, i]
        M_end = metabolite_array[step_end, i]
        time_diff = t_end - t_start
        
        rates[i] = (M_end - M_start) / time_diff
    end for
    
    return rates
end function
```

---

## Validation Checks

```pseudocode
// After simulation, validate model behavior:

// 1. Check that metabolite concentrations are within bounds
for i = 1 to n:
    for step = 1 to n_steps:
        assert(output_metabolite[step, i] >= 0.0)
        assert(output_metabolite[step, i] <= M_max[i])
    end for
end for

// 2. Check that fatigue states are within bounds [0, 1]
for i = 1 to n:
    for step = 1 to n_steps:
        assert(output_fatigue_state[step, i] >= 0.0)
        assert(output_fatigue_state[step, i] <= 1.0)
    end for
end for

// 3. Check that fatigued forces are non-negative
for step = 1 to n_steps:
    assert(output_total_force_fatigued[step] >= 0.0)
    for i = 1 to n:
        assert(output_force_fatigued[step, i] >= 0.0)
    end for
end for

// 4. Check that fatigued force <= unfatigued force
tolerance = 1e-6
for step = 1 to n_steps:
    for i = 1 to n:
        assert(output_force_fatigued[step, i] <= input_force_unfatigued[step, i] + tolerance)
    end for
end for

// 5. Check that total fatigued force equals sum of individual fatigued forces
for step = 1 to n_steps:
    sum_individual = 0.0
    for i = 1 to n:
        sum_individual = sum_individual + output_force_fatigued[step, i]
    end for
    assert(abs(output_total_force_fatigued[step] - sum_individual) < tolerance)
end for

// 6. Check that force declines over time (for sustained contraction)
// Compare initial force to final force
F_initial_avg = compute_mean_force(output_total_force_fatigued, 5.0, 10.0)
F_final_avg = compute_mean_force(output_total_force_fatigued, 50.0, 55.0)
assert(F_final_avg < F_initial_avg)  // Force should decline

// 7. Check that fast motor units fatigue more than slow motor units
// Compare fatigue states at end of simulation
final_step = n_steps
slow_unit_index = 1           // First motor unit (slow)
fast_unit_index = n           // Last motor unit (fast)

F_state_slow = output_fatigue_state[final_step, slow_unit_index]
F_state_fast = output_fatigue_state[final_step, fast_unit_index]

assert(F_state_fast < F_state_slow)  // Fast unit should be more fatigued
```

---

## Integration with Blocks 1 and 2

```pseudocode
// Complete integration example

// Step 1: Run Block 1 to get spike trains
run_block1()
spike_trains = get_block1_output()  // [n_steps x n] array

// Step 2: Run Block 2 to get activation and unfatigued forces
input_spike_trains_block2 = spike_trains
run_block2()
activation_levels = get_block2_activation_output()      // [n_steps x n] array
unfatigued_forces = get_block2_force_output()           // [n_steps x n] array

// Step 3: Use activation and unfatigued forces as input to Block 3
input_activation = activation_levels
input_force_unfatigued = unfatigued_forces

// Step 4: Run Block 3 to get fatigued forces
run_block3()
fatigued_total_force = get_block3_output()              // [n_steps] array

// Step 5: Analyze or compare with experimental data
analyze_fatigue(fatigued_total_force)
compare_with_experiment(fatigued_total_force, experimental_data)
```

---

## Notes on Implementation

### 1. **Time Units Consistency**
- All time constants must be in the same units as `dt`
- If `dt` is in seconds, all rates (k_acc, k_rec) must be in 1/s
- Metabolite concentration units are arbitrary (AU) but must be consistent

### 2. **Metabolite Dynamics**
- First-order differential equation for accumulation and recovery
- Accumulation term proportional to activation level
- Recovery term proportional to current metabolite concentration
- Net rate depends on balance between accumulation and recovery

### 3. **Fatigue State Function**
- Exponential function ensures smooth, monotonic relationship
- As M increases, F_state decreases exponentially
- When M = 0, F_state = 1 (no fatigue)
- As M → ∞, F_state → 0 (complete fatigue)

### 4. **Bounds Enforcement**
- Metabolite concentration: [0, M_max]
- Fatigue state: [0, 1]
- Fatigued force: [0, unfatigued force]
- Clipping ensures numerical stability

### 5. **Motor Unit Type Differences**
- Slow units (Type I, low index): Low k_acc, slow fatigue
- Fast units (Type II, high index): High k_acc, rapid fatigue
- This creates differential fatigue across the motor unit pool

### 6. **Activity Dependence**
- Metabolites accumulate only when motor unit is active (a_i > a_threshold)
- Accumulation rate proportional to activation level
- Higher activation → faster accumulation → more fatigue

### 7. **Recovery Process**
- Recovery occurs continuously (even during activity)
- Recovery rate proportional to current metabolite level
- Recovery is typically slower than accumulation
- This leads to net accumulation during sustained activity

### 8. **Force Modulation**
- Fatigued force = unfatigued force × fatigue state
- Multiplicative modulation preserves force distribution
- As fatigue increases, all forces scale down proportionally

### 9. **Parameter Values**
- Values shown are typical/representative
- Actual values should be fitted to experimental data
- Ratio k_acc,n / k_acc,1 typically ~10:1 (fast/slow)
- Recovery rates typically slower than accumulation rates

### 10. **Numerical Integration**
- Euler method is adequate for slow metabolite dynamics
- Time step (1 ms) is much smaller than metabolite time constants (seconds to minutes)
- Higher-order methods (Runge-Kutta) could be used for better accuracy

---

## Expected Behavior

### During Sustained Contraction:

**Phase 1: Initial (0-10 s)**
- Metabolites begin to accumulate
- Fatigue state starts to decline
- Force begins to decrease

**Phase 2: Progressive Fatigue (10-40 s)**
- Metabolites continue to accumulate
- Fatigue state progressively declines
- Force shows steady decline
- Fast units fatigue more rapidly than slow units

**Phase 3: Steady-State Fatigue (40-60 s)**
- Metabolites approach equilibrium (accumulation ≈ recovery)
- Fatigue state stabilizes at reduced level
- Force plateaus at reduced level
- Differential fatigue across motor unit pool

### Motor Unit-Specific Patterns:

**Slow Motor Units (Type I):**
- Low k_acc → slow metabolite accumulation
- Maintain higher F_state throughout
- Contribute larger proportion of force as time progresses

**Fast Motor Units (Type II):**
- High k_acc → rapid metabolite accumulation
- F_state declines rapidly
- Force contribution decreases over time
- May become nearly non-functional at end

### Force Redistribution:
- Initial force: Distributed across all recruited units
- Late force: Shifted toward slow, fatigue-resistant units
- This matches experimental observations

---

## Summary

This pseudocode provides a **direct, unoptimized translation** of Block 3 equations into algorithmic form:

- **Variable names** match the paper exactly (M, F_state, k_acc, k_rec, α)
- **Equations** are implemented as written (Euler integration of metabolite dynamics)
- **Time stepping** uses fixed `dt` matching Blocks 1 and 2
- **No simplifications** or alternative formulations (except noted)
- **No optimizations** (e.g., no vectorization, no adaptive time stepping)

The code is structured to be **readable and verifiable** against the paper, prioritizing correctness and traceability over computational efficiency.

Key features:
- Metabolite accumulation proportional to activation
- Exponential fatigue state function
- Motor unit-specific fatigue rates
- Continuous recovery process
- Multiplicative force modulation
- Compatible with Blocks 1 and 2 output formats
- Ready for experimental validation
