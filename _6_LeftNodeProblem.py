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

def _6_SolveLeftNode(index0, index1, index2):
    
    time_Elapsed_RN, ObjValueRN = 0.0, 0.0
    start = time.time()
    
    ################ Limits at the current node with the limits of node with lowest LB
    # 1. At plants
    g.Lp_CN = copy.deepcopy(g.Lp_LowestLB)
    g.Up_CN = copy.deepcopy(g.Up_LowestLB)
        
    # 2. At DCs
    g.Ld_CN = copy.deepcopy(g.Ld_LowestLB)
    g.Ud_CN = copy.deepcopy(g.Ud_LowestLB)
        
    # 3. On Arcs from Plants to DC
    g.L1_CN = copy.deepcopy(g.L1_LowestLB)
    g.U1_CN = copy.deepcopy(g.U1_LowestLB)
    
    # 4. On Arcs from DCs to Customers
    g.L2_CN = copy.deepcopy(g.L2_LowestLB)
    g.U2_CN = copy.deepcopy(g.U2_LowestLB)
    
    ################ Update upper limit for the variable with worst approximation
    if index0 == 'production':
        for k in range(g.V1):
            if index1 == k:
                print("Old Upper limit: %.2f" % (g.Up_CN[k]))
                g.Up_CN[k] = g.xLowestLB[g.pos_v1[k]]
                #print("Solution at plant %d is %.2f" % (k, g.xLowestLB[g.pos_v1[k]]))
                print("New Upper limit: %.2f" % (g.Up_CN[k]))
                #print("Max dev at plant: %d" % (k))
                #print("Upper limit set to %.2f" % (g.Up_CN[k]))
                #print("pos of the plant is %d" % (g.pos_v1[k]))                
                #input("press enter")    
                
    if index0 == 'handling':
        for j in range(g.V2):
            if index1 == j:
                g.Ud[j] = g.xLowestLB[g.pos_v2[j]]
                
    if index0 == 'flowarc1':
        for k in range(g.V1):
            if index1 == k:
                for j in range(g.V2):
                    if index2 == j:
                        g.U1_CN[k][j] = g.xLowestLB[g.pos_x1[k][j]]
    
    if index0 == 'flowarc2':    
        for j in range(g.V2):
            if index1 == j:
                for i in range(g.I):
                    if index2 == i:
                        g.U2_CN[j][i] = g.xLowestLB[g.pos_x2[j][i]]
                        
    ################ Find Slope and Constant     
    ConstantValue = 0.0
    # 1. At plants
    for k in range(g.V1):
        f_Lp        = g.hp[k]*pow(g.Lp_CN[k], g.lambdaP)
        f_Up        = g.hp[k]*pow(g.Up_CN[k], g.lambdaP)
        g.mp[k]     = (f_Up - f_Lp) / (g.Up_CN[k]- g.Lp_CN[k])
        g.constp[k] = f_Lp - g.mp[k]*g.Lp_CN[k]        
        ConstantValue = ConstantValue + g.constp[k]
            
    # 2. At DCs
    for j in range(g.V2):
        f_Ld        = g.hd[j]*pow(g.Ld_CN[j], g.lambdaD)
        f_Ud        = g.hd[j]*pow(g.Ud_CN[j], g.lambdaD)
        g.md[j]     = (f_Ud - f_Ld)/(g.Ud_CN[j] - g.Ld_CN[j])
        g.constd[j] = f_Ld - g.md[j]*g.Ld_CN[j]
        ConstantValue = ConstantValue + g.constd[j]
        
    # 3. On Arcs from Plants to DC
    for k in range(g.V1):
        for j in range(g.V2):
            f_L1           = g.h1[k][j]*pow(g.L1_CN[k][j], g.lambda1)
            f_U1           = g.h1[k][j]*pow(g.U1_CN[k][j], g.lambda1)
            g.m1[k][j]     = (f_U1 - f_L1) / (g.U1_CN[k][j] - g.L1_CN[k][j])
            g.const1[k][j] = f_L1 - g.m1[k][j] * g.L1_CN[k][j]            
            ConstantValue = ConstantValue + g.const1[k][j]
            
    # 4. On Arcs from DCs to Customers
    for j in range(g.V2):
        for i in range(g.I):
            f_L2           = g.h2[j][i] * pow(g.L2_CN[j][i], g.lambda2)
            f_U2           = g.h2[j][i] * pow(g.U2_CN[j][i], g.lambda2)
            g.m2[j][i]     = (f_U2 - f_L2) / (g.U2_CN[j][i] - g.L2_CN[j][i])  
            g.const2[j][i] = f_L2 - g.m2[j][i] * g.L2_CN[j][i]
            ConstantValue = ConstantValue + g.const2[j][i] 
            
    ################ Mathematical model at Left Node
    # Create model
    mLN = Model("RootNode")
    
    # Define variables
    z1 = [mLN.add_var(var_type=BINARY) for j in range(g.V1)]
    v1 = [mLN.add_var() for j in range(g.V1)]
    z2 = [mLN.add_var(var_type=BINARY) for j in range(g.V2)]
    v2 = [mLN.add_var() for j in range(g.V2)]
    x1 = {(k, j): mLN.add_var() for k in range(g.V1) for j in range(g.V2)}
    x2 = {(j, i): mLN.add_var() for j in range(g.V2) for i in range(g.I)}
            
    # Set Objective Function
    mLN.objective = minimize(
        xsum(g.Fp[k] * z1[k] for k in range(g.V1)) + 
        xsum(g.Fd[j] * z2[j] for j in range(g.V2)) +
        xsum(g.mp[k] * v1[k] for k in range(g.V1)) + 
        xsum(g.md[j] * v2[j] for j in range(g.V2)) +
        xsum(g.m1[k][j] * x1[k, j] for k in range(g.V1) for j in range(g.V2)) + 
        xsum(g.m2[j][i] * x2[j, i] for j in range(g.V2) for i in range(g.I))
        )
        
    # Set Constraints
    # 1. Production Capacity at Plants
    for k in range(g.V1):
        mLN.add_constr(xsum(x1[k, j] for j in range(g.V2)) <= g.Cp[k] * z1[k])
    
    # 2. Production volume at plants
    for k in range(g.V1):
        mLN += xsum(x1[k, j] for j in range(g.V2)) == v1[k]
    
    # 3. Handling Capacity at DCs
    for j in range(g.V2):
        mLN += xsum(x1[k, j] for k in range(g.V1)) <= g.Cd[j] * z2[j]
        
    # 4. Handling Volume at DCs
    for j in range(g.V2):
        mLN += xsum(x1[k, j] for k in range(g.V1)) <= v2[j]
        
    # 5. Flow balance at DCs
    for j in range(g.V2):
        mLN += xsum(x1[k, j] for k in range(g.V1)) == xsum(x2[j, i] for i in range(g.I))
    
    # 6. Demand Satifaction
    for i in range(g.I):
        mLN += xsum(x2[j, i] for j in range(g.V2)) == g.D[i]
    
    # 7. Limits on concave functions
    for k in range(g.V1):
        mLN += v1[k] >= g.Lp_CN[k] 
        mLN += v1[k] <= g.Up_CN[k]
    
    for j in range(g.V2):
        mLN += v2[j] >= g.Ld_CN[j] 
        mLN += v2[j] <= g.Ud_CN[j]
    
    for k in range(g.V1):
        for j in range(g.V2):
            mLN += x1[k, j] >= g.L1_CN[k][j]
            mLN += x1[k, j] <= g.U1_CN[k][j]
    
    for j in range(g.V2):
        for i in range(g.I):
            mLN += x2[j, i] >= g.L2_CN[j][i]
            mLN += x2[j, i] <= g.U2_CN[j][i]
    
    mLN.optimize()
    
    # print("Solution with cost {} found.".format(mLN.objective_value))
    end = time.time() 
    time_Elapsed_RN = end - start

    LB_LN = mLN.objective_value
    #LB_LN = LB_LN + ConstantValue
    
    # Extract solution at the current node and Find Upper Bound at Root Node
    S = g.V1 + g.V1 + g.V1 * g.V2 + g.V2 + g.V2 + g.V2 * g.I    
    SolVector = [-1.0 for s in range(S)]
    
    UB_LN = 0.0
    
    for k in range(g.V1):
        UB_LN += z1[k].x * g.Fp[k]
        SolVector[g.pos_z1[k]] = z1[k].x
        
        
    for k in range(g.V1):
        UB_LN += g.hp[k] * pow(v1[k].x, g.lambdaP)
        SolVector[g.pos_v1[k]] = v1[k].x
        
    for k in range(g.V1):
        for j in range(g.V2):
            UB_LN += g.h1[k][j] * pow(x1[k, j].x, g.lambda1)
            SolVector[g.pos_x1[k][j]] = x1[k, j].x
            
    for j in range(g.V2):
        UB_LN += z2[j].x * g.Fd[j]
        SolVector[g.pos_z2[j]] = z2[j].x
        
    for j in range(g.V2):
        UB_LN += g.hd[j] * pow(v2[j].x, g.lambdaD)
        SolVector[g.pos_v2[j]] = v2[j].x
        
    for j in range(g.V2):
        for i in range(g.I):
            UB_LN += g.h2[j][i] * pow(x2[j, i].x, g.lambda2)
            SolVector[g.pos_x2[j][i]] = x2[j, i].x
    
    print("Lower and Upper Bounds At Left Node are: %.2f and %.2f"% (LB_LN, UB_LN))
    print("Constant Value: %.2f" % (ConstantValue))
    #print("Elapsed Time ROOT NODE (secs): %.2f" % (time_Elapsed_RN))    
    #input('press enter')
    return LB_LN, UB_LN, SolVector
