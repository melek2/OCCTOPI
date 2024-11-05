import warnings

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.transforms
import numpy
import scipy
import time
import csv
import math
import pandas
import plotly

warnings.simplefilter(action='ignore', category=FutureWarning)

def dateFmt(str):
    #time.strptime converts the csv's text timestamp into a python datetime object
    #time.mktime converts that into seconds since the unix epoch
    #if you want to use datetime objects instead of epoch, remove the outer function
    return time.mktime(time.strptime(str, '%Y-%m-%d %H:%M:%S'))

def loadFile(path):
    with open(path, 'rt', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        time = []
        val = []
        for row in reader:
            if row[0] != "time":
                time.append(dateFmt(row[0]))
                val.append(int(row[1])/1000) # /1000 to convert from mW to W
        return [time, val]

# loads each of the csvs into a pair of arrays
# printer[0] is an array of unix epoch time for each datapoint
# printer[1] is the value of the datapoint in watts
printer = loadFile('data/printer-data.csv')
water = loadFile('data/water-data.csv')
# time is in seconds since unix epoch


# print out some characterizable data for each dataset
def characterize(data):
    # data min, max, average?
    ch = {}

    # hack
    noZeroArray = []
    for i in data[1]:
        if i != 0:
            noZeroArray.append(i)

    ch["min"] = numpy.min(noZeroArray)
    ch["max"] = numpy.max(noZeroArray)
    ch["avg"] = numpy.average(noZeroArray)

    ch["std"] = numpy.std(noZeroArray)

    print("Min Power: " + str(ch["min"]))
    print("Max Power: " + str(ch["max"]))
    print("Avg Power: " + str(ch["avg"]))
    print("Std Deviation: " + str(ch["std"]))

    # find every time the data goes above the standard deviation, and measure
    # the gap between each of those times, and add it to the gaps array

    # the goal is to recognize how periodic the data is based on how consistent
    # the gap times are

    # todo: change counter from # of datapoints to amount of time passed
    gaps = []
    counter = 0
    for i in range(len(data[1])):
        #loop through all data, if data is greater than standard deviation, then
        if (data[1][i] > ch["std"]):
            # if counter is 0 it means the last data point was also greater than standard deviation,
            # there's no need to add a 0 to the gaps, just skip it
            if counter > 0:
                gaps.append(counter)
                counter = 0
        else:
            # if this datapoint isn't above std dev, just add 1 to the counter to measure the distance to the next point that is above std dev
            counter += 1

    ch["gap-std"] = 1/numpy.std(gaps)
    print("Periodicity: " + str(ch["gap-std"]))
    #characteristics["gaps"] = gaps

    return ch

binCount = 1000
maxValue = 1000 # 100,000 mW
# convert the input data of power over time to a new graph which is
# a measure of how long was spent at each power level
def convertToProbability(data):
    distribution = numpy.zeros(binCount)
    totalCounts = len(data[1])

    for w in data[1]:
        wR = round(w/maxValue*binCount)
        if wR >= binCount:
            wR = binCount - 1
        if wR != 0:
            distribution[wR] += 1

    for i in range(len(distribution)):
        distribution[i] = distribution[i] / totalCounts

    return distribution

print("Printer")
characterize(printer)

pDF = pandas.read_csv("data/printer-data.csv")
pDF2 = pDF.loc[(pDF != 0).all(axis=1)]
pDF2.iloc[:,int(1)] = pDF2.iloc[:,1].div(int(1000.0))
print("")
print(pDF2.describe())
print("")
print("")
print("Water Dispenser")
characterize(water)
print("")
pDF = pandas.read_csv("data/water-data.csv")
pDF2 = pDF.loc[(pDF != 0).all(axis=1)]
pDF2.iloc[:,int(1)] = pDF2.iloc[:,1].div(int(1000))
print(pDF2.describe())

# TODO: this function just returns an array representing a histogram of how long the data spent at each power level
# for this data to actually be usable, it should be clustered into some scalar values, with something like GMM,
# and feed that into the characterize() function's output

printerDist = convertToProbability(printer)
waterDist = convertToProbability(water)


# plot the data
fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(2,2)

ax1.plot(water[1])
ax1.set_xlabel("Time")
ax1.set_ylabel("Power (W)")
ax1.axhline(y=numpy.std(water[1]), color='g', linestyle='-')
ax1.text(
        0.0, 1.0, "Water Dispenser", transform=(
            ax1.transAxes + matplotlib.transforms.ScaledTranslation(0, +7/72, fig.dpi_scale_trans)),
        fontsize='medium', va='bottom', fontfamily='sans serif')

ax2.plot(numpy.linspace(0, maxValue, binCount),waterDist)
ax2.set_xlabel("Power (W)")
ax2.set_ylabel("Density")


ax3.plot(printer[1])
ax3.set_xlabel("Time")
ax3.set_ylabel("Power (W)")
ax3.axhline(y=numpy.std(printer[1]), color='g', linestyle='-')
ax3.text(
        0.0, 1.0, "Printer", transform=(
            ax3.transAxes + matplotlib.transforms.ScaledTranslation(0, +7/72, fig.dpi_scale_trans)),
        fontsize='medium', va='bottom', fontfamily='sans serif')



ax4.plot(numpy.linspace(0, maxValue, binCount), printerDist)
ax4.set_xlabel("Power (W)")
ax4.set_ylabel("Density")
plt.show()
