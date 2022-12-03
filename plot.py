import matplotlib.pyplot as plt
import numpy as np
from textwrap import wrap

import io_manager


class Plot:
    """
    Plot data and save plots in files
    """
    _dpi = 100  # default resolution

    def _get_dpi(self):
        """
        :return: DPI for the output files
        """
        return self._dpi

    def _plot_line(self, x_points, y_points, highlight, title, x_label='omp_threads', y_label='time, [s]'):
        """
        Plot a single line
        :param y_points: Y-axis points
        :param x_points: X-axis points
        :param highlight: Coordinates of a point that should be highlighted
        :param title: Title of the plot
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: None
        """
        # set up the canvas
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid()
        plt.xticks(x_points)
        plt.title(title + ' plot')

        # plot performance values
        plt.plot(x_points, y_points)
        # plot minimum (best) value
        plt.plot(highlight[0], highlight[1], marker="o", markersize=15,
                 markeredgecolor="black", markerfacecolor="red",
                 alpha=0.7)

        # visualize and save the plot
        # plt.show()
        self._save_file(title)

        plt.clf()

    def _plot_bar(self, data, labels, highlight, title, x_label='time, [s]', y_label='flags'):
        """
        Plot a horizontal bar plot
        :param data: Data values
        :param labels: Data labels
        :param highlight: Data value of a bar that should be highlighted
        :param title: Title of the plot
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: None
        """
        # set up the canvas
        plt.xlabel(y_label)
        plt.xlabel(x_label)
        # plt.grid()
        plt.title(title + ' plot')

        # make sure labels fit into the canvas
        labels = ['\n'.join(wrap(l, 30)) for l in labels]

        # plot performance values
        y_pos = np.arange(len(labels))
        f = plt.figure()
        f.set_figwidth(10)
        f.set_figheight(int(len(data) * 0.5))
        hbars = plt.barh(labels, data, align='center',
                         color=['steelblue' if (d > highlight[1])
                                else 'lightcoral' for d in data])
        plt.bar_label(hbars, label_type='center', fmt='%.4f')
        plt.tight_layout()

        # visualize and save the plot
        # plt.show()
        self._save_file(title)
        
        plt.clf()

    def _save_file(self, title):
        """
        Save plot to the file
        :param title: Title of the plot (will be used in a file name)
        :return: None
        """
        output_filename = title + '.png'
        plt.savefig(output_filename, dpi=self._get_dpi())
        io_manager.print_dbg_info('File ' + output_filename + ' is saved')

    def plot_compiler_flags(self, data, labels, title, x_label='time, [s]', y_label='flags'):
        """
        Generate bar plot for a set of compiler flags
        :param data: Data values
        :param labels: Data labels
        :param title: Plot title
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: none
        """
        best_value = min(data)
        best_pos = labels[data.index(best_value)]

        self._plot_bar(data, labels, (best_pos, best_value), title, x_label, y_label)

    def plot_scalability(self, x_points, y_points, title, x_label='omp_threads', y_label='time, [s]'):
        """
        Generate plot for scalability
        :param x_points: X-axis points
        :param y_points: Y-axis points
        :param title: Title of the plot
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: None
        """
        best_value = min(y_points)
        best_pos = x_points[y_points.index(best_value)]

        self._plot_line(x_points, y_points, (best_pos, best_value), title, x_label, y_label)

    def plot_parallel_efficiency(self, x_points, y_points, title, x_label='omp_threads', y_label='time, [s]'):
        """
        Generate plot for parallel efficiency
        :param x_points: X-axis points
        :param y_points: Y-axis points
        :param title: Title of the plot
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: None
        """
        efficiency = [None]*len(y_points)
        for ind, val in enumerate(y_points):
            procs = x_points[ind]
            efficiency[ind] = y_points[0] / val / procs

        # min_value = min(efficiency)
        # min_pos = efficiency.index(min_value) + 1
        last_value = 0.0
        last_pos = 0
        threshold = 0.02    # ~= 20% drop
        for ind, val in enumerate(efficiency):
            if ind != 0:
                grad = abs((last_value - val) / (x_points[ind] - x_points[last_pos]))
                if grad > threshold:
                    break
            last_value = val
            last_pos = ind

        self._plot_line(x_points, efficiency, (x_points[last_pos], last_value), title, x_label, y_label)
