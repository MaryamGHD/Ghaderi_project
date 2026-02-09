"""
Test version with debug output to check recruitment
"""
import numpy as np

# Simulation parameters
dt = 0.001
T_total = 10.0  # Shorter simulation
n_steps = int(T_total / dt)

# Motor unit pool
n = 10  # Fewer units for debugging

# Parameters
RTE_1 = 0.01
RR = 100
g = 15.0
sigma_noise = 0.02
Delta_H = 0.01

# Initialize RTE
RTE = np.zeros(n)
for i in range(n):
    RTE[i] = RTE_1 * np.exp((i) * np.log(RR) / (n - 1))

print("Recruitment thresholds:")
for i in range(n):
    print(f"MU {i}: RTE = {RTE[i]:.4f}")
print()

# State variables
is_recruited = np.zeros(n, dtype=bool)

# Simulation
print("Starting simulation...")
for step in range(n_steps):
    t = step * dt
    
    # Drive
    t_ramp = 5.0
    e_target = 0.30
    if t < t_ramp:
        e_t = e_target * (t / t_ramp)
    else:
        e_t = e_target
    
    # Noise
    xi_t = np.random.normal(0, sigma_noise)
    
    # Effective drive
    e_eff = e_t + xi_t
    
    # Check recruitment
    for i in range(n):
        if not is_recruited[i]:
            if e_eff >= RTE[i]:
                is_recruited[i] = True
                print(f"t={t:.3f}s: MU {i} recruited (e_eff={e_eff:.4f}, RTE={RTE[i]:.4f})")
    
    # Print status every second
    if step % int(1.0 / dt) == 0:
        print(f"t={t:.1f}s: e_t={e_t:.4f}, e_eff={e_eff:.4f}, recruited={np.sum(is_recruited)}/{n}")

print()
print(f"Final: {np.sum(is_recruited)} / {n} motor units recruited")
