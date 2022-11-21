import matplotlib.pyplot as plt
import numpy as np

class Plot:
    def plot_line(self, data, x_range, highlight, title, x_label='omp_threads', y_label='time, [s]'):
        # set up the canvas
        plt.ylabel('time, [s]')
        plt.xlabel(x_label)
        plt.grid()
        plt.xticks(x_range)
        plt.title(title + ' plot')

        # plot performance values
        plt.plot(x_range, data)
        # plot minimum (best) value
        plt.plot(highlight[0], highlight[1], marker="o", markersize=15,
                markeredgecolor="black", markerfacecolor="red",
                alpha=0.7)

        # visualize and save the plot
        # plt.show()
        plt.savefig(title + '.png')
        plt.clf()


    def plot_scalability(self, data, x_range, title, x_label='omp_threads', y_label='time, [s]'):
        best_value = min(data)
        best_pos = x_range[data.index(best_value)]

        self.plot_line(data, x_range, (best_pos, best_value), title, x_label, y_label)


    def plot_parallel_efficiency(self, data, x_range, title, x_label='omp_threads', y_label='time, [s]'):
        efficiency = [None]*len(data)
        for ind, val in enumerate(data):
            procs = x_range[ind]
            efficiency[ind] = data[0] / val / procs

        # min_value = min(efficiency)
        # min_pos = efficiency.index(min_value) + 1
        best_value = 0.0
        best_pos = 0
        threshold = 0.020  # == 20% drop
        for ind, val in enumerate(efficiency):
            if ind != 0:
                grad = abs((best_value - val) / (x_range[ind] - x_range[best_pos-1]))
                if grad <= threshold:
                    best_value = val
                    best_pos = x_range[ind]
                else:
                    break
            else:
                best_value = val
                best_pos = ind + 1

        self.plot_line(efficiency, x_range, (best_pos, best_value), title, x_label, y_label)
