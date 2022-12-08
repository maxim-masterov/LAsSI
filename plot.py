from cProfile import label
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.style as style
import numpy as np
from textwrap import wrap

import io_manager


class Plot:
    """
    Plot data and save plots in files
    """
    _dpi = 120  # default resolution

    def _get_dpi(self):
        """
        :return: DPI for the output files
        """
        return self._dpi

    def _plot_line(self, x_points, y_points, highlight, title, key_labels, x_label='omp_threads', y_label='time, [s]'):
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
        num_data_sets = len(x_points)

        # set up the canvas
        f = plt.figure()
        ax = plt.subplot(111)
        f.set_figwidth(10)
        f.set_figheight(max(int(num_data_sets * 0.3), 8))

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid()
        plt.xticks(x_points[0])
        plt.title(title + ' plot')

        # for data_set_id in range(num_data_sets):
        #     # plot performance values
        #     plt.plot(x_points[data_set_id], y_points[data_set_id], label=key_labels[data_set_id])
        #     # plot minimum (best) value
        #     plt.plot(highlight[0][data_set_id], highlight[1][data_set_id], marker="o", markersize=15,
        #             markeredgecolor="black", markerfacecolor="red",
        #             alpha=0.7)

        # NUM_COLORS = num_data_sets
        cm = plt.get_cmap('viridis')

        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        for data_set_id in range(num_data_sets):
            # plot performance values
            line = ax.plot(x_points[data_set_id], y_points[data_set_id], label=key_labels[data_set_id])
            if num_data_sets == 1:
                color_id = 1
            else:
                color_id = float(data_set_id)/float(num_data_sets - 1)
            line[0].set_color(cm(color_id))
            line[0].set_linewidth(2)
            # plot minimum (best) value
            ax.plot(highlight[0][data_set_id], highlight[1][data_set_id], marker="o", markersize=15,
                    markeredgecolor="black", markerfacecolor="red",
                    alpha=0.7)

        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
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
        f = plt.figure()
        f.set_figwidth(10)
        f.set_figheight(int(len(data) * 0.5))

        plt.xlabel(y_label)
        plt.xlabel(x_label)
        # plt.grid()
        plt.title(title + ' plot')

        # make sure labels fit into the canvas
        labels = ['\n'.join(wrap(l, 30)) for l in labels]

        # plot performance values
        y_pos = np.arange(len(labels))

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

    def plot_scalability(self, x_points, y_points, title, key_labels, x_label='cores', y_label='time, [s]'):
        """
        Generate plot for scalability
        :param x_points: X-axis points
        :param y_points: Y-axis points
        :param title: Title of the plot
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: None
        """
        self.check_number_of_sets(x_points, y_points)
        self.check_number_of_sets(x_points[0], y_points[0])

        num_data_sets = len(x_points)
        best_value = [None] * num_data_sets
        best_pos = [None] * num_data_sets

        for data_set_id in range(num_data_sets):
            loc_x_points = x_points[data_set_id]
            loc_y_points = y_points[data_set_id]
            loc_best_value = min(loc_y_points)
            loc_best_pos = loc_x_points[loc_y_points.index(loc_best_value)]

            best_value[data_set_id] = loc_best_value
            best_pos[data_set_id] = loc_best_pos

        self._plot_line(x_points, y_points, (best_pos, best_value), title, key_labels, x_label, y_label)

    def plot_parallel_efficiency(self, x_points, y_points, title, key_labels, x_label='cores', y_label='time, [s]'):
        """
        Generate plot for parallel efficiency
        :param x_points: X-axis points
        :param y_points: Y-axis points
        :param title: Title of the plot
        :param x_label: X-axis label
        :param y_label: Y-axis label
        :return: None
        """
        self.check_number_of_sets(x_points, y_points)
        self.check_number_of_sets(x_points[0], y_points[0])

        num_data_sets = len(x_points)
        best_value = [None] * num_data_sets
        best_pos = [None] * num_data_sets

        efficiency = [[0 for i in range(len(x_points[0]))] for y in range(num_data_sets)]
        for data_set_id in range(num_data_sets):
            loc_x_points = x_points[data_set_id]
            loc_y_points = y_points[data_set_id]
            ref_y_point = loc_y_points[0]
            for ind, val in enumerate(loc_y_points):
                procs = loc_x_points[ind]
                efficiency[data_set_id][ind] = ref_y_point / val / procs

            last_value = 0.0
            last_pos = 0
            threshold = 0.2    # drop by 20%
            for ind, val in enumerate(efficiency[data_set_id]):
                if ind != 0:
                    # grad = abs((last_value - val) / (loc_x_points[ind] - loc_x_points[last_pos]))
                    # print(data_set_id, ': ', grad, last_value, val, loc_x_points[ind], loc_x_points[last_pos])
                    # if grad > threshold:
                    #     break
                    if val < (1 - threshold):
                        break
                last_value = val
                last_pos = ind
            best_value[data_set_id] = last_value
            best_pos[data_set_id] = loc_x_points[last_pos]

        self._plot_line(x_points, efficiency, (best_pos, best_value), title, key_labels, x_label, y_label)

    def check_number_of_sets(self, x_points, y_points):
        """
        Check if x and y lists have the same lenghts. Exit on failure.
        :param x_points: List of points in x direction
        :param y_points: List of points in y direction
        :return: None
        """
        if len(x_points) != len(y_points):
            io_manager.print_err_info('Missmatch between the lengths of \'x\' and \'y\' lists: ' 
                                      + str(len(x_points)) + '/' + str(len(y_points)))
            exit(1)
