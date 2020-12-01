from pymonitor import getSymbols, calcRatio, calcRoc, calcSignal, calcDbs, plotChart

def test_all():
  XLU, VTI, SPY = getSymbols()
  assert len(XLU) > 100
  assert len(VTI) > 100
  assert len(SPY) > 100
  dfRatio = calcRatio(XLU, VTI, SPY)
  assert len(dfRatio) > 100
  dfRoc = calcRoc(dfRatio)
  assert len(dfRoc) > 100

def test_plotChart():
  pass

"""--------+---------+---------+---------+---------+---------+---------+---------+---------|
|                                M A I N   P R O C E D U R E                               |
|----------+---------+---------+---------+---------+---------+---------+---------+-------"""
def main():
  test_all()
  test_plotChart()

if __name__ == "__main__":
  main()
