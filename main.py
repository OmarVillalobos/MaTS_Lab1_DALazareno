"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Lab 1.                                                                                     -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: diegolazareno                                                                               -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/diegolazareno/MaTS_Lab1_DALazareno                                   -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

#%% .py files
import data
import functions

# Settings
import pandas as pd
pd.set_option('display.float_format', '{:.2f}'.format)

#%% Passive investment strategy

def passiveInvestingStrategy(dates : "Dates", capital : "Initial capital", commission : "Commission"):
    """
    passiveInvestingStrategy executes a passive investment strategy for the given periods.
    
    *dates: is a list that contains the start and end dates for all the periods that will be tested.
    *capital: is the initial capital.
    *commission: is the commission for each transaction.
    
    Returns:
    *results: a dictionary that contains the passive investment strategy results for each tested period.
    
    """
    
    results = {}
    
    for i in range(len(dates)):
        
        results[dates[i][0]] = {}
        
        # Data reading and wrangling
        filepath = "files/NAFTRAC_" + dates[i][0].replace("-", "") + ".csv"
        datan = data.readData(filepath)
        datan = functions.dataCleaningAndFiltering(datan)
        
        # Data download
        historicPrices = functions.dataDownload(list(datan["Ticker"]), dates[i][0], dates[i][1])
        
        # Passive investment strategy
        portfolioInfo, portfolioPerformance, globalResults = functions.passiveInvestingPortfolio(datan, historicPrices, capital, commission)
        
        results[dates[i][0]]["portfolioInfo"] = portfolioInfo
        results[dates[i][0]]["portfolioPerformance"] = portfolioPerformance
        results[dates[i][0]]["globalResults"] = globalResults
        
    return results

