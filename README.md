"""
===============================================================================
FIGURE GENERATION — reproduces Figures 1-7 exactly as they appear in the paper
===============================================================================

HOW TO RUN
----------
1. Run 01_analysis_pipeline.py first is NOT required -- this script is
   self-contained and reloads/recomputes what it needs.
2. Install dependencies (one time only):
     pip install pandas numpy matplotlib --break-system-packages
3. Run:
     python 02_generate_figures.py
4. Output: 7 PNG files (fig1_...png to fig7_...png) saved in the same folder.

Each figure's code block is preceded by a comment explaining what it shows
and which paper section it supports.
===============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans"})

# ---- Load and prepare data (same steps as 01_analysis_pipeline.py) ----
df = pd.read_csv("Energy_Harvester_Dataset.csv")
df.columns = ["datetime", "wspd", "ucomp", "vcomp", "wcomp", "elevation", "an4"]
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").drop_duplicates(subset="datetime").reset_index(drop=True)
df["wdir"] = np.degrees(np.arctan2(-df["ucomp"], -df["vcomp"])) % 360
df["alpha"] = np.degrees(np.arctan2(df["vcomp"], df["ucomp"]))
df["abs_alpha"] = df["alpha"].abs()

# ==============================================================================
# FIGURE 1 — Time series of wind speed and harvester output (Section 3.1)
# ==============================================================================
fig, ax1 = plt.subplots(figsize=(11, 4))
ax1.plot(df["datetime"], df["wspd"], color="#1f77b4", lw=0.6)
ax1.set_ylabel("Wind speed (m/s)", color="#1f77b4")
ax1.tick_params(axis="y", labelcolor="#1f77b4")
ax1.set_xlabel("Date")
ax2 = ax1.twinx()
ax2.plot(df["datetime"], df["an4"], color="#d62728", lw=0.6, alpha=0.7)
ax2.set_ylabel("Harvester output, an4 (mV)", color="#d62728")
ax2.tick_params(axis="y", labelcolor="#d62728")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig("fig1_timeseries.png", dpi=200)
plt.close()
print("Saved fig1_timeseries.png")

# ==============================================================================
# FIGURE 2 — Correlation matrix (Section 3.2)
# ==============================================================================
cols = ["wspd", "ucomp", "vcomp", "wcomp", "elevation", "an4"]
corr = df[cols].corr()
fig, ax = plt.subplots(figsize=(5.5, 5))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right")
ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8,
                 color="white" if abs(corr.iloc[i, j]) > 0.5 else "black")
plt.colorbar(im, label="Pearson r")
plt.tight_layout()
plt.savefig("fig2_correlation.png", dpi=200)
plt.close()
print("Saved fig2_correlation.png")

# ==============================================================================
# FIGURE 3 — Wind speed vs output with 3 model fits (Section 3.3)
# ==============================================================================
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(df["wspd"], df["an4"], s=6, alpha=0.25, color="gray", label="Observations")
xs = np.linspace(df["wspd"].min(), df["wspd"].max(), 200)
ax.plot(xs, 28.212 * xs - 23.885, color="#1f77b4", lw=2, label="Linear (R\u00b2=0.70)")
ax.plot(xs, 4.573 * xs ** 2.272, color="#2ca02c", lw=2, ls="--", label="Power law (R\u00b2=0.65)")
c3 = np.polyfit(df["wspd"], df["an4"], 3)
ax.plot(xs, np.polyval(c3, xs), color="#d62728", lw=2, ls=":", label="Cubic poly (R\u00b2=0.73)")
ax.set_xlabel("Wind speed (m/s)"); ax.set_ylabel("Harvester output, an4 (mV)")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig("fig3_scatter_models.png", dpi=200)
plt.close()
print("Saved fig3_scatter_models.png")

# ==============================================================================
# FIGURE 4 — Elevation angle effect within wind-speed bins (Section 3.4)
# ==============================================================================
df["wspd_bin2"] = pd.cut(df["wspd"], bins=[0, 1.5, 2.5, 3.5, 5, 7],
                          labels=["0-1.5", "1.5-2.5", "2.5-3.5", "3.5-5", "5-7"])
fig, axes = plt.subplots(1, 5, figsize=(15, 3.5), sharey=True)
for i, (name, sub) in enumerate(df.groupby("wspd_bin2", observed=True)):
    axes[i].scatter(sub["elevation"], sub["an4"], s=8, alpha=0.4, color="#1f77b4")
    if len(sub) > 5:
        z = np.polyfit(sub["elevation"], sub["an4"], 1)
        xs2 = np.linspace(sub["elevation"].min(), sub["elevation"].max(), 50)
        axes[i].plot(xs2, np.polyval(z, xs2), color="#d62728", lw=2)
    axes[i].set_title(f"wspd: {name} m/s (n={len(sub)})", fontsize=9)
    axes[i].set_xlabel("Elevation (deg)")
axes[0].set_ylabel("an4 (mV)")
plt.tight_layout()
plt.savefig("fig4_elevation_bins.png", dpi=200)
plt.close()
print("Saved fig4_elevation_bins.png")

# ==============================================================================
# FIGURE 5 — Wind rose colored by mean output (Section 3.5)
# ==============================================================================
wdir_bins = np.arange(0, 361, 30)
df["wdir_bin"] = pd.cut(df["wdir"], bins=wdir_bins, include_lowest=True)
rose = df.groupby("wdir_bin", observed=True).agg(mean_an4=("an4", "mean"),
                                                    freq=("an4", "count")).reset_index()
angles = np.radians(wdir_bins[:-1] + 15)
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection="polar")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
ax.bar(angles, rose["freq"], width=np.radians(28),
       color=plt.cm.YlOrRd(rose["mean_an4"] / rose["mean_an4"].max()), edgecolor="k", linewidth=0.5)
sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=rose["mean_an4"].min(), vmax=rose["mean_an4"].max()))
plt.colorbar(sm, ax=ax, pad=0.1, shrink=0.7, label="Mean an4 (mV)")
plt.tight_layout()
plt.savefig("fig5_windrose.png", dpi=200)
plt.close()
print("Saved fig5_windrose.png")

# ==============================================================================
# FIGURE 6 — Output vs wind speed, headwind vs backwind (Section 3.7)
# ==============================================================================
fig, ax = plt.subplots(figsize=(6.5, 5.5))
head = df[df["abs_alpha"] < 90]
back = df[df["abs_alpha"] >= 90]
ax.scatter(back["wspd"], back["an4"], s=8, alpha=0.3, color="#7f7f7f",
           label=f"Backwind, |\u03b1|\u226590\u00b0 (n={len(back)})")
ax.scatter(head["wspd"], head["an4"], s=8, alpha=0.3, color="#1f77b4",
           label=f"Headwind, |\u03b1|<90\u00b0 (n={len(head)})")
xs = np.linspace(0, df["wspd"].max(), 100)
ax.plot(xs, 37.06 * xs - 34.68, color="#08306b", lw=2.5, label="Headwind fit (R\u00b2=0.82, slope=37.1)")
ax.plot(xs, 19.07 * xs - 15.31, color="#525252", lw=2.5, ls="--", label="Backwind fit (R\u00b2=0.87, slope=19.1)")
ax.set_xlabel("Wind speed (m/s)"); ax.set_ylabel("Harvester output, an4 (mV)")
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(bottom=-10)
plt.tight_layout()
plt.savefig("fig6_hemisphere.png", dpi=200)
plt.close()
print("Saved fig6_hemisphere.png")

# ==============================================================================
# FIGURE 7 — Output as a function of incidence angle alpha (Section 3.7)
# ==============================================================================
alpha_bins = np.arange(-180, 181, 20)
df["alpha_bin"] = pd.cut(df["alpha"], bins=alpha_bins, include_lowest=True)
rose2 = df.groupby("alpha_bin", observed=True).agg(mean_an4=("an4", "mean"),
                                                      freq=("an4", "count")).reset_index()
centers = alpha_bins[:-1] + 10
angles2 = np.radians(centers)
fig = plt.figure(figsize=(6.5, 6.5))
ax = fig.add_subplot(111, projection="polar")
ax.set_theta_zero_location("N"); ax.set_theta_direction(1)
ax.bar(angles2, rose2["freq"], width=np.radians(18),
       color=plt.cm.viridis(rose2["mean_an4"] / rose2["mean_an4"].max()), edgecolor="k", linewidth=0.4)
sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(vmin=rose2["mean_an4"].min(), vmax=rose2["mean_an4"].max()))
plt.colorbar(sm, ax=ax, pad=0.1, shrink=0.7, label="Mean an4 (mV)")
ax.set_xticks(np.radians([0, 90, 180, 270]))
ax.set_xticklabels(["\u03b1=0\u00b0\n(optimal, from W)", "\u03b1=+90\u00b0\n(from N)",
                     "\u03b1=\u00b1180\u00b0\n(from E, back)", "\u03b1=\u221290\u00b0\n(from S)"], fontsize=8)
plt.tight_layout()
plt.savefig("fig7_incidence_rose.png", dpi=200)
plt.close()
print("Saved fig7_incidence_rose.png")

print("\nAll 7 figures generated. Compare them visually to the figures in the paper.")
