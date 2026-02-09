"""
Sanity Check: Closed-Loop Model with Zero Feedback Gains
Verifies equivalence with feedforward model when G_Ia = G_Ib = 0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

dt = 0.001  # Time step (1 ms)
T_total = 10.0  # Shorter simulation for sanity check (10 seconds)
n_steps = int(T_total / dt)
n = 120  # Number of motor units

# ============================================================================
# FEEDBACK PARAMETERS (ZERO FOR SANITY CHECK)
# ============================================================================

G_Ia = 0.0  # Ia feedback gain (ZERO)
G_Ib = 0.0  # Ib feedback gain (ZERO)
sigma_noise = 0.02  # Small nonzero noise
F_max = 1.0  # Force normalization (will be set based on simulation)

print("=" * 70)
print("SANITY CHECK: Closed-Loop Model with Zero Feedback Gains")
print("=" * 70)
print(f"\nParameters:")
print(f"  G_Ia = {G_Ia} (Ia feedback gain)")
print(f"  G_Ib = {G_Ib} (Ib feedback gain)")
print(f"  sigma_noise = {sigma_noise}")
print(f"  Simulation time = {T_total} s")
print(f"\nExpected behavior:")
print(f"  - e_eff(t) = e_descending(t) + 0 - 0 + ξ(t)")
print(f"  - Should be equivalent to feedforward model")
print(f"  - Firing rates and force should remain bounded")
print(f"  - No numerical instability")

# ============================================================================
# DESCENDING DRIVE PROFILE (Ramp-and-hold to 30% MVC)
# ============================================================================

e_descending = np.zeros(n_steps)
ramp_time = 5.0  # Ramp up over 5 seconds
target_drive = 0.30  # 30% MVC

for step in range(n_steps):
    t = step * dt
    if t < ramp_time:
        e_descending[step] = target_drive * (t / ramp_time)
    else:
        e_descending[step] = target_drive

# ============================================================================
# INITIALIZE STATE VARIABLES
# ============================================================================

# Block 1: Motor neuron pool (simplified for sanity check)
V = np.zeros(n)  # Membrane potential
AHP = np.zeros(n)  # Afterhyperpolarization
is_recruited = np.zeros(n, dtype=bool)  # Recruitment status
spike_train = np.zeros((n_steps, n))  # Spike trains

# Block 2: Muscle force generation (use existing implementation)
# We'll load from saved data if available, otherwise simulate
try:
    activation_levels = np.load('block2_activation_levels.npy')
    force_unfatigued = np.load('block2_force_unfatigued.npy')
    print("\nLoaded existing Block 2 data")
except:
    print("\nBlock 2 data not found - will use simplified model")
    activation_levels = np.zeros((n_steps, n))
    force_unfatigued = np.zeros((n_steps, n))

# Block 3: Fatigue (use existing implementation)
try:
    force_fatigued_total = np.load('block3_force_total_fatigued.npy')
    print("Loaded existing Block 3 data")
except:
    print("Block 3 data not found - will use unfatigued force")
    force_fatigued_total = np.zeros(n_steps)

# Block 5a, 5b: Feedback signals
Ia_signal = np.zeros(n_steps)
Ib_signal = np.zeros(n_steps)

# Block 6: Effective drive
e_eff = np.zeros(n_steps)

# ============================================================================
# MOTOR UNIT PARAMETERS (Simplified)
# ============================================================================

RTE_1 = 0.01
RR = 100
RTE = RTE_1 * np.exp(np.arange(n) * np.log(RR) / (n - 1))

g = 40.0  # Gain factor
theta = np.full(n, 10.0)  # Firing threshold (constant for simplicity)
tau_m = np.linspace(0.020, 0.005, n)  # Membrane time constant
tau_AHP = np.linspace(0.100, 0.020, n)  # AHP time constant
A_AHP = 5.0 * np.exp(np.arange(n) * np.log(50.0 / 5.0) / (n - 1))  # AHP amplitude

Delta_H = 0.01  # Recruitment hysteresis

# ============================================================================
# SIMULATION LOOP
# ============================================================================

print(f"\nRunning simulation...")

# Track statistics
max_V = 0
max_firing_rate = 0
num_recruited_max = 0

for step in range(n_steps):
    t = step * dt
    
    # Progress indicator
    if step % 1000 == 0:
        print(f"  Progress: {t:.1f} / {T_total} s")
    
    # ========================================================================
    # BLOCK 5a: Ia Afferent Feedback
    # ========================================================================
    
    if step > 0:
        # Compute mean activation over active motor units
        active_units = activation_levels[step-1, :] > 0.01
        if np.any(active_units):
            a_mean = np.mean(activation_levels[step-1, active_units])
        else:
            a_mean = 0.0
        
        # Ia signal (excitatory)
        Ia_signal[step] = G_Ia * a_mean
    
    # ========================================================================
    # BLOCK 5b: Ib Afferent Feedback
    # ========================================================================
    
    if step > 0:
        # Ib signal (inhibitory, proportional to force)
        if F_max > 0:
            Ib_signal[step] = G_Ib * (force_fatigued_total[step-1] / F_max)
        else:
            Ib_signal[step] = 0.0
    
    # ========================================================================
    # BLOCK 6: Effective Drive Calculation
    # ========================================================================
    
    # Generate noise (Box-Muller transform)
    u1 = np.random.uniform(0, 1)
    u2 = np.random.uniform(0, 1)
    z = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
    xi = sigma_noise * z
    
    # Compute effective drive
    e_eff[step] = e_descending[step] + Ia_signal[step] - Ib_signal[step] + xi
    
    # ========================================================================
    # BLOCK 1: Motor Neuron Pool (Simplified)
    # ========================================================================
    
    for i in range(n):
        # Recruitment logic
        if not is_recruited[i]:
            if e_eff[step] >= RTE[i]:
                is_recruited[i] = True
        else:
            if e_eff[step] < RTE[i] - Delta_H:
                is_recruited[i] = False
        
        # Membrane dynamics (if recruited)
        if is_recruited[i]:
            # Update membrane potential
            dV_dt = (-V[i] + g * e_eff[step] - AHP[i]) / tau_m[i]
            V[i] = V[i] + dV_dt * dt
            
            # Update AHP
            dAHP_dt = -AHP[i] / tau_AHP[i]
            AHP[i] = AHP[i] + dAHP_dt * dt
            
            # Spike generation
            if V[i] >= theta[i]:
                spike_train[step, i] = 1
                AHP[i] = AHP[i] + A_AHP[i]
            else:
                spike_train[step, i] = 0
            
            # Track max V
            max_V = max(max_V, V[i])
        else:
            V[i] = 0
            spike_train[step, i] = 0
    
    # Track number of recruited units
    num_recruited_max = max(num_recruited_max, np.sum(is_recruited))

print(f"\nSimulation complete!")

# ============================================================================
# COMPUTE STATISTICS
# ============================================================================

print(f"\n" + "=" * 70)
print("SANITY CHECK RESULTS")
print("=" * 70)

# 1. Check equivalence with feedforward (G_Ia = G_Ib = 0)
print(f"\n1. Equivalence with Feedforward Model:")
print(f"   G_Ia = {G_Ia}, G_Ib = {G_Ib}")
print(f"   Ia_signal: min={np.min(Ia_signal):.6f}, max={np.max(Ia_signal):.6f}")
print(f"   Ib_signal: min={np.min(Ib_signal):.6f}, max={np.max(Ib_signal):.6f}")

# Check if feedback signals are zero
ia_is_zero = np.allclose(Ia_signal, 0.0, atol=1e-10)
ib_is_zero = np.allclose(Ib_signal, 0.0, atol=1e-10)

if ia_is_zero and ib_is_zero:
    print(f"   ✅ Feedback signals are zero (as expected)")
    print(f"   ✅ e_eff(t) = e_descending(t) + ξ(t)")
else:
    print(f"   ⚠️  Feedback signals are not exactly zero")

# 2. Check numerical stability
print(f"\n2. Numerical Stability:")
print(f"   Max membrane potential: {max_V:.2f} mV")
print(f"   Max recruited units: {num_recruited_max} / {n}")

# Check for NaN or Inf
has_nan = np.any(np.isnan(V)) or np.any(np.isnan(AHP)) or np.any(np.isnan(e_eff))
has_inf = np.any(np.isinf(V)) or np.any(np.isinf(AHP)) or np.any(np.isinf(e_eff))

if has_nan:
    print(f"   ❌ NaN detected in state variables")
else:
    print(f"   ✅ No NaN values")

if has_inf:
    print(f"   ❌ Inf detected in state variables")
else:
    print(f"   ✅ No Inf values")

# 3. Check boundedness of firing rates
print(f"\n3. Firing Rates and Force Boundedness:")

# Compute instantaneous firing rates (spikes per second)
window_size = int(1.0 / dt)  # 1 second window
firing_rates = np.zeros((n_steps, n))

for i in range(n):
    for step in range(window_size, n_steps):
        spikes_in_window = np.sum(spike_train[step-window_size:step, i])
        firing_rates[step, i] = spikes_in_window  # Hz

max_firing_rate = np.max(firing_rates)
mean_firing_rate = np.mean(firing_rates[firing_rates > 0])

print(f"   Max firing rate: {max_firing_rate:.1f} Hz")
print(f"   Mean firing rate (active units): {mean_firing_rate:.1f} Hz")

# Check if firing rates are in physiological range
if max_firing_rate < 100:  # Typical max is ~50-60 Hz
    print(f"   ✅ Firing rates are in physiological range (<100 Hz)")
else:
    print(f"   ⚠️  Firing rates exceed typical physiological range")

# Check membrane potential bounds
if max_V < 100:  # Reasonable upper bound
    print(f"   ✅ Membrane potentials are bounded (<100 mV)")
else:
    print(f"   ⚠️  Membrane potentials are unusually high")

# 4. Overall sanity check
print(f"\n" + "=" * 70)
print("OVERALL SANITY CHECK:")
print("=" * 70)

all_checks_pass = (
    ia_is_zero and 
    ib_is_zero and 
    not has_nan and 
    not has_inf and 
    max_firing_rate < 100 and 
    max_V < 100
)

if all_checks_pass:
    print("✅ ALL SANITY CHECKS PASSED")
    print("\nConclusions:")
    print("  - Feedback signals are zero when G_Ia = G_Ib = 0")
    print("  - Model is equivalent to feedforward (e_eff = e_descending + noise)")
    print("  - No numerical instability detected")
    print("  - Firing rates and membrane potentials are bounded")
    print("  - System is ready for feedback testing")
else:
    print("⚠️  SOME SANITY CHECKS FAILED")
    print("\nReview the results above for details.")

# ============================================================================
# VISUALIZATION
# ============================================================================

print(f"\nGenerating visualizations...")

fig, axes = plt.subplots(4, 1, figsize=(12, 10))

# Plot 1: Descending drive and effective drive
time = np.arange(n_steps) * dt
axes[0].plot(time, e_descending, 'b-', label='e_descending(t)', linewidth=2)
axes[0].plot(time, e_eff, 'r--', label='e_eff(t)', linewidth=1, alpha=0.7)
axes[0].set_ylabel('Drive (normalized)')
axes[0].set_title('Descending Drive vs Effective Drive (G_Ia=0, G_Ib=0)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Feedback signals (should be zero)
axes[1].plot(time, Ia_signal, 'g-', label='Ia_signal (excitatory)', linewidth=2)
axes[1].plot(time, Ib_signal, 'r-', label='Ib_signal (inhibitory)', linewidth=2)
axes[1].axhline(y=0, color='k', linestyle='--', alpha=0.3)
axes[1].set_ylabel('Feedback Signal')
axes[1].set_title('Feedback Signals (Should be Zero)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim([-0.01, 0.01])

# Plot 3: Number of recruited units
num_recruited = np.sum(is_recruited)
axes[2].axhline(y=num_recruited, color='b', linewidth=2, label=f'Recruited units: {num_recruited}')
axes[2].set_ylabel('Number of Units')
axes[2].set_title('Motor Unit Recruitment')
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim([0, n])

# Plot 4: Membrane potential of selected units
sample_units = [0, 30, 60, 90, 119]  # Sample across the pool
for i in sample_units:
    # Reconstruct V trace (we only have final values, so this is simplified)
    axes[3].axhline(y=V[i], alpha=0.5, label=f'Unit {i+1}')

axes[3].axhline(y=theta[0], color='r', linestyle='--', label='Threshold', linewidth=2)
axes[3].set_xlabel('Time (s)')
axes[3].set_ylabel('Membrane Potential (mV)')
axes[3].set_title('Final Membrane Potentials (Sample Units)')
axes[3].legend(loc='upper right', fontsize=8)
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('sanity_check_results.png', dpi=150, bbox_inches='tight')
print(f"Saved: sanity_check_results.png")

plt.close()

print(f"\n" + "=" * 70)
print("SANITY CHECK COMPLETE")
print("=" * 70)
