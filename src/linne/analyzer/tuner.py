import os
import re

from linne.analyzer.sound import Table as SoundTable
from linne.analyzer.sound import Sound
from linne.analyzer.dataset import Dataset
import numpy

class Stat:
    def __init__(self):
        self.sound = None
        self.data = []
        self.threshold = None       
        
    def read(self,sample):
        # Read from sample
        filter = self.sound.filter
        if  filter == "RMS":
            self.data.append(sample.rms)
        elif filter == "SV":
            self.data.append(sample.variance)
        else:
            print "Unknown filter type : %s" % filter
            
    def calc(self):
        # Calculate the new threshold value
        self.threshold = numpy.average(numpy.array(self.data))
        return self.threshold

table = SoundTable()

# For collect the phonetic data from sampling file
stat = {}

print "Reading sound.csv..."
table.open("sound.csv")
print "%d of record(s) read." % len(table)

for sound in table:
    item = Stat()
    item.sound = sound
    item.threshold = sound.threshold
    stat[sound.phonetic] = item

datasetList = []

cwd = os.getcwd()
files = os.listdir(cwd)

for f in files:
    filename , ext = os.path.splitext(f)
    if ext == ".wav":
        print "Reading %s dataset..." % filename
        dataset = Dataset(filename)
        try:
            dataset.open()
            datasetList.append(dataset)
        except IOError,e:
            print e

# Collecting threshold value from dataset
for dataset in datasetList:
    sampleList = dataset.phoneticList()
    for sample in sampleList:
        if not stat.has_key(sample.phonetic):
            print "Warning! Phonetic not found in sound.csv: %s" % sample.phonetic
            continue
        stat[sample.phonetic].read(sample)

print "Calculate the new threshold value..."

for key in stat:
    s = stat[key]
    old = s.threshold
    new = s.calc()
    if old != new:
        print "%s : %f -> %f" % (key , old,new)
        s.sound.threshold = s.threshold

print "Saving to sound.csv..."
table.save("sound.csv")
print "Done"
