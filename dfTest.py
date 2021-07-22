
import pandas as pd
source = "https://www.dropbox.com/s/nuoi78pkna9956o/throughputTest.csv?dl=1"
header_list = ["Date", "Throughput"]
df = pd.read_csv(source, names=header_list)
df['Date'] = df['Date'].astype('datetime64[ns]')

print(df.head())
