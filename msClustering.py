import ClusteringCollection
import utils
import MethodListExtraction
import os
import linearRegression
import re
import sklearn
from sklearn.preprocessing import StandardScaler

y_pred = []


def createMethodList(path):
    # path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/"
    pathwrite = path + "MethodNameList.txt"
    filenames = MethodListExtraction.readfilelist(path)
    method_list = MethodListExtraction.methodname(filenames)
    MethodListExtraction.writeMethodList(method_list, pathwrite)
    print "Method list created."


def dataExtract(workspace, path, path_flat, path_pprof, clu_method, num_clusters, plot_in_2D=True, orderInSizeDir=None):
    global y_pred
    path = workspace + path
    path_flat = workspace + path_flat
    paths = utils.readfilelist(path)
    path_flats = utils.readfilelist(path_flat)
    for Tobe_Cluster_dir, Flat_dir in zip(paths, path_flats):
        # read flat time proportion
        X = utils.fileread(Tobe_Cluster_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = utils.method_read(method_name_path)
        orderindex = utils.readmethodnames()
        X = utils.insertzero(X, method_list, orderindex)
        X = utils.deleteword(X)
        print "original number of methods: " + str(len(X))

        # the second parameter is threshold
        # X = utils.removeSeldomUsingMethods(X, 0.3)

        # the second parameter is threshold
        # remove_idxes = utils.removeSeldomUsingMethods_byIdx(X, 0.2)
        # X = utils.remove_methods_byIdx(X, remove_idxes)

        print "number of methods after removing infrequent methods:" + str(len(X))
        X = utils.reverse(X, orderindex)
        X = utils.normalization(X)

        '''
        X_tmp = utils.reorder_matrix_size(X, orderInSizeDir)
        if X_tmp is None:
            print "Oh, shit, it's wrong"
            return
        else:
            X = X_tmp
        '''

        # using scikit to normalize
        # X = StandardScaler().fit_transform(X)

        # read flat time. Do not need normalization.
        X_flat = utils.fileread(Flat_dir)
        X_flat = utils.insertzero(X_flat, method_list, orderindex)
        X_flat = utils.deleteword(X_flat)

        # X_flat = utils.remove_methods_byIdx(X_flat, remove_idxes)

        X_flat = utils.reverse(X_flat, orderindex)

        '''
        X_tmp = utils.reorder_matrix_size(X_flat, orderInSizeDir)
        if X_tmp is None:
            print "Oh, shit, it's wrong"
            return
        else:
            X_flat = X_tmp
        '''


        '''
            TODO
            get version_name here
            '''
        pieces = Tobe_Cluster_dir.split('/')
        version_name = pieces[len(pieces) - 1]
        version_name = version_name[:len(version_name) - 4]
        # Y = utils.extract_totaltime_each(workspace + path_pprof + version_name + '/')

        # version_name_for_Y is used because the data is so big, i can't copy it from Mac to Linux.
        version_name_for_Y = Flat_dir.split('/')
        version_name_for_Y = version_name_for_Y[len(version_name_for_Y)-1]
        version_name_for_Y = version_name_for_Y[:len(version_name_for_Y)-4]
        Y = utils.extract_totaltime_each_measured('/Users/qiweibao/Downloads/users/jxm844/research/result/html_large1500/', version_name_for_Y)
        # Y = utils.extract_totaltime_each('/media/psf/Home/Downloads/test_automation_422/profdata_pfm_largesize_classified/'+version_name_for_Y+'/data/')

        # Y = utils.remove_methods_byIdx(Y, remove_idxes)

        '''
        Y_tmp = utils.reorder_matrix_size(Y, orderInSizeDir)
        if Y_tmp is None:
            print "Oh, shit, it's wrong"
            return
        else:
            Y = Y_tmp
        '''

        # output dir for clustering result pictures
        dir_pieces = Tobe_Cluster_dir.split('/')
        png_name = dir_pieces[len(dir_pieces) - 1]
        png_name = png_name[:len(png_name) - 4] + ".png"
        pic_dir = Tobe_Cluster_dir[:len(Tobe_Cluster_dir) - len(dir_pieces[len(dir_pieces) - 1])] + "output/"
        if not os.path.exists(pic_dir):
            os.mkdir(pic_dir)

        utils.output_matrix(X, pic_dir, png_name[:len(png_name) - 4] + "X")
        # utils.output_matrix(Y, pic_dir, png_name[:len(png_name) - 4] + "Y")
        outputdir = pic_dir + png_name[:len(png_name) - 4] + "Y.txt"
        MethodListExtraction.writeMethodList(Y, outputdir)

        pic_dir += png_name

        if clu_method is "Hierarchical":
            picdir = pic_dir[:len(pic_dir) - 4] + "hierarchical" + ".png"
            cluster_idx = clu_Hierarchical(X, pic_dir, picdir, num_clusters)
            split_data_from_cluster(cluster_idx, X_flat, Y, pic_dir)
        elif clu_method is "Kmeans":
            cluster_idx = clu_Kmeans(X, pic_dir, num_clusters)
            split_data_from_cluster(cluster_idx, X_flat, Y, pic_dir)
        elif clu_method is "DBSCAN":
            cluster_idx = clu_DBSCAN(X, pic_dir, plot_in_2D)
            split_data_from_cluster(cluster_idx, X_flat, Y, pic_dir)
        elif clu_method is "Spectral":
            cluster_idx = clu_spectral(X, pic_dir, num_clusters, plot_in_2D)
            split_data_from_cluster(cluster_idx, X_flat, Y, pic_dir)
            '''clusters = utils.cluster_mapping(cluster_idx, X_flat)
            total_times = utils.cluster_mapping(cluster_idx, Y)
            clusters_num = 1
            for cluster_X, total_time_Y in zip(clusters, total_times):
                # linear_regression(cluster_X, total_time_Y)
                utils.output_matrix(cluster_X, pic_dir[:len(pic_dir)-4], "_X"+str(clusters_num))
                # output_matrix(total_time_Y, pic_dir, "total_time_Y"+str(num_clusters))
                outputdir = pic_dir[:len(pic_dir)-4] + "_Y"+str(clusters_num) + ".txt"
                MethodListExtraction.writeMethodList(total_time_Y, outputdir)
                clusters_num += 1'''
        else:
            print "error"
            return


def split_data_from_cluster(cluster_idx, X_flat, Y, pic_dir):
    clusters = utils.cluster_mapping(cluster_idx, X_flat)
    total_times = utils.cluster_mapping(cluster_idx, Y)
    clusters_num = 1
    for cluster_X, total_time_Y in zip(clusters, total_times):
        # linear_regression(cluster_X, total_time_Y)
        utils.output_matrix(cluster_X, pic_dir[:len(pic_dir)-4], "_X"+str(clusters_num))
        # output_matrix(total_time_Y, pic_dir, "total_time_Y"+str(num_clusters))
        outputdir = pic_dir[:len(pic_dir)-4] + "_Y"+str(clusters_num) + ".txt"
        MethodListExtraction.writeMethodList(total_time_Y, outputdir)
        clusters_num += 1
    Clu_idx_dir = pic_dir[:len(pic_dir)-4] + "_idx" + ".txt"
    MethodListExtraction.writeMethodList(cluster_idx, Clu_idx_dir)

def linear_regression(X, Y):
    linearRegression.simpleEquation(X, Y)


def clu_Hierarchical(X, pic_dir, picdir, num_clusters):
    # hierarchical clustering
    Cl_result, cluster_idx = ClusteringCollection.HierarchicalCluster(X, num_clusters)
    cophenet = ClusteringCollection.CophenetEvaluate(Cl_result, X)
    print cophenet
    ClusteringCollection.drawHierarchical(Cl_result, picdir)
    ClusteringCollection.plotHierarchical(Cl_result, X, cluster_idx, pic_dir)
    return cluster_idx


def clu_spectral(X, pic_dir, num_clusters, plot_in_2D):
    cluster_idx = ClusteringCollection.Spectral_Cluster(X, pic_dir, num_clusters, plot_in_2D)
    return cluster_idx


def clu_Kmeans(X, pic_dir, num_clusters):
    # kmeans clustering
    cluster_idx = ClusteringCollection.createKmeans(X, num_clusters)
    ClusteringCollection.plotKmeans(X, cluster_idx, pic_dir)
    return cluster_idx


def clu_DBSCAN(X, pic_dir, plot_in_2D):
    cluster_idx = ClusteringCollection.DBSCAN(X, pic_dir, plot_in_2D)
    # ClusteringCollection.drawDBSCAN(Cl_result, pic_dir)
    return cluster_idx


if __name__ == "__main__":
    # path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/"

    # workspace = "/home/majunqi/research/result/test_test/"
    workspace = "/Users/qiweibao/Downloads/test_automation_test_422/"
    # workspace = "/media/psf/Home/Downloads/test_automation_422/"

    path = "processed_data_largesize/"
    path_flat = "processed_data_largesize_flat/"
    path_pprof = "profdata_pfm_largesize_classified/"

    orderInSizeDir = "/Users/qiweibao/Code/Python/order_in_size.txt"
    # orderInSizeDir = "/home/majunqi/Desktop/order_in_size.txt"


    # if method list already exists, comment out this line
    # createMethodList(workspace + path)

    # choose clustering method
    # clu_method = "Hierarchical"
    # clu_method = "DBSCAN"
    clu_method = "Kmeans"
    # clu_method = "Spectral"
    clusters = 2
    # plot either in 2D or 3D
    twoD = False
    dataExtract(workspace, path, path_flat, path_pprof, clu_method, clusters, twoD, orderInSizeDir)
