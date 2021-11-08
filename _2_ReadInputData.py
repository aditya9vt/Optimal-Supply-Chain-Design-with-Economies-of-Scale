
import _1_GlobalVarDefs as g
## We can add 'n' number of function definitions in one module

def _1_ReadData(pno):

    ################ Read Data from text file character by character
    file_name = 'InputData_Pno'+str(pno)+'.dat'
    
    file = open(file_name,mode='r')
    array = file.read().split()
   
    arrayFinal = [0 for i in range(len(array))]
    for n in range(len(array)):
        arrayFinal[n] = float(array[n])

    # 1. Instance Size
    pos=0
    g.V2 = int(arrayFinal[pos])
    pos = pos + 1
    g.V1 = int(arrayFinal[pos])
    pos = pos + 1
    g.I = int(arrayFinal[pos])
    pos = pos + 1
    
    # 2. Plant Capacities
    g.Cp = [0 for k in range(g.V2)]
    for k in range(g.V2):
        g.Cp[k] = arrayFinal[pos]
        pos = pos + 1    
    
    # 3. Plant Fixed Costs
    g.Fp = [0 for k in range(g.V2)]
    for k in range(g.V2):
        g.Fp[k] = arrayFinal[pos]
        pos = pos + 1
    
    # 4. Plant Production Costs
    g.hp = [0 for k in range(g.V2)]
    for k in range(g.V2):
        g.hp[k] = arrayFinal[pos]
        pos = pos + 1

    # 5. DC Capacities
    g.Cd = [0 for j in range(g.V1)]
    for j in range(g.V1):
        g.Cd[j] = arrayFinal[pos]
        pos = pos + 1    

    # 6. DC Fixed Costs
    g.Fd = [0 for j in range(g.V1)]
    for j in range(g.V1):
        g.Fd[j] = arrayFinal[pos]
        pos = pos + 1    

    # 7. DC Handling Costs
    g.hd = [0 for j in range(g.V1)]
    for j in range(g.V1):
        g.hd[j] = arrayFinal[pos]
        pos = pos + 1    
  
    # 8. Transportation costs plant to DC arcs
    g.h1 = [[0 for j in range(g.V1)] for k in range(g.V2)]
    for k in range(g.V2):
        for j in range(g.V1):
            g.h1[k][j] = arrayFinal[pos]
            pos = pos + 1     
    
    # 9. Transportation cost DC to customer arcs
    g.h2 = [[0 for i in range(g.I)] for j in range(g.V1)]
    for j in range(g.V1):
        for i in range(g.I):
            g.h2[j][i] = arrayFinal[pos]
            pos = pos + 1  

    # 10. Customer Demand
    g.D = [0 for i in range(g.I)]    
    for i in range(g.I):
        g.D[i] = arrayFinal[pos]
        pos = pos + 1  

    
    ################ Initialize lower and uppers limits on variables in concave functions
    ################ This will used as first input to the root node problem of the BB tree
    
    # 1. At plants
    g.Lp = [0 for k in range(g.V2)]
    g.Up = [0 for k in range(g.V2)]
    for k in range(g.V2):
        g.Lp[k] = 0
        g.Up[k] = min(g.Cp[k], sum(g.D))
    
    # 2. At DCs
    g.Ld = [0 for j in range(g.V1)]
    g.Ud = [0 for j in range(g.V1)]
    for j in range(g.V1):
        g.Ld[j] = 0
        g.Ud[j] = min(g.Cd[j], sum(g.D))
    
    # 3. On Arcs from Plants to DC
    g.L1 = [[0 for j in range(g.V1)] for k in range(g.V2)]
    g.U1 = [[0 for j in range(g.V1)] for k in range(g.V2)]
    for k in range(g.V2):
        for j in range(g.V1):
            g.L1[k][j] = 0
            g.U1[k][j] = min(g.Cp[k], g.Cd[j], sum(g.D))

    # 4. On Arcs from DCs to Customers
    g.L2 = [[0 for i in range(g.I)] for j in range(g.V1)]
    g.U2 = [[0 for i in range(g.I)] for j in range(g.V1)]
    for j in range(g.V1):
        for i in range(g.I):
            g.L2[j][i] = 0
            g.U2[j][i] = min(g.Cd[j], g.D[i])
    
    
    ################ Initialize slopes and constants with '0' value
    g.mp     = [0 for k in range(g.V2)]
    g.constp = [0 for k in range(g.V2)]

    g.md     = [0 for j in range(g.V1)]
    g.constd = [0 for j in range(g.V1)]

    g.m1     = [[0 for j in range(g.V1)] for k in range(g.V2)]
    g.const1 = [[0 for j in range(g.V1)] for k in range(g.V2)]

    g.m2     = [[0 for i in range(g.I)] for j in range(g.V1)]
    g.const2 = [[0 for i in range(g.I)] for j in range(g.V1)]

    print("End of DATA READING FUNCTION")
