
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def convert_to_datetime(string_date):
    return datetime.strptime(string_date, '%m/%d/%Y')

def toInt(throughputString):
    return int(throughputString)

def main():
    source = "https://www.dropbox.com/s/1wo4t5ydkrzderr/throughput.csv?dl=1"
    header_list = ["Date", "Throughput"]
    df = pd.read_csv(source, names=header_list)

    # for index, row in df.iterrows():
    #     df['Date'] = datetime.strptime(df['Date'], '%m/%d/%Y')

    df["Date"] = df["Date"].apply(convert_to_datetime)
    df['Throughput'] = df["Throughput"].apply(toInt)
    df['Log returns'] = np.log(df['Throughput']/df['Throughput'].shift())

    df['Log returns'].std()


    x = datetime(2021, 7, 26)
    x = datetime(x.year, x.month, x.day, 0, 0, 0)
    x = x - timedelta(days=1)
    print(x)

    index = df.index
    condition = df["Date"] == x
    startDate = index[condition]
    indices = startDate.tolist()
    print(indices)


    volatility = df['Log returns'][indices[0]]
    print(volatility)

    print(df)


main()