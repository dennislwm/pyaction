from datetime import date, datetime, timedelta; today = date.today()
import pandas as pd
import yfinance

SPY = yfinance.download("SPY", start=today-timedelta(weeks=52), end=today)
if not SPY.empty:
  print("Downloaded SPY (" + str(len(SPY)) + " rows)")
else:
  print("Error in download")
 