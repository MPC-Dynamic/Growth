import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# INPUTS
# ---------------------------

# Example: load your utilization data
# Replace with your actual file / column
df = pd.read_excel("Flattened Parking Count Data_YC_with plot.xlsx")

# Assume you already computed utilization column (0–1 scale)
# If not, define it like:
# df["utilization"] = df["occupancy"] / capacity

util = df["utilization"].dropna().values

# Survey PPR (example for Yacht Club)
PPR = 0.2854   # 28.54%

# ---------------------------
# SURVIVAL FUNCTION
# ---------------------------

# Sort utilization values
u_vals = np.sort(util)

# Compute survival function S(u) = P(U >= u)
survival = 1 - np.arange(len(u_vals)) / len(u_vals)

# ---------------------------
# FIND THRESHOLD u*
# ---------------------------

# Find closest match where survival ≈ PPR
idx = np.argmin(np.abs(survival - PPR))
u_star = u_vals[idx]

print(f"Behavioral threshold u*: {u_star:.3f}")

# ---------------------------
# PLOT
# ---------------------------

plt.figure(figsize=(7,5))

# Survival curve
plt.plot(u_vals, survival, label="Survival Function P(U ≥ u)")

# Horizontal PPR line
plt.axhline(PPR, linestyle="--", label=f"PPR = {PPR:.2f}")

# Vertical threshold line
plt.axvline(u_star, linestyle="--", label=f"u* = {u_star:.2f}")

# Intersection point
plt.scatter([u_star], [PPR])

plt.xlabel("Utilization (u)")
plt.ylabel("P(U ≥ u)")
plt.title("Calibration Curve: Yacht Club")

plt.legend()
plt.grid(True)

plt.show()
