import matplotlib.pyplot as plt

nNodes = []

# Populate mean weight (x values)
for i in range(0, 15):
    nNodes.append(100 + (i*50))

# Populate average delta (y values)
average_delta = []
spr_success = []
ldr_success = [average_delta[i]+spr_success[i] for i in range(len(average_delta))]

fig, ax1 = plt.subplots()

ax1.set_xlabel('Number of nodes')
ax1.set_ylabel('Average Delta (%)', color='tab:red')
ax1.plot(nNodes, average_delta, color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.set_ylabel('Average P(Success) (%)', color='tab:blue')  # we already handled the x-label with ax1
ax2.plot(nNodes, spr_success, color='tab:blue', label="SPR")
ax2.plot(nNodes, ldr_success, linestyle='dashed', color='tab:blue', label="LDR")
ax2.tick_params(axis='y', labelcolor='tab:blue')
ax2.legend()

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()