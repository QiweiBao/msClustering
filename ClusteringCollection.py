from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
import re
from pylab import *
from scipy.cluster.vq import *
import seaborn as sns;
import time

from sklearn import cluster
from sklearn.metrics import consensus_score
from mpl_toolkits.mplot3d import Axes3D

sns.set()


# read data
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

# Draw scatter with first 2 columns
def drawScatter(a, b):
    plt.figure(figsize=(25, 10))
    plt.scatter(a, b)
    plt.show()


# calculate mean for each character (used in PCA)
def zeroMean(X):
    meanVal = np.mean(X, axis=0)
    newData = X - meanVal
    return newData, meanVal


# PCA
def pca(X, n):
    newData, meanVal = zeroMean(X)

    # Calculate the Covariance matrix. If rowvar is not zero, each column means one sample; else, each line is one sample.
    # Here one line is one HTML, so rowvar is 0
    # return is in ndarray format
    covMat = np.cov(newData, rowvar=0)

    eigVals, eigVects = np.linalg.eig(np.mat(covMat))
    eigValIndice = np.argsort(eigVals)
    n_eigValIndice = eigValIndice[-1: - (n + 1): -1]

    # get index of the largest n eigenvalues
    n_eigVect = eigVects[:, n_eigValIndice]
    lowDDataMat = newData * n_eigVect
    # refactoring data
    reconMat = (lowDDataMat * n_eigVect.T) + meanVal
    return lowDDataMat, reconMat


# Hierarchical clustering
def HierarchicalCluster(X):
    Cl_result = linkage(X, 'ward')
    return Cl_result


# Use cophenet evaluating clustering performance
def CophenetEvaluate(Cl_result, X):
    co, coph_dists = cophenet(Cl_result, pdist(X))
    return co


# show distances on picture
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


# Draw hierarchical result
def drawHierarchical(Cl_result, picdir):
    plt.figure(figsize=(50, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('functions')
    plt.ylabel('distance')
    # original
    dendrogram(Cl_result, leaf_rotation=90., leaf_font_size=8.)
    # truncated for 12 times
    # dendrogram(Cl_result, truncate_mode='lastp', p=12, leaf_rotation=90., leaf_font_size=12., show_contracted=True)
    # show distance
    # fancy_dendrogram(Cl_result, truncate_mode='lastp', p=30, leaf_rotation=90., leaf_font_size=12., show_contracted=True, annotate_above=10)
    # show picture after drawing
    # plt.show()
    savefig(picdir)


# Calculate mean and deviation to describe the input metrix
def MeanandDev(X):
    tmpsum, avgtmp, times, dev = 0.0, 0, 0, 0
    sca_line = []
    Sca = []
    for line in X:
        for data in line:
            data = float(data)
            tmpsum = data + tmpsum
            times = 1 + times
        avgtmp = float(tmpsum) / float(times)  # Calculate the average
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


# K-means algorithm, inputs are features and number of clusters to take
def createKmeans(X, picdir, clusters):
    centroids, variance = kmeans(X, clusters)
    code, distance = vq(X, centroids)
    figure()
    ndx = where(code == 0)[0]
    plot(X[ndx, 0], X[ndx, 1], '*')
    ndx = where(code == 1)[0]
    plot(X[ndx, 0], X[ndx, 1], 'r.')
    ndx = where(code == 2)[0]
    plot(X[ndx, 0], X[ndx, 1], 'y.')
    plot(centroids[:, 0], centroids[:, 1], 'go')
    axis('off')
    # show()
    savefig(picdir)


# use seaborn to show result visualize.
def Heatmap(X):
    g = sns.clustermap(X, standard_scale=1)
    sns.plt.show()


def Spectral_Cluster(X, pic_dir, clusters, plot_in_2D):
    colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
    colors = np.hstack([colors] * 20)
    Cl_result = cluster.SpectralClustering(n_clusters=clusters,
                                           eigen_solver='arpack',
                                           affinity="nearest_neighbors").fit(X)
    # print Cl_result
    if hasattr(Cl_result, 'labels_'):
        y_pred = Cl_result.labels_.astype(np.int)
    else:
        y_pred = Cl_result.predict(X)

    clustering_algorithms = [Cl_result]
    # plot
    # plt.subplot(4, len(clustering_algorithms), 1)
    # if i_dataset == 0:
    #     plt.title(name, size=18)

    if plot_in_2D:
        # use pca
        lowDDataMat, reconMat = pca(X, 2)
        #plt.scatter(X[:, 0], X[:, 1], color=colors[y_pred].tolist())
        plt.scatter(lowDDataMat[:, 0].ravel().tolist()[0], lowDDataMat[:, 1].ravel().tolist()[0], color = colors[y_pred].tolist())
        if hasattr(Cl_result, 'cluster_centers_'):
            centers = Cl_result.cluster_centers_
            center_colors = colors[:len(centers)]
            print centers
            plt.scatter(centers[:, 2], centers[:, 4], s = 100, c = center_colors)
    else :
        #3 D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        lowDDataMat, reconMat = pca(X, 3)
        ax.scatter(lowDDataMat[:, 0].ravel().tolist()[0], lowDDataMat[:, 1].ravel().tolist()[0], lowDDataMat[:, 2].ravel().tolist()[0], color = colors[y_pred].tolist(), marker = 'o')
        if hasattr(Cl_result, 'cluster_centers_'):
            centers = Cl_result.cluster_centers_
            center_colors = colors[:len(centers)]
            print centers
            ax.scatter(centers[:, 2], centers[:, 3], centers[:, 4], color = center_colors)
        # print centers[:, 0], centers[:, 1]
    # plt.xlim(-0.5, 0.5)
    # plt.ylim(-0.5, 0.5)
    # plt.xticks(())
    # plt.yticks(())
    # plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'),
    #          transform=plt.gca().transAxes, size=15,
    #          horizontalalignment='right')
    # plot_num += 1
    savefig(pic_dir)
    # plt.show()
    return y_pred

def DBSCAN(X, pic_dir, plot_in_2D):
    db = cluster.DBSCAN(eps=0.3, min_samples=10).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    times = 1
    if plot_in_2D is False:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = 'k'

        class_member_mask = (labels == k)

        if plot_in_2D is True:
            lowDDataMat, reconMat = pca(X, 2)
            xy = lowDDataMat[class_member_mask & core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=14, label = times)

            xy = lowDDataMat[class_member_mask & ~core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=6,)
            times += 1
        else:
            lowDDataMat, reconMat = pca(X, 3)
            xy = lowDDataMat[class_member_mask & core_samples_mask]
            ax.scatter(xy[:, 0].ravel().tolist()[0], xy[:, 1].ravel().tolist()[0], xy[:, 2].ravel().tolist()[0], color=col, marker = 'o', label = times)

            xy = lowDDataMat[class_member_mask & ~core_samples_mask]
            ax.scatter(xy[:, 0].ravel().tolist()[0], xy[:, 1].ravel().tolist()[0], xy[:, 2].ravel().tolist()[0], color=col, marker = 'o')

            times += 1
        plt.legend(loc='upper left')
    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()

    # savefig(pic_dir)
    # print('Estimated number of clusters: %d' % n_clusters_)
    # print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    # print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    # print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    # print("Adjusted Rand Index: %0.3f"
    #       % metrics.adjusted_rand_score(labels_true, labels))
    # print("Adjusted Mutual Information: %0.3f"
    #       % metrics.adjusted_mutual_info_score(labels_true, labels))
    # print("Silhouette Coefficient: %0.3f"
    #       % metrics.silhouette_score(X, labels))

if __name__ == "__main__":
    '''dirname = "/Users/qiweibao/Code/Python/Inputdata/data.txt"
    X = fileread(dirname)
    #X = normalization(X)
    outputdir = "/Users/qiweibao/Code/Python/Output.png"
    Spectral_Cluster(X, outputdir, 3, True)

    #use pca
    lowDDataMat,reconMat = pca(X,2)
    drawScatter(lowDDataMat[:, 0].ravel().tolist()[0], lowDDataMat[:, 1].ravel().tolist()[0])
    
    Cl_result = HierarchicalCluster(X)
    cophenet = CophenetEvaluate(Cl_result, X)
    print cophenet
    drawHierarchical(Cl_result)'''
# createKmeans(X)
# Sca = MeanandDev(X)
# drawScatter(zip(*Sca)[0], zip(*Sca)[1])