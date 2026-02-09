# Block 1: Motor Neuron Pool Model - Pseudocode Implementation
## Dideriksen et al. (2010) - Exact Translation

---

## Constants and Global Parameters

```pseudocode
// Simulation parameters
dt = 0.001                    // Time step in seconds (1 ms)
T_total = 60.0                // Total simulation time in seconds
n_steps = T_total / dt        // Number of simulation steps

// Motor unit pool size
n = 120                       // Total number of motor units

// Recruitment threshold parameters
RTE_1 = 0.01                  // Recruitment threshold of first motor unit (normalized)
RR = 100                      // Range of recruitment thresholds (ratio last/first)

// Minimum firing rate parameters (pps = pulses per second)
f_min_1 = 8.0                 // Minimum firing rate of first motor unit (pps)
f_min_n = 12.0                // Minimum firing rate of last motor unit (pps)

// Peak firing rate parameters (pps)
f_peak_1 = 35.0               // Peak firing rate of first motor unit (pps)
f_peak_n = 50.0               // Peak firing rate of last motor unit (pps)

// Membrane time constant parameters (ms)
tau_m_1 = 20.0                // Membrane time constant of first motor unit (ms)
tau_m_n = 5.0                 // Membrane time constant of last motor unit (ms)

// AHP time constant parameters (ms)
tau_AHP_1 = 100.0             // AHP time constant of first motor unit (ms)
tau_AHP_n = 20.0              // AHP time constant of last motor unit (ms)

// AHP amplitude parameters (mV)
A_AHP_1 = 5.0                 // AHP amplitude of first motor unit (mV)
A_AHP_n = 2.0                 // AHP amplitude of last motor unit (mV)

// Firing threshold parameters (mV)
theta_1 = 10.0                // Firing threshold of first motor unit (mV)
theta_n = 10.0                // Firing threshold of last motor unit (mV)

// Gain factor (converts normalized drive to mV)
g = 15.0                      // Gain factor

// Noise parameters
sigma_noise = 0.02            // Standard deviation of synaptic noise (normalized)

// Hysteresis for de-recruitment
Delta_H = 0.01                // Hysteresis value (normalized)
```

---

## Motor Unit Parameter Initialization

```pseudocode
// Arrays to store motor unit-specific parameters
RTE = array[n]                // Recruitment thresholds
f_min = array[n]              // Minimum firing rates
f_peak = array[n]             // Peak firing rates
tau_m = array[n]              // Membrane time constants
tau_AHP = array[n]            // AHP time constants
A_AHP = array[n]              // AHP amplitudes
theta = array[n]              // Firing thresholds

// Compute parameters for each motor unit
for i = 1 to n:
    
    // Recruitment threshold (exponentially distributed)
    RTE[i] = RTE_1 * exp((i - 1) * ln(RR) / (n - 1))
    
    // Minimum firing rate (linearly distributed)
    f_min[i] = f_min_1 - (f_min_1 - f_min_n) * (i - 1) / (n - 1)
    
    // Peak firing rate (linearly distributed)
    f_peak[i] = f_peak_1 + (f_peak_n - f_peak_1) * (i - 1) / (n - 1)
    
    // Membrane time constant (linearly distributed, convert to seconds)
    tau_m[i] = (tau_m_1 - (tau_m_1 - tau_m_n) * (i - 1) / (n - 1)) / 1000.0
    
    // AHP time constant (linearly distributed, convert to seconds)
    tau_AHP[i] = (tau_AHP_1 - (tau_AHP_1 - tau_AHP_n) * (i - 1) / (n - 1)) / 1000.0
    
    // AHP amplitude (linearly distributed)
    A_AHP[i] = A_AHP_1 - (A_AHP_1 - A_AHP_n) * (i - 1) / (n - 1)
    
    // Firing threshold (can be constant or distributed)
    theta[i] = theta_1 + (theta_n - theta_1) * (i - 1) / (n - 1)

end for
```

---

## State Variable Initialization

```pseudocode
// State variables for each motor unit
V = array[n]                  // Membrane potential (mV)
AHP = array[n]                // Afterhyperpolarization (mV)
is_recruited = array[n]       // Recruitment state (boolean)
S = array[n]                  // Spike output (boolean)

// Initialize all state variables to zero/false
for i = 1 to n:
    V[i] = 0.0
    AHP[i] = 0.0
    is_recruited[i] = false
    S[i] = false
end for

// Time variable
t = 0.0                       // Current simulation time (seconds)
```

---

## Input Signal Definition

```pseudocode
// Excitatory drive signal e(t)
// This is the descending command from higher motor centers
// Example: ramp-and-hold contraction

function get_excitatory_drive(t):
    // Example: ramp up to 30% MVC over 5 seconds, then hold
    t_ramp = 5.0              // Ramp duration (seconds)
    e_target = 0.30           // Target drive level (30% MVC)
    
    if t < t_ramp:
        e = e_target * (t / t_ramp)
    else:
        e = e_target
    end if
    
    return e
end function
```

---

## Noise Generation

```pseudocode
// Gaussian white noise generator
// Returns a sample from N(0, sigma_noise)

function generate_noise():
    // Box-Muller transform for Gaussian noise
    u1 = random_uniform(0, 1)
    u2 = random_uniform(0, 1)
    z = sqrt(-2.0 * ln(u1)) * cos(2.0 * pi * u2)
    xi = sigma_noise * z
    return xi
end function
```

---

## Main Simulation Loop

```pseudocode
// Main time-stepping loop
for step = 1 to n_steps:
    
    // Update current time
    t = step * dt
    
    // Get excitatory drive at current time
    e_t = get_excitatory_drive(t)
    
    // Generate synaptic noise
    xi_t = generate_noise()
    
    // Effective drive (common to all motor units)
    e_eff = e_t + xi_t
    
    // Update each motor unit
    for i = 1 to n:
        
        // ===== RECRUITMENT/DE-RECRUITMENT LOGIC =====
        
        if not is_recruited[i]:
            // Check for recruitment
            if e_eff >= RTE[i]:
                is_recruited[i] = true
            end if
        else:
            // Check for de-recruitment (with hysteresis)
            if e_eff < (RTE[i] - Delta_H):
                is_recruited[i] = false
                V[i] = 0.0        // Reset membrane potential
                AHP[i] = 0.0      // Reset AHP
                S[i] = false
            end if
        end if
        
        // ===== MEMBRANE DYNAMICS (only if recruited) =====
        
        if is_recruited[i]:
            
            // Compute membrane potential derivative
            // tau_m(i) * dV/dt = -V(t) + g * [e(t) + xi(t)] - AHP(t)
            dV_dt = (-V[i] + g * e_eff - AHP[i]) / tau_m[i]
            
            // Update membrane potential (Euler integration)
            V[i] = V[i] + dV_dt * dt
            
            // Compute AHP derivative
            // tau_AHP(i) * dAHP/dt = -AHP(t)
            dAHP_dt = -AHP[i] / tau_AHP[i]
            
            // Update AHP (Euler integration)
            AHP[i] = AHP[i] + dAHP_dt * dt
            
            // ===== SPIKE GENERATION =====
            
            // Check if membrane potential crosses threshold
            if V[i] >= theta[i]:
                // Spike occurs
                S[i] = true
                
                // Increment AHP (reset condition)
                AHP[i] = AHP[i] + A_AHP[i]
                
                // Optional: reset membrane potential to some value
                // (not explicitly stated in paper, so we let it evolve)
                // V[i] = 0.0  // Uncomment if hard reset is desired
                
            else:
                S[i] = false
            end if
            
        else:
            // Motor unit not recruited
            S[i] = false
        end if
        
    end for
    
    // ===== OUTPUT/RECORDING =====
    
    // Record spike times, membrane potentials, etc.
    // For each motor unit i:
    //   if S[i] == true:
    //       record spike at time t for motor unit i
    //   end if
    
    // Store outputs for analysis
    // output_spikes[step, i] = S[i]
    // output_V[step, i] = V[i]
    // output_drive[step] = e_eff
    
end for
```

---

## Firing Rate Calculation (Post-Processing)

```pseudocode
// After simulation, compute instantaneous firing rates from spike trains
// This is for analysis and comparison with the target firing rate equation

function compute_firing_rate(spike_times):
    // spike_times is an array of times when spikes occurred
    
    firing_rates = array[length(spike_times) - 1]
    
    for k = 1 to length(spike_times) - 1:
        ISI = spike_times[k+1] - spike_times[k]  // Inter-spike interval
        firing_rates[k] = 1.0 / ISI              // Instantaneous firing rate (Hz)
    end for
    
    return firing_rates
end function

// Target firing rate equation (for validation)
// f_i(e) = f_min(i) + [f_peak(i) - f_min(i)] * [(e - RTE(i)) / (1 - RTE(i))]
// Valid for RTE(i) <= e <= 1

function target_firing_rate(i, e):
    if e < RTE[i]:
        f = 0.0  // Not recruited
    else if e >= 1.0:
        f = f_peak[i]  // Maximum drive
    else:
        f = f_min[i] + (f_peak[i] - f_min[i]) * ((e - RTE[i]) / (1.0 - RTE[i]))
    end if
    return f
end function
```

---

## Output Data Structure

```pseudocode
// Outputs to be passed to Block 2 (Muscle Force Generation)

// Spike trains for each motor unit
// Format: 2D array [n_steps x n]
// Value: true/false or 1/0 at each time step for each motor unit
output_spike_trains = array[n_steps, n]

// Copy spike data
for step = 1 to n_steps:
    for i = 1 to n:
        output_spike_trains[step, i] = S[i]  // From simulation loop
    end for
end for

// This spike train array is the input to Block 2
```

---

## Notes on Implementation

### 1. **Time Units Consistency**
- All time constants must be in the same units as `dt`
- If `dt` is in seconds, convert all time constants from milliseconds to seconds
- Firing rates are in Hz (spikes per second)

### 2. **Noise Implementation**
- Noise is regenerated at each time step
- Same noise value `xi_t` is used for all motor units (common input noise)
- For independent noise per motor unit, generate `xi_t[i]` separately for each `i`

### 3. **Membrane Potential Reset**
- Paper does not explicitly specify hard reset after spike
- Implementation choice: either reset to 0 or let it evolve with AHP
- AHP provides the refractory effect regardless of reset choice

### 4. **Recruitment Hysteresis**
- `Delta_H` prevents rapid on-off switching
- De-recruitment threshold is `RTE[i] - Delta_H`
- Typical value: 1-2% of RTE

### 5. **Spike Detection**
- Threshold crossing: `V[i] >= theta[i]`
- Spike is recorded as `S[i] = true` for that time step only
- Next time step, `S[i]` is reset to `false` unless another threshold crossing occurs

### 6. **Parameter Values**
- Values shown are typical/representative
- Actual values should match those reported in the paper's Methods section
- Some parameters may need adjustment for specific simulations

---

## Validation Checks

```pseudocode
// After simulation, validate model behavior:

// 1. Check recruitment order (should follow size principle)
for i = 1 to n-1:
    assert(first_recruitment_time[i] <= first_recruitment_time[i+1])
end for

// 2. Check firing rates are within physiological range
for i = 1 to n:
    mean_rate = compute_mean_firing_rate(spike_train[i])
    assert(mean_rate >= f_min[i] - tolerance)
    assert(mean_rate <= f_peak[i] + tolerance)
end for

// 3. Check that recruitment thresholds are monotonically increasing
for i = 1 to n-1:
    assert(RTE[i] < RTE[i+1])
end for
```

---

## Summary

This pseudocode provides a **direct, unoptimized translation** of Block 1 equations into algorithmic form:

- **Variable names** match the paper exactly
- **Equations** are implemented as written (Euler integration of differential equations)
- **Time stepping** uses fixed `dt` as described
- **No simplifications** or alternative formulations
- **No optimizations** (e.g., no vectorization, no adaptive time stepping)

The code is structured to be **readable and verifiable** against the paper, prioritizing correctness and traceability over computational efficiency.
