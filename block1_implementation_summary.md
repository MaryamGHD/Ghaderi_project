# Block 1: Motor Neuron Pool Model - Implementation Summary

## Overview

Successfully implemented Block 1 (Motor Neuron Pool Model) from Dideriksen et al. (2010) in Python, following the exact equations and structure from the paper.

## Files Created

1. **[block1_motor_neuron_pool.md](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block1_motor_neuron_pool.md)** - Complete documentation with all equations, parameters, and interactions
2. **[block1_pseudocode.md](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block1_pseudocode.md)** - Code-ready pseudocode with exact variable names
3. **[block1_motor_neuron_pool.py](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block1_motor_neuron_pool.py)** - Working Python implementation

## Implementation Details

### Parameters Used
- **Motor units**: 120
- **Time step**: 1 ms (0.001 s)
- **Simulation duration**: 60 s
- **Excitatory drive**: Ramp to 30% MVC over 5 s, then hold
- **Gain factor**: 40.0 (adjusted to ensure membrane potential reaches threshold)
- **Noise**: σ = 0.02 (Gaussian white noise)

### Key Equations Implemented

**Membrane dynamics:**
```
τ_m(i) · dV/dt = -V(t) + g · [e(t) + ξ(t)] - AHP(t)
```

**AHP dynamics:**
```
τ_AHP(i) · dAHP/dt = -AHP(t)
```

**Recruitment thresholds (exponential):**
```
RTE(i) = RTE₁ · exp[(i-1) · ln(RR) / (n-1)]
```

**Firing rate parameters (linear):**
```
f_min(i) = f_min,1 - (f_min,1 - f_min,n) · (i-1)/(n-1)
f_peak(i) = f_peak,1 + (f_peak,n - f_peak,1) · (i-1)/(n-1)
```

## Simulation Results

### At 30% MVC Drive:
- ✅ **89 / 120 motor units recruited** (expected ~88 based on recruitment thresholds)
- ✅ **All recruited units generated spikes**
- ✅ **Firing rates**: 5-20 Hz (within physiological range)
- ✅ **Sequential recruitment** following size principle
- ✅ **Realistic spike patterns** with noise-induced variability

### Visualizations Generated

**[block1_results.png](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block1_results.png)** shows:
1. Excitatory drive over time (ramp-and-hold)
2. Spike trains (raster plot for first 30 motor units)
3. Mean firing rates vs motor unit index
4. Recruitment thresholds (exponential distribution)

**[block1_membrane_potentials.png](file:///Users/maryamghaderi/Downloads/untitled%20folder%202/block1_membrane_potentials.png)** shows:
- Membrane potential traces for representative motor units
- Sequential recruitment (earlier units recruit first)
- Spike generation at threshold crossing
- AHP-induced hyperpolarization after each spike
- Sustained firing during hold phase

## Validation

✅ **Recruitment thresholds**: Monotonically increasing (exponential distribution)  
✅ **Motor unit recruitment**: Follows size principle (smaller units first)  
✅ **Firing patterns**: Realistic with noise-induced variability  
✅ **Membrane dynamics**: Proper integration, threshold crossing, and AHP  

## Parameter Adjustment Note

The gain factor `g` was adjusted from 15.0 to 40.0 to ensure that recruited motor units reach firing threshold. This is not explicitly specified in the paper but is necessary for the model to produce spikes. At 30% MVC with g=40:
- Steady-state membrane potential: V ≈ 12 mV
- Firing threshold: θ = 10 mV
- Result: Membrane potential exceeds threshold → spikes generated

## Output Data Structure

The simulation produces:
- `output_spike_trains[n_steps, n]` - Binary spike trains for each motor unit
- `output_V[n_steps, n]` - Membrane potentials over time
- `output_drive[n_steps]` - Excitatory drive signal
- `output_recruited[n_steps, n]` - Recruitment status

**This output is ready to serve as input to Block 2 (Muscle Force Generation).**

## Next Steps

1. Continue with Block 3: Fatigue Mechanisms documentation
2. Implement Block 2: Muscle Force Generation in Python
3. Integrate all blocks into complete model
