import operator
import os
import pandas as pd
import numpy as np
import sys
import _1_GlobalVarDefs as g
import _0_MainCode as mc
import time
import csv

from mip import Model, xsum, minimize, BINARY
from collections import OrderedDict

def _4_SolveRotNode():
    
    time_Elapsed_RN, ObjValueRN = 0.0, 0.0
    start = time.time()
            
    ################ Find Slope and Constant     
    # 1. At plants
    for k in range(g.V2):
        f_Lp        = g.hp[k]*pow(g.Lp[k], g.lambdaP)
        f_Up        = g.hp[k]*pow(g.Up[k], g.lambdaP)
        g.mp[k]     = (f_Up - f_Lp) / (g.Lp[k]- g.Up[k])
        g.constp[k] = f_Lp - g.mp[k]*g.Lp[k]
            
    # 2. At DCs
    for j in range(g.V1):
        f_Ld        = g.hd[j]*pow(g.Ld[j], g.lambdaD)
        f_Ud        = g.hd[j]*pow(g.Ud[j], g.lambdaD)
        g.md[j]     = (f_Ud - f_Ld)/(g.Ud[j] - g.Ld[j])
        g.constd[j] = f_Ld - g.md[j]*g.Ld[j]
        
    # 3. On Arcs from Plants to DC
    for k in range(g.V2):
        for j in range(g.V1):
            f_L1           = g.h1[k][j]*pow(g.L1[k][j], g.lambda1)
            f_U1           = g.h1[k][j]*pow(g.U1[k][j], g.lambda1)
            g.m1[k][j]     = (f_U1 - f_L1) / (g.U1[k][j] - g.L1[k][j])
            g.const1[k][j] = f_L1 - g.m1[k][j] * g.L1[k][j]            

    # 4. On Arcs from DCs to Customers
    for j in range(g.V1):
        for i in range(g.I):
            f_L2           = g.h2[j][i] * pow(g.L2[j][i], g.lambda2)
            f_U2           = g.h2[j][i] * pow(g.U2[j][i], g.lambda2)
            g.m2[j][i]     = (f_U2 - f_L2) / (g.U2[j][i] - g.L2[j][i])  
            g.const2[j][i] = f_L2 - g.m2[j][i] * g.L2[j][i]
    
    ################ Mathematical model at Root Node
    # Create model
    mRN = Model("RootNode")
    
    # Define variables
    z2 = [mRN.add_var(var_type=BINARY) for j in range(g.V2)]
    v2 = [mRN.add_var() for j in range(g.V2)]
    z1 = [mRN.add_var(var_type=BINARY) for j in range(g.V1)]
    v1 = [mRN.add_var() for j in range(g.V1)]
    x2 = {(k, j): mRN.add_var() for k in range(g.V2) for j in range(g.V1)}
    x1 = {(j, i): mRN.add_var() for j in range(g.V1) for i in range(g.I)}
            
    # Set Objective Function
    mRN.objective = minimize(
        xsum(g.Fp[k] * z2[k] for k in range(g.V2)) + 
        xsum(g.Fd[j] * z1[j] for j in range(g.V1)) +
        xsum(g.mp[k] * v2[k] for k in range(g.V2)) + 
        xsum(g.md[j] * v1[j] for j in range(g.V1)) +
        xsum(g.m1[k][j] * x1[k, j] for k in range(g.V2) for j in range(g.V1)) + 
        xsum(g.m2[j][i] * x2[j, i] for j in range(g.V1) for i in range(g.I))
        )
        
    # Set Constraints
    # 1. Production Capacity at Plants
    for k in range(g.V2):
        mRN.add_constr(xsum(x1[k, j] for j in range(g.V1)) <= g.Cp[k] * z2[k])
    
    # 2. Production volume at plants
    for k in range(g.V2):
        mRN += xsum(x1[k, j] for j in range(g.V1)) == v2[k]
    
    # 3. Handling Capacity at DCs
    for j in range(g.V1):
        mRN += xsum(x1[k, j] for k in range(g.V2)) <= g.Cd[j] * z1[j]
        
    # 4. Handling Volume at DCs
    for j in range(g.V1):
        mRN += xsum(x1[k, j] for k in range(g.V2)) <= v1[j]
        
    # 5. Flow balance at DCs
    for j in range(g.V1):
        mRN += xsum(x1[k, j] for k in range(g.V2)) == xsum(x2[j, i] for i in range(g.I))
    
    # 6. Demand Satifaction
    for i in range(g.I):
        mRN += xsum(x2[j, i] for j in range(g.V1)) == g.D[i]
    
    # 7. Limits on concave functions
    for k in range(g.V2):
        mRN += v2[k] >= g.Lp[k] 
        mRN += v2[k] <= g.Up[k]
    
    for j in range(g.V1):
        mRN += v1[j] >= g.Ld[j] 
        mRN += v1[j] <= g.Ud[j]
    
    for k in range(g.V2):
        for j in range(g.V1):
            mRN += x1[k, j] >= g.L1[k][j]
            mRN += x1[k, j] <= g.U1[k][j]
    
    for j in range(g.V1):
        for i in range(g.I):
            mRN += x2[j, i] >= g.L2[j][i]
            mRN += x2[j, i] <= g.U2[j][i]
    
    mRN.optimize()
    
    print("Solution with cost {} found.".format(mRN.objective_value))
    end = time.time() 
    time_Elapsed_RN = end - start

    LB_RN = mRN.objective_value
    
    # Find Upper Bound at Root Node
    UB_RN = 0.0
    
    for k in range(g.V2):
        UB_RN += z2[k].x * g.Fp[k]
    
    for j in range(g.V1):
        UB_RN += z1[j].x * g.Fd[j]
    
    for k in range(g.V2):
        UB_RN += g.hp[k] * pow(v2[k].x, g.lambdaP)
        
    for j in range(g.V1):
        UB_RN += g.hd[j] * pow(v1[j].x, g.lambdaD)
    
    for k in range(g.V2):
        for j in range(g.V1):
            UB_RN += g.h1[k][j] * pow(x1[k, j].x, g.lambda1)

    for j in range(g.V1):
        for i in range(g.I):
            UB_RN += g.h2[j][i] * pow(x2[j, i].x, g.lambda2)
            
    print("Upper Bound At Root Node: %f"% (UB_RN))
    print("Elapsed Time ROOT NODE (secs): %.2f" % (time_Elapsed_RN))    
    
    return ObjValueRN
