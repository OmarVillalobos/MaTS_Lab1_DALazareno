"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Lab 1.                                                                                     -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: diegolazareno                                                                               -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/diegolazareno/MaTS_Lab1_DALazareno                                   -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Required libraries
import pandas as pd
import yfinance as yf
import datetime as dt
import numpy as np


def dataCleaningAndFiltering(data : "NAFTRAC allocations historic file"):
    """
    dataCleaningAndFiltering cleans and filters relevant information (tickers and weights) from the NAFTRAC 
    index composition.
    
    *data: is a DataFrame that contains all NAFTRAC allocations from a certain time period.
    
    Returns:
    *naftrac: is a DataFrame that contains cleaned and filtered ticker symbols with their respectives weights.
    
    """
    
    # Data cleaning
    tickers = list(map(lambda ticker : ticker.replace("*", "").replace(".", "-"), list(data["Ticker"])))
    remove = ["KOFL", "KOFUBL", "USD", "BSMXB", "NMKA", "MXN"]
    naftrac = pd.DataFrame(columns = ["Ticker", "Weight"], index = range(len(tickers)))
    
    i = 0
    for ticker in tickers:
        if ticker not in remove:
            naftrac.iloc[i, 0] = ticker
            naftrac.iloc[i, 1] = data["Peso (%)"][i] / 100
            i += 1
    
    return naftrac.dropna()


def dataDownload(tickers : "Ticker symbols", start : "Start date", end : "End date"):
    """
    dataDownload downloads the adjusted closing prices for all given ticker symbols between two dates.
    
    *tickers: is a list with all ticker symbols (in string format).
    *start: is the starting date for the data download. 
    *end: is the ending date for the data download.
    
    Returns:
    *data: a DataFrame that contains the adjusted closing prices for all the given ticker symbols.
    
    """
    
    # Data download
    data = pd.DataFrame()
    
    for ticker in tickers:
        data[ticker] = yf.download(ticker + ".MX", start = start, end = end, progress = False)["Adj Close"]
        
    # Filtering stocks with no info
    for col in list(data.columns):
        if sum(data[col].isna()) == len(data):
            data.drop([col], axis = 1, inplace = True)
    
    return data


def passiveInvestingPortfolio(data : "NAFTRAC info", prices : "Historic prices", 
                              capital : "Initial capital", commission : "Commission per transaction"):
    """
    passiveInvestingPortfolio executes a passive investment strategy.
    
    *data: is the NAFTRAC information (composition and weights).
    *prices: historic stock prices.
    *capital: is the initial capital.
    *commission: is the commission per transaction.
    
    Returns:
    *portfolioInfo: a DataFrame that contains relevant information about the portfolio. 
    *portfolioPerformance: a DataFrame that contains the portfolio performance.
    *globalResults: a DataFrame with the strategy global results.
    
    """
    # Delisted ticker symbols (last information)
    delisted = list(prices.isna().any()[prices.isna().any() == True].index)
    lastPrice = {}
    
    if len(delisted) > 0:
        for ticker in delisted:
            lastPrice[ticker] = prices[ticker][prices[ticker] > 0][-1]
    
    # Stock prices to a monthly temporality
    prices.reset_index(inplace = True)
    prices = prices[(prices["Date"].dt.month.shift(-1) - prices["Date"].dt.month) != 0].copy()        
    prices.set_index(["Date"], inplace = True)
    prices.fillna(0, inplace = True)    
    
    # Portfolio Information
    portfolioInfo = pd.DataFrame(index = list(prices.columns))
    portfolioInfo["Capital allocation"] = np.array([data["Weight"][i] for i in range(len(data)) if data["Ticker"][i] in list(prices.columns)]) * capital
    portfolioInfo["Cost per share (commission included)"] = prices.iloc[0, :].values * (1 + commission) 
    portfolioInfo["Purchased shares"] = list(map(lambda i : np.floor(i), portfolioInfo["Capital allocation"] / portfolioInfo["Cost per share (commission included)"]))
    portfolioInfo["Position value"] = prices.iloc[0, :].values * portfolioInfo["Purchased shares"].values 
    portfolioInfo["Commission"] = portfolioInfo["Capital allocation"] - portfolioInfo["Position value"]
    portfolioInfo["Weight"] = portfolioInfo["Position value"].values / portfolioInfo["Position value"].sum() 
    
    # Cash and sale of delisted stocks
    cash = capital - np.dot(portfolioInfo["Purchased shares"].values, portfolioInfo["Cost per share (commission included)"].values)    
    
    if len(delisted) > 0:
        for ticker in delisted:
            cash += lastPrice[ticker] * (1 - commission) * portfolioInfo.loc[ticker, "Purchased shares"]
    
    # Portfolio performance
    portfolioPerformance = pd.DataFrame(index = prices.index)
    portfolioPerformance["Portfolio value"] = [portfolioInfo["Position value"].sum()] + list(np.dot(prices.iloc[1:, :].values, portfolioInfo["Purchased shares"].values)) 
    portfolioPerformance["Return"] = portfolioPerformance["Portfolio value"].pct_change() 
    portfolioPerformance["Cumulative return"] = (portfolioPerformance["Return"] + 1).cumprod() - 1
    portfolioPerformance.iloc[0, 1] = 0
    portfolioPerformance.iloc[0, 2] = 0
    
    # Global results
    globalResults = pd.DataFrame({"Initial portfolio value" : '${:,.2f}'.format(portfolioInfo["Position value"].sum()), 
                                  "Final portfolio value" : '${:,.2f}'.format(portfolioPerformance["Portfolio value"][-1]), 
                                  "Return" : str(round(portfolioPerformance["Cumulative return"][-1] * 100, 2)) + "%", 
                                  "Cash" : '${:,.2f}'.format(cash), "Total capital" : '${:,.2f}'.format(cash + portfolioPerformance["Portfolio value"][-1])}, 
                                  index = ["Results"])
    
    return portfolioInfo, portfolioPerformance, globalResults
    
