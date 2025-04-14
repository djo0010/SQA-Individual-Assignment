## Workshop Name: Simplistic White-box Fuzzing 

## Description 

Develop a simple fuzzer to test an existing implementation of a simple calculator 

## Targeted Courses 

Software Quality Assurance 

## Activities 

### Pre-lab Content Dissemination 

White-box fuzzing is a fuzzing technique where the source code of a software is leveraged 
to generate test cases. The goal of these test cases is to find bugs in the source code, so that these bugs 
are found and fixed early at the development stage. As part of this workshop we will develop a simple fuzzer 
that fuzzes an existing implementation of a simple calculator.   

### In-class Hands-on Experience 

- Go to announcements on CANVAS. See the announcement on `Workshop 7`
- We will use a loop to generate alphanumeric values and pass it into `divide`
- Calculate Branch coverage and Statement coverage for the four test cases showed in the class.
- Recording of this hands-on experience is available on CANVAS 

### Workshop 7 (Post Lab Experience) 
- Open `w7.py` 
- Implement the `simpleFuzzer` method so that it can generate alphanumeric values, and these values are plugged into the `simpleCalculator` method. Feel free to use the strings here: https://github.com/minimaxir/big-list-of-naughty-strings/blob/master/blns.json
- Record the crash messages. You should be recording 10 errors as part of your implementation. Submit the screenshots.
- Submit your code, i.e., the `w7.py` file and the error messages @ Workshop 7 on CANVAS. 
- Due: Apr 20, 2025

- ### Workshop 7 (Rubric) 
- Branch and statement coverage for four test cases          = 20%
- Screenshots of 10 crash messages and code implementation   = 80%
