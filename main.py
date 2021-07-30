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

#####--------------------------------------------
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

from datetime import datetime, timedelta

volatility = 0.1
isBought = False


class Algorithm(QCAlgorithm):
    def Initialize(self):
        isBought = False
        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2021, 7, 28)

        self.EnableAutomaticIndicatorWarmUp = True

        self.portfolio = ["DAL", "AC", "AAL", "BLNK"]
        for stock in self.portfolio:
            self.AddEquity(stock, Resolution.Hour)

        self.Schedule.On(self.DateRules.EveryDay("DAL"), self.TimeRules.AfterMarketOpen("DAL", 30), self.GetSource)
        self.Schedule.On(self.DateRules.EveryDay("DAL"), self.TimeRules.AfterMarketOpen("DAL", 2), self.checkIfBought)

    # def OnWarmUpFinished(self):
    #     self.checkIfBought()

    def OnData(self, data):
        self.arimax()

    def arimax(self):
        self.Debug("OnData")
        for stock in self.portfolio:
            if (stock != "BLNK"):
                self.arima = self.ARIMA(stock, 10, 1, 10, 50)
                self.ar = self.ARIMA(stock, 1, 1, 0, 50)
                self.last = self.ar.Current.Value

                if self.arima.IsReady:
                    if abs(self.arima.Current.Value - self.ar.Current.Value) > 1:
                        difference = self.arima.Current.Value - self.last

                        if (abs(difference) > 7):
                            self.SetHoldings(stock, difference * -(0.08 * volatility))
                            self.Debug("Buying: " + str(stock))
                            self.Debug(self.Portfolio.MarginRemaining)

                            isBought = True

                    self.last = self.arima.Current.Value

    def convert_to_datetime(self, string_date):
        return datetime.strptime(string_date, '%m/%d/%Y')

    def toInt(self, throughputString):
        return int(throughputString)

    def checkIfBought(self):
        stock = "BLNK"
        self.arima = self.ARIMA(stock, 10, 1, 10, 50)
        self.ar = self.ARIMA(stock, 1, 1, 0, 50)
        self.last = self.ar.Current.Value

        if self.arima.IsReady:
            if abs(self.arima.Current.Value - self.ar.Current.Value) > 1:
                difference = self.arima.Current.Value - self.last
                try:
                    self.Debug("Buying: " + str("BLNK") + " at end of day.")
                    self.MarketOnOpenOrder("BLNK", min(difference * -(0.01 * volatility), ))
                    self.Debug(self.Portfolio.MarginRemaining)
                except:
                    self.Debug("End of day buy failure")
        # try:
        #     # self.SetHoldings(self.BiggestGainer, self.difference)
        #     self.Debug("Buying: " + str("BLNK") +" at end of day.")
        #     self.MarketOnOpenOrder("BLNK", 0.1);
        # except:
        #     self.Debug("End of day buy failure")

    def GetSource(self):
        self.Debug("New Day")
        try:
            source = self.Download("https://www.dropbox.com/s/1wo4t5ydkrzderr/throughput.csv?dl=1")
            header_list = ["Date", "Throughput"]
            df = pd.read_csv(StringIO(source), names=header_list)
            df["Date"] = df["Date"].apply(self.convert_to_datetime)
            df["Throughput"] = df["Throughput"].apply(self.toInt)
            df['Log returns'] = np.log(df['Throughput'] / df['Throughput'].shift())
            df['Log returns'].std()

            currentDate = self.Time
            currentDate = datetime(currentDate.year, currentDate.month, currentDate.day, 0, 0, 0)
            currentDate = currentDate - timedelta(days=2)

            index = df.index
            condition = df["Date"] == currentDate
            startDate = index[condition]
            indices = startDate.tolist()

            volatility = df['Log returns'][indices[0]]

        except:
            volatility = 0.1

        self.Debug(volatility)