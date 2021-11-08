import pandas as pd
import numpy as np
import sys
import time
import _1_GlobalVarDefs as g
import _2_ReadInputData as r
import _3_MainFunction as mf

#import scipy.stats as st

# import multiprocessing as mp
# print("Number of processors: ", mp.cpu_count())

#print ("This is the name of the script: ", sys.argv[0])

if __name__ == '__main__':   
    
    ################ Global initializaton of the data variables
    g.init()    
    g.LimitsSlopesAndConstants()
    
    ################ Read Input Parameters File
    file_name = 'InputParameters.dat'
    file = open(file_name,mode='r')
    array = file.read().split()
   
    arrayFinal = [0 for i in range(len(array))]
    for n in range(len(array)):
        arrayFinal[n] = float(array[n])
    
    start_Pno = int(arrayFinal[0])
    end_Pno   = int(arrayFinal[1])
    g.lambdaP = arrayFinal[2]
    g.lambdaD = arrayFinal[3]
    g.lambda1 = arrayFinal[4]
    g.lambda2 = arrayFinal[5]    
    
    a = 100.0
    print("Value of a: %f" % (a))
    ################ For now lets run problem instances sequentially.
    # Later we will figure out how to run all the instances in parallel using
    # parallel computing capabilities of Python
    for pno in range(start_Pno, end_Pno + 1):

        ################ Read Data 
        r._1_ReadData(pno)        
        
        ################ Call Main Function (Branch-and-Bound Algorithm)        
        
        ListNodes = [] # Initial list to save every node of the Branch-and-bound tree        
        
        ObjValue = mf._0_MainFunction(ListNodes)
                   
        print("END OF Pno: %d with Supply Chain Cost: %f"%(pno, ObjValue))
    
    print("END OF SCRIPT")
    

    