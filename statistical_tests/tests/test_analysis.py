import pandas as pd
import numpy as np
from scipy.stats import f_oneway
import unittest

class TestStatisticalAnalysis(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.data = {
            'Group1': [1, 2, 3, 4, 5],
            'Group2': [2, 3, 4, 5, 6],
            'Group3': [3, 4, 5, 6, 7]
        }
        self.df = pd.DataFrame(self.data)

    def test_one_way_anova(self):
        # Perform one-way ANOVA
        f_stat, p_value = f_oneway(self.df['Group1'], self.df['Group2'], self.df['Group3'])
        
        # Check if the p-value is less than the significance level (0.05)
        self.assertLess(p_value, 0.05)

    def test_anova_with_different_means(self):
        # Modify data to have different means
        self.data['Group4'] = [10, 11, 12, 13, 14]
        self.df = pd.DataFrame(self.data)
        
        f_stat, p_value = f_oneway(self.df['Group1'], self.df['Group4'])
        
        # Check if the p-value is less than the significance level (0.05)
        self.assertLess(p_value, 0.05)

if __name__ == '__main__':
    unittest.main()