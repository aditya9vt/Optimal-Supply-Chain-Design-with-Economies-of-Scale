import operator
import os
import pandas as pd
import numpy as np
import sys
import _1_GlobalVarDefs as g
import _0_MainCode as mc
import time
import csv
import copy
from mip import Model, xsum, minimize, BINARY
from collections import OrderedDict

def _5_FindBranchingIndex(x):    
    # NOTE: The other required inputs for this step are the lower (g.L..) and upper (g.U..) limits 
    # on the variables which should be updated after the step of extracting the node 
    # with lowest lower bound value. 
    
    index0, index1, index2 = 'temp', -1, -1
    # index0: represent the type of variable with worst approximation
    # index1: first index of variable type index0
    # index2: first index of variable type index0 (it is only valid in case 
    #                                             index0 is production or hanling variable)
    
    ################ Find approximation errors only in case of positive flows
    # 1. At plants    
    err_p_max, k_max  = -100, -1
    for k in range(g.V1):
        if x[g.pos_v1[k]] > 0.00001:
            f_Lp   = g.hp[k]*pow(g.Lp[k], g.lambdaP)
            f_Up   = g.hp[k]*pow(g.Up[k], g.lambdaP)
            mp     = (f_Up - f_Lp) / (g.Up[k]- g.Lp[k])
            constp = f_Lp - g.mp[k]*g.Lp[k]
            err_p  = g.hp[k] * pow(x[g.pos_v1[k]], g.lambdaP) - (mp * x[g.pos_v1[k]] + constp)  
            #print("plant: %d, slope: %.2f, err_p: %.2f; solution value: %.2f; upper limit: %.2f" % (k, mp, err_p, x[g.pos_v1[k]], g.Up[k]))
            if err_p > err_p_max:
                err_p_max = err_p
                k_max = k                
        
    # 2. At DCs
    err_d_max, j_max  = -100, -1
    for j in range(g.V2):
        if x[g.pos_v2[j]] > 0.00001:
            f_Ld   = g.hd[j]*pow(g.Ld[j], g.lambdaD)
            f_Ud   = g.hd[j]*pow(g.Ud[j], g.lambdaD)
            md     = (f_Ud - f_Ld)/(g.Ud[j] - g.Ld[j])
            constd = f_Ld - g.md[j]*g.Ld[j]
            err_d = g.hd[j] * pow(x[g.pos_v2[j]], g.lambdaD) - (md * x[g.pos_v2[j]] + constd)
            #print("DC: %d, slope: %.2f, err_p: %.2f; solution value: %.2f; upper limit: %.2f" % (j, md, err_d, x[g.pos_v2[j]], g.Ud[j]))
            if err_d > err_d_max:
                err_d_max = err_d
                j_max = j
                
    # 3. On Arcs from Plants to DC
    err_arc1_max, arc1_k_max, arc1_j_max = -100, -1, -1
    for k in range(g.V1):
        for j in range(g.V2):
            if x[g.pos_x1[k][j]] > 0.00001:
                f_L1   = g.h1[k][j]*pow(g.L1[k][j], g.lambda1)
                f_U1   = g.h1[k][j]*pow(g.U1[k][j], g.lambda1)
                m1     = (f_U1 - f_L1) / (g.U1[k][j] - g.L1[k][j])
                const1 = f_L1 - g.m1[k][j] * g.L1[k][j]
                err_arc1 = g.h1[k][j]*pow(x[g.pos_x1[k][j]], g.lambda1) - (m1*x[g.pos_x1[k][j]] + const1)
                #print("plant: %d, DC: %d, slope: %.2f, err_p: %.2f; solution value: %.2f; upper limit: %.2f" % (k, j, m1, err_arc1, x[g.pos_x1[k][j]], g.U1[k][j]))
                if err_arc1 > err_arc1_max:
                    err_arc1_max = err_arc1
                    arc1_k_max = k
                    arc1_j_max = j
                    
    # 4. On Arcs from DCs to Customers
    err_arc2_max, arc2_j_max, arc2_i_max = -100, -1, -1
    for j in range(g.V2):
        for i in range(g.I):
            if x[g.pos_x2[j][i]] > 0:
                f_L2   = g.h2[j][i] * pow(g.L2[j][i], g.lambda2)
                f_U2   = g.h2[j][i] * pow(g.U2[j][i], g.lambda2)
                m2     = (f_U2 - f_L2) / (g.U2[j][i] - g.L2[j][i])  
                const2 = f_L2 - g.m2[j][i] * g.L2[j][i]
                err_arc2 = g.h2[j][i]*pow(x[g.pos_x2[j][i]], g.lambda2) - (m2*x[g.pos_x2[j][i]] + const2)
                #print("DC: %d, Cust: %d, slope: %.2f, err_p: %.2f; solution value: %.2f; upper limit: %.2f" % (j, i, m2, err_arc2, x[g.pos_x2[j][i]], g.U2[j][i]))
                if err_arc2 > err_arc2_max:
                    err_arc2_max = err_arc2
                    arc2_j_max = j
                    arc2_i_max = i
                    
    ################ Final index
    err_max = -100
    if err_max < err_p_max:
        err_max = err_p_max
        index0, index1, index2 = 'production', k_max, -1
    
    if err_max < err_d_max:
        err_max = err_d_max
        index0, index1, index2 = 'handling', j_max, -1
    
    if err_max < err_arc1_max:
        err_max = err_arc1_max
        index0, index1, index2 = 'flowarc1', arc1_k_max, arc1_j_max
    
    if err_max < err_arc2_max:
        err_max = err_arc2_max
        index0, index1, index2 = 'flowarc2', arc2_j_max, arc2_i_max
    
    print("maximum approximation error: %.0f" % err_max)
    print("Max err cat: %s; index1: %d; index2: %d" % (index0, index1, index2))
        
    time_Elapsed_RN, ObjValueRN = 0.0, 0.0
    start = time.time()
            
    
    # print("Solution with cost {} found.".format(mRN.objective_value))
    end = time.time() 
    time_Elapsed_RN = end - start

    
    return index0, index1, index2
