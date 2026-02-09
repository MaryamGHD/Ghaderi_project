"""
Block 1: Motor Neuron Pool Model - Python Implementation
Dideriksen et al. (2010) - Exact Translation from Pseudocode

This implementation follows the pseudocode line-by-line with:
- Identical variable names
- Identical equations
- Identical update timing
- No optimizations, refactoring, or simplifications
"""


import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt



# ============================================================================
# CONSTANTS AND GLOBAL PARAMETERS
# ============================================================================

# Simulation parameters
dt = 0.001                    # Time step in seconds (1 ms)
T_total = 60.0                # Total simulation time in seconds
n_steps = int(T_total / dt)   # Number of simulation steps

# Motor unit pool size
n = 120                       # Total number of motor units

# Recruitment threshold parameters
RTE_1 = 0.01                  # Recruitment threshold of first motor unit (normalized)
RR = 100                      # Range of recruitment thresholds (ratio last/first)

# Minimum firing rate parameters (pps = pulses per second)
f_min_1 = 8.0                 # Minimum firing rate of first motor unit (pps)
f_min_n = 12.0                # Minimum firing rate of last motor unit (pps)

# Peak firing rate parameters (pps)
f_peak_1 = 35.0               # Peak firing rate of first motor unit (pps)
f_peak_n = 50.0               # Peak firing rate of last motor unit (pps)

# Membrane time constant parameters (ms)
tau_m_1 = 20.0                # Membrane time constant of first motor unit (ms)
tau_m_n = 5.0                 # Membrane time constant of last motor unit (ms)

# AHP time constant parameters (ms)
tau_AHP_1 = 100.0             # AHP time constant of first motor unit (ms)
tau_AHP_n = 20.0              # AHP time constant of last motor unit (ms)

# AHP amplitude parameters (mV)
A_AHP_1 = 5.0                 # AHP amplitude of first motor unit (mV)
A_AHP_n = 2.0                 # AHP amplitude of last motor unit (mV)

# Firing threshold parameters (mV)
theta_1 = 10.0                # Firing threshold of first motor unit (mV)
theta_n = 10.0                # Firing threshold of last motor unit (mV)

# Gain factor (converts normalized drive to mV)
g = 40.0                      # Gain factor (increased to ensure V reaches threshold)

# Noise parameters
sigma_noise = 0.02            # Standard deviation of synaptic noise (normalized)

# Hysteresis for de-recruitment
Delta_H = 0.01                # Hysteresis value (normalized)


# ============================================================================
# MOTOR UNIT PARAMETER INITIALIZATION
# ============================================================================

# Arrays to store motor unit-specific parameters
RTE = np.zeros(n)             # Recruitment thresholds
f_min = np.zeros(n)           # Minimum firing rates
f_peak = np.zeros(n)          # Peak firing rates
tau_m = np.zeros(n)           # Membrane time constants
tau_AHP = np.zeros(n)         # AHP time constants
A_AHP = np.zeros(n)           # AHP amplitudes
theta = np.zeros(n)           # Firing thresholds

# Compute parameters for each motor unit
for i in range(n):
    
    # Recruitment threshold (exponentially distributed)
    RTE[i] = RTE_1 * np.exp((i) * np.log(RR) / (n - 1))
    
    # Minimum firing rate (linearly distributed)
    f_min[i] = f_min_1 - (f_min_1 - f_min_n) * (i) / (n - 1)
    
    # Peak firing rate (linearly distributed)
    f_peak[i] = f_peak_1 + (f_peak_n - f_peak_1) * (i) / (n - 1)
    
    # Membrane time constant (linearly distributed, convert to seconds)
    tau_m[i] = (tau_m_1 - (tau_m_1 - tau_m_n) * (i) / (n - 1)) / 1000.0
    
    # AHP time constant (linearly distributed, convert to seconds)
    tau_AHP[i] = (tau_AHP_1 - (tau_AHP_1 - tau_AHP_n) * (i) / (n - 1)) / 1000.0
    
    # AHP amplitude (linearly distributed)
    A_AHP[i] = A_AHP_1 - (A_AHP_1 - A_AHP_n) * (i) / (n - 1)
    
    # Firing threshold (can be constant or distributed)
    theta[i] = theta_1 + (theta_n - theta_1) * (i) / (n - 1)


# ============================================================================
# STATE VARIABLE INITIALIZATION
# ============================================================================

# State variables for each motor unit
V = np.zeros(n)               # Membrane potential (mV)
AHP = np.zeros(n)             # Afterhyperpolarization (mV)
is_recruited = np.zeros(n, dtype=bool)  # Recruitment state (boolean)
S = np.zeros(n, dtype=bool)   # Spike output (boolean)

# Initialize all state variables to zero/false
for i in range(n):
    V[i] = 0.0
    AHP[i] = 0.0
    is_recruited[i] = False
    S[i] = False

# Time variable
t = 0.0                       # Current simulation time (seconds)


# ============================================================================
# INPUT SIGNAL DEFINITION
# ============================================================================

def get_excitatory_drive(t):
    """
    Excitatory drive signal e(t)
    This is the descending command from higher motor centers
    Example: ramp-and-hold contraction
    """
    # Example: ramp up to 30% MVC over 5 seconds, then hold
    t_ramp = 5.0              # Ramp duration (seconds)
    e_target = 0.30           # Target drive level (30% MVC)
    
    if t < t_ramp:
        e = e_target * (t / t_ramp)
    else:
        e = e_target
    
    return e


# ============================================================================
# NOISE GENERATION
# ============================================================================

def generate_noise():
    """
    Gaussian white noise generator
    Returns a sample from N(0, sigma_noise)
    """
    # Box-Muller transform for Gaussian noise
    u1 = np.random.uniform(0, 1)
    u2 = np.random.uniform(0, 1)
    z = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
    xi = sigma_noise * z
    return xi


# ============================================================================
# OUTPUT DATA STRUCTURES
# ============================================================================

# Outputs to be passed to Block 2 (Muscle Force Generation)
# Spike trains for each motor unit
# Format: 2D array [n_steps x n]
# Value: True/False at each time step for each motor unit
output_spike_trains = np.zeros((n_steps, n), dtype=bool)

# Additional outputs for analysis
output_V = np.zeros((n_steps, n))           # Membrane potentials
output_drive = np.zeros(n_steps)            # Excitatory drive
output_time = np.zeros(n_steps)             # Time vector
output_recruited = np.zeros((n_steps, n), dtype=bool)  # Recruitment status


# ============================================================================
# MAIN SIMULATION LOOP
# ============================================================================

print("Starting simulation...")
print(f"Total time: {T_total} s")
print(f"Time step: {dt*1000} ms")
print(f"Number of motor units: {n}")
print(f"Number of steps: {n_steps}")
print()

# Main time-stepping loop
for step in range(n_steps):
    
    # Update current time
    t = step * dt
    
    # Get excitatory drive at current time
    e_t = get_excitatory_drive(t)
    
    # Generate synaptic noise
    xi_t = generate_noise()
    
    # Effective drive (common to all motor units)
    e_eff = e_t + xi_t
    
    # Update each motor unit
    for i in range(n):
        
        # ===== RECRUITMENT/DE-RECRUITMENT LOGIC =====
        
        if not is_recruited[i]:
            # Check for recruitment
            if e_eff >= RTE[i]:
                is_recruited[i] = True
        else:
            # Check for de-recruitment (with hysteresis)
            if e_eff < (RTE[i] - Delta_H):
                is_recruited[i] = False
                V[i] = 0.0        # Reset membrane potential
                AHP[i] = 0.0      # Reset AHP
                S[i] = False
        
        # ===== MEMBRANE DYNAMICS (only if recruited) =====
        
        if is_recruited[i]:
            
            # Compute membrane potential derivative
            # tau_m(i) * dV/dt = -V(t) + g * [e(t) + xi(t)] - AHP(t)
            dV_dt = (-V[i] + g * e_eff - AHP[i]) / tau_m[i]
            
            # Update membrane potential (Euler integration)
            V[i] = V[i] + dV_dt * dt
            
            # Compute AHP derivative
            # tau_AHP(i) * dAHP/dt = -AHP(t)
            dAHP_dt = -AHP[i] / tau_AHP[i]
            
            # Update AHP (Euler integration)
            AHP[i] = AHP[i] + dAHP_dt * dt
            
            # ===== SPIKE GENERATION =====
            
            # Check if membrane potential crosses threshold
            if V[i] >= theta[i]:
                # Spike occurs
                S[i] = True
                
                # Increment AHP (reset condition)
                AHP[i] = AHP[i] + A_AHP[i]
                
                # Optional: reset membrane potential to some value
                # (not explicitly stated in paper, so we let it evolve)
                # V[i] = 0.0  # Uncomment if hard reset is desired
                
            else:
                S[i] = False
            
        else:
            # Motor unit not recruited
            S[i] = False
    
    # ===== OUTPUT/RECORDING =====
    
    # Store outputs for analysis
    output_spike_trains[step, :] = S
    output_V[step, :] = V
    output_drive[step] = e_eff
    output_time[step] = t
    output_recruited[step, :] = is_recruited
    
    # Progress indicator (every 10 seconds)
    if step % int(10.0 / dt) == 0:
        print(f"Progress: {t:.1f} / {T_total} s")

print()
print("Simulation complete!")
print()


# ============================================================================
# FIRING RATE CALCULATION (POST-PROCESSING)
# ============================================================================

def compute_firing_rate(spike_times):
    """
    Compute instantaneous firing rates from spike trains
    This is for analysis and comparison with the target firing rate equation
    """
    if len(spike_times) < 2:
        return np.array([])
    
    firing_rates = np.zeros(len(spike_times) - 1)
    
    for k in range(len(spike_times) - 1):
        ISI = spike_times[k+1] - spike_times[k]  # Inter-spike interval
        firing_rates[k] = 1.0 / ISI              # Instantaneous firing rate (Hz)
    
    return firing_rates


def target_firing_rate(i, e):
    """
    Target firing rate equation (for validation)
    f_i(e) = f_min(i) + [f_peak(i) - f_min(i)] * [(e - RTE(i)) / (1 - RTE(i))]
    Valid for RTE(i) <= e <= 1
    """
    if e < RTE[i]:
        f = 0.0  # Not recruited
    elif e >= 1.0:
        f = f_peak[i]  # Maximum drive
    else:
        f = f_min[i] + (f_peak[i] - f_min[i]) * ((e - RTE[i]) / (1.0 - RTE[i]))
    
    return f


# ============================================================================
# ANALYSIS AND VISUALIZATION
# ============================================================================

print("Analyzing results...")

# Extract spike times for each motor unit
spike_times_all = []
for i in range(n):
    spike_indices = np.where(output_spike_trains[:, i])[0]
    spike_times = output_time[spike_indices]
    spike_times_all.append(spike_times)

# Compute mean firing rates for recruited motor units
mean_firing_rates = np.zeros(n)
for i in range(n):
    if len(spike_times_all[i]) > 1:
        ISIs = np.diff(spike_times_all[i])
        mean_firing_rates[i] = 1.0 / np.mean(ISIs)
    else:
        mean_firing_rates[i] = 0.0

# Count recruited motor units (based on final recruitment status)
n_recruited_final = np.sum(is_recruited)
n_with_spikes = np.sum(mean_firing_rates > 0)
print(f"Number of recruited motor units (final): {n_recruited_final} / {n}")
print(f"Number of motor units with spikes: {n_with_spikes} / {n}")
if n_recruited_final > n_with_spikes:
    print(f"Note: {n_recruited_final - n_with_spikes} recruited units did not spike (membrane potential did not reach threshold)")
print()

# ============================================================================
# VALIDATION CHECKS
# ============================================================================

print("Validation checks:")

# 1. Check recruitment order (should follow size principle)
first_recruitment_time = np.zeros(n)
for i in range(n):
    if len(spike_times_all[i]) > 0:
        first_recruitment_time[i] = spike_times_all[i][0]
    else:
        first_recruitment_time[i] = np.inf

recruitment_order_valid = True
for i in range(n-1):
    if first_recruitment_time[i] < np.inf and first_recruitment_time[i+1] < np.inf:
        if first_recruitment_time[i] > first_recruitment_time[i+1]:
            recruitment_order_valid = False
            break

print(f"1. Recruitment order follows size principle: {recruitment_order_valid}")

# 2. Check firing rates are within physiological range
tolerance = 5.0  # Hz
firing_rates_valid = True
for i in range(n):
    if mean_firing_rates[i] > 0:
        if mean_firing_rates[i] < f_min[i] - tolerance or mean_firing_rates[i] > f_peak[i] + tolerance:
            firing_rates_valid = False
            break

print(f"2. Firing rates within physiological range: {firing_rates_valid}")

# 3. Check that recruitment thresholds are monotonically increasing
RTE_monotonic = np.all(np.diff(RTE) > 0)
print(f"3. Recruitment thresholds monotonically increasing: {RTE_monotonic}")
print()


# ============================================================================
# VISUALIZATION
# ============================================================================

print("Creating visualizations...")

# Create figure with multiple subplots
fig, axes = plt.subplots(4, 1, figsize=(12, 10))

# Plot 1: Excitatory drive over time
axes[0].plot(output_time, output_drive, 'b-', linewidth=1)
axes[0].set_ylabel('Excitatory Drive (normalized)')
axes[0].set_title('Block 1: Motor Neuron Pool Model - Simulation Results')
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim([0, T_total])

# Plot 2: Raster plot of spike trains (show subset of motor units)
n_show = min(30, n)  # Show first 30 motor units
for i in range(n_show):
    spike_times = spike_times_all[i]
    if len(spike_times) > 0:
        axes[1].plot(spike_times, np.ones_like(spike_times) * (i+1), 'k.', markersize=1)

axes[1].set_ylabel(f'Motor Unit (1-{n_show})')
axes[1].set_xlabel('Time (s)')
axes[1].set_title(f'Spike Trains (first {n_show} motor units)')
axes[1].set_xlim([0, T_total])
axes[1].set_ylim([0, n_show+1])
axes[1].grid(True, alpha=0.3)

# Plot 3: Mean firing rates vs motor unit index
recruited_indices = np.where(mean_firing_rates > 0)[0]
axes[2].plot(recruited_indices + 1, mean_firing_rates[recruited_indices], 'bo', markersize=4, label='Simulated')
axes[2].plot(np.arange(n) + 1, f_min, 'r--', linewidth=1, label='f_min')
axes[2].plot(np.arange(n) + 1, f_peak, 'g--', linewidth=1, label='f_peak')
axes[2].set_xlabel('Motor Unit Index')
axes[2].set_ylabel('Firing Rate (Hz)')
axes[2].set_title('Mean Firing Rates')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Plot 4: Recruitment thresholds
axes[3].plot(np.arange(n) + 1, RTE, 'k-', linewidth=2)
axes[3].set_xlabel('Motor Unit Index')
axes[3].set_ylabel('Recruitment Threshold (normalized)')
axes[3].set_title('Recruitment Thresholds (exponentially distributed)')
axes[3].grid(True, alpha=0.3)
axes[3].set_yscale('log')

plt.tight_layout()
plt.savefig('/Users/maryamghaderi/Downloads/untitled folder 2/block1_results.png', dpi=150)
print("Saved figure: block1_results.png")
print()

# Additional figure: Membrane potential traces for selected motor units
fig2, ax = plt.subplots(1, 1, figsize=(12, 6))

# Show membrane potential for a few representative motor units
units_to_show = [0, n//4, n//2, 3*n//4, n-1]  # First, 25%, 50%, 75%, last
colors = ['blue', 'green', 'orange', 'red', 'purple']

time_window = [0, 10]  # Show first 10 seconds
time_mask = (output_time >= time_window[0]) & (output_time <= time_window[1])

for idx, i in enumerate(units_to_show):
    if mean_firing_rates[i] > 0:
        ax.plot(output_time[time_mask], output_V[time_mask, i], 
                color=colors[idx], linewidth=1, 
                label=f'MU {i+1} (RTE={RTE[i]:.3f})')

ax.axhline(y=theta[0], color='k', linestyle='--', linewidth=1, label='Threshold')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Membrane Potential (mV)')
ax.set_title('Membrane Potential Traces (first 10 seconds)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(time_window)

plt.tight_layout()
plt.savefig('/Users/maryamghaderi/Downloads/untitled folder 2/block1_membrane_potentials.png', dpi=150)
print("Saved figure: block1_membrane_potentials.png")
print()

print("All done!")
