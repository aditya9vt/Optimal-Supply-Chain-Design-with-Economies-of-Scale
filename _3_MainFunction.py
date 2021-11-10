import operator
import os
import pandas as pd
import numpy as np
import sys
import _1_GlobalVarDefs as g
import _4_RootNodeProblem as RN
import _0_MainCode as mc
import time
import csv
import copy

# BEGIN: MAIN FUNCTION DEFINITION
def _0_MainFunction(ListNodes):
    
    time_Elapsed, ObjValue = 0.0, 0.0
    start = time.time()
            
    ArcSol = [[ np.random.randint(100) for j in range(2)] for k in range(3)]
        
    NodeInfo = g.Nodes(10,100,34,67,[1,0,2,3],ArcSol)
    ListNodes.append(NodeInfo)    
    
    ArcSol = [[ np.random.randint(100) for j in range(2)] for k in range(3)]
    NodeInfo = g.Nodes(20,200,13,17,[5,0,243,2],ArcSol)
    ListNodes.append(NodeInfo)
    
    ArcSol = [[ np.random.randint(100) for j in range(2)] for k in range(3)]
    NodeInfo = g.Nodes(20,200,23,17,[5,0,243,2],ArcSol)
    ListNodes.append(NodeInfo)
    
    # Find the index in the list with lowest lower bound value
    index = min(range(len(ListNodes)), key=lambda i: ListNodes[i].LB)
        
    del ListNodes[index]
    
    ################ START BRANCH AND BOUND ALGORITHM
    # Step 1: Solve root node of the model. (For root node, initial limits on 
    # concave variables are already set in _2_ReadInputData script)
    LB_CN, UB_CN, g.xCN = RN._4_SolveRotNode()
    
    # Update values of 
    g.LB_Best, g.UB_Best = LB_CN, UB_CN
    g.xBest = copy.deepcopy(g.xCN)
    
    # Step 2: Call Deviation Function
    end = time.time() 
    time_Elapsed = end - start

        
    print("Elapsed Time (secs): %.2f" % (time_Elapsed))
    print("END OF MAIN FUNCTION")
    return 0.0
