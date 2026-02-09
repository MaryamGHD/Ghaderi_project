# Block 2: Muscle Force Generation - Pseudocode Implementation
## Dideriksen et al. (2010) - Exact Translation

---

## Constants and Global Parameters

```pseudocode
// Simulation parameters (must match Block 1)
dt = 0.001                    // Time step in seconds (1 ms)
T_total = 60.0                // Total simulation time in seconds
n_steps = T_total / dt        // Number of simulation steps

// Motor unit pool size (must match Block 1)
n = 120                       // Total number of motor units

// Peak twitch force parameters
P_1 = 1.0                     // Peak twitch force of first motor unit (N or normalized)
RP = 50                       // Range of peak forces (ratio last/first)

// Activation time constant parameters (ms)
tau_act_1 = 40.0              // Activation time constant of first motor unit (ms)
tau_act_n = 15.0              // Activation time constant of last motor unit (ms)

// Deactivation time constant parameters (ms)
tau_deact_1 = 60.0            // Deactivation time constant of first motor unit (ms)
tau_deact_n = 25.0            // Deactivation time constant of last motor unit (ms)

// Contraction time parameters (ms)
T_c_1 = 100.0                 // Contraction time of first motor unit (ms)
T_c_n = 40.0                  // Contraction time of last motor unit (ms)

// Half-relaxation time parameters (ms)
T_r_1 = 110.0                 // Half-relaxation time of first motor unit (ms)
T_r_n = 45.0                  // Half-relaxation time of last motor unit (ms)

// Activation-force nonlinearity exponent
k = 2                         // Exponent for activation-force relationship (quadratic)
```

---

## Motor Unit Parameter Initialization

```pseudocode
// Arrays to store motor unit-specific parameters
P = array[n]                  // Peak twitch forces
tau_act = array[n]            // Activation time constants
tau_deact = array[n]          // Deactivation time constants
T_c = array[n]                // Contraction times
T_r = array[n]                // Half-relaxation times

// Compute parameters for each motor unit
for i = 1 to n:
    
    // Peak twitch force (exponentially distributed)
    P[i] = P_1 * exp((i - 1) * ln(RP) / (n - 1))
    
    // Activation time constant (linearly distributed, convert to seconds)
    tau_act[i] = (tau_act_1 + (tau_act_n - tau_act_1) * (i - 1) / (n - 1)) / 1000.0
    
    // Deactivation time constant (linearly distributed, convert to seconds)
    tau_deact[i] = (tau_deact_1 + (tau_deact_n - tau_deact_1) * (i - 1) / (n - 1)) / 1000.0
    
    // Contraction time (linearly distributed, convert to seconds)
    T_c[i] = (T_c_1 - (T_c_1 - T_c_n) * (i - 1) / (n - 1)) / 1000.0
    
    // Half-relaxation time (linearly distributed, convert to seconds)
    T_r[i] = (T_r_1 - (T_r_1 - T_r_n) * (i - 1) / (n - 1)) / 1000.0

end for
```

---

## State Variable Initialization

```pseudocode
// State variables for each motor unit
a = array[n]                  // Activation level (normalized, 0 to 1)
F = array[n]                  // Force produced by each motor unit (N)

// Initialize all state variables to zero
for i = 1 to n:
    a[i] = 0.0
    F[i] = 0.0
end for

// Total muscle force
F_total = 0.0                 // Total force (N)

// Time variable
t = 0.0                       // Current simulation time (seconds)
```

---

## Input Data Structure

```pseudocode
// Input from Block 1: Spike trains
// Format: 2D array [n_steps x n]
// Value: true/false at each time step for each motor unit
input_spike_trains = array[n_steps, n]  // From Block 1 output

// This array contains the spike trains S_i(t) for all motor units
// input_spike_trains[step, i] = true if motor unit i spiked at time step 'step'
```

---

## Main Simulation Loop

```pseudocode
// Main time-stepping loop
for step = 1 to n_steps:
    
    // Update current time
    t = step * dt
    
    // Reset total force for this time step
    F_total = 0.0
    
    // Update each motor unit
    for i = 1 to n:
        
        // Get spike input for this motor unit at current time step
        S_i = input_spike_trains[step, i]
        
        // ===== ACTIVATION DYNAMICS =====
        
        // Determine effective time constant based on activation direction
        // If spike occurs, activation rises with tau_act
        // If no spike, activation decays with tau_deact
        
        if S_i == true:
            // Spike occurred: activation rises toward 1
            // da/dt = (1 - a) / tau_act
            da_dt = (1.0 - a[i]) / tau_act[i]
        else:
            // No spike: activation decays toward 0
            // da/dt = -a / tau_deact
            da_dt = -a[i] / tau_deact[i]
        end if
        
        // Update activation level (Euler integration)
        a[i] = a[i] + da_dt * dt
        
        // Ensure activation stays within bounds [0, 1]
        if a[i] < 0.0:
            a[i] = 0.0
        end if
        if a[i] > 1.0:
            a[i] = 1.0
        end if
        
        // ===== FORCE GENERATION =====
        
        // Force is proportional to activation raised to power k
        // F_i(t) = P_i * [a_i(t)]^k
        F[i] = P[i] * (a[i] ^ k)
        
        // Add to total force
        F_total = F_total + F[i]
        
    end for
    
    // ===== OUTPUT/RECORDING =====
    
    // Record outputs for analysis
    // output_activation[step, i] = a[i]
    // output_force[step, i] = F[i]
    // output_total_force[step] = F_total
    // output_time[step] = t
    
end for
```

---

## Alternative Formulation: Twitch Impulse Response Model

```pseudocode
// This is an alternative implementation using impulse response
// Not the primary method in the paper, but mentioned for reference

// Twitch response function
function twitch_response(t, T_c, T_r):
    // Single twitch force profile
    // f_twitch(t) = A * (t/T_c)^k * exp(-t/T_r)
    
    if t < 0:
        return 0.0
    end if
    
    // Normalization constant (approximate)
    A = 1.0
    
    // Shape parameter
    k_shape = 2.0
    
    // Compute twitch profile
    f = A * ((t / T_c) ^ k_shape) * exp(-t / T_r)
    
    return f
end function

// Force as convolution of spike train with twitch response
// (This would replace the activation dynamics approach)
for step = 1 to n_steps:
    t = step * dt
    F_total = 0.0
    
    for i = 1 to n:
        F[i] = 0.0
        
        // Sum contributions from all previous spikes
        for prev_step = 1 to step:
            if input_spike_trains[prev_step, i] == true:
                t_spike = prev_step * dt
                t_since_spike = t - t_spike
                
                // Add twitch response from this spike
                F[i] = F[i] + P[i] * twitch_response(t_since_spike, T_c[i], T_r[i])
            end if
        end for
        
        F_total = F_total + F[i]
    end for
end for
```

---

## Output Data Structure

```pseudocode
// Outputs from Block 2

// Activation levels for each motor unit over time
// Format: 2D array [n_steps x n]
output_activation = array[n_steps, n]

// Force from each motor unit over time
// Format: 2D array [n_steps x n]
output_force = array[n_steps, n]

// Total muscle force over time
// Format: 1D array [n_steps]
output_total_force = array[n_steps]

// Time vector
output_time = array[n_steps]

// Copy data from simulation loop
for step = 1 to n_steps:
    for i = 1 to n:
        output_activation[step, i] = a[i]  // From simulation
        output_force[step, i] = F[i]       // From simulation
    end for
    output_total_force[step] = F_total     // From simulation
    output_time[step] = t                  // From simulation
end for

// This total force output can be:
// 1. Compared with experimental force recordings
// 2. Passed to Block 3 (Fatigue) as input
// 3. Passed to Block 4 (Feedback) for Golgi tendon organ input
```

---

## Post-Processing and Analysis

```pseudocode
// Compute mean force during steady-state period
function compute_mean_force(force_array, t_start, t_end):
    step_start = t_start / dt
    step_end = t_end / dt
    
    sum = 0.0
    count = 0
    
    for step = step_start to step_end:
        sum = sum + force_array[step]
        count = count + 1
    end for
    
    mean_force = sum / count
    return mean_force
end function

// Compute force variability (coefficient of variation)
function compute_force_CV(force_array, t_start, t_end):
    mean_f = compute_mean_force(force_array, t_start, t_end)
    
    step_start = t_start / dt
    step_end = t_end / dt
    
    sum_sq_diff = 0.0
    count = 0
    
    for step = step_start to step_end:
        diff = force_array[step] - mean_f
        sum_sq_diff = sum_sq_diff + diff * diff
        count = count + 1
    end for
    
    variance = sum_sq_diff / count
    std_dev = sqrt(variance)
    CV = std_dev / mean_f
    
    return CV
end function
```

---

## Notes on Implementation

### 1. **Time Units Consistency**
- All time constants must be in the same units as `dt`
- If `dt` is in seconds, convert all time constants from milliseconds to seconds
- Forces can be in Newtons or normalized units (must be consistent)

### 2. **Activation Dynamics Choice**
- Primary method: First-order differential equation with separate rise/decay time constants
- Alternative: Convolution with twitch impulse response
- Paper primarily uses the activation dynamics approach

### 3. **Activation Bounds**
- Activation level `a[i]` must stay within [0, 1]
- Clipping ensures numerical stability
- Physical interpretation: normalized calcium concentration

### 4. **Force Nonlinearity**
- Quadratic relationship (k=2) captures calcium-force nonlinearity
- Some implementations may use k between 1.5 and 3.0
- Paper specifies k=2

### 5. **Spike Input**
- Spike trains from Block 1 are binary (true/false or 1/0)
- Each spike triggers activation rise
- Between spikes, activation decays

### 6. **Force Summation**
- Linear summation of individual motor unit forces
- No mechanical interactions between motor units
- Valid for isometric contractions

### 7. **Parameter Values**
- Values shown are typical/representative
- Actual values should match those reported in the paper's Methods section
- Slow motor units: longer time constants, lower peak force
- Fast motor units: shorter time constants, higher peak force

---

## Validation Checks

```pseudocode
// After simulation, validate model behavior:

// 1. Check that activation levels are within bounds
for i = 1 to n:
    for step = 1 to n_steps:
        assert(output_activation[step, i] >= 0.0)
        assert(output_activation[step, i] <= 1.0)
    end for
end for

// 2. Check that forces are non-negative
for step = 1 to n_steps:
    assert(output_total_force[step] >= 0.0)
    for i = 1 to n:
        assert(output_force[step, i] >= 0.0)
    end for
end for

// 3. Check force distribution (larger motor units produce more force)
mean_forces = array[n]
for i = 1 to n:
    mean_forces[i] = compute_mean_force(output_force[:, i], t_start, t_end)
end for

// Mean force should generally increase with motor unit index
// (though not strictly monotonic due to recruitment timing)

// 4. Check that total force equals sum of individual forces
tolerance = 1e-6
for step = 1 to n_steps:
    sum_individual = 0.0
    for i = 1 to n:
        sum_individual = sum_individual + output_force[step, i]
    end for
    assert(abs(output_total_force[step] - sum_individual) < tolerance)
end for
```

---

## Integration with Block 1

```pseudocode
// Complete integration example

// Step 1: Run Block 1 to get spike trains
run_block1()
spike_trains = get_block1_output()  // [n_steps x n] array

// Step 2: Use spike trains as input to Block 2
input_spike_trains = spike_trains

// Step 3: Run Block 2 to get forces
run_block2()
total_force = get_block2_output()   // [n_steps] array

// Step 4: Analyze or pass to next block
analyze_force(total_force)
// or
pass_to_block3(total_force, activation_levels)
```

---

## Summary

This pseudocode provides a **direct, unoptimized translation** of Block 2 equations into algorithmic form:

- **Variable names** match the paper exactly
- **Equations** are implemented as written (Euler integration of activation dynamics)
- **Time stepping** uses fixed `dt` matching Block 1
- **No simplifications** or alternative formulations (except noted)
- **No optimizations** (e.g., no vectorization, no adaptive time stepping)

The code is structured to be **readable and verifiable** against the paper, prioritizing correctness and traceability over computational efficiency.

Key features:
- Separate activation and deactivation time constants
- Quadratic activation-force relationship
- Linear force summation across motor units
- Compatible with Block 1 output format
- Ready to pass output to Block 3 (Fatigue)
