import operator
import os
import pandas as pd
import numpy as np
import sys
import _1_GlobalVarDefs as g
import _4_RootNodeProblem as RN
import _5_BranchingIndex as B
import _6_LeftNodeProblem as LN
import _0_MainCode as mc
import time
import csv
import copy

# BEGIN: MAIN FUNCTION DEFINITION
def _0_MainFunction(ListNodes):
    
    TreeNodeNumber = 0
    time_Elapsed, ObjValue = 0.0, 0.0
    start = time.time()
            
    # ArcSol = [[ np.random.randint(100) for j in range(2)] for k in range(3)]
        
    # NodeInfo = g.Nodes(10,100,34,67,[1,0,2,3],ArcSol)
    # ListNodes.append(NodeInfo)    
    
    # ArcSol = [[ np.random.randint(100) for j in range(2)] for k in range(3)]
    # NodeInfo = g.Nodes(20,200,13,17,[5,0,243,2],ArcSol)
    # ListNodes.append(NodeInfo)
    
    # ArcSol = [[ np.random.randint(100) for j in range(2)] for k in range(3)]
    # NodeInfo = g.Nodes(20,200,23,17,[5,0,243,2],ArcSol)
    # ListNodes.append(NodeInfo)
    
    # # Find the index in the list with lowest lower bound value
    # index = min(range(len(ListNodes)), key=lambda i: ListNodes[i].LB)
        
    # del ListNodes[index]
    
    ################ START BRANCH AND BOUND ALGORITHM
    # Step 1: Solve root node of the model. (For root node, initial limits on 
    # concave variables are already set in _2_ReadInputData script)
    LB_CN, UB_CN, g.xCN = RN._4_SolveRootNode()
    
    # Update values of limits and solutions of the node with lowest LB 
    # which is same as root node limits at this point
    g.xLowestLB = copy.deepcopy(g.xCN)
    
    # 1. At plants
    g.Lp_LowestLB = copy.deepcopy(g.Lp)
    g.Up_LowestLB = copy.deepcopy(g.Up)
        
    # 2. At DCs
    g.Ld_LowestLB = copy.deepcopy(g.Ld)
    g.Ud_LowestLB = copy.deepcopy(g.Ud)
        
    # 3. On Arcs from Plants to DC
    g.L1_LowestLB = copy.deepcopy(g.L1)
    g.U1_LowestLB = copy.deepcopy(g.U1)
    
    # 4. On Arcs from DCs to Customers
    g.L2_LowestLB = copy.deepcopy(g.L2)
    g.U2_LowestLB = copy.deepcopy(g.U2)
    
    # Update values of 
    g.LB_Best, g.UB_Best = LB_CN, UB_CN
    g.xBest = copy.deepcopy(g.xCN)
    
    # Step 2: Call Deviation Function
    index0, index1, index2 = B._5_FindBranchingIndex(g.xCN)    
    #print("Max err cat: %s; index1: %d; index2: %d" % (index0, index1, index2))
    
    OptGap = (g.UB_Best - g.LB_Best) * 100/ g.UB_Best
    print("Current OptGap: %.2f" % (OptGap))
    
    ################ START ENUMERATION ONLY IF DESIRED OPT GAP IS NOT REACHED
    if(OptGap > g.Desired_OptGap):
        
        print("Start Enumerating")
        start_loop = time.time()
        
        # increment TreeNodeNumber to represent actual node number of the tree
        TreeNodeNumber = TreeNodeNumber + 1
        
        # solve left node
        LB_CN, UB_CN, g.xCN = LN._6_SolveLeftNode(index0, index1, index2)        
        
        
        end_loop = time.time() 
        time_elapsed_loop = end_loop - start_loop
    
    end = time.time() 
    time_Elapsed = end - start

        
    print("Elapsed Time (secs): %.2f" % (time_Elapsed))
    print("END OF MAIN FUNCTION")
    return 0.0
