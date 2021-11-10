# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 23:37:38 2020

@author: umroot
"""

# Data Definition File to declare data variables to be global
def init():
    global V1 # Number of potential plants
    global V2 # Number of potential warehouses
    global I # Number of customers
        
    global Cp, Fp, hp # Plant capacities, fixed costs and production costs    
    global Cd, Fd, hd # DC capacities, fixed costs and handling costs    
    global h1 # Plant to DC arcs transportation costs       
    global h2 # DC to customer arcs transportation costs    
    global D # Customer demand
    
    global lambdaP, lambdaD, lambda1, lambda2 # Concavity factors (level of Economies of scale) 
    # on plants, DC, plant to DC arcs, DC to DC arcs, and DC to customer arcs, respectively
    
    global pos_z1, pos_v1, pos_x1, pos_z2, pos_v2, pos_x2 #positions for variables in 
    # a solution vector xCN and xBest
    
    global xCN, xBest # Vecctors to save solution of current node and best solution
    global LB_Best, UB_Best # Best lower and upper bound values
    
# To save information of every node in ListNodes list  
class Nodes():
    def __init__(self, TreeNodeNumber, IterationNumber, LowerBound, UpperBound, SolVector,
                 SolVector2):
        self.TN  = TreeNodeNumber
        self.Itr = IterationNumber
        self.LB  = LowerBound
        self.UB  = UpperBound
        self.x   = SolVector
        self.y   = SolVector2

def LimitsSlopesAndConstants():
    global Lp, Up # Lower and Upper Limits on production variables at plants
    global Ld, Ud # Lower and Upper Limits on handling variables at DCs
    global L1, U1 # Lower and Upper Limits on flow variables from plants to DCs
    global L2, U2 # Lower and Upper Limits on flow variables from plants to DCs
    
    global mp, constp # Slopes and Constants on production variables at plants
    global md, constd # Slopes and Constants on handling variables at DCs
    global m1, const1 # Slopes and Constants on flow variables from plants to DCs
    global m2, const2 # Slopes and Constants on flow variables from plants to DCs
    