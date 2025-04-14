'''
Effat Farhana
'''

import random 

def divide(v1, v2):

   if isinstance(v1, str) and v1.isnumeric()== False:
      return "At least one input is non-numeric"

   if isinstance(v2, str) and v2.isnumeric()== False:
      return "At least one input is non-numeric"
   
   v1 = float(v1)
   v2 = float(v2)

   if v2!=0:
    return v1 / v2 
   else:
      return "Dvision by zero"
      
   
     

def fuzzValues(val1, val2):
   res = divide(val1, val2)
   return res  

def simpleFuzzer(): 
   resFromMethod = fuzzValues(1, 0)
   print(resFromMethod) 
   resFromMethod = fuzzValues("124", "2")
   print(resFromMethod) 
   resFromMethod = fuzzValues(0.80, 1.20)
   print(resFromMethod) 
   resFromMethod = fuzzValues("abcd", "2")
   print(resFromMethod) 

   
   


if __name__=='__main__':
    simpleFuzzer()
