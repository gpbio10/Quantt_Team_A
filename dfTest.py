
import pandas as pd
import numpy as np
import datetime

source = "https://www.dropbox.com/s/nuoi78pkna9956o/throughputTest.csv?dl=1"
header_list = ["Date", "Throughput"]
df = pd.read_csv(source, names=header_list)
# df['Date'] = df['Date'].astype('datetime64[ns]')

for index, row in df.iterrows():
    date_time_obj = datetime.datetime.strptime(row['Date'], '%m/%d/%Y')
    row['Date'] = date_time_obj
    row['Throughput'] = float(row['Throughput'].replace(',', ''))
#
df['Log returns'] = np.log(df['Throughput']/df['Throughput'].shift())

df['Log returns'].std()

print(df.head())
