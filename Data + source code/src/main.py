import ast
import pandas as pd

import json
from src.backtest_types.db_series import DBSeries
from src.backtest_types.roll_options import RollOptions
from src.exceptions import BacktestFactoryException

__all__ = ['BacktestFactory', 'get_schema', 'get_types', 'run_backtest']

CLASS_MAPPINGS = {
    'DBSeries': DBSeries,
    'RollOptions': RollOptions
}


class BacktestFactory(object):

    def run_backtest(self, conf):
        if 'Type' not in conf:
            raise BacktestFactoryException('Backtest type should be specified')

        if conf['Type'] not in CLASS_MAPPINGS:
            raise BacktestFactoryException('Unknown backtest type: %s' % conf['Type'])

        if 'Underlyings' in conf:
            for i in range(len(conf['Underlyings'])):
                if 'Index' not in conf['Underlyings'][i]:
                    raise BacktestFactoryException('Component backtest information should be specified')
                conf['Underlyings'][i]['Object'] = self.run_backtest(conf['Underlyings'][i]['Index'])

        bt_obj = CLASS_MAPPINGS[conf['Type']]()

        bt_obj.run(conf)

        return bt_obj


def get_schema(bt_type):
    if bt_type not in CLASS_MAPPINGS:
        raise BacktestFactoryException('Unknown backtest type: %s' % bt_type)

    return CLASS_MAPPINGS[bt_type].schema()


def get_types():
    return list(CLASS_MAPPINGS.keys())


def run_backtest(conf):
    return BacktestFactory().run_backtest(conf)


if __name__ == '__main__':

    from datetime import datetime as dt
    import os

    config_path = 'input_configuration_deltastrike_fixed_notional.json'

    dict_month_choice = {'1m': 20,
                         '3m': 60,
                         '6m': 125,
                         '9m': 185,
                         '1y': 250}

    udl_choice = "SPX Index"
    for month_choice in ['1m', '3m', '6m', '9m']:
        putratio_no_cost = f"Putratio_no_cost_{month_choice}"
        putratio_with_cost = f"Putratio_cost_{month_choice}"
        new_dump_folder = os.path.abspath(os.path.join('..'))
        for path_append in ['RESULTS', f"DeltaStrike_backtests Fixed notional_{udl_choice}"]:
            new_dump_folder = os.path.join(new_dump_folder, path_append)
            if not os.path.exists(new_dump_folder):
                os.mkdir(new_dump_folder)

        if not os.path.exists(new_dump_folder):
            os.mkdir(new_dump_folder)

        all_backtests = [putratio_with_cost]

        for backtest_name in all_backtests:

            with open(config_path) as config_file:
                content = config_file.read()
                try:
                    dict_json = json.load(config_file)
                except (ValueError, TypeError):
                    content = content.replace('true', 'True').replace('false', 'False')
                    dict_json = ast.literal_eval(content)
                configuration = dict_json['Configurations'][0]['Index'] if 'Configurations' in dict_json else dict_json

            if udl_choice != "SPX Index":
                configuration["Underlyings"][0]["Index"]["Name"] = udl_choice
                configuration["Underlyings"][1]["Index"]["Name"] = "SGBVRVG1 Index" if udl_choice == "SX5E Index" else "SGBVRNK1 Index"
                configuration['Calendar']['Holidays'] = "SX5E_TRD" if udl_choice == "SX5E Index" else "RITOK"

            # change start and end date
            volatilities_df = pd.read_hdf(os.path.abspath(os.path.join("..", "Data_cache.h5")),
                                          key="implied_volatility_data").fillna(method='ffill')
            volatilities_df.columns = pd.MultiIndex.from_tuples(list(map(eval, volatilities_df.columns)))
            volatilities_df = volatilities_df
            configuration['Calendar']['LaunchDate'] = f'{volatilities_df.index[0].year + 1}-01-01'
            configuration['Calendar']['EndDate'] = volatilities_df.index[-1].strftime("%Y-%m-%d")

            if 'Putratio' in backtest_name:
                put_1_strike = int(configuration['Parameters']['Groups'][0]['DeltaStrike'] * 100)
                put_2_strike = int(configuration['Parameters']['Groups'][1]['DeltaStrike'] * 100)
                long_short_1 = configuration['Parameters']['Groups'][0]['LongShort'].lower()
                long_short_2 = configuration['Parameters']['Groups'][1]['LongShort'].lower()
                type_1 = configuration['Parameters']['Groups'][0]['Type']
                type_2 = configuration['Parameters']['Groups'][1]['Type']
                backtest_name += f"_{put_1_strike}d{long_short_1}{type_1}{put_2_strike}d{long_short_2}{type_2}"

            if 'no_cost' in backtest_name:
                config_groups = []
                for group_ in configuration['Parameters']['Groups']:
                    group_["VegaEntryFees"] = 0.
                    config_groups.append(group_)
                configuration['Parameters']['Groups'] = config_groups
            elif 'no_DH' in backtest_name:
                config_groups = []
                for group_ in configuration['Parameters']['Groups']:
                    group_["DeltaHedged"] = False
                    config_groups.append(group_)
                configuration['Parameters']['Groups'] = config_groups
            else:
                put_2_strike = int([x for x in configuration['Parameters']['Groups'] if x["VegaEntryFees"] > 0][0]['DeltaStrike'] * 100)
                put_2_fees = [x for x in configuration['Parameters']['Groups'] if x["VegaEntryFees"] > 0][0]['VegaEntryFees']
                backtest_name += f"_{put_2_fees}VegaFeesOn{put_2_strike}d"

            for group_ in configuration['Parameters']['Groups']:
                group_['NbOptions'] = dict_month_choice[month_choice]
                group_['NextMaturity'] = dict_month_choice[month_choice]

            with open(os.path.join(new_dump_folder, f'{backtest_name}.json'), 'w') as file:
                file.write(json.dumps(configuration))

            start = dt.now()
            bt = run_backtest(configuration)

            t = (dt.now() - start).total_seconds()
            print('%s seconds' % t)

            df_intermediate_res = bt.intermediate_results_dump()
            filename = f"{configuration['Underlyings'][0]['Index']['Name'].split(' ')[0]}_{backtest_name}"
            df_intermediate_res.to_hdf(os.path.join(new_dump_folder, f'{filename}.h5'))
            columns_to_choose = [x for x in df_intermediate_res.columns if
                                 x.split(' ')[0] in ['vol_premium_component', 'gamma_covariance_effect', 'vega_term',
                                                     'd_gamma_term', 'residual_drift_term']]
            df_intermediate_res = df_intermediate_res.reindex(columns=['IL'] + columns_to_choose)

            df_intermediate_res.to_excel(os.path.join(new_dump_folder, f'{filename}.xlsx'), engine="openpyxl")
