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
'''dir0 = "./Inputdata/05bc443e7e516b9767f6220284d75e2e2a704c1a.txt"
dir1 = "./Inputdata/0bae9c6be8569347f743d07138d0afcb32ceebd6.txt"
dir2 = "./Inputdata/2702de3370e40c30b4dfc3b5d81981c3564e1d2f.txt"
dir3 = "./Inputdata/28747b348493ecb174e710f802b8ab1e1b806ca2.txt"
dir4 = "./Inputdata/3116d69c332f3f2a8ae7020fdd997cdba81f7854.txt"
dir5 = "./Inputdata/488ab6d9fc7a87aae254f5ae13929d73f253b6f6.txt"
dir6 = "./Inputdata/4d9265aca864e88505fed1ffdee9ed0d22b92abd.txt"
dir7 = "./Inputdata/567e3e3050d01c08ea02bf4865faaa6fb42bf64f.txt"
dir8 = "./Inputdata/591b40a08e64e079d1977db6dce5d28c21f8bf7b.txt"
dir9 = "./Inputdata/79f11c1a32806d2d3b2b48002c6423280da96f0a.txt"
dir10 = "./Inputdata/9a0020664ed21d9488647c1ae77194a1cce493ec.txt"
dir11 = "./Inputdata/b1bd32bf60d9f64d071f970fc90ed0b6f2c8e6ae.txt"
dir12 = "./Inputdata/dc53d700f53c9b925fc6084ba38cb16c7a880fee.txt"
dir13 = "./Inputdata/f4f82d64b802e98101542a270d2b41afd667a9e7.txt"'''

#read data
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

#get list of all the method names
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

#If one method exist in the list of method names but not in one version, data of this method in this HTML file should be all zero.
def insertzero(X, method_list):
	tmp = []
	res = []
	zero = []
	for init in range(len(method_list)):
		X_tmp_arr = np.array(X)
		X_tmp_arr = [row[:1] for row in X_tmp_arr]
		if method_list[init] not in X_tmp_arr:
			#form "0" for 50 times
			for z in xrange(50):
				zero.append('0')
			res.append(zero)
			zero = []
		else:
			index = X_tmp_arr.index(method_list[init])
			#tmp = [X[i][index] for i in range(14)]
			tmp = X[index]
			res.append(tmp)
	return res

#Axisymmetric reverse the matrix so that each line represent to one HTML webpage.
def reverse(X):
	tmp = []
	res = []
	for init in range(61, 71):
		index = order.index(str(init))
		for i in X:
			tmp.append(float(i[index]))
		res.append(tmp)
		tmp = []
	res = np.array(res)
	return res

#delete method names
def deleteword(X):
	#todo
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
	Tobe_Cluster_dir = "./Inputdata/processed_data_largesize/3116d69c332f3f2a8ae7020fdd997cdba81f7854.txt"
	X = fileread(Tobe_Cluster_dir)
	method_name_path = "./InputData/processed_data_largesize/MethodNameList.txt" 
	method_list = method_read(method_name_path)
	
	X = insertzero(X, method_list)
	X = deleteword(X)
	X = reverse(X)
	Cl_result = msClustering.HierarchicalCluster(X)
	cophenet = msClustering.CophenetEvaluate(Cl_result, X)
	print cophenet
	msClustering.drawHierarchical(Cl_result)
