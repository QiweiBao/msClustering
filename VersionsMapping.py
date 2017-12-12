limport os
import glob
from pylab import *
from scipy.spatial.distance import pdist
import re

def VersionsMapping(path, version1, version2, reverse, s, l):
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


def output_matrix(X, dir, filename, vers_name):
    path = dir + "difference-" + vers_name + "/";
    if not os.path.exists(path):
        os.mkdir(path)
    path = path + filename + ".txt"
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
    path = "processed_data_largesize/output_spectral/"
    version1 = "79f11c1a32806d2d3b2b48002c6423280da96f0a"
    version2 = "05bc443e7e516b9767f6220284d75e2e2a704c1a"
    vers_name = version1[:5]+'-'+version2[:5]
    reverse = False
    s, l = '0', '1'
    res_c1, res_c2, res_imm_c12, res_imm_c21 = VersionsMapping(workspace + path, version1, version2, reverse, s, l)
    output_matrix(res_c1, workspace + path, "C1", vers_name)
    output_matrix(res_c2, workspace + path, "C2", vers_name)
    output_matrix(res_imm_c12, workspace + path, "C12", vers_name)
    output_matrix(res_imm_c21, workspace + path, "C21", vers_name)