'''
Akond Rahman
Simple Python file to demonstrate logging 
'''
import numpy as np
from sklearn.model_selection import KFold
from sklearn.datasets import load_iris
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.metrics import accuracy_score
import myLogger


def simpleDiv(a, b):
    return a/b 


if __name__=='__main__': 
   logObj  = myLogger.giveMeLoggingObject()
   logObj.info("This is for the demonstration of workshop 10.")
   print('Welcome to the simple division calculator!')
   logObj.info("The calculator application has started...")
   a = input('Type in first number: ') 
   b = input('Type in second number: ')
   a , b = int(a), int(b)
   logObj.info("The arguments that were provided -> a:{}, b:{}".format( a, b ))
   simpleDiv(a, b) 



#    logObj.info("Simple application started.")
#    logObj.info('First number is: %s', a)    
#    logObj.info('Second number is: %s', b) 