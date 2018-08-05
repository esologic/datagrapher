import matplotlib
from matplotlib import ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plot
from datetime import datetime
from multiprocessing import Process
from statistics import mean, median_low, median_high, stdev, StatisticsError
import pickle
import random

from collections import deque


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

    def __init__(self, title, unit, data_set, y_axis_limits=None, smart_y_max=True):
        self.title = title
        self.unit = unit
        self.data_set = data_set

        self.stats = EasyStats(data_set)

        # set the limits of the y axis
        if y_axis_limits is None:
            if smart_y_max:
                smallest_y = min(data_set)
                largest_y = mean(data_set) + 3*stdev(data_set)
                self.y_axis_limits = smallest_y, largest_y
            else:
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

        figure, axes = plot.subplots(len(self.graph_sets), figsize=self.figure_size)

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
        figure.text(lowest.x0, (lowest.y0 - 0.08), "Note: " + self.note, horizontalalignment='left', verticalalignment='bottom')

        # save the plot
        if self.filename is not None:
            plot.savefig(self.filename)
        else:
            plot.savefig("output.png")

    def render_as_image(self, filename, as_process=True):
        self.filename = filename

        if as_process:
            render_process = Process(target=self.__run_matpotlib__)
            render_process.start()
            render_process.join()
        else:
            self.__run_matpotlib__()

    def render_as_pickle(self, pickle_path):
        with open(pickle_path, "wb") as file:
            pickle.dump(self, file)
            file.flush()


class TimeSeriesDataGrapher(object):

    def __init__(self, title, note, graph_table, figure_size=(12, 12), filename=None):
        """
        DataGrapher is a wrapper for matplotlib that takes in multiple DataSets and plots them on the same x axis
        :param title: The title of the figure
        :param x_axis_label: The label of the installations x axis
        :param note: The note left below the figure
        :param graph_table: A list of GraphSet objects to be plotted
        :param y_axis_limits: A place for the user to set the limits of the x axis
        :param figure_size: The size of the image in inches
        :param filename: The name of the file to be saved
        :param show: If set to true, the graph will be shown after it is rendered
        """

        self.title = title
        self.note = note
        self.graph_table = graph_table
        self.figure_size = figure_size
        self.filename = filename

    def __run_matpotlib__(self):

        # make sure empty sets are ignored
        good_sets = []

        for gs in self.graph_table:
            if len(gs) > 0:
                good_sets.append(gs)

        x_values_unsorted = set()

        for time_series_graph_set in good_sets:
            for stamp in time_series_graph_set.timestamps:
                x_values_unsorted.add(stamp)

        x_values_sorted = list(reversed(sorted(list(x_values_unsorted))))

        x_value_strings = []
        for x_value in x_values_sorted:
            x_value_strings.append(x_value.strftime("%I:%M:%S.%f"))

        figure, axes = plot.subplots(len(good_sets), figsize=self.figure_size)

        # Draw the chart title
        figure.text(0.5, 1, self.title, horizontalalignment='center', verticalalignment='top', fontweight="bold",
                    fontsize="x-large")

        # Draw the x axis label
        figure.text(0.5, 0.075, "Time", horizontalalignment='center', verticalalignment='bottom',
                    fontweight="bold")

        # Draw the timestamp
        figure.text(1, 0, datetime.now().strftime("%I:%M:%S%p - %d %B %Y"), horizontalalignment='right',
                    verticalalignment='bottom', fontsize='x-small', transform=plot.gcf().transFigure)

        # Adjust the padding of the plot
        plot.subplots_adjust(left=0.125, right=0.85, bottom=0.1 + 0.05, top=0.975, wspace=0.2, hspace=0.1)

        lowest = None
        final = None

        for index, graph_set in enumerate(good_sets):

            # if there is only one axis, it will be just the object, not a list of objects
            try:
                axis = axes[index]
            except TypeError:
                axis = axes

            # set the name label of the axis
            axis.text(1.01, .5, graph_set.name, horizontalalignment='left', verticalalignment='top',
                      transform=axis.transAxes, rotation='horizontal')

            # set the y axis label for this axis to the unit of this data set provided by the user
            axis.set_ylabel(graph_set.unit, rotation='vertical')

            y_values = []
            for x_value in x_values_sorted:
                if x_value in graph_set.timestamps:
                    y_values.append(graph_set.value_at_time(x_value))
                else:
                    y_values.append(0)

            stats = EasyStats(graph_set.values)

            axis.set_ylim([0, stats.max + stats.standard_deviation])

            axis.xaxis.set_visible(False)

            # if the data is greater than the mean + 1 stdev, it is highlighted in red

            print("bg start")
            print(y_values)
            bar_graph = axis.bar(range(len(y_values), 0, -1), y_values)
            print("bg end")

            print("making bar")
            for datum, bar, in zip(y_values, bar_graph):
                if datum > stats.mean * 2:
                    bar.set_color("red")
                else:
                    bar.set_color("blue")
            print("bar done")

            legend_text = "Min: " + str(stats.min) + ", "
            legend_text += "Max: " + str(stats.max) + "\n"
            legend_text += "Mean: " + str(stats.mean) + ", "
            legend_text += "Mode: " + str(stats.mode) + ", "
            legend_text += "Stdev: " + str(stats.standard_deviation)

            # draw the legend
            axis.text(0.025, 0.90, legend_text, verticalalignment='top', fontsize=10, transform=axis.transAxes, bbox=dict(boxstyle='square', facecolor='wheat', alpha=0.5))

            lowest = axis.get_position()
            final = axis

        final.set_xticks(x_value_strings)
        final.xaxis.set_visible(True)

        xticks = ticker.MaxNLocator(10)

        final.xaxis.set_major_locator(xticks)

        for label in final.get_xticklabels():
            label.set_rotation(15)

        # Draw the note
        figure.text(lowest.x0, (lowest.y0 - 0.08), "Note: " + self.note, horizontalalignment='left', verticalalignment='bottom')

        # save the plot
        if self.filename is not None:
            plot.savefig(self.filename)
        else:
            plot.savefig("output.png")

        print("rendered")

    def render_as_image(self, filename, as_process=True):
        self.filename = filename

        if as_process:
            render_process = Process(target=self.__run_matpotlib__)
            render_process.start()
            render_process.join()
        else:
            self.__run_matpotlib__()

    def render_as_pickle(self, pickle_path):
        with open(pickle_path, "wb") as file:
            pickle.dump(self, file)
            file.flush()


class TimeSeriesValue(object):

    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp


class TimeSeriesGraphSet(object):

    def __init__(self, name, unit, maxlen):
        """
        Rules:
        1. Impossible to have two datapoints at the same time
        :param name:
        :param unit:
        :param maxlen:
        """

        self.name = name
        self.unit = unit
        self.__values__ = []
        self.__timestamp_to_value__ = {}

    def add_value(self, value, timestamp):
        self.__values__.append(TimeSeriesValue(value, timestamp))
        self.__timestamp_to_value__[timestamp] = value

    def value_at_time(self, timestamp):
        return self.__timestamp_to_value__[timestamp]

    @property
    def values(self):
        return list(i.value for i in self.__values__)

    @property
    def timestamps(self):
        return self.__timestamp_to_value__.keys()

    @property
    def most_recent_value(self):
        try:
            return self.__values__[-1].value
        except KeyError:
            return None

    def __len__(self):
        return len(self.__values__)

    def __iter__(self):
        return iter(self.__values__)



class TimeSeriesGraphTable(object):

    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.__series_dict__ = {}

    def __iter__(self):
        return iter(self.__series_dict__.values())

    def __len__(self):
        return len(self.__series_dict__)

    def add_new_gset(self, name, unit):

        if name in self.__series_dict__:
            raise KeyError(name + " already in table")
        else:
            self.__series_dict__[name] = TimeSeriesGraphSet(name, unit, self.maxlen)

    def add_gset(self, gset):

        if gset.name in self.__series_dict__:
            raise KeyError(gset.name + " already in table")
        else:
            self.__series_dict__[gset.name] = gset

    def add_value(self, name, value, timestamp=None):

        if timestamp is None:
            timestamp = datetime.now()

        try:
            self.__series_dict__[name].add_value(value, timestamp)
        except KeyError:
            raise KeyError(name + " doesn't exist in the table")

    def __getitem__(self, item):
        return self.__series_dict__[item]

