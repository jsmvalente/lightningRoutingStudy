import matplotlib.pyplot as plt

nNodes = []

# Populate mean weight (x values)
for i in range(0, 9):
    nNodes.append(100 + (i*50))

# Populate average delta (y values)
ldr_success = [37.85, 35.35, 28.0, 31.55, 23.5, 25.75, 24.15, 24.3, 24.45]
spr_success = [37.25, 34.2, 26.1, 30.05, 21.1, 22.55, 21.05, 19.7, 19.95]
spr_apl = [2.33, 2.83, 3.23, 3.19, 3.61, 3.8, 4.15, 4.15, 4.25]
ldr_apl = [2.38, 2.96, 3.52, 3.41, 4.02, 4.49, 4.73, 4.89, 5.09]
average_delta = [ldr_success[i]-spr_success[i] for i in range(len(ldr_success))]

fig, (ax1, ax3) = plt.subplots(2)

# Set the first axis (first subplot) with tthe deltas
ax1.set_xlabel('Number of nodes')
ax1.set_ylabel(r'$\overline{\Delta}$' + ' (%)', color='tab:red')
ax1.plot(nNodes, average_delta, color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

# Set the second axis (first subplot) with P(Success) for both solutions (shares x_axis with ax1)
ax2.set_ylabel(r'$\overline{P(Success)}$' + ' (%)', color='tab:blue')  # we already handled the x-label with ax1
ax2.plot(nNodes, spr_success, color='tab:blue', label="SPR")
ax2.plot(nNodes, ldr_success, linestyle='dashed', color='tab:blue', label="LDR")
ax2.tick_params(axis='y', labelcolor='tab:blue')
ax2.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", borderaxespad=0, ncol=3)

# Set the third axis (second subplot) with the the APL for LDR and SPR
ax3.set_xlabel('Number of nodes')
ax3.set_ylabel('APL')
ax3.plot(nNodes, spr_apl, color='tab:blue', label="SPR")
ax3.plot(nNodes, ldr_apl, linestyle='dashed', color='tab:blue', label="LDR")
ax3.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", borderaxespad=0, ncol=3)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()