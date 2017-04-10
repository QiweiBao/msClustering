import numpy as np

def simpleEquation(X, y):
	X = map(list, zip(*X))
	trans = np.column_stack(X + [[1] * len(X[0])])
	res = np.linalg.lstsq(trans,y)[0]
	print res