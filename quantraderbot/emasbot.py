from re import S
from pandas.core.frame import DataFrame
import telegram
import config
from binance.client import Client
from binance.enums import * 
import time
import datetime
import telegram_send
from tradingview_ta import TA_Handler, Interval, Exchange
import numpy as np
import pandas as pd
import pandas_ta as pta
import matplotlib.pyplot as plt
import seaborn as sns
# import ta_lib

# pd.set_option('display.max_columns', None)  # or 1000
# pd.set_option('display.max_rows', None)  # or 1000

# Instanciando el cliente de binance
client = Client(config.API_KEY, config.API_SECRET, tld='com')

# Global Variables declarations
klingerbulls = ()
klingerbullsarray = []
klingerbears = ()
klingerbearsarray =[]
kvodfraw = pd.DataFrame()
kvodf = pd.DataFrame()
klinger = pd.DataFrame()



def analizecrypto(symbolTicker, candles, candlehist):

    if candles == '1d':
        candletype = Client.KLINE_INTERVAL_1DAY
    elif candles == '4h':
        candletype = Client.KLINE_INTERVAL_4HOUR
    elif candles == '1h':
        candletype = Client.KLINE_INTERVAL_1HOUR
    elif candles == '1w':
        candletype = Client.KLINE_INTERVAL_1WEEK
    elif candles == '1M':
        candletype = Client.KLINE_INTERVAL_1MONTH
    elif candles == '5m':
        candletype = Client.KLINE_INTERVAL_5MINUTE
    elif candles == '15m':
        candletype = Client.KLINE_INTERVAL_15MINUTE
    elif candles == '30m':
        candletype = Client.KLINE_INTERVAL_30MINUTE

    # candleType = candleType.trim('')
    print(candletype, candlehist)
    global kvodf

    ## Get historical candles data
    klines = client.get_historical_klines(symbolTicker, candletype, candlehist)
    print(len(klines))
    try:
        ## Create a dataframe with candle's data
        kvodfraw = pd.DataFrame(klines)
        print('index seteado')
        ## Validate if data is not empty
        if (len(klines) != 0): 
            print(symbolTicker)
            # print(mindf)
            ## Create columns in kvo dataframe from candle's dataframe
            kvodf['open'] = kvodfraw[1]
            kvodf['high'] = kvodfraw[2]
            kvodf['low'] = kvodfraw[3]
            kvodf['close'] = kvodfraw[4]
            kvodf['volume'] = kvodfraw[5]
            # print('Precios de apertura \n', kvodf)
            kvodf['timestamp'] = pd.to_datetime(kvodfraw[0], unit='ms')
            kvodf = kvodf.set_index(kvodf['timestamp'])
            ## Setting collumns dataframe object type as numeric type 
            kvodf['open'] = pd.to_numeric(kvodf['open'], errors='coerce')
            kvodf['high'] = pd.to_numeric(kvodf['high'], errors='coerce')
            kvodf['low'] = pd.to_numeric(kvodf['low'], errors='coerce')
            kvodf['close'] = pd.to_numeric(kvodf['close'], errors='coerce')
            kvodf['volume'] = pd.to_numeric(kvodf['volume'], errors='coerce')
            # print(kvodf['high'])
            kvodf = kvodf.drop(columns=['timestamp'], axis=1)
            kvodf.reset_index(drop=False, inplace = True)
            # print(kvodf.info(verbose=True))

            # Detecting Doji Candles
            doji = pta.cdl_doji(kvodf['open'], kvodf['high'], kvodf['low'], kvodf['close'])
            kvodf['isDoji'] = doji
            kvodf['isDoji'] = pd.to_numeric(kvodf['isDoji'], errors='coerce')
            # print('Updated with DOJI Candles data:\n', kvodf)

            ## Calculate klinger volume oscillator default, 34, 55, EMA 13
            klinger = pta.kvo(kvodf['high'], kvodf['low'], kvodf['close'], kvodf['volume'])
            # print('Klinger: %s' % (klinger))
            # print(klinger['KVO_34_55_13'])
            # print(klinger['KVOs_34_55_13'])

            # Adding klinger data to general dataframe
            kvodf['KVO'] = klinger['KVO_34_55_13']
            kvodf['KVOs'] = klinger['KVOs_34_55_13']
            kvodf['KVO'] = pd.to_numeric(kvodf['KVO'], errors='coerce')
            kvodf['KVOs'] = pd.to_numeric(kvodf['KVOs'], errors='coerce')

            # print('Updated with klinger  data:\n', kvodf)

            # Calculate RSI 
            rsi = pta.rsi(kvodf['close'], length=14)
            kvodf['rsi'] = rsi
            kvodf['rsi'] = pd.to_numeric(kvodf['rsi'], errors='coerce')                    
            # print('Updated with RSI data:\n', kvodf)

            # Calculate SMAs
            ema20 = pta.ema(kvodf['close'], 20)
            kvodf['ema_20'] = ema20
            kvodf['ema_20'] = pd.to_numeric(kvodf['ema_20'], errors='coerce')                    
            # print('Updated with EMA 20 data:\n', kvodf)

            ema55 = pta.ema(kvodf['close'], 55)
            kvodf['ema_55'] = ema55
            kvodf['ema_55'] = pd.to_numeric(kvodf['ema_55'], errors='coerce')                    
            # print('Updated with EMA 55 data:\n', kvodf) 
            
            ema200 = pta.ema(kvodf['close'], 200)
            kvodf['ema_200'] = ema200
            kvodf['ema_200'] = pd.to_numeric(kvodf['ema_200'], errors='coerce')                    
            # print('Updated with EMA 200 data:\n', kvodf)


            # Calculate Squeeze Momentum Indicator
            sqzmom = pta.squeeze(kvodf['high'], kvodf['low'], kvodf['close'])
            kvodf['SQZMOM'] = sqzmom['SQZ_20_2.0_20_1.5']
            kvodf['SQZMOM'] = pd.to_numeric(kvodf['SQZMOM'], errors='coerce')                    
            # print('Updated with SqueezeMomemtum data:\n', kvodf)


            ## Calculate ADX
            adx = pta.adx(kvodf['high'], kvodf['low'], kvodf['close'])
            kvodf[['ADX_14', 'ADX_DMP_14', 'ADX_DMN_14']] = adx[['ADX_14', 'DMP_14', 'DMN_14' ]]
            kvodf['ADX_14'] = pd.to_numeric(kvodf['ADX_14'], errors='coerce')                    
            kvodf['ADX_DMP_14'] = pd.to_numeric(kvodf['ADX_DMP_14'], errors='coerce')                    
            kvodf['ADX_DMN_14'] = pd.to_numeric(kvodf['ADX_DMN_14'], errors='coerce')                    
            # print('Updated with ADX data:\n', kvodf)

            # Calculate BollingerBands 
            bbands = pta.bbands(kvodf['close'], length=20, std=2, offset=0)
            kvodf[['BBL', 'BBM', 'BBU']] = bbands[['BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']]
            kvodf['BBL'] = pd.to_numeric(kvodf['BBL'], errors='coerce')
            kvodf['BBM'] = pd.to_numeric(kvodf['BBM'], errors='coerce') 
            kvodf['BBU'] = pd.to_numeric(kvodf['BBU'], errors='coerce')                     
            # print('Updated with BollingerBands data:\n', bbands)


           # Calculate CCI
            cci = pta.cci(kvodf['high'], kvodf['low'], kvodf['close'], length=20)
            kvodf['CCI'] = cci
            kvodf['CCI'] = pd.to_numeric(kvodf['CCI'], errors='coerce')                    
            # print('Updated with CCI data:\n', kvodf)


            ## Calculate Volume Weighted Average Price
            # vwap = pta.vwap(kvodf['high'], kvodf['low'], kvodf['close'], kvodf['volume'])
            # kvodf[['ADX_14', 'ADX_DMP_14', 'ADX_DMN_14']] = vwap[['ADX_14', 'DMP_14', 'DMN_14' ]]
            # kvodf['ADX_14'] = pd.to_numeric(kvodf['ADX_14'], errors='coerce')                                    
            # print('Updated with VWAP data:\n', vwap)
                
        return kvodf

    except Exception as e:
        print(e)

def isDoji(isDojidata):
    print(isDojidata)
    for k in range(1,5):
        doji = isDojidata.iloc[-k]
        if doji == 100: return True
    print(doji)
    return False

 ### This section is for data analizing ###
##########################################

i = True
while i == True:
    try:
        ## Getting all tickers
        listoftickers = client.get_all_tickers()
        doji = []
        # symbolTicker = ''
        # btcdom = client.get_ticker('BTCUSDT')
        # print(btcdom)
        alltickers = len(listoftickers)
        # telegram_send.send(messages=[" \U0001F4C8 \U0001F4C9 \U0001F4CA" + 
        #                              "\n\n Vamos a analizar las " + str(alltickers) + 
        #                              " cryptos que hay en Binance al día de hoy." + 
        #                             #  "\n Tiempo sugerido para el trade es de 1 a 2 horas." +
        #                             #  "\n Para buscar entrada usa bandas de bollinger en grafico de 15 MINUTES."
        #                              "\n Para buscar entrada usa bandas de bollinger en grafico de 4 HORAS."
        #                             #  "\n Para buscar entrada usa bandas de bollinger en grafico de 1 HORA."
        #                             #  "\n Para buscar entrada usa bandas de bollinger en grafico DIARIO."
        #                             #  "\n Para buscar entrada usa bandas de bollinger en grafico SEMANAL."
        #                              "\n\n \U0001F4C8 \U0001F4C9 \U0001F4CA"])
        cryptodata = pd.DataFrame()
        for tick in listoftickers:
            symbolTicker = tick['symbol']
            print(symbolTicker)
            # if symbolTicker[-3:] != 'ETH' and symbolTicker[-3:] != 'BTC' and symbolTicker[-4:] != 'USDT': continue
            if symbolTicker[-4:] != 'USDT': continue
            # if symbolTicker[-3:] != 'BTC': continue
            
            # cryptodata = analizecrypto(symbolTicker, '1d' , "18 months ago UTC")
            # cryptodata = analizecrypto(symbolTicker, '1w' , "24 months ago UTC")
            cryptodata = analizecrypto(symbolTicker, '4h' , "6 months ago UTC")
            # cryptodata = analizecrypto(symbolTicker, '1h' , "4 months ago UTC")
            # cryptodata = analizecrypto(symbolTicker, '15m' , "8 days ago UTC")
            # cryptodata = cryptodata.dropna()
            print ('data \n', cryptodata)
            # Detecting doji pattern in the last 3 candles
            try: 
                isdoji = isDoji(cryptodata['isDoji'])
                print('Some of Last 3 daily candles is a doji: ', isdoji)
                print('\n\n')
            except:
                print('Cannot Calculate if there is a doji')
            

            try: 
                rsi = cryptodata['rsi'].iloc[-1]
                print(rsi)

            except:
                print('Cannot Calculate if there is a doji')

            # # # check if crypto assets is oversell
            if rsi > 0.0: 

                try: 
                    ## Calculate distance bw klinger and signal in %
                    kgrsigdist = 100 * ( 1 - np.abs((cryptodata['KVO'].iloc[-1])/(cryptodata['KVOs'].iloc[-1])) )
                    print('distancia entre klinger y señal:  %s' % (kgrsigdist))
                except:
                    print('Cannot calculate distance between klinger ans signal')
                try:
                    ## Calculate distance ema20 and las close price in %
                    dist_closema20 = 100 * ( 1 - np.abs((cryptodata['ema_20'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la ema 20 y el precio es:  %s' % (dist_closema20))
                except:
                    print('Cannot calculate distance between ema20 and last close price')
                try:
                    ## Calculate distance ema55 and las close price in %
                    dist_closema55 = 100 * ( 1 - np.abs((cryptodata['ema_55'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la ema 55 y el precio es:  %s' % (dist_closema55))
                except:
                    print('Cannot calculate distance between ema55 and last close price')

                ## Calculate distance BBU and Close Price
                try:
                    if cryptodata['BBU'].iloc[-1] == cryptodata['BBL'].iloc[-1] and cryptodata['BBU'].iloc[-1] == cryptodata['BBM'].iloc[-1]: continue
                    dist_closebbu = 100 * ( 1 - np.abs((cryptodata['BBU'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la Bolliger up y el precio es:  %s' % (dist_closebbu))
                    dist_closebbl = 100 * ( 1 - np.abs((cryptodata['BBL'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la bollinger low y el precio es:  %s' % (dist_closebbl))
                    dist_closebbm = 100 * ( 1 - np.abs((cryptodata['BBM'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la bollinger mid y el precio es:  %s' % (dist_closebbm))
                except:
                    print('Cannot calculate distance between bollinger bands and last close price')

                try:

                    # if dist_closebbl > -0.1 and dist_closebbl < 0.1:
                    # if dist_closebbl > -10 and dist_closebbl < 10:
                    if np.abs(dist_closema20) > 0 and np.abs(dist_closema20) < 1.0 and cryptodata['close'].iloc[-1] > cryptodata['ema_20'].iloc[-1]:
                    # if np.abs(dist_closema55) > 0 and np.abs(dist_closema55) < 50.0:
                    # if np.abs(dist_closema55) > 0 and np.abs(dist_closema55) < 5.0 and cryptodata['SQZMOM'].iloc[-1] > 1.0 and cryptodata['ADX_14'].iloc[-1] > 25.0:
                    # if np.abs(dist_closema20) > 0 and np.abs(dist_closema20) < 30.0 and cryptodata['SQZMOM'].iloc[-1] < 0 and cryptodata['ADX_14'].iloc[-1] < 23:
                    # if np.abs(dist_closema55) < 2 and cryptodata['SQZMOM'].iloc[-1] > 0 and cryptodata['ADX_14'].iloc[-1] > 27:
                    # if np.abs(kgrsigdist) > 0.0 and np.abs(kgrsigdist) < 5.0 and (cryptodata['KVO'].iloc[-2] < cryptodata['KVOs'].iloc[-1]):
                        # if cryptodata['KVO'].iloc[-2] < cryptodata['KVOs'].iloc[-2] and cryptodata['KVO'].iloc[-1] > cryptodata['KVOs'].iloc[-1]:
                        print('Oportunidad de compra: %s, at price: %s' % (symbolTicker, cryptodata['close'].iloc[-1]))
                        klingerbullsarray.append(symbolTicker)
                        # telegram_send.send(messages=["REVISA EL PRECIO DE \n" + "******* " + symbolTicker + "\nDistancia a la EMA20: " + np.abs(dist_closema20) + "%" + "\nPrecio de Cierre: " + cryptodata['close'].iloc[-1] + "\n\n" ])
                        # analizedcrypto = (symbolTicker, dist_closebbl, cryptodata['close'].iloc[-1], cryptodata['ema_20'].iloc[-1], np.abs(dist_closema20), cryptodata['rsi'].iloc[-1], cryptodata['isDoji'].iloc[-1], cryptodata['SQZMOM'].iloc[-1], cryptodata['ADX_14'].iloc[-1], np.abs(kgrsigdist))
                        tickerSymbolTA = TA_Handler(
                            symbol=symbolTicker,
                            screener="crypto",
                            exchange="binance",
                            interval=Interval.INTERVAL_15_MINUTES
                        )
                        recommend = tickerSymbolTA.get_analysis().oscillators.get('COMPUTE')['CCI']
                        print('recommend')
                        analizedcryptobb = (symbolTicker, recommend, dist_closebbl, cryptodata['close'].iloc[-1], cryptodata['BBL'].iloc[-1], cryptodata['BBM'].iloc[-1], cryptodata['BBU'].iloc[-1])
                        with open('klingerbullsemas.list', 'a') as klingerbearslist:
                            klingerbearslist.write(str(analizedcryptobb))
                            klingerbearslist.write('\n')
                            klingerbearslist.close()
                        closeprice = cryptodata['close'].iloc[-1]
                        stoplosslow = round((cryptodata['low'].iloc[-1])*0.985, 5)
                        rsi = round(cryptodata['rsi'].iloc[-1], 5)
                        sqz = round(cryptodata['SQZMOM'].iloc[-1], 5)
                        adx = round(cryptodata['ADX_14'].iloc[-1], 5)
                        bbl = round(cryptodata['BBL'].iloc[-1], 5)
                        bbu = round(cryptodata['BBU'].iloc[-1], 5)
                        bbm = round(cryptodata['BBM'].iloc[-1], 5)
                        cci = round(cryptodata['CCI'].iloc[-1], 5)
                        print(cci)

                        # if cci < -150.0:
                        # if recommend == 'BUY' or recommend == 'STRONG_BUY':
                            # telegram_send.send(messages=[" \U00002B06 \U00002B06 LONG/COMPRA en: " + 
                            #                             symbolTicker + 
                            #                             # "\n TradingView dice: " + recommend +
                            #                             "\n\n Entrada en: " + str(bbl) + 
                            #                             "\n STOPLOSS: " + str(stoplosslow) +
                            #                             "\n\n cierra 75% de la posición en: " + str(bbm) +
                            #                             "\n Y sube SL a precio de entrada"
                            #                             "\n\n Cierra-100% en: " + str(bbu)])
                        # telegram_send.send(messages=["Valle verde!!" + "\nPrecio cerca de la EMA55:  " + symbolTicker + "\nSQZ= " + str(sqz) + "\nADX" + str(adx) + "\nPrice= " + str(closeprice) ])
                        # telegram_send.send(messages=["Precio en la EMA20:  " + symbolTicker + "\nRSI= " + str(rsi) + "\nPRICE= " + str(closeprice) ])
                except: 
                    print('There is not enought data to calculate EMAs')
           
            #######################################
            ##### check if crypto assets is overbuy
            if rsi > 0.0: 

                try: 
                    ## Calculate distance bw klinger and signal in %
                    kgrsigdist = 100 * ( 1 - np.abs((cryptodata['KVO'].iloc[-1])/(cryptodata['KVOs'].iloc[-1])) ) 
                    print('distancia entre klinger y señal:  %s' % (kgrsigdist))
                except:
                    print('Cannot calculate distance between klinger ans signal')
                try:
                    ## Calculate distance ema20 and las close price in %
                    dist_closema20 = 100 * ( 1 - np.abs((cryptodata['ema_20'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la ema 20 y el precio es:  %s' % (dist_closema20))
                except:
                    print('Cannot calculate distance between ema20 and last close price')
                try:
                    ## Calculate distance ema55 and las close price in %
                    dist_closema55 = 100 * ( 1 - np.abs((cryptodata['ema_55'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la ema 55 y el precio es:  %s' % (dist_closema55))
                except:
                    print('Cannot calculate distance between ema55 and last close price')
                # ## Calculate distance BBU and Close Price
                try:
                    if cryptodata['BBU'].iloc[-1] == cryptodata['BBL'].iloc[-1] and cryptodata['BBU'].iloc[-1] == cryptodata['BBM'].iloc[-1]: continue
                    dist_closebbu = 100 * ( 1 - np.abs((cryptodata['BBU'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la Bolliger up y el precio es:  %s' % (dist_closebbu))
                    dist_closebbl = 100 * ( 1 - np.abs((cryptodata['BBL'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la bollinger low y el precio es:  %s' % (dist_closebbl))
                    dist_closebbm = 100 * ( 1 - np.abs((cryptodata['BBM'].iloc[-1])/(cryptodata['close'].iloc[-1])) ) 
                    print('distancia entre la bollinger mid y el precio es:  %s' % (dist_closebbm))
                except:
                    print('Cannot calculate distance between bollinger bands and last close price')


                try:
                    # if dist_closebbu in range [0.0, 1.0]:
                    # if np.abs(dist_closebbu) > -0.1 and np.abs(dist_closebbu) < 0.1:
                    # if np.abs(dist_closebbu) > -10 and np.abs(dist_closebbu) < 10:
                    if np.abs(dist_closema55) > 0 and np.abs(dist_closema55) < 1.0 and cryptodata['close'].iloc[-1] > cryptodata['ema_55'].iloc[-1]:
                    # if np.abs(dist_closema20) > 0 and np.abs(dist_closema20) < 2.0:
                    # if np.abs(dist_closema20) < 10 and cryptodata['SQZMOM'].iloc[-1] < 0 and cryptodata['ADX_14'].iloc[-1] < 23.0:
                    # if np.abs(dist_closema55) < 5 and cryptodata['SQZMOM'].iloc[-1] > 0 and cryptodata['ADX_14'].iloc[-1] > 27:
                    # if np.abs(dist_closema55) > -5.0 and np.abs(dist_closema55) < 5.0 and cryptodata['SQZMOM'].iloc[-1] > 1.0 and cryptodata['ADX_14'].iloc[-1] > 25.0:
                    # if np.abs(dist_closebbu) > 0 and np.abs(dist_closebbu) < 1.0:
                    # if np.abs(kgrsigdist) > 0.0 and np.abs(kgrsigdist) < 5.0 and (cryptodata['KVO'].iloc[-2] > cryptodata['KVOs'].iloc[-1]):
                        # if cryptodata['KVO'].iloc[-2] < cryptodata['KVOs'].iloc[-2] and cryptodata['KVO'].iloc[-1] > cryptodata['KVOs'].iloc[-1]:
                        print('Oportunidad de compra: %s, at price: %s' % (symbolTicker, cryptodata['close'].iloc[-1]))
                        klingerbearsarray.append(symbolTicker)
                        # analizedcrypto = (symbolTicker, dist_closebbu, cryptodata['close'].iloc[-1], cryptodata['ema_20'].iloc[-1], np.abs(dist_closema20), cryptodata['rsi'].iloc[-1], cryptodata['isDoji'].iloc[-1], cryptodata['SQZMOM'].iloc[-1], cryptodata['ADX_14'].iloc[-1], np.abs(kgrsigdist))
                        tickerSymbolTA = TA_Handler(
                            symbol=symbolTicker,
                            screener="crypto",
                            exchange="binance",
                            interval=Interval.INTERVAL_15_MINUTES
                        )
                        recommend = tickerSymbolTA.get_analysis().oscillators.get('COMPUTE')['CCI']
                        print('recommend')
                        analizedcryptobb = (symbolTicker, recommend, dist_closebbl, cryptodata['close'].iloc[-1], cryptodata['BBU'].iloc[-1], cryptodata['BBM'].iloc[-1], cryptodata['BBL'].iloc[-1])

                        with open('klingerbearsemas.list', 'a') as klingerbearslist:
                            klingerbearslist.write(str(analizedcryptobb))
                            klingerbearslist.write('\n')
                            klingerbearslist.close()
                        closeprice = cryptodata['close'].iloc[-1]
                        stoplosshigh = round((cryptodata['high'].iloc[-1])*1.015, 5)
                        rsi = round(cryptodata['rsi'].iloc[-1], 5)
                        sqz = round(cryptodata['SQZMOM'].iloc[-1], 5)
                        adx = round(cryptodata['ADX_14'].iloc[-1], 5)
                        bbl = round(cryptodata['BBL'].iloc[-1], 5)
                        bbu = round(cryptodata['BBU'].iloc[-1], 5)
                        bbm = round(cryptodata['BBM'].iloc[-1], 5)
                        cci = round(cryptodata['CCI'].iloc[-1], 5)
                        print(cci)

                        # if recommend == 'SELL' or recommend == 'STRONG_SELL':
                        # if cci > 150.0:
                        #     print(cci)
                        #     telegram_send.send(messages=[" \U00002B07 \U00002B07 SHORT/VENTA en: " +
                        #                                 symbolTicker + 
                        #                                 # "\n TradingView dice: " + recommend +
                        #                                 "\n\n Entrada en: " + str(bbu) + 
                        #                                 "\n STOPLOSS: " + str(stoplosshigh) +
                        #                                 "\n\n Take Profit 75% en: " + str(bbm) +
                        #                                 "\n Y sube SL a precio de entrada"
                        #                                 "\n\n Cierra-100% en: " + str(bbl)])
                        # telegram_send.send(messages=["Valle verde!!" + "\nPrecio cerca de la EMA55:  " + symbolTicker + "\nSQZ= " + str(sqz) + "\nADX= " + str(adx) + "\nPrice= " + str(closeprice) ])
                        # telegram_send.send(messages=["Precio cerca de la EMA20:  " + symbolTicker + "\nRSI= " + str(rsi) + "\nPRICE= " + str(closeprice) ])

                except: 
                    print('There is not enought data to calculate EMAs')
        print(klingerbearsarray) 
        print(klingerbullsarray)

    except: 
        print('Hubo un error inesperado con el api de Binance')
    print('Se analizaron todas las cripto, revisamos en 300 segundos!!!')
    # telegram_send.send(messages=["\n ᕙ(⇀‸↼‶)ᕗ [̲̅$̲̅(̲̅5̲̅)̲̅$̲̅] ᕙ(⇀‸↼‶)ᕗ [̲̅$̲̅(̲̅5̲̅)̲̅$̲̅] \n"
    #                              "\n SE ANALIZARON TODAS LAS CRYPTO de BINANCE, REVISAMOS DE NUEVO EN 300 SEGUNDOS!!" 
    #                              "\n\n \U000023F2 \U000023F2" ])

    time.sleep(300)
    # i = False

