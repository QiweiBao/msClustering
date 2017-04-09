import ClusteringCollection
import data_extract
import MethodListExtraction
import os
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


def dataExtract(path, pathflat, clu_method, clusters, plot_in_2D=True):
    global y_pred
    paths = data_extract.readfilelist(path)
    for Tobe_Cluster_dir, Flat_dir in zip(paths, pathflat):
        #read flat time proportion
        X = data_extract.fileread(Tobe_Cluster_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = data_extract.method_read(method_name_path)
        orderindex = data_extract.readmethodnames()
        X = data_extract.insertzero(X, method_list, orderindex)
        X = data_extract.deleteword(X)
        print "original number of methods: " + str(len(X))

        #read flat time. Do not need normalization.
        X_flat = data_extract.fileread(Flat_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = data_extract.method_read(method_name_path)
        orderindex = data_extract.readmethodnames()
        X_flat = data_extract.insertzero(X_flat, method_list, orderindex)
        X_flat = data_extract.deleteword(X_flat)
        X_flat = data_extract.reverse(X_flat, orderindex)

        # the second parameter is threshold
        # X = data_extract.removeSeldomUsingMethods(X, 0.5)

        print "number of methods after removing infrequent methods:" + str(len(X))
        X = data_extract.reverse(X, orderindex)
        X = data_extract.normalization(X)

        # using scikit to normalize
        # X = StandardScaler().fit_transform(X)

        #output dir for clustering result pictures
        dir_pieces = Tobe_Cluster_dir.split('/')
        png_name = dir_pieces[len(dir_pieces) - 1]
        png_name = png_name[:len(png_name) - 4] + ".png"
        pic_dir = Tobe_Cluster_dir[:len(Tobe_Cluster_dir) - len(dir_pieces[len(dir_pieces) - 1])] + "pics/"
        if not os.path.exists(pic_dir):
            os.mkdir(pic_dir)

        output_X(X, pic_dir, png_name[:len(png_name) - 10])

        pic_dir += png_name

        if clu_method is "Hierarchical":
            clu_Hierarchical(X, pic_dir)
        elif clu_method is "Kmeans":
            clu_Kmeans(X, pic_dir)
        elif clu_method is "DBSCAN":
            clu_DBSCAN(X, pic_dir,  plot_in_2D)
        elif clu_method is "Spectral":
            y_pred = clu_spectral(X, pic_dir, clusters, plot_in_2D)
        else:
            print "error"
            return



def output_X(X, pic_dir, file_name):
    path = pic_dir + "X" + file_name + ".txt"
    f = open(path, "w")
    for row in X:
        f.writelines("%s " % item for item in row)
        f.write('\n')
    f.close()


def clu_Hierarchical(X, pic_dir):
    # hierarchical clustering
    Cl_result = ClusteringCollection.HierarchicalCluster(X)
    cophenet = ClusteringCollection.CophenetEvaluate(Cl_result, X)
    print cophenet

    ClusteringCollection.drawHierarchical(Cl_result, pic_dir)


def clu_spectral(X, pic_dir, clusters, plot_in_2D):
    #TODO 
    y_pred = ClusteringCollection.Spectral_Cluster(X, pic_dir, clusters, plot_in_2D)
    X_flat = [] #matrix


def clu_Kmeans(X, pic_dir):
    # kmeans clustering
    ClusteringCollection.createKmeans(X, pic_dir)


def clu_DBSCAN(X, pic_dir, plot_in_2D):
    Cl_result = ClusteringCollection.DBSCAN(X, pic_dir, plot_in_2D)
    # ClusteringCollection.drawDBSCAN(Cl_result, pic_dir)


if __name__ == "__main__":
    # path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/"
    path = "/home/majunqi/research/result/test_automation/processed_data_largesize/"
    pathflat = "" #dir include time of flat
    # createMethodList(path)
    # choose clustering method
    # clu_method = "Hierarchical"
    # clu_method = "DBSCAN"
    # clu_method = "Kmeans"
    clu_method = "Spectral"
    clusters = 2
    #plot either in 2D or 3D
    twoD = False
    dataExtract(path, pathflat, clu_method, clusters, twoD)
