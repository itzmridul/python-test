from datetime import date
from nsepy import get_history
import pandas as pd
import numpy as np
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file

def SMA(ohlc, period=4, column="Close"):
    return pd.Series(ohlc[column].rolling(center=False, window=period, min_periods=period).mean(),name="SMA")

def into_week(df):
    df.reset_index(level='Date', inplace=True)
    df = df.apply(pd.to_numeric, errors='ignore')
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df['timeseries'] = df.index
    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum', 'timeseries': 'last'}
    df2 = df.resample('W-Fri').apply(ohlc_dict)
    df2.reset_index(level='Date', inplace=True)
    df2['Date'] = df2['timeseries']
    df2.set_index('Date', inplace=True)
    df['MA_4'] = SMA(df2,4)
    df['MA_16'] = SMA(df2, 16)
    df['MA_28'] = SMA(df2, 28)
    df['MA_40'] = SMA(df2, 40)
    df['MA_52'] = SMA(df2, 52)
    df['Volume_Shock'] = pd.Series(np.where(((df['Volume']-df['Volume'].shift())/df['Volume'].shift())>0.1,1,np.where(((df['Volume']-df['Volume'].shift())/df['Volume'].shift())<-0.1,1,0)), index=df.index, name="Volume_Shock")
    df['Volume_direc'] = pd.Series(np.where(((df['Volume'] - df['Volume'].shift()) / df['Volume'].shift()) > 0.1, 1,np.where(((df['Volume'] - df['Volume'].shift()) / df['Volume'].shift()) < -0.1,0, np.nan)), index=df.index, name="Volume_direc")
    df['Price_Shock'] = pd.Series(np.where(((df['Close'] - df['Close'].shift()) / df['Close'].shift()) > 0.02, 1,np.where(((df['Close'] - df['Close'].shift()) / df['Close'].shift()) < -0.02,1,0)), index=df.index, name="Price_Shock")
    df['Price_direc'] = pd.Series(np.where(((df['Close'] - df['Close'].shift()) / df['Close'].shift()) > 0.02, 1,np.where(((df['Close'] - df['Close'].shift()) / df['Close'].shift()) < -0.02,0,np.nan)), index=df.index, name="Price_direc")
    df['Shock_without_volume'] = pd.Series(np.where( (df['Price_Shock']==1) & (df['Volume_Shock']==0) ,1,0), index=df.index, name="Shock_without_volume")
    return (df[['Open','High','Low','Close','Volume','MA_4','MA_16','MA_28','MA_40','MA_52','Volume_Shock','Volume_direc','Price_Shock','Price_direc','Shock_without_volume']])


if __name__=='__main__':
    symbol = input('Enter symbol of any stock : ')
    data = get_history(symbol=symbol, start=date(2015,1,1), end=date(2016,12,31))
    data = data[['Open','High','Low','Close','Volume']]
    #sbin['sma']=SMA(sbin,2)
    df=(into_week(data))
    #print(sbin)
    output_file("index.html")
    p1 = figure()
    p1 = figure(x_axis_type="datetime", title="Stock Closing Prices")
    p1.grid.grid_line_alpha = 0.3
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Price'
    p1.line(df.index, df['Close'], color='#A6CEE3', legend=symbol)
    p1.circle(df.index, np.where(df['Shock_without_volume']==1,df['Close'],np.nan), size=4, color='red', alpha=1)
    show((p1))
