from factor_model_builder import FactorModelBuilder
fmb = FactorModelBuilder()
fmb.build_factor_model(
        target_symbol = 'CCL',
        factor_symbols = ['SPY','VIXY'],
        data_start_date = '2021-05-07',
        data_end_date = '2026-05-07'
)
fmb.run_ols_regression()
