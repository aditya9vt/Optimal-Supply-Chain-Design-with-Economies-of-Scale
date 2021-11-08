# Supply-Chain-Design-with-Economies-of-Scale (WIP)

The problem presented in this repository is one of my PhD works. The goal is to optimize a large-size classical production-distribution types supply chain network with economies of scale. In practice, the economies of scale is modeled using concave function, which makes the resultant model a non-convex optimization problem. 

Solving non-convex mathematical problem is a challenging task. To the best of our knowledge, BARON is the most efficeint commercial solver to solve such problems (concave minimization in our case). However, the results provided by BARON are very sub-optimal, in particular, the supply chain network has very huge supply chain costs (sum of facilities opening, production, handling and transportation costs). 

Therefore, to over come this challenge, we provide a (spatial) Branch-and-Bound algorithm. Our solution method provides a supply chain network with total cost 20% less than that of the network provided by BARON. The submitted work and results can be found here: https://github.com/aditya9vt/Resume-and-Other-Documents/blob/gh-pages/Article_SCNDwithConcaveCosts.pdf. To see the comparison between BARON and our method, you can refer to the table 7 on page 23. Additionally, our algorithm is capable of providing solutions within 1% of the best solution in nearly 30 mins (see Table 8 Page 24) for a supply chain with 40 potential plants, 85 potential DCs and 1500 customers.

The original algorithm is built-in C language using structures (for user-defined data types) to represent data at every node of the Branch-and-Bound tree. The aim of this repository is to provide a python implementation of the algorithm using classes and to use parallel computing feature of python to improve the computation time of the algorithm.

NOTE: The repository is still a work-in-progress, and the paper is under second round of revision. For any specific detail, kindly reach to me at aditya9vt@gmail.com.


