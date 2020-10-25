import matplotlib.pyplot as plt

mean_weight = []

# Populate mean weight (x values)
for i in range(1, 16):
    mean_weight.append(0.2*i)

# Populate average delta (y values)
average_delta = [0.4, 2.16, 2.34, 2.38, 2.4, 2.31, 2.25, 1.65, 1.84, 1.2, 1.36, 1.49, 1.49, 0.99, 1.18]
spr_success = [58.62, 42.16, 31.95, 28.04, 24.5, 20.74, 18.08, 16.99, 15.54, 14.12, 13.64, 11.98, 11.75, 11.14, 10.15]
ldr_success = [average_delta[i]+spr_success[i] for i in range(len(average_delta))]

fig, ax1 = plt.subplots()

ax1.set_xlabel('Mean Weight')
ax1.set_ylabel(r'$\overline{\Delta}$' + ' (%)', color='tab:red')
ax1.plot(mean_weight, average_delta, color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.set_ylabel(r'$\overline{P(Success)}$' + ' (%)', color='tab:blue')  # we already handled the x-label with ax1
ax2.plot(mean_weight, spr_success, color='tab:blue', label="SPR")
ax2.plot(mean_weight, ldr_success, linestyle='dashed', color='tab:blue', label="LDR")
ax2.tick_params(axis='y', labelcolor='tab:blue')
ax2.legend()

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()