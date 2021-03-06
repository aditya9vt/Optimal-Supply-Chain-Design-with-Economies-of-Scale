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

def _4_SolveRootNode():
    
    time_Elapsed_RN, ObjValueRN = 0.0, 0.0
    start = time.time()
            
    ################ Find Slope and Constant     
    # 1. At plants
    for k in range(g.V1):
        f_Lp        = g.hp[k]*pow(g.Lp[k], g.lambdaP)
        f_Up        = g.hp[k]*pow(g.Up[k], g.lambdaP)
        g.mp[k]     = (f_Up - f_Lp) / (g.Up[k]- g.Lp[k])
        g.constp[k] = f_Lp - g.mp[k]*g.Lp[k]
            
    # 2. At DCs
    for j in range(g.V2):
        f_Ld        = g.hd[j]*pow(g.Ld[j], g.lambdaD)
        f_Ud        = g.hd[j]*pow(g.Ud[j], g.lambdaD)
        g.md[j]     = (f_Ud - f_Ld)/(g.Ud[j] - g.Ld[j])
        g.constd[j] = f_Ld - g.md[j]*g.Ld[j]
        
    # 3. On Arcs from Plants to DC
    for k in range(g.V1):
        for j in range(g.V2):
            f_L1           = g.h1[k][j]*pow(g.L1[k][j], g.lambda1)
            f_U1           = g.h1[k][j]*pow(g.U1[k][j], g.lambda1)
            g.m1[k][j]     = (f_U1 - f_L1) / (g.U1[k][j] - g.L1[k][j])
            g.const1[k][j] = f_L1 - g.m1[k][j] * g.L1[k][j]            

    # 4. On Arcs from DCs to Customers
    for j in range(g.V2):
        for i in range(g.I):
            f_L2           = g.h2[j][i] * pow(g.L2[j][i], g.lambda2)
            f_U2           = g.h2[j][i] * pow(g.U2[j][i], g.lambda2)
            g.m2[j][i]     = (f_U2 - f_L2) / (g.U2[j][i] - g.L2[j][i])  
            g.const2[j][i] = f_L2 - g.m2[j][i] * g.L2[j][i]
    
    ################ Mathematical model at Root Node
    # Create model
    mRN = Model("RootNode")
    
    # Define variables
    z1 = [mRN.add_var(var_type=BINARY) for j in range(g.V1)]
    v1 = [mRN.add_var() for j in range(g.V1)]
    z2 = [mRN.add_var(var_type=BINARY) for j in range(g.V2)]
    v2 = [mRN.add_var() for j in range(g.V2)]
    x1 = {(k, j): mRN.add_var() for k in range(g.V1) for j in range(g.V2)}
    x2 = {(j, i): mRN.add_var() for j in range(g.V2) for i in range(g.I)}
            
    # Set Objective Function
    mRN.objective = minimize(
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
        mRN.add_constr(xsum(x1[k, j] for j in range(g.V2)) <= g.Cp[k] * z1[k])
    
    # 2. Production volume at plants
    for k in range(g.V1):
        mRN += xsum(x1[k, j] for j in range(g.V2)) == v1[k]
    
    # 3. Handling Capacity at DCs
    for j in range(g.V2):
        mRN += xsum(x1[k, j] for k in range(g.V1)) <= g.Cd[j] * z2[j]
        
    # 4. Handling Volume at DCs
    for j in range(g.V2):
        mRN += xsum(x1[k, j] for k in range(g.V1)) <= v2[j]
        
    # 5. Flow balance at DCs
    for j in range(g.V2):
        mRN += xsum(x1[k, j] for k in range(g.V1)) == xsum(x2[j, i] for i in range(g.I))
    
    # 6. Demand Satifaction
    for i in range(g.I):
        mRN += xsum(x2[j, i] for j in range(g.V2)) == g.D[i]
    
    # 7. Limits on concave functions
    for k in range(g.V1):
        mRN += v1[k] >= g.Lp[k] 
        mRN += v1[k] <= g.Up[k]
    
    for j in range(g.V2):
        mRN += v2[j] >= g.Ld[j] 
        mRN += v2[j] <= g.Ud[j]
    
    for k in range(g.V1):
        for j in range(g.V2):
            mRN += x1[k, j] >= g.L1[k][j]
            mRN += x1[k, j] <= g.U1[k][j]
    
    for j in range(g.V2):
        for i in range(g.I):
            mRN += x2[j, i] >= g.L2[j][i]
            mRN += x2[j, i] <= g.U2[j][i]
    
    mRN.optimize()
    
    # print("Solution with cost {} found.".format(mRN.objective_value))
    end = time.time() 
    time_Elapsed_RN = end - start

    LB_RN = mRN.objective_value
    
    # Extract solution at the current node and Find Upper Bound at Root Node
    S = g.V1 + g.V1 + g.V1 * g.V2 + g.V2 + g.V2 + g.V2 * g.I    
    SolVector = [-1.0 for s in range(S)]
    
    UB_RN = 0.0
    
    for k in range(g.V1):
        UB_RN += z1[k].x * g.Fp[k]
        SolVector[g.pos_z1[k]] = z1[k].x
        
        
    for k in range(g.V1):
        UB_RN += g.hp[k] * pow(v1[k].x, g.lambdaP)
        SolVector[g.pos_v1[k]] = v1[k].x
        
    for k in range(g.V1):
        for j in range(g.V2):
            UB_RN += g.h1[k][j] * pow(x1[k, j].x, g.lambda1)
            SolVector[g.pos_x1[k][j]] = x1[k, j].x
            
    for j in range(g.V2):
        UB_RN += z2[j].x * g.Fd[j]
        SolVector[g.pos_z2[j]] = z2[j].x
        
    for j in range(g.V2):
        UB_RN += g.hd[j] * pow(v2[j].x, g.lambdaD)
        SolVector[g.pos_v2[j]] = v2[j].x
        
    for j in range(g.V2):
        for i in range(g.I):
            UB_RN += g.h2[j][i] * pow(x2[j, i].x, g.lambda2)
            SolVector[g.pos_x2[j][i]] = x2[j, i].x
    
    print("Lower and Upper Bounds At Root Node are: %.2f and %.2f"% (LB_RN, UB_RN))
    print("Elapsed Time ROOT NODE (secs): %.2f" % (time_Elapsed_RN))    
    
    return LB_RN, UB_RN, SolVector
