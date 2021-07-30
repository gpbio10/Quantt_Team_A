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

isBought = False
volatility = 0.1


class Algorithm(QCAlgorithm):
    def Initialize(self):
        isBought = False
        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2021, 7, 28)

        self.EnableAutomaticIndicatorWarmUp = True

        self.portfolio = ["DAL", "AC", "AAL", "BLNK"]
        for stock in self.portfolio:
            self.AddEquity(stock, Resolution.Hour)

        self.Schedule.On(self.DateRules.EveryDay("DAL"), self.TimeRules.AfterMarketOpen("DAL", 60), self.GetSource)
        self.Schedule.On(self.DateRules.EveryDay("DAL"), self.TimeRules.AfterMarketOpen("DAL", 2), self.checkIfBought)

    def OnData(self, data):
        self.arimax()

    def arimax(self):
        self.Debug("OnData")
        for stock in self.portfolio:
            if (stock != "BLNK"):

                data = self.History([stock], 45, Resolution.Hour)['close'].values

                d = 0

                p = adfuller(data)[1]

                if (p > 0.05):
                    first_diff = np.diff(data, 1)
                    first_diff = np.delete(first_diff, 0)

                    p = adfuller(first_diff)[1]

                    d = 1

                    if (p > 0.05):
                        d = 2

                self.arima = self.ARIMA(stock, 10, d, 10, 50)
                self.ar = self.ARIMA(stock, 1, 1, 0, 50)
                self.last = self.ar.Current.Value

                if self.arima.IsReady:
                    if abs(self.arima.Current.Value - self.ar.Current.Value) > 1:
                        difference = self.arima.Current.Value - self.last

                        if (abs(difference) > 7):

                            try:
                                # self.MarketOrder(stock, min( self.Portfolio.MarginRemaining, -(difference * volatility * 2000)/self.last))
                                self.SetHoldings(stock, difference * -(0.08 * volatility))
                                self.Debug(
                                    "Buying: " + str(stock) + "  " + str(min(0.33, difference * (0.08 * volatility))))

                            except:
                                self.Debug("Error buying")

                            # self.Debug(stock + " " + str(((-difference * volatility * 2000)/self.last)))
                            self.Debug(self.Portfolio.MarginRemaining)

                            isBought = True

                    self.last = self.arima.Current.Value

    def convert_to_datetime(self, string_date):
        return datetime.strptime(string_date, '%m/%d/%Y')

    def toInt(self, throughputString):
        return int(throughputString)

    def checkIfBought(self):
        stock = "BLNK"
        if (isBought is False):
            self.arima = self.ARIMA(stock, 10, 1, 10, 50)
            self.ar = self.ARIMA(stock, 1, 1, 0, 50)
            self.last = self.ar.Current.Value

            if self.arima.IsReady:
                difference = self.arima.Current.Value - self.last
                try:
                    self.Debug("Buying: " + str("BLNK") + " at end of day.")
                    self.MarketOnCloseOrder("BLNK", 1)
                    # self.Debug(stock + " " + str(20 * (difference * -(0.5 * volatility))))
                    self.Debug(self.Portfolio.MarginRemaining)
                except:
                    self.Debug("End of day buy failure")

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