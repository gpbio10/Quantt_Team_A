from clr import AddReference

AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *

import pandas as pd
import numpy as np
from io import StringIO

from statsmodels.tsa.stattools import adfuller


class Algorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2021, 7, 12)

        self.EnableAutomaticIndicatorWarmUp = True

        self.portfolio = ["DAL", "AC", "AAL"]
        for stock in self.portfolio:
            self.AddEquity(stock, Resolution.Hour)

        source = self.Download("https://www.dropbox.com/s/nuoi78pkna9956o/throughputTest.csv?dl=1")
        header_list = ["Date", "Throughput"]
        df = pd.read_csv(StringIO(source), names=header_list)
        df['Date'] = df['Date'].astype('datetime64[ns]')

        self.Schedule.On(self.DateRules.EveryDay("DAL"), self.TimeRules.AfterMarketOpen("DAL", 210), self.GetSource)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        self.arimax()

    def arimax(self):
        for stock in self.portfolio:

            # closing_prices = self.History(stock, 20, Resolution.Hour).values

            self.arima = self.ARIMA(stock, 10, 1, 10, 50)
            self.ar = self.ARIMA(stock, 1, 1, 0, 50)
            self.last = self.ar.Current.Value

            if self.arima.IsReady:
                if abs(self.arima.Current.Value - self.ar.Current.Value) > 1:
                    self.Debug("Arima Current: " + str(self.arima.Current.Value) + " Last: " + str(self.last))
                    difference = self.arima.Current.Value - self.last
                    if self.arima.Current.Value > self.last:
                        if (abs(difference) > 10):
                            self.SetHoldings(stock, 0.33)
                        else:
                            self.SetHoldings(stock, difference * 0.033)
                    self.Debug(difference)
                self.last = self.arima.Current.Value

    def GetSource(self):
        source = self.Download("https://www.dropbox.com/s/nuoi78pkna9956o/throughputTest.csv?dl=1")
        header_list = ["Date", "Throughput"]
        df = pd.read_csv(StringIO(source), names=header_list)
        df['Date'] = df['Date'].astype('datetime64[ns]')

