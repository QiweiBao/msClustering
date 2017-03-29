'''
--------------------------------------
    Created by Qiwei Bao on 03/22/2017
--------------------------------------
'''

from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
import re
from pylab import *
from scipy.cluster.vq import *
import os

order = []
method = []
method_list = []
method_list_tmp = []


# Get list of names included in the dir
def readfilelist(path):
    files = os.listdir(path)
    # print files
    res = []
    for filename in files:
        if ("MethodNameList.txt" not in filename) and (".txt" in filename):
            filename = path + filename
            res.append(filename)
    return res


# read method names from each file
def readmethod(dir):
    file = open(dir)
    while True:
        read = file.readline()
        if not read:
            break
        else:
            method = read.split()
            for data in method:
                if re.search('.*([a-zA-Z]+).*', data):
                    method_list_tmp.append(data)
    method_list_tmp.sort()
    return method_list_tmp


# Get list of method names from all files.
def methodname(filenames):
    index = 0
    method_init = []
    file = open(filenames[0])
    while True:
        read = file.readline()
        if not read:
            break
        else:
            method = read.split()
            for data in method:
                if re.search('.*([a-zA-Z]+).*', data):
                    method_init.append(data)
    method_init.sort()
    for dir in range(1, len(filenames)):
        readmethod(filenames[dir])
        method_init = merge(method_init, method_list_tmp)
    return method_init


# merge 2 methods
def merge(m1, m2):
    for m in range(len(m1)):
        for n in range(len(m2)):
            if m1[m] != m2[n] and m2[n] not in m1:
                if m1[m] > m2[n]:
                    m1.insert(m, m2[n])
    return m1


# Write method list into a text.
def writeMethodList(method_list, pathwrite):
    clearMethodList(pathwrite)
    output = open(pathwrite, 'wb+')
    for i in method_list:
        output.write(str(i))
        output.write("\n")
    output.close()


# clear method name list before write
def clearMethodList(pathwrite):
    if os.path.isfile(pathwrite):
        os.remove(pathwrite)


def main():
    path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/"
    pathwrite = path + "MethodNameList.txt"
    filenames = readfilelist(path)
    method_list = methodname(filenames)
    writeMethodList(method_list, pathwrite)


if __name__ == "__main__":
    main()
