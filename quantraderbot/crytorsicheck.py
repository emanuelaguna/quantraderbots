from pandas.core.frame import DataFrame
import config
from binance.client import Client
from binance.enums import * 
import time
import datetime
import numpy as np
import pandas as pd
import pandas_ta as pta
import matplotlib.pyplot as plt
import seaborn as sns
# pd.set_option('display.max_columns', None)  # or 1000
# pd.set_option('display.max_rows', None)  # or 1000

client = Client(config.API_KEY, config.API_SECRET, tld='com')
minimumrsicryptosobrecomprado = ()
minimumrsicryptosobrecompradoarray = []
minimumrsicryptosobrevendido = ()
minimumrsicryptosobrevendidoarray =[]
mindf = pd.DataFrame()
listoftickers = client.get_all_tickers()
for tick in listoftickers:
    # if tick['symbol'][-4:] == 'USDT' or tick['symbol'][-3:] == 'BTC':
    if tick['symbol'][-3:] == 'BTC':
        klines = client.get_historical_klines(tick['symbol'], Client.KLINE_INTERVAL_1DAY, "3 months ago UTC")
        # print(len(klines))
        try:
            mindf = pd.DataFrame(klines)
            mindf.index = pd.to_datetime(mindf[0], unit='ms')
            mindf = mindf.drop(columns=[0], axis=1)
            if (len(klines) != 0): 
                print(tick['symbol'])
                # print(mindf)
                mindf[4] = pd.to_numeric(mindf[4], errors='coerce')
                minrsitick = pta.rsi(mindf[4], length=14)
                print(minrsitick.tail(1))
                if ( minrsitick.tail(1)[0] <= 50 ): 
                    print('RSI Sobrevendido: %s' % (minrsitick.tail(1)[0]))
                    minimumrsicryptosobrevendido = (tick['symbol'],minrsitick.tail(1)[0])
                    minimumrsicryptosobrevendidoarray.append(minimumrsicryptosobrevendido)

                elif ( minrsitick.tail(1)[0] >= 50.1 ): 
                    print('RSI Sobrecomprado: %s' % (minrsitick.tail(1)[0]))
                    minimumrsicryptosobrecomprado = (tick['symbol'],minrsitick.tail(1)[0])
                    minimumrsicryptosobrecompradoarray.append(minimumrsicryptosobrecomprado)

        except Exception as e:
            print(e)
print (minimumrsicryptosobrevendidoarray)
print (minimumrsicryptosobrecompradoarray)

