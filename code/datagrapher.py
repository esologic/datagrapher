from random import randint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot
from datetime import datetime
from multiprocessing import Process
from statistics import mean, median_low, median_high, stdev
import pickle


class EasyStats(object):

    def __init__(self, raw_data, round_place=10):
        self.raw_data = raw_data

        self.mean = round(mean(raw_data), round_place)
        self.mode = round(max(set(raw_data), key=raw_data.count), round_place)
        self.median_low = round(median_low(raw_data), round_place)
        self.median_high = round(median_high(raw_data), round_place)
        self.max = round(max(raw_data), round_place)
        self.min = round(min(raw_data), round_place)
        self.standard_deviation = round(stdev(raw_data), round_place)


class GraphSet(object):

    def __init__(self, title, unit, data_set, y_axis_limits=None):
        self.title = title
        self.unit = unit
        self.data_set = data_set

        self.stats = EasyStats(data_set)

        # set the limits of the y axis
        if y_axis_limits is None:
            smallest_y = min(data_set)
            largest_y = max(data_set)
            self.y_axis_limits = smallest_y, largest_y
        else:
            self.y_axis_limits = y_axis_limits


class DataGrapher(object):

    def __init__(self, title, x_axis_label, note, graph_sets, figure_size=(12, 12), filename=None):
        """
        DataGrapher is a wrapper for matplotlib that takes in multiple DataSets and plots them on the same x axis
        :param title: The title of the figure
        :param x_axis_label: The label of the installations x axis
        :param note: The note left below the figure
        :param graph_sets: A list of GraphSet objects to be plotted
        :param y_axis_limits: A place for the user to set the limits of the x axis
        :param figure_size: The size of the image in inches
        :param filename: The name of the file to be saved
        :param show: If set to true, the graph will be shown after it is rendered
        """

        self.title = title
        self.x_axis_label = x_axis_label
        self.note = note
        self.graph_sets = graph_sets
        self.figure_size = figure_size
        self.filename = filename

    def __run_matpotlib__(self):

        # create an range iterable with the length of the longest data set on the input
        x_values = range(len(max(self.graph_sets, key=lambda d_set: len(d_set.data_set)).data_set))

        # set the limits of the x axis
        x_min, x_max = 0, len(x_values)

        figure, axes = plot.subplots(len(self.graph_sets), sharex=True, figsize=self.figure_size)

        # Draw the chart title
        figure.text(0.5, 1, self.title, horizontalalignment='center', verticalalignment='top', fontweight="bold",
                    fontsize="x-large")

        b = .1

        # Draw the x axis label
        figure.text(0.5, b, self.x_axis_label, horizontalalignment='center', verticalalignment='bottom',
                    fontweight="bold")

        # Draw the timestamp
        figure.text(1, 0, datetime.now().strftime("%I:%M:%S%p - %d %B %Y"), horizontalalignment='right',
                    verticalalignment='bottom', fontsize='x-small', transform=plot.gcf().transFigure)

        # Adjust the padding of the plot
        plot.subplots_adjust(left=0.125, right=0.85, bottom=b + 0.05, top=0.975, wspace=0.2, hspace=0.1)

        lowest = None

        for index, graph_set in enumerate(self.graph_sets):

            # if there is only one axis, it will be just the object, not a list of objects
            try:
                axis = axes[index]
            except TypeError:
                axis = axes

            # set the name label of the axis
            axis.text(1.01, .5, graph_set.title, horizontalalignment='left', verticalalignment='top',
                      transform=axis.transAxes, rotation='horizontal')

            # set the y axis label for this axis to the unit of this data set provided by the user
            axis.set_ylabel(graph_set.unit, rotation='vertical')

            # set the limits of the x and y axes to the standard for this chart
            axis.set_ylim([graph_set.y_axis_limits[0], graph_set.y_axis_limits[1] + graph_set.stats.standard_deviation])
            axis.set_xlim([x_min, x_max])

            # if the data is greater than the mean + 1 stdev, it is highlighted in red
            for datum, bar, in zip(graph_set.data_set, axis.bar(x_values, graph_set.data_set)):
                if datum > graph_set.stats.mean + graph_set.stats.standard_deviation:
                    bar.set_color('r')
                else:
                    bar.set_color('b')

            legend_text = "Min: " + str(graph_set.stats.min) + ", "
            legend_text += "Max: " + str(graph_set.stats.max) + "\n"
            legend_text += "Mean: " + str(graph_set.stats.mean) + ", "
            legend_text += "Mode: " + str(graph_set.stats.mode) + ", "
            legend_text += "Stdev: " + str(graph_set.stats.standard_deviation)

            # draw the legend
            axis.text(0.025, 0.90, legend_text, verticalalignment='top', fontsize=10, transform=axis.transAxes,
                      bbox=dict(boxstyle='square', facecolor='wheat', alpha=0.5))

            lowest = axis.get_position()

        # Draw the note
        figure.text(lowest.x0, (lowest.y0 - (lowest.height + 0.0125)), "Note: " + self.note, horizontalalignment='left', verticalalignment='bottom')

        # save the plot
        if self.filename is not None:
            plot.savefig(self.filename)
        else:
            plot.savefig("output.png")

    def render_as_image(self, filename):
        self.filename = filename
        render_process = Process(target=self.__run_matpotlib__)
        render_process.start()
        render_process.join()

    def render_as_pickle(self, pickle_path):
        with open(pickle_path, "wb") as file:
            pickle.dump(self, file)
            file.flush()
