from datetime import date, datetime, timedelta; today = date.today()
import pandas as pd
from ta.momentum import ROCIndicator
import yfinance

XLU = yfinance.download("XLU", start=today-timedelta(weeks=52), end=today)
VTI = yfinance.download("VTI", start=today-timedelta(weeks=52), end=today)
SPY = yfinance.download("SPY", start=today-timedelta(weeks=52), end=today)

dfOp = XLU.iloc[:,0] / VTI.iloc[:,0]
dfHi = XLU.iloc[:,1] / VTI.iloc[:,1]
dfLo = XLU.iloc[:,2] / VTI.iloc[:,2]
dfCl = XLU.iloc[:,3] / VTI.iloc[:,3]
dfAd = XLU.iloc[:,4] / VTI.iloc[:,4]
dfVo = XLU.iloc[:,5] / VTI.iloc[:,5]

dfRatio = pd.concat([dfOp, dfHi, dfLo, dfCl, dfAd, dfVo], axis=1)
dfRatio.columns = ['Open', 'High', 'Low', 'Close', 'Adjusted', 'Volume']

dfOp = ROCIndicator(close=dfRatio["Open"], n=20)
dfHi = ROCIndicator(close=dfRatio["High"], n=20)
dfLo = ROCIndicator(close=dfRatio["Low"], n=20)
dfCl = ROCIndicator(close=dfRatio["Close"], n=20)

dfRoc = pd.concat([dfOp, dfHi, dfLo, dfCl], axis=1)
dfRoc.columns = ['Open', 'High', 'Low', 'Close']

dfOp = pd.concat([dfRoc['Open']>=0, dfRoc['Open']<0], axis=1)
dfHi = pd.concat([dfRoc['High']>=0, dfRoc['High']<0], axis=1)
dfLo = pd.concat([dfRoc['Low']>=0, dfRoc['Low']<0], axis=1)
dfCl = pd.concat([dfRoc['Close']>=0, dfRoc['Close']<0], axis=1)
dfOp = dfOp.iloc[:,0].apply(int) - dfOp.iloc[:,1].apply(int)
dfHi = dfHi.iloc[:,0].apply(int) - dfHi.iloc[:,1].apply(int)
dfLo = dfLo.iloc[:,0].apply(int) - dfLo.iloc[:,1].apply(int)
dfCl = dfCl.iloc[:,0].apply(int) - dfCl.iloc[:,1].apply(int)

dfRet = pd.concat([SPY, dfRoc, dfSum], axis=1)
dfRet.index.name = 'Date'
dfRet.columns = ['Open','High','Low','Close','Adjusted','Volume','ROC.Open','ROC.High','ROC.Low','ROC.Close','Dbs']

dfRet['DbsMa'] = dfRet['Dbs'].rolling(7).mean()
