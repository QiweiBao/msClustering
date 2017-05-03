import os
import glob
from pylab import *
from scipy.spatial.distance import pdist
import re

def VersionsMapping(path, version1, version2, reverse):
    v1_path = open(path + version1 + "_idx.txt", "r")
    v2_path = open(path + version2 + "_idx.txt", "r")
    v1, v2 = [], []
    for v1_idx in v1_path.read():
        for idx in v1_idx:
            if idx != '\n':
                v1.append(idx)
    for v2_idx in v2_path.read():
        for idx in v2_idx:
            if idx != '\n':
                v2.append(idx)
    res_c1, res_c2, res_imm_c12, res_imm_c21= [], [], [], []
    len_res = len(v1)
    print len_res
    i = 0
    s, l = '1', '2'
    if reverse is True:
        while (i < len_res):
            if v1[i] == s and v2[i] == s:
                res_imm_c12.append(i)
            elif v1[i] == l  and v2[i] == l :
                res_imm_c21.append(i)
            elif v1[i] == s and v2[i] == l :
                res_c1.append(i)
            else:
                res_c2.append(i)
            i += 1
    else:
        while (i < len_res):
            if v1[i] == s and v2[i] == s:
                res_c1.append(i)
            elif v1[i] == l  and v2[i] == l :
                res_c2.append(i)
            elif v1[i] == s and v2[i] == l :
                res_imm_c12.append(i)
            else:
                res_imm_c21.append(i)
            i += 1

    return res_c1, res_c2, res_imm_c12, res_imm_c21


def output_matrix(X, dir, filename):
    path = dir + "difference/" + filename + ".txt"
    if os.path.isfile(path):
        os.remove(path)

    output = open(path, 'wb+')
    writeline = ""
    for line in X:
        line = str(line)
        output.write(line)
        output.write("\t")
    output.close()

if __name__ == "__main__":
    workspace = "/Users/qiweibao/Downloads/test_automation_test_422/"
    path = "processed_data_largesize/output_hierarchical/"
    version1 = "9a0020664ed21d9488647c1ae77194a1cce493ec"
    version2 = "488ab6d9fc7a87aae254f5ae13929d73f253b6f6"
    reverse = False
    res_c1, res_c2, res_imm_c12, res_imm_c21 = VersionsMapping(workspace + path, version1, version2, reverse)
    output_matrix(res_c1, workspace + path, "C1")
    output_matrix(res_c2, workspace + path, "C2")
    output_matrix(res_imm_c12, workspace + path, "C12")
    output_matrix(res_imm_c21, workspace + path, "C21")