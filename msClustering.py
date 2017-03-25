from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
import re
from pylab import *
from scipy.cluster.vq import *
import seaborn as sns; sns.set()

#read data
def fileread(dirname):
	tmp = []
	X = []
	file = open(dirname)
	Indexmark = ""
	while True:
		read = file.readline()
		if not read:
			break
		else:
			method = read.split()
			for data in method:
				'''if  re.search('.*([a-zA-Z]+).*', data):
					continue'''
				if Indexmark == "":
					Indexmark = data
					continue
				else:
					tmp.append(float(data))
			X.append(tmp)
			tmp = []
			Indexmark = ""
	X = np.array(X)
	return X

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
			data = (data - mindata) / delta
			tmp.append(data)
		res.append(tmp)
		tmp = []
	res = np.array(res)
	return res


#Draw scatter with first 2 columns
def drawScatter(a, b):
	plt.figure(figsize=(25, 10))
	plt.scatter(a, b)
	plt.show()

#Hierarchical clustering
def HierarchicalCluster(X):
	Cl_result = linkage(X, 'ward')
	return Cl_result

#Use cophenet evaluating clustering performance
def CophenetEvaluate(Cl_result, X):
	co, coph_dists = cophenet(Cl_result, pdist(X))
	return co

#show distances on picture
def fancy_dendrogram(*args, **kwargs):
	max_d = kwargs.pop('max_d', None)
	if max_d and 'color_threshold' not in kwargs:
		kwargs['color_threshold'] = max_d
	annotate_above = kwargs.pop('annotate_above', 0)

	ddata = dendrogram(*args, **kwargs)

	if not kwargs.get('no_plot', False):
		plt.title('Hierarchical Clustering Dendrogram (truncated)')
		plt.xlabel('sample index or (cluster size)')
		plt.ylabel('distance')
		for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
			x = 0.5 * sum(i[1:3])
			y = d[1]
			if y > annotate_above:
				plt.plot(x, y, 'o', c=c)
				plt.annotate("%.3g" % y, (x, y), xytext=(0, -5), textcoords='offset points', va='top', ha='center')
		if max_d:
			plt.axhline(y=max_d, c='k')
	return ddata

#Draw hierarchical result
def drawHierarchical(Cl_result):
	plt.figure(figsize=(50, 10))
	plt.title('Hierarchical Clustering Dendrogram')
	plt.xlabel('functions')
	plt.ylabel('distance')
	#original
	#dendrogram(Cl_result, leaf_rotation=90., leaf_font_size=8.)
	#truncated for 12 times
	#dendrogram(Cl_result, truncate_mode='lastp', p=12, leaf_rotation=90., leaf_font_size=12., show_contracted=True)
	#show distance
	fancy_dendrogram(Cl_result, truncate_mode='lastp', p=30, leaf_rotation=90., leaf_font_size=12., show_contracted=True, annotate_above=10)
	plt.show()

#Calculate mean and deviation to describe the input metrix
def MeanandDev(X):
	tmpsum, avgtmp, times, dev = 0.0, 0, 0, 0
	sca_line = []
	Sca = []
	for line in X:
		for data in line:
			data = float(data)
			tmpsum = data + tmpsum
			times = 1 + times
		avgtmp = float(tmpsum) / float(times) #Calculate the average
		times = 0
		sca_line.append(avgtmp)

		for data in line:
			data = float(data)
			dev = dev + (data - avgtmp) * (data - avgtmp)
			times += 1
		dev = float(dev) / times
		dev = dev ** 0.5
		times = 0
		sca_line.append(dev)

		Sca.append(sca_line)
		sca_line = []
		tmpsum, avgtmp, times, dev = 0.0, 0, 0, 0
	return Sca

#K-means algorithm, inputs are features and number of clusters to take
def createKmeans(X):
	centroids, variance = kmeans(X, 3)
	code, distance = vq(X, centroids)
	figure()
	ndx = where(code==0)[0]
	plot(X[ndx,0], X[ndx,1],'*')
	ndx = where(code==1)[0]
	plot(X[ndx, 0],X[ndx,1], 'r.')
	ndx = where(code==2)[0]
	plot(X[ndx, 0],X[ndx,1], 'y.')
	plot(centroids[:, 0],centroids[:, 1], 'go')
	axis('off')
	show()
	
#use seaborn to show result visualize.
def clu_heatmap(X):
	g = sns.clustermap(X, standard_scale=1)
	sns.plt.show()

if __name__ == "__main__":
	dirname = "./Inputdata/data.txt"
	X = fileread(dirname)
	X = normalization(X)
	Cl_result = HierarchicalCluster(X)
	cophenet = CophenetEvaluate(Cl_result, X)
	print cophenet
	drawHierarchical(Cl_result)
	#createKmeans(X)
	#Sca = MeanandDev(X)
	#drawScatter(zip(*Sca)[0], zip(*Sca)[1])
