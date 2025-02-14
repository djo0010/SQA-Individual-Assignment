## Workshop 3

## Workshop Name: Automated Information Flow Analysis with Taint Tracking

## Description 

Use existing code to track a susceptible data value across a program 

## Targeted Courses 

Software Quality Assurance 

## Activities 

### Pre-lab Content Dissemination 

In our class lectures we learned the importance on why bugs and security vulnerabilities need to be discovered pro-actively. Even though there are a wide a range of tools, without tracking the flow of data we might not be find a bug or a vulnerability accurately. One approach to find a bug or a vulnerability accurately is taint tracking, where we first designate a taint, and then track the taint across a program. In this workshop we will develop a program that uses existing code provided by the instructor to track a taint, i.e., a data value.  

### In-class Hands-on Experience 


- Check the code out in `(https://github.com/effat/SQA-2025/blob/ALAMOSE/workshops/workshop3-taint/calc.py)` and `(https://github.com/effat/SQA-2025/blob/ALAMOSE/workshops/workshop3-taint/analysis.py)`
- Understand the code in `workshop3/calc.py` to see manually how simpleCalculator() works
- Write the flow of execution for `workshop3/calc.py` 
- Understand the code in `workshop3/analysis.py` to understand how parse tree and relevant components from `workshop3/calc.py` have been extracted

### Submission 
- Complete the `checkFlow` function in `workshop3/analysis.py` so that the flow of execution for `workshop3/calc.py` is captured i.e., I get `1000->val1->v1->res`
- Feel free to use the `Pandas` dataframe [selection operators](https://pandas.pydata.org/docs/user_guide/10min.html#selection)
- Upload a zip file at Assignment 3 @ CANVAS conataining
   - Your code implementation, i.e., the updated `analysis.py` file
   - A pdf file describing the flow of execution of `workshop3/calc.py`  
- Due: Mar 2, 2025

###  Rubric
- Description of flow of execution for calc.py [20%]
- Implementation of analysis.py [70%]
- Explataion of implementation of analysis.py as code comment [10%]
  


