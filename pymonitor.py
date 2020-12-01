"""--------+---------+---------+---------+---------+---------+---------+---------+---------|
|                                C U S T O M   L I B R A R Y                               |
|----------+---------+---------+---------+---------+---------+---------+---------+-------"""
from pyfxgit.ChartCls import ChartCls
from ruamel.yaml import YAML
#-------------
# Data library
import pandas as pd
from ta.momentum import ROCIndicator
import yfinance
#-----------------
# Standard library
#   Gmail setup: https://myaccount.google.com/apppasswords
from datetime import date, datetime, timedelta; today = date.today()
from email.message import EmailMessage
import smtplib
import os

DBS_LIMIT = 3.75
DBS_PERIOD = 9   # previous 7
DBS_NEUTRAL = 'NEUTRAL'
DBS_BULL = 'BULLISH'
DBS_BEAR = 'BEARISH'

"""
| Get config
"""
def getConfig():
  yaml = YAML()
  #-----------------
  # Initial variable
  setting = ("""
    pymonitor:
      gmail: ""
      gmail_app_password: ""
  """)
  config = yaml.load(setting)

  #--------------------------------------
  # A YAML file supercedes os environment
  if os.path.exists("config.yaml"):
    with open("config.yaml") as f:
      config = yaml.load(f)
  #-------------------------
  # Read from os environment
  if not os.path.exists("config.yaml"):
    config["pymonitor"]["gmail"] = os.environ['INPUT_GMAIL']
    config["pymonitor"]["gmail_app_password"] = os.environ['INPUT_GMAIL_APP_PASSWORD']

  return config

"""
| Download data from yfinance
"""
def getSymbols():
  XLU = yfinance.download("XLU", start=today-timedelta(weeks=52), end=today)
  VTI = yfinance.download("VTI", start=today-timedelta(weeks=52), end=today)
  SPY = yfinance.download("SPY", start=today-timedelta(weeks=52), end=today)
  return XLU, VTI, SPY

"""
| Calculate ration XLU/VLI
"""
def calcRatio(XLU, VTI, SPY):
  dfOp = XLU.iloc[:,0] / VTI.iloc[:,0]
  dfHi = XLU.iloc[:,1] / VTI.iloc[:,1]
  dfLo = XLU.iloc[:,2] / VTI.iloc[:,2]
  dfCl = XLU.iloc[:,3] / VTI.iloc[:,3]
  dfAd = XLU.iloc[:,4] / VTI.iloc[:,4]
  dfVo = XLU.iloc[:,5] / VTI.iloc[:,5]
  dfRatio = pd.concat([dfOp, dfHi, dfLo, dfCl, dfAd, dfVo], axis=1)
  dfRatio.columns = ['Open', 'High', 'Low', 'Close', 'Adjusted', 'Volume']
  return dfRatio

"""
| Calculate rate of change from ta
"""
def calcRoc(dfRatio):
  taOp = ROCIndicator(close=dfRatio["Open"], n=20)
  taHi = ROCIndicator(close=dfRatio["High"], n=20)
  taLo = ROCIndicator(close=dfRatio["Low"], n=20)
  taCl = ROCIndicator(close=dfRatio["Close"], n=20)
  dfRoc = pd.concat([taOp.roc(), taHi.roc(), taLo.roc(), taCl.roc()], axis=1)
  dfRoc.columns = ['Open', 'High', 'Low', 'Close']
  return dfRoc

"""
| Calculate signal as sum of ROC(open), ROC(high), ROC(low), ROC(close)
"""
def calcSignal(dfRoc):
  dfOp = pd.concat([dfRoc['Open']>=0, dfRoc['Open']<0], axis=1)
  dfHi = pd.concat([dfRoc['High']>=0, dfRoc['High']<0], axis=1)
  dfLo = pd.concat([dfRoc['Low']>=0, dfRoc['Low']<0], axis=1)
  dfCl = pd.concat([dfRoc['Close']>=0, dfRoc['Close']<0], axis=1)
  dfOp = dfOp.iloc[:,0].apply(int) - dfOp.iloc[:,1].apply(int)
  dfHi = dfHi.iloc[:,0].apply(int) - dfHi.iloc[:,1].apply(int)
  dfLo = dfLo.iloc[:,0].apply(int) - dfLo.iloc[:,1].apply(int)
  dfCl = dfCl.iloc[:,0].apply(int) - dfCl.iloc[:,1].apply(int)
  dfSum = dfOp + dfHi + dfLo + dfCl
  return dfSum

"""
| Return Dataframe as concat of SPY, ROC and sum (Dbs)
"""
def calcDbs(SPY, dfRoc, dfSum):
  dfRet = pd.concat([SPY, dfRoc, dfSum], axis=1)
  dfRet.index.name = 'Date'
  dfRet.columns = ['Open','High','Low','Close','Adjusted','Volume','ROC.Open','ROC.High','ROC.Low','ROC.Close','Dbs']
  """
  | Calculate MA of sum (Dbs)
  |   Lower period = earlier shift
  """
  dfRet['DbsMa'] = dfRet['Dbs'].rolling(DBS_PERIOD).mean()
  return dfRet

"""
| Alert via E-Mail
"""
def alertDbs(dfRet):
  strSubject = ''
  strBody = ''
  NL = '\n'
  #------------------
  # Get last two rows
  #   Extract col Dbs
  dblPrev = dfRet.tail(2).iloc[0,:]['DbsMa']
  dblCurr = dfRet.tail(2).iloc[1,:]['DbsMa']
  #------------------------------------------
  # Case | Curr  | Prev  | Action
  #    1 | Same  | Same  | No Alert
  #    2 | White | Color | Alert Neutral Bias
  #    3 | Color | White | Alert Bull or Bear
  def strStatus(dblVal):
    strRet = DBS_NEUTRAL
    if dblVal >= DBS_LIMIT:
      strRet = DBS_BEAR
    elif dblVal <= -DBS_LIMIT:
      strRet = DBS_BULL
    return strRet
  
  strPrev = strStatus(dblPrev)
  strCurr = strStatus(dblCurr)
  #---------------
  # Case 1: 
  #   Return empty
  if strPrev == strCurr:
    return strSubject, strBody
  #---------------
  # Case 2: 
  #   Return alert
  if strCurr == DBS_NEUTRAL:
    strSubject = 'Dbs trend shift to NEUTRAL (bias to ' + strPrev + ')'
    strBody = "# " + strSubject + NL + NL
    strBody = strBody + "Date: " + str(today) + NL + NL
    strBody = strBody + "[Dbs Chart](https://github.com/dennislwm/pyaction/blob/master/_ChartC_0.1_Dbs.png)" + NL + NL
    strBody = strBody + "[Pyaction Repo](https://github.com/dennislwm/pyaction)"
  #---------------
  # Case 3: 
  #   Return alert
  if strPrev == DBS_NEUTRAL:
    strSubject = 'Dbs trend shift to ' + strCurr
    strBody = "# " + strSubject + NL + NL
    strBody = strBody + "Date: " + str(today) + NL + NL
    strBody = strBody + "[Dbs Chart](https://github.com/dennislwm/pyaction/blob/master/_ChartC_0.1_Dbs.png)" + NL + NL
    strBody = strBody + "[Pyaction Repo](https://github.com/dennislwm/pyaction)"
  
  return strSubject, strBody

"""
| Send E-Mail using Gmail
"""
def send_gmail(strSubject, strBody):
  config = getConfig()
  strGmail = config['pymonitor']['gmail']
  strGmailAppPwd = config['pymonitor']['gmail_app_password']

  if strGmail == '':
    return
  
  print("Send email " + strSubject) 
  msg = EmailMessage()
  msg['Subject'] = strSubject
  msg['From'] = strGmail
  msg['To'] = strGmail
  msg.set_content(strBody)
  with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(strGmail, strGmailAppPwd)
    smtp.send_message(msg)

"""
| Plot and save chart
"""
def plotChart(dfRet, strSuffix):
  chart = ChartCls(dfRet, intSub=2)
  chart.BuildOscillator(1, dfRet['Dbs'], intUpper=3, intLower=-3, strTitle="Dbs")
  chart.BuildOscillator(0, dfRet['DbsMa'], intUpper=DBS_LIMIT, intLower=-DBS_LIMIT, strTitle="DbsMa")
  lstTag = chart.BuildOscillatorTag(dfRet, 'DbsMa', DBS_LIMIT)
  chart.MainAddSpan(dfRet['Tag'], lstTag[lstTag>0], 0.2, 'red')
  chart.MainAddSpan(dfRet['Tag'], lstTag[lstTag<0], 0.2, 'green')
  chart.BuildMain(strTitle="SPY")
  """
  | Save chart
  """
  chart.save(strSuffix)
  print("Success: Saved chart")

"""--------+---------+---------+---------+---------+---------+---------+---------+---------|
|                                M A I N   P R O C E D U R E                               |
|----------+---------+---------+---------+---------+---------+---------+---------+-------"""
def main():
  getConfig()
  XLU, VTI, SPY = getSymbols()
  dfRatio = calcRatio(XLU, VTI, SPY)
  dfRoc = calcRoc(dfRatio)
  dfSum = calcSignal(dfRoc)
  dfRet = calcDbs(SPY, dfRoc, dfSum)
  plotChart(dfRet, "Dbs")
  strSubject, strBody = alertDbs(dfRet)
  if strSubject != '':
    send_gmail(strSubject, strBody)

if __name__ == "__main__":
  main()
