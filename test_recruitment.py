"""
Quick test to debug recruitment thresholds
"""
import numpy as np

# Parameters from main code
n = 120
RTE_1 = 0.01
RR = 100

# Compute RTE for first few motor units
RTE = np.zeros(n)
for i in range(n):
    RTE[i] = RTE_1 * np.exp((i) * np.log(RR) / (n - 1))

print("First 10 motor unit recruitment thresholds:")
for i in range(10):
    print(f"MU {i+1}: RTE = {RTE[i]:.6f}")

print(f"\nLast motor unit: RTE = {RTE[-1]:.6f}")
print(f"\nDrive level at 30% MVC: 0.30")
print(f"Number of MUs that should be recruited at 0.30: {np.sum(RTE <= 0.30)}")
