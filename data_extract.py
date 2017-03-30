from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
import re
from pylab import *
from scipy.cluster.vq import *
import msClustering

order = []
method = []
method_list = []
method_list_tmp = []


# read data
def fileread(dirname):
    tmp = []
    X = []
    file = open(dirname)
    while True:
        read = file.readline()
        if not read:
            break
        elif not re.search('.*([a-zA-Z]+).*', read):
            for s in read.split():
                order.append(s)
        else:
            method = read.split()
            for data in method:
                tmp.append(data)
            X.append(tmp)
            tmp = []
    return X


# get list of all the method names
def method_read(dirname):
    file = open(dirname)
    res = []
    while True:
        read = file.readline()
        if not read:
            break
        elif re.search('.*([a-zA-Z]+).*', read):
            method = read.split()
            for data in method:
                if re.search('.*([a-zA-Z]+).*', data):
                    res.append(data)
    return res


# If one method exist in the list of method names but not in one version, data of this method in this HTML file should be all zero.
def insertzero(X, method_list):
    tmp = []
    res = []
    zero = []
    for init in range(len(method_list)):
        X_tmp_arr = np.array(X)
        X_tmp_arr = [row[:1] for row in X_tmp_arr]
        if method_list[init] not in X_tmp_arr:
            # form "0" for 50 times
            for z in xrange(50):
                zero.append('0')
            res.append(zero)
            zero = []
        else:
            index = X_tmp_arr.index(method_list[init])
            tmp = X[index]
            res.append(tmp)
    return res


# Axisymmetric reverse the matrix so that each line represent to one HTML webpage.
def reverse(X):
    tmp = []
    res = []
    empty = 0
    for init in range(0, 1574):
        index = order.index(str(init))
        for i in X:
            tmp.append(float(i[index])) if index < len(i) else tmp.append(float(empty))
        res.append(tmp)
        tmp = []
    res = np.array(res)
    return res


# delete method names
def deleteword(X):
    # todo
    res, tmp = [], []
    for line in X:
        for data in line:
            if not re.search('.*([a-zA-Z]+).*', data):
                tmp.append(data)
        res.append(tmp)
        tmp = []
    res = np.array(res)
    return res


if __name__ == "__main__":
    Tobe_Cluster_dir = "/home/majunqi/research/result/test_automation/processed_data_largesize/0bae9c6be8569347f743d07138d0afcb32ceebd6.txt"
    X = fileread(Tobe_Cluster_dir)
    method_name_path = "/home/majunqi/research/result/test_automation/processed_data_largesize/MethodNameList.txt"
    method_list = method_read(method_name_path)

    X = insertzero(X, method_list)
    X = deleteword(X)
    X = reverse(X)
    Cl_result = msClustering.HierarchicalCluster(X)
    cophenet = msClustering.CophenetEvaluate(Cl_result, X)
    print cophenet
    msClustering.drawHierarchical(Cl_result)

    #msClustering.createKmeans(X)