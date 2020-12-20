"""
Data source crawler from Sina using easyquotation

Input Args:

sys.argv:
1 - stock list path
2 - date in 2020-02-03 format
3 - number of stocks per process
4 - 


Outputs:
Crawling results stored in a form of
.
+-- 2020-02-03
|   +-- 600001
|       +-- 0.pkl
|       +-- 1.pkl



"""
import easyquotation as eq 
from multiprocessing import Process, Queue
import sys 




def main():
    """
    Driver function that establishes connection and report failures
    """


