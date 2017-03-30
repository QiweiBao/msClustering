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
import msClustering
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
def insertzero(X, method_list, orderindex):
    tmp = []
    res = []
    zero = []
    start = orderindex[0]
    end = orderindex[1]
    for init in range(len(method_list)):
        X_tmp_arr = np.array(X)
        X_tmp_arr = [row[:1] for row in X_tmp_arr]
        if method_list[init] not in X_tmp_arr:
            # form "0" for (end - start + 1) times
            for z in xrange(end - start + 1):
                zero.append('0')
            res.append(zero)
            zero = []
        else:
            index = X_tmp_arr.index(method_list[init])
            # tmp = [X[i][index] for i in range(14)]
            tmp = X[index]
            res.append(tmp)
    return res


# Axisymmetric reverse the matrix so that each line represent to one HTML webpage.
def reverse(X, orderindex):
    tmp = []
    res = []
    start = orderindex[0]
    end = orderindex[1]
    for init in range(start, end):
        index = order.index(str(init))
        for i in X:
            tmp.append(float(i[index]))
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


# names in list order
def readmethodnames():
    minorder, maxorder = 0, 0
    for i in order:
        if int(i) < minorder:
            minorder = int(i)
        if int(i) > maxorder:
            maxorder = int(i)
    res = []
    res.append(minorder)
    res.append(maxorder)
    return res

def removeSeldomUsingMethods(X, threshold):
    # row is method
    # column is html
    new_X = []
    for method in X:
        total = 0
        num = 0
        for html in method:
            total = total + float(html)
            num += 1
        # this can be set automatically
        if total/num >= threshold:
            new_X.append(method)
    return new_X


if __name__ == "__main__":
    path = "/home/majunqi/research/result/test_automation/processed_data_largesize/"
    paths = readfilelist(path)
    for Tobe_Cluster_dir in paths:
        X = fileread(Tobe_Cluster_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = method_read(method_name_path)
        orderindex = readmethodnames()
        X = insertzero(X, method_list, orderindex)
        X = deleteword(X)
        print "original number of methods: " + str(len(X))
        X = removeSeldomUsingMethods(X, 0.2)
        print "number of methods after removing infrequent methods:" + str(len(X))
        X = reverse(X, orderindex)
        # hierarchical clustering
        Cl_result = msClustering.HierarchicalCluster(X)
        cophenet = msClustering.CophenetEvaluate(Cl_result, X)
        print cophenet

        dir_pieces = Tobe_Cluster_dir.split('/')
        png_name = dir_pieces[len(dir_pieces)-1]
        png_name = png_name[:len(png_name)-4] + ".png"
        pic_dir = Tobe_Cluster_dir[:len(Tobe_Cluster_dir) - len(dir_pieces[len(dir_pieces)-1])] + "pics/"
        if not os.path.exists(pic_dir):
            os.mkdir(pic_dir)
        print pic_dir+png_name
        msClustering.drawHierarchical(Cl_result, pic_dir+png_name)

        # kmeans clustering
        '''msClustering.createKmeans(X)'''
