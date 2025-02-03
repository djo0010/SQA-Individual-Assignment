import unittest
import source 


class TestCalc(unittest.TestCase):
    def testSub1(self):
        self.assertEqual(1, source.performSub(2, 1), "Bug in implementation. Results should be 1.") 

    def testSub2(self):
        self.assertEqual(1001, source.performSub(2001, 1000), "Bug in implementation. Results should be 1001.") 
    
    def testSub3(self):
        self.assertEqual(-5, source.performSub(2, 7), "Bug in implementation. Results should be -5.") 

   
if __name__ == '__main__': 
    unittest.main()
