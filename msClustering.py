import msClustering
import data_extract
import MethodListExtraction

def createMethodList(path):
	#path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/" 
	pathwrite = path  + "MethodNameList.txt" 
	filenames = MethodListExtraction.readfilelist(path)
	method_list = MethodListExtraction.methodname(filenames)
	MethodListExtraction.writeMethodList(method_list, pathwrite)
	print "Method list created."

def dataExtract(path, clu_method):
    paths = data_extract.readfilelist(path)
    for Tobe_Cluster_dir in paths:
        X = data_extract.fileread(Tobe_Cluster_dir)
        method_name_path = path + "MethodNameList.txt"
        method_list = data_extract.method_read(method_name_path)
        orderindex = data_extract.readmethodnames()
        X = data_extract.insertzero(X, method_list, orderindex)
        X = data_extract.deleteword(X)
        print "original number of methods: " + str(len(X))

        #the second parameter is threshold

        X = data_extract.removeSeldomUsingMethods(X, 0.2)
        print "number of methods after removing infrequent methods:" + str(len(X))
        X = data_extract.reverse(X, orderindex)
        X = msClustering.normalization(X)

		dir_pieces = Tobe_Cluster_dir.split('/')
        png_name = dir_pieces[len(dir_pieces)-1]
        png_name = png_name[:len(png_name)-4] + ".png"
        pic_dir = Tobe_Cluster_dir[:len(Tobe_Cluster_dir) - len(dir_pieces[len(dir_pieces)-1])] + "pics/"
        if not os.path.exists(pic_dir):
            os.mkdir(pic_dir)
        pic_dir += png_name

        if clu_method is "Hierarchical":
        	clu_Hierarchical(X, pic_dir)
        elif clu_method is "Kmeans":
        	clu_Kmeans(X)
        

def clu_Hierarchical(X, pic_dir):
        # hierarchical clustering
        Cl_result = msClustering.HierarchicalCluster(X)
        cophenet = msClustering.CophenetEvaluate(Cl_result, X)
        print cophenet

        msClustering.drawHierarchical(Cl_result, pic_dir)

def clu_Kmeans(X):
        # kmeans clustering
        msClustering.createKmeans(X)

if __name__ == "__main__":
	path = "/Users/qiweibao/Code/Python/InputData/processed_data_largesize/" 
	createMethodList(path)
	#choose clustering method
	clu_method = "Hierarchical"
	dataExtract(path, clu_method) 
