import requests
import pandas as pd
from functools import reduce
import statsmodels.api as sm
from config_manager import ConfigManager


class FactorModelBuilder:
    def __init__(self):
        config_manager = ConfigManager()
        self.api_key = config_manager.load_api_key('FMP','api_key')

    def _filter_dates(self, df:pd.DataFrame, return_frequency:str):
        if return_frequency == "M":
            df = df.sort_values('date')
            df = df.groupby(df['date'].dt.to_period('M'), as_index=False).last()
            return df
    
    def _download(self, symbol:str, monthly_frequency:str) -> pd.DataFrame:
        url = "https://financialmodelingprep.com/api/v3/historical-price-full/{}".format(symbol)

        params = {
            "serietype": "line",
            "apikey": self.api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        hist = data['historical']

        df = pd.DataFrame(hist)[::-1]
        df['symbol'] = symbol
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['date'])

        df = self._filter_dates(df, monthly_frequency)
        df['return'] = df['close'].pct_change(1)
        df = df[['date','return']]
        df.columns = ['date',symbol]
        return df.dropna()

    def build_factor_model(self, target_symbol:str, 
                           factor_symbols:list, 
                           data_start_date: str,
                           data_end_date: str,
                           return_frequency:str = "M"
                          ) -> None:
        dfs = []

        all_symbols = [target_symbol] + factor_symbols
    
        for symbol in all_symbols:
            df = self._download(symbol, return_frequency)
    
            df = df[['date', symbol]].copy()
            df['date'] = pd.to_datetime(df['date'])
    
            dfs.append(df)
    
        df = reduce(lambda left, right: pd.merge(left, right, on='date', how='inner'), dfs)
        df = df[(df['date'] >= data_start_date) & (df['date'] <= data_end_date)]
        
        self.factor_model_data = df
        self.target_symbol = target_symbol
        self.factor_symbols = factor_symbols

    def run_ols_regression(self):
        X = sm.add_constant(self.factor_model_data[self.factor_symbols])
        y = self.factor_model_data[self.target_symbol]
        model = sm.OLS(y,X)
        return model.fit(cov_type='HAC', cov_kwds={'maxlags': 3}).summary()
