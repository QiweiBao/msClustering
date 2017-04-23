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
import ClusteringCollection
import os
import decimal

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


# Normalize data. Output should be within 0~1.
def normalization(X):
    maxdata = 0.0
    mindata = 0.0
    res, tmp = [], []
    for line in X:
        for data in line:
            if data > maxdata:
                maxdata = data
            if data < mindata:
                mindata = data
    delta = maxdata - mindata
    for line in X:
        for data in line:
            # data = str(round((data - mindata) / delta, 4))
            data = (data - mindata) / delta
            data = "{0:.4f}".format(data)
            tmp.append(float(data))
        res.append(tmp)
        tmp = []
    res = np.array(res)
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
    end = orderindex[1] + 1
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
    # X = X.tolist()
    res, tmp = [], []
    for line in X:
        for data in line:
            data = str(data)
            if not re.search('.*([a-zA-Z]+).*', data):
                if ('.' not in data) or (data.split('.')[1] == None):
                    data = float(data)
                    tmp.append(data)
                else:
                    # truncate 7 numbers after decimal point
                    data = data.split('.')[0] + '.' + data.split('.')[1][:7]
                    data = float(data)
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


# old, maybe not useful
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
        if total / num >= threshold:
            new_X.append(method)
    return new_X


def removeSeldomUsingMethods_byIdx(X, threshold):
    # row is method
    # column is html
    remove_idxes = []
    idx = 0
    for method in X:
        total = 0
        num = 0
        for html in method:
            total = total + float(html)
            num += 1
        if total / num >= threshold:
            remove_idxes.append(idx)
        idx += 1
    return remove_idxes


def remove_methods_byIdx(X, remove_idxes):
    new_X = []
    idx_now = 0
    for idx in remove_idxes:
        if idx_now != idx:
            new_X.append(X[idx_now])
        idx_now += 1

    return new_X


def extract_totaltime_each(path):
    files_dir = os.listdir(path)
    # files_dir = sorted(files_dir)
    # files_dir.sort()
    files_dir = natural_sort(files_dir)
    Y = list()
    for file_dir in files_dir:
        file = open(path+file_dir, "r")
        line_one = file.readline()
        line_one = line_one.split()
        total_time = line_one[0]
        # #   unit is ms
        # if total_time.__contains__('ms'):
        #     total_time = total_time[: len(total_time) - 2]
        #     total_time = long(total_time) / 1000
        #     total_time = str(total_time)
        # # unit is s
        # else:
        #     total_time = total_time[: len(total_time) - 1]
        Y.append(total_time)

    return Y


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


# map original data into small clusters based on index
'''
For now, the clusters number is 2.
If the clusters number is not fixed, bug remains.
'''

'''
def cluster_mapping(index_list, X):
    clu_one = list()
    clu_two = list()
    start = index_list[0]
    for i in index_list:
        if i < start:
            start = i
    for index in range(0, len(index_list)):
        if index_list[index] == start:
            clu_one.append(X[index])
        elif index_list[index] == start + 1:
            clu_two.append(X[index])

    clusters = list()
    clusters.append(clu_one)
    clusters.append(clu_two)
    return clusters
'''


def cluster_mapping(index_list, X):
    clu_tmp = []
    cluster = []
    # start = index_list[0]
    # end = index_list[0]
    start = -1
    end = -1
    for i in index_list:
        if (i != -1) and ((i < start) or (start is -1)):
            start = i
        if i > end:
            end = i
    for clu_number in range(start, end + 1):
        for index in range(0, len(index_list)):
            if index_list[index] == clu_number:
                clu_tmp.append(X[index])
        cluster.append(clu_tmp)
        clu_tmp = []

    return cluster


def output_matrix(X, pic_dir, file_name):
    path = pic_dir + file_name + ".txt"
    '''
    f = open(path, "w")
    for row in X:
        # f.writelines("%s " % item for item in row)
        f.write(row)
        f.write('\n')
    f.close()
    '''
    clearMethodList(path)
    output = open(path, 'wb+')
    writeline = ""
    for line in X:
        for i in line:
            writeline += str(i)
            writeline += "  "
        output.write(writeline)
        output.write("\n")
        writeline = ""
    output.close()


# clear method name list before write
def clearMethodList(pathwrite):
    if os.path.isfile(pathwrite):
        os.remove(pathwrite)


'''
sample input:

if __name__ == "__main__":
    dir1 = "/home/majunqi/research/cc-sample-largesize1500/1"
    dir2 = "/home/majunqi/research/cc-sample-largesize1500/2"
    dir3 = "/home/majunqi/research/cc-sample-largesize1500/3"
    dir4 = "/home/majunqi/research/cc-sample-largesize1500/4"
    dir5 = "/home/majunqi/research/cc-sample-largesize1500/5"
    dir6 = "/home/majunqi/research/cc-sample-largesize1500/6"

    dirs = [dir1, dir2,dir3,dir4,dir5,dir6]
    paths = sortfile_size(dirs, True)
    f = open('/home/majunqi/Desktop/order_size.txt', 'w')
    for path in paths:
        f.write(path+'\n')
    f.close()

'''


# reverse = True: sort file from large to small
# reverse = False: sort file from small to large

def sortfile_size(dirnames, reverse=False):
    """ Return list of file paths in directory sorted by file size """

    # Get list of files
    filepaths = []
    for dirname in dirnames:
        for basename in os.listdir(dirname):
            filename = os.path.join(dirname, basename)
            if os.path.isfile(filename):
                filepaths.append(filename)

    # Re-populate list with filename, size tuples
    for i in xrange(len(filepaths)):
        filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))

    # Sort list by file size
    # If reverse=True sort from largest to smallest
    # If reverse=False sort from smallest to largest
    filepaths.sort(key=lambda filename: filename[1], reverse=reverse)

    # Re-populate list with just filenames
    for i in xrange(len(filepaths)):
        filepaths[i] = filepaths[i][0]

    i = 0
    names = []
    for filename in filepaths:
        pieces = filename.split('/')
        filename = pieces[len(pieces) - 1]

        names.append(filename[:len(filename) - 5])
        i += 1
    return names


# Re-order metrix by html size.
def reorder_matrix_size(X, orderInSizeDir):
    htmlSizeOrders = open(orderInSizeDir)
    htmlSizeOrder = []
    while True:
        read = htmlSizeOrders.readline()
        if not read:
            break
        else:
            htmlSizeOrder.append(int(read))
    if len(X) != len(htmlSizeOrder):
        print "number of order doesn't match matrix lines"
        return
    htmlIndexBySize = sorted(range(len(htmlSizeOrder)), key=lambda k: htmlSizeOrder[k])
    res = []
    for index in htmlIndexBySize:
        res.append(X[index])
    res = np.array(res)
    return res


if __name__ == "__main__":
    '''path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/"
    Tobe_Cluster_dir = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/f4f82d64b802e98101542a270d2b41afd667a9e7.txt"
    #paths = readfilelist(path)
    X = fileread(Tobe_Cluster_dir)
    method_name_path = path + "MethodNameList.txt"
    method_list = method_read(method_name_path)
    orderindex = readmethodnames()
    X = insertzero(X, method_list, orderindex)
    X = deleteword(X)
    print "original number of methods: " + str(len(X))

    #the second parameter is threshold

    X = removeSeldomUsingMethods(X, 0.2)
    print "number of methods after removing infrequent methods:" + str(len(X))
    X = reverse(X, orderindex)
    X = ClusteringCollection.normalization(X)

    for Tobe_Cluster_dir in paths:
        X = fileread(Tobe_Cluster_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = method_read(method_name_path)
        orderindex = readmethodnames()
        X = insertzero(X, method_list, orderindex)
        X = deleteword(X)
        print "original number of methods: " + str(len(X))

        #the second parameter is threshold

        X = removeSeldomUsingMethods(X, 0.2)
        print "number of methods after removing infrequent methods:" + str(len(X))
        X = reverse(X, orderindex)
        X = msClustering.normalization(X)

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
        # msClustering.createKmeans(X)
'''
