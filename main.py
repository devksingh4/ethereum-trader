# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import cbpro
import time
import sys
import pandas as pd
from auth import Credentials
from values import granularities
from technical import calculate_ema, calculate_macd
# %%

class MACDTrader:
    def __init__(self, macd_signal: float, auth: dict):
      self.cbclient: cbpro.PublicClient = cbpro.PublicClient()
      self.data: dict= dict.fromkeys(granularities)
      self.granularities: dict = granularities
      self.final_granularity: int = ''
      self.macd_signal: float = macd_signal
      self.update_data()
    def update_data(self) -> None:
      """Get data from CB Pro API"""
      print("Updating data...")
      for g in self.granularities:
        self.data[g] = pd.DataFrame(self.cbclient.get_product_historic_rates(
            'ETH-DAI', granularity=granularities[g]))
        self.data[g].columns = ['Time', 'Low',
                                'High', 'Open', 'Close', 'Volume']

    def run_strategy(self) -> int:
      """
      Define trading strategy here that will be run on each time step.
      
      Parameters:
      None

      Returns:
      action (float): trading action to take (1 is buy, 0 is hold, -1 is sell)
      """
      print("Performing analysis...")
      self.ema12, self.ema26, self.macd = dict.fromkeys(
          granularities), dict.fromkeys(granularities), dict.fromkeys(granularities)
      self.ema12['1-HR'] = calculate_ema(self.data['1-HR'], period=12)
      self.ema26['1-HR'] = calculate_ema(self.data['1-HR'], period=26)
      self.ema12['6-HR'] = calculate_ema(self.data['6-HR'], period=12)
      self.ema26['6-HR'] = calculate_ema(self.data['6-HR'], period=26)
      last_ema26_6hr: float= self.ema26['6-HR'].iat[-1]
      last_ema26_1hr: float = self.ema26['1-HR'].iat[-1]
      if last_ema26_1hr < last_ema26_6hr:
        self.final_granularity = '1-HR'
      else:
        self.final_granularity = '15-MIN'
        self.ema12['15-MIN'] = calculate_ema(
            self.data['15-MIN'], period=12)
        self.ema26['15-MIN'] = calculate_ema(
            self.data['15-MIN'], period=26)
      ema12: pd.Series = self.ema12[self.final_granularity]
      ema26: pd.Series = self.ema26[self.final_granularity]
      last_ema26: float = ema26.iat[-1]
      last_ema12: float = ema12.iat[-1]
      last_macd: float = calculate_macd(last_ema12, last_ema26)
      if last_macd > self.macd_signal:
        return 1
      elif last_macd < -1 * self.macd_signal:
        return -1
      else:
        return 0

    def execute_trade(self, action: int, creds: Credentials, amount: float = 1.0) -> None:
        """
        Contact the Coinbase API and execute the trade
        """
        side = 'buy' if action == 1 else 'sell'
        print(f"Executing {side}...")
        self.authclient = cbpro.AuthenticatedClient(*creds.getCreds())
        if action == 0:
          return False
        dai_account = list(filter(lambda x: x['currency'] == 'DAI', self.authclient.get_accounts()))[0]
        eth_account = list(filter(lambda x: x['currency'] == 'ETH', self.authclient.get_accounts()))[0]
        dai_avail = amount * float(dai_account['available'])
        eth_avail = amount * float(eth_account['available'])
        if dai_avail < 10.00:
          print("Not enough funds available to transact. Need at least 10 DAI.")
          return
        resp = ''
        if side == 'buy':
          resp = self.authclient.place_market_order(product_id='ETH-DAI', side=side, funds=dai_avail)
          print(f'Placed {side} order of {dai_avail} DAI!')
        elif side == 'sell':
          resp = self.authclient.place_market_order(product_id='ETH-DAI', side=side, funds=eth_avail)
          print(f'Placed {side} order of {eth_avail} ETH!')
        return resp

# %%
print("Starting trader...")
trader: MACDTrader = MACDTrader(macd_signal=3, auth={})
authDetails: Credentials = Credentials('auth.json')
print("Trader started!")
try:
  while True:
    trader.update_data()
    action: int = trader.run_strategy()
    trader.execute_trade(action, creds=authDetails)
    print("Sleeping for 15 minutes...")
    time.sleep(60 * 15)  # 15-min is the lowest update point
except KeyboardInterrupt:
  print('Exiting!')
  sys.exit(0)