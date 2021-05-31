import numpy as np


def calculate_ema(df, period):
  """
  Calculate the exponential moving average (EMA) of the close price over a given window/period

  Parameters:
  df (pd.DataFrame): Dataframe containing historical price data
  period (int): 
  """
  weights = np.arange(1, period + 1)
  ema = df['Close'].rolling(period).apply(
    lambda prices: np.dot(prices, weights)/weights.sum(), raw=True)
  return ema


def calculate_sma(df, period):
  """
  Calculate the simple moving average (SMA) of the close price over a given window/period
  """
  sma = df['Close'].rolling(period).apply(
    lambda prices: prices.mean(), raw=True)
  return sma


def calculate_macd(ema12, ema26):
  """
  Calculate the Moving average convergence divergence (MACD) value.

  Parameters: 
  ema12 (float, int, pd.Series, np.array): EMA12 value or values
  ema26 (float, int, pd.Series, np.array): EMA26 value or values

  Returns:
  macd (float, int, pd.Series, np.array): MACD value or values
  """
  return ema12 - ema26
