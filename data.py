"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Lab 1.                                                                                     -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: diegolazareno                                                                               -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/diegolazareno/MaTS_Lab1_DALazareno                                   -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Required libraries
import pandas as pd


def readData(filePath : "Is the csv file path"):
    """
    readData reads a csv file. 
    
    *filePath: is the csv file path.
    
    Returns:
    *data: a DataFrame that contains the data from the csv file.
    
    """
    
    data = pd.read_csv(filePath, skiprows = range(2)).dropna()
    
    return data

