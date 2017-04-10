import ClusteringCollection
import data_extract
import MethodListExtraction
import os
import linearRegression
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


def dataExtract(workspace, path, path_flat, path_pprof, clu_method, clusters, plot_in_2D=True):
    global y_pred
    path = workspace + path
    path_flat = workspace + path_flat
    paths = data_extract.readfilelist(path)
    path_flats = data_extract.readfilelist(path_flat)
    for Tobe_Cluster_dir, Flat_dir in zip(paths, path_flats):
        # read flat time proportion
        X = data_extract.fileread(Tobe_Cluster_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = data_extract.method_read(method_name_path)
        orderindex = data_extract.readmethodnames()
        X = data_extract.insertzero(X, method_list, orderindex)
        X = data_extract.deleteword(X)
        print "original number of methods: " + str(len(X))

        # the second parameter is threshold
        # X = data_extract.removeSeldomUsingMethods(X, 0.5)

        print "number of methods after removing infrequent methods:" + str(len(X))
        X = data_extract.reverse(X, orderindex)
        X = data_extract.normalization(X)

        # using scikit to normalize
        # X = StandardScaler().fit_transform(X)

        # read flat time. Do not need normalization.
        X_flat = data_extract.fileread(Flat_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = data_extract.method_read(method_name_path)
        orderindex = data_extract.readmethodnames()
        X_flat = data_extract.insertzero(X_flat, method_list, orderindex)
        X_flat = data_extract.deleteword(X_flat)
        X_flat = data_extract.reverse(X_flat, orderindex)

        '''
            TODO
            get version_name here
            '''
        pieces = Tobe_Cluster_dir.split('/')
        version_name = pieces[len(pieces)-1]
        version_name = version_name[:len(version_name)-4]
        Y = extract_totaltime_each(workspace+path_pprof+version_name+'/')

        # output dir for clustering result pictures
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
            clu_DBSCAN(X, pic_dir, plot_in_2D)
        elif clu_method is "Spectral":
            y_pred = clu_spectral(X, pic_dir, clusters, plot_in_2D)
            clusters = extract_everycluster_data(y_pred, X_flat)

            for cluster_X in clusters:
                linear_regression(cluster_X, Y)
        else:
            print "error"
            return


def extract_totaltime_each(path):
    files_dir = os.listdir(path)
    sorted(files_dir)
    Y = list()
    for file_dir in files_dir:
        file = open(path+file_dir, "r")
        line_one = file.readline()
        line_one = line_one.split()
        total_time = line_one[0]
        if total_time.__contains__('ms'):
            total_time = total_time[: len(total_time) - 2]
            total_time = long(total_time) / 1000
            total_time = str(total_time)
        else:
            total_time = total_time[: len(total_time) - 1]
        Y.append(total_time)

    return Y


def linear_regression(X, Y):
    linearRegression.simpleEquation(X, Y)


def extract_everycluster_data(index_list, X_flat):
    clu_one = list()
    clu_two = list()
    for index in index_list:
        if index == 0:
            clu_one.append(X_flat[index])
        elif index == 1:
            clu_two.append(X_flat[index])

    clusters = list()
    clusters.append(clu_one)
    clusters.append(clu_two)
    return clusters


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
    # TODO
    y_pred = ClusteringCollection.Spectral_Cluster(X, pic_dir, clusters, plot_in_2D)
    return y_pred


def clu_Kmeans(X, pic_dir):
    # kmeans clustering
    ClusteringCollection.createKmeans(X, pic_dir)


def clu_DBSCAN(X, pic_dir, plot_in_2D):
    Cl_result = ClusteringCollection.DBSCAN(X, pic_dir, plot_in_2D)
    # ClusteringCollection.drawDBSCAN(Cl_result, pic_dir)


if __name__ == "__main__":
    # path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/"
    workspace = "/home/majunqi/research/result/test_automation_test/"
    path = "processed_data_largesize/"
    path_flat = "processed_data_largesize_flat/"
    path_pprof = "profdata_pfm_largesize_classified/"

    # if method list already exists, comment out this line
    # createMethodList(path)

    # choose clustering method
    # clu_method = "Hierarchical"
    # clu_method = "DBSCAN"
    # clu_method = "Kmeans"
    clu_method = "Spectral"
    clusters = 2
    # plot either in 2D or 3D
    twoD = False
    dataExtract(workspace, path, path_flat, path_pprof, clu_method, clusters, twoD)
