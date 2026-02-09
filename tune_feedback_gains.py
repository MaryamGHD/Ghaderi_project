"""
Systematic Tuning of Feedback Gains G_Ia and G_Ib
Following the strategy defined in feedback_gain_parameter_strategy.md

Strategy:
1. Start with G_Ia = G_Ib = 0 (baseline)
2. Gradually increase G_Ia (excitatory feedback)
3. Increase G_Ib to maintain stability (G_Ib >= G_Ia)
4. Measure force CV, firing rates, stability
5. Select final values based on physiological realism
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

dt = 0.001  # Time step (1 ms)
T_total = 60.0  # Full simulation (60 seconds)
n_steps = int(T_total / dt)
n = 120  # Number of motor units

print("=" * 80)
print("SYSTEMATIC TUNING OF FEEDBACK GAINS G_Ia AND G_Ib")
print("=" * 80)

# ============================================================================
# GAIN COMBINATIONS TO TEST
# ============================================================================

# Following the tuning strategy:
# Step 1: Baseline (no feedback)
# Step 2: Add Ia feedback only (excitatory)
# Step 3: Add Ib feedback (inhibitory, G_Ib >= G_Ia)
# Step 4: Balanced feedback

gain_combinations = [
    # (G_Ia, G_Ib, Description)
    (0.0, 0.0, "Baseline (no feedback)"),
    (0.1, 0.0, "Ia only (weak excitatory)"),
    (0.2, 0.0, "Ia only (moderate excitatory)"),
    (0.3, 0.0, "Ia only (strong excitatory)"),
    (0.0, 0.1, "Ib only (weak inhibitory)"),
    (0.0, 0.2, "Ib only (moderate inhibitory)"),
    (0.0, 0.3, "Ib only (strong inhibitory)"),
    (0.1, 0.1, "Balanced (weak)"),
    (0.2, 0.2, "Balanced (moderate)"),
    (0.2, 0.3, "Ib > Ia (stable, moderate)"),
    (0.3, 0.4, "Ib > Ia (stable, strong)"),
]

print(f"\nTesting {len(gain_combinations)} gain combinations:")
for i, (g_ia, g_ib, desc) in enumerate(gain_combinations):
    print(f"  {i+1}. G_Ia={g_ia:.1f}, G_Ib={g_ib:.1f} - {desc}")

# ============================================================================
# LOAD EXISTING BLOCK DATA
# ============================================================================

print(f"\nLoading existing block data...")

try:
    activation_levels = np.load('block2_activation.npy')
    force_unfatigued = np.load('block2_force.npy')
    print(f"  ✓ Loaded Block 2 data: activation and unfatigued force")
except:
    print(f"  ✗ Block 2 data not found - cannot proceed")
    print(f"  Please run Block 2 simulation first")
    exit(1)

try:
    force_fatigued = np.load('block3_force_fatigued.npy')
    force_total_fatigued = np.load('block3_force_total_fatigued.npy')
    print(f"  ✓ Loaded Block 3 data: fatigued force")
except:
    print(f"  ✗ Block 3 data not found - using unfatigued force")
    force_fatigued = force_unfatigued.copy()
    force_total_fatigued = np.sum(force_unfatigued, axis=1)

# Set F_max based on maximum force
F_max = np.max(force_total_fatigued)
if F_max == 0:
    F_max = 1.0  # Fallback
print(f"  F_max = {F_max:.3f} N (for normalization)")

# ============================================================================
# DESCENDING DRIVE PROFILE
# ============================================================================

e_descending = np.zeros(n_steps)
ramp_time = 5.0
target_drive = 0.30

for step in range(n_steps):
    t = step * dt
    if t < ramp_time:
        e_descending[step] = target_drive * (t / ramp_time)
    else:
        e_descending[step] = target_drive

# ============================================================================
# MOTOR UNIT PARAMETERS
# ============================================================================

RTE_1 = 0.01
RR = 100
RTE = RTE_1 * np.exp(np.arange(n) * np.log(RR) / (n - 1))

g = 40.0
theta = np.full(n, 10.0)
tau_m = np.linspace(0.020, 0.005, n)
tau_AHP = np.linspace(0.100, 0.020, n)
A_AHP = 5.0 * np.exp(np.arange(n) * np.log(50.0 / 5.0) / (n - 1))
Delta_H = 0.01

sigma_noise = 0.02

# ============================================================================
# RESULTS STORAGE
# ============================================================================

results = []

# ============================================================================
# TUNING LOOP
# ============================================================================

for test_idx, (G_Ia, G_Ib, description) in enumerate(gain_combinations):
    
    print(f"\n" + "=" * 80)
    print(f"TEST {test_idx + 1}/{len(gain_combinations)}: {description}")
    print(f"G_Ia = {G_Ia:.1f}, G_Ib = {G_Ib:.1f}")
    print("=" * 80)
    
    # Initialize state variables
    V = np.zeros(n)
    AHP = np.zeros(n)
    is_recruited = np.zeros(n, dtype=bool)
    spike_train = np.zeros((n_steps, n))
    
    Ia_signal = np.zeros(n_steps)
    Ib_signal = np.zeros(n_steps)
    e_eff = np.zeros(n_steps)
    
    # Simulation loop
    print(f"Running simulation...")
    
    for step in range(n_steps):
        t = step * dt
        
        if step % 10000 == 0:
            print(f"  Progress: {t:.1f} / {T_total} s")
        
        # Block 5a: Ia feedback
        if step > 0:
            active_units = activation_levels[step-1, :] > 0.01
            if np.any(active_units):
                a_mean = np.mean(activation_levels[step-1, active_units])
            else:
                a_mean = 0.0
            Ia_signal[step] = G_Ia * a_mean
        
        # Block 5b: Ib feedback
        if step > 0:
            Ib_signal[step] = G_Ib * (force_total_fatigued[step-1] / F_max)
        
        # Block 6: Effective drive
        u1 = np.random.uniform(0, 1)
        u2 = np.random.uniform(0, 1)
        z = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
        xi = sigma_noise * z
        
        e_eff[step] = e_descending[step] + Ia_signal[step] - Ib_signal[step] + xi
        
        # Block 1: Motor neuron pool
        for i in range(n):
            # Recruitment
            if not is_recruited[i]:
                if e_eff[step] >= RTE[i]:
                    is_recruited[i] = True
            else:
                if e_eff[step] < RTE[i] - Delta_H:
                    is_recruited[i] = False
            
            # Membrane dynamics
            if is_recruited[i]:
                dV_dt = (-V[i] + g * e_eff[step] - AHP[i]) / tau_m[i]
                V[i] = V[i] + dV_dt * dt
                
                dAHP_dt = -AHP[i] / tau_AHP[i]
                AHP[i] = AHP[i] + dAHP_dt * dt
                
                if V[i] >= theta[i]:
                    spike_train[step, i] = 1
                    AHP[i] = AHP[i] + A_AHP[i]
                else:
                    spike_train[step, i] = 0
            else:
                V[i] = 0
                spike_train[step, i] = 0
    
    # ========================================================================
    # COMPUTE METRICS
    # ========================================================================
    
    print(f"Computing metrics...")
    
    # 1. Force statistics (steady-state: last 30 seconds)
    steady_start = int(30.0 / dt)
    F_steady = force_total_fatigued[steady_start:]
    
    F_mean = np.mean(F_steady)
    F_std = np.std(F_steady)
    F_CV = (F_std / F_mean * 100) if F_mean > 0 else 0
    
    # 2. Firing rate statistics
    window_size = int(1.0 / dt)
    firing_rates = np.zeros((n_steps, n))
    
    for i in range(n):
        for step in range(window_size, n_steps):
            spikes_in_window = np.sum(spike_train[step-window_size:step, i])
            firing_rates[step, i] = spikes_in_window
    
    firing_rates_steady = firing_rates[steady_start:, :]
    active_mask = firing_rates_steady > 0
    
    if np.any(active_mask):
        mean_firing_rate = np.mean(firing_rates_steady[active_mask])
        max_firing_rate = np.max(firing_rates_steady)
    else:
        mean_firing_rate = 0
        max_firing_rate = 0
    
    # 3. Stability checks
    has_nan = np.any(np.isnan(V)) or np.any(np.isnan(e_eff))
    has_inf = np.any(np.isinf(V)) or np.any(np.isinf(e_eff))
    is_stable = not (has_nan or has_inf) and max_firing_rate < 100
    
    # 4. Feedback contribution
    Ia_mean = np.mean(Ia_signal[steady_start:])
    Ib_mean = np.mean(Ib_signal[steady_start:])
    net_feedback = Ia_mean - Ib_mean
    
    # Store results
    results.append({
        'G_Ia': G_Ia,
        'G_Ib': G_Ib,
        'description': description,
        'F_mean': F_mean,
        'F_CV': F_CV,
        'mean_firing_rate': mean_firing_rate,
        'max_firing_rate': max_firing_rate,
        'is_stable': is_stable,
        'Ia_mean': Ia_mean,
        'Ib_mean': Ib_mean,
        'net_feedback': net_feedback,
    })
    
    # Print results
    print(f"\nResults:")
    print(f"  Force (steady-state):")
    print(f"    Mean: {F_mean:.3f} N")
    print(f"    CV: {F_CV:.2f}%")
    print(f"  Firing rates:")
    print(f"    Mean (active): {mean_firing_rate:.1f} Hz")
    print(f"    Max: {max_firing_rate:.1f} Hz")
    print(f"  Feedback:")
    print(f"    Ia (mean): {Ia_mean:.4f}")
    print(f"    Ib (mean): {Ib_mean:.4f}")
    print(f"    Net: {net_feedback:+.4f}")
    print(f"  Stability: {'✓ STABLE' if is_stable else '✗ UNSTABLE'}")

# ============================================================================
# SUMMARY AND RECOMMENDATIONS
# ============================================================================

print(f"\n" + "=" * 80)
print("TUNING SUMMARY")
print("=" * 80)

# Create summary table
print(f"\n{'Test':<5} {'G_Ia':<6} {'G_Ib':<6} {'F_CV%':<8} {'FR(Hz)':<8} {'Stable':<8} {'Description':<30}")
print("-" * 80)

for i, r in enumerate(results):
    stable_str = "✓" if r['is_stable'] else "✗"
    print(f"{i+1:<5} {r['G_Ia']:<6.1f} {r['G_Ib']:<6.1f} {r['F_CV']:<8.2f} {r['mean_firing_rate']:<8.1f} {stable_str:<8} {r['description']:<30}")

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print(f"\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

# Filter stable configurations
stable_results = [r for r in results if r['is_stable']]

if not stable_results:
    print("\n⚠️  No stable configurations found!")
    print("Consider reducing gain values or checking model parameters.")
else:
    # Find configuration with CV closest to physiological range (2-4%)
    target_CV = 3.0
    best_result = min(stable_results, key=lambda r: abs(r['F_CV'] - target_CV))
    
    print(f"\nBest configuration (CV closest to {target_CV}%):")
    print(f"  G_Ia = {best_result['G_Ia']:.1f}")
    print(f"  G_Ib = {best_result['G_Ib']:.1f}")
    print(f"  Description: {best_result['description']}")
    print(f"  Force CV: {best_result['F_CV']:.2f}%")
    print(f"  Mean firing rate: {best_result['mean_firing_rate']:.1f} Hz")
    print(f"  Stability: ✓")
    
    # Alternative: Balanced feedback
    balanced = [r for r in stable_results if r['G_Ib'] >= r['G_Ia'] and r['G_Ia'] > 0]
    if balanced:
        moderate_balanced = min(balanced, key=lambda r: abs(r['G_Ia'] - 0.2))
        print(f"\nAlternative (balanced, G_Ib >= G_Ia):")
        print(f"  G_Ia = {moderate_balanced['G_Ia']:.1f}")
        print(f"  G_Ib = {moderate_balanced['G_Ib']:.1f}")
        print(f"  Description: {moderate_balanced['description']}")
        print(f"  Force CV: {moderate_balanced['F_CV']:.2f}%")
        print(f"  Mean firing rate: {moderate_balanced['mean_firing_rate']:.1f} Hz")

# ============================================================================
# VISUALIZATION
# ============================================================================

print(f"\nGenerating comparison plots...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Extract data for plotting
G_Ia_vals = [r['G_Ia'] for r in results]
G_Ib_vals = [r['G_Ib'] for r in results]
CV_vals = [r['F_CV'] for r in results]
FR_vals = [r['mean_firing_rate'] for r in results]
stable_vals = [r['is_stable'] for r in results]

# Plot 1: Force CV vs G_Ia (Ib = 0)
ia_only = [r for r in results if r['G_Ib'] == 0]
if ia_only:
    ia_G_Ia = [r['G_Ia'] for r in ia_only]
    ia_CV = [r['F_CV'] for r in ia_only]
    axes[0, 0].plot(ia_G_Ia, ia_CV, 'go-', linewidth=2, markersize=8, label='Ia only (G_Ib=0)')
    axes[0, 0].axhline(y=3.0, color='r', linestyle='--', label='Target CV (3%)')
    axes[0, 0].set_xlabel('G_Ia (Ia feedback gain)')
    axes[0, 0].set_ylabel('Force CV (%)')
    axes[0, 0].set_title('Effect of Ia Feedback on Force Variability')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Force CV vs G_Ib (Ia = 0)
ib_only = [r for r in results if r['G_Ia'] == 0]
if ib_only:
    ib_G_Ib = [r['G_Ib'] for r in ib_only]
    ib_CV = [r['F_CV'] for r in ib_only]
    axes[0, 1].plot(ib_G_Ib, ib_CV, 'ro-', linewidth=2, markersize=8, label='Ib only (G_Ia=0)')
    axes[0, 1].axhline(y=3.0, color='r', linestyle='--', label='Target CV (3%)')
    axes[0, 1].set_xlabel('G_Ib (Ib feedback gain)')
    axes[0, 1].set_ylabel('Force CV (%)')
    axes[0, 1].set_title('Effect of Ib Feedback on Force Variability')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Firing rate vs gains
balanced = [r for r in results if r['G_Ia'] == r['G_Ib']]
if balanced:
    bal_gains = [r['G_Ia'] for r in balanced]
    bal_FR = [r['mean_firing_rate'] for r in balanced]
    axes[1, 0].plot(bal_gains, bal_FR, 'bo-', linewidth=2, markersize=8, label='Balanced (G_Ia=G_Ib)')
    axes[1, 0].set_xlabel('Feedback Gain (G_Ia = G_Ib)')
    axes[1, 0].set_ylabel('Mean Firing Rate (Hz)')
    axes[1, 0].set_title('Effect of Balanced Feedback on Firing Rate')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Stability map (G_Ia vs G_Ib)
stable_Ia = [r['G_Ia'] for r in results if r['is_stable']]
stable_Ib = [r['G_Ib'] for r in results if r['is_stable']]
unstable_Ia = [r['G_Ia'] for r in results if not r['is_stable']]
unstable_Ib = [r['G_Ib'] for r in results if not r['is_stable']]

if stable_Ia:
    axes[1, 1].scatter(stable_Ia, stable_Ib, c='green', s=100, marker='o', label='Stable', alpha=0.7)
if unstable_Ia:
    axes[1, 1].scatter(unstable_Ia, unstable_Ib, c='red', s=100, marker='x', label='Unstable', alpha=0.7)

# Add G_Ib = G_Ia line
max_gain = max(max(G_Ia_vals), max(G_Ib_vals))
axes[1, 1].plot([0, max_gain], [0, max_gain], 'k--', alpha=0.3, label='G_Ib = G_Ia')
axes[1, 1].set_xlabel('G_Ia (Ia feedback gain)')
axes[1, 1].set_ylabel('G_Ib (Ib feedback gain)')
axes[1, 1].set_title('Stability Map')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('feedback_gain_tuning_results.png', dpi=150, bbox_inches='tight')
print(f"Saved: feedback_gain_tuning_results.png")

plt.close()

print(f"\n" + "=" * 80)
print("TUNING COMPLETE")
print("=" * 80)
