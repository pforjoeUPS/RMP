import unittest
from unittest.mock import patch, MagicMock
from EquityHedging.datamanager.data_handler import MktDataHandler, DataHandler
from EquityHedging.datamanager.data_lists import  BMK_DATA_FP
import pandas as pd
import os
os.chdir('../../..')
mkt_filepath = os.getcwd() + '\\EquityHedging\\data\\returns_data\\bmk_returns-new.xlsx'


class TestMktDataHandler(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_init(self, mock_read_excel_data):
        mock_data = {
            'Sheet1': pd.DataFrame({'Column1': [1, 2, 3], 'Column2': [4, 5, 6]}),
            'Sheet2': pd.DataFrame({'Column1': [7, 8, 9], 'Column2': [10, 11, 12]})
        }
        mock_read_excel_data.return_value = mock_data

        mkt_data_handler = MktDataHandler()

        self.assertTrue(mkt_data_handler.include_eq)
        self.assertEqual(mkt_data_handler.eq_bmk, 'MSCI ACWI')
        self.assertTrue(mkt_data_handler.include_fi)
        self.assertEqual(mkt_data_handler.fi_bmk, 'FI Benchmark')
        self.assertFalse(mkt_data_handler.include_cm)
        self.assertIsNone(mkt_data_handler.cm_bmk)
        self.assertFalse(mkt_data_handler.include_fx)
        self.assertIsNone(mkt_data_handler.fx_bmk)

        # mock_read_excel_data.assert_called_once_with(filepath=BMK_DATA_FP, sheet_name=None)

        mkt_data_handler_with_cm = MktDataHandler(include_cm=True)
        self.assertTrue(mkt_data_handler_with_cm.include_cm)
        self.assertEqual(mkt_data_handler_with_cm.cm_bmk, 'Commodities (BCOM)')

        mkt_data_handler_with_fx = MktDataHandler(include_fx=True)
        self.assertTrue(mkt_data_handler_with_fx.include_fx)
        self.assertEqual(mkt_data_handler_with_fx.fx_bmk, 'U.S. Dollar Index')

        mkt_data_handler_no_eq_fi = MktDataHandler(include_eq=False, include_fi=False)
        self.assertFalse(mkt_data_handler_no_eq_fi.include_eq)
        self.assertIsNone(mkt_data_handler_no_eq_fi.eq_bmk)
        self.assertFalse(mkt_data_handler_no_eq_fi.include_fi)
        self.assertIsNone(mkt_data_handler_no_eq_fi.fi_bmk)

        self.assertIsInstance(mkt_data_handler.mkt_returns, dict)

    @patch('EquityHedging.datamanager.data_handler.MktDataHandler')
    def test_get_mkt_key(self, mock_mkt_data_handler):
        mock_instance = mock_mkt_data_handler.return_value
        mock_instance.get_mkt_returns.return_value = None

        mkt_data_handler_all_assets = MktDataHandler(mkt_filepath, include_eq=True, include_fi=True, include_cm=True, include_fx=True)
        expected_key_all_assets = {'Equity': 'MSCI ACWI', 'Fixed Income': 'FI Benchmark',
                                   'Commodities': 'Commodities (BCOM)', 'FX': 'U.S. Dollar Index'}
        self.assertEqual(mkt_data_handler_all_assets.mkt_key, expected_key_all_assets)

        mkt_data_handler_only_eq = MktDataHandler(mkt_filepath, include_eq=True)
        expected_key_only_eq = {'Equity': 'MSCI ACWI',  'Fixed Income': 'FI Benchmark'}
        self.assertEqual(mkt_data_handler_only_eq.mkt_key, expected_key_only_eq)


        mkt_data_handler_only_cm = MktDataHandler(mkt_filepath, include_cm=True)
        expected_key_only_cm = {'Equity': 'MSCI ACWI', 'Fixed Income': 'FI Benchmark', 'Commodities': 'Commodities (BCOM)'}
        self.assertEqual(mkt_data_handler_only_cm.mkt_key, expected_key_only_cm)


        mkt_data_handler_only_fx = MktDataHandler(mkt_filepath, include_fx=True)
        expected_key_only_fx = {'Equity': 'MSCI ACWI', 'Fixed Income': 'FI Benchmark','FX': 'U.S. Dollar Index'}
        self.assertEqual(mkt_data_handler_only_fx.mkt_key, expected_key_only_fx)


        mkt_data_handler_no_assets = MktDataHandler(mkt_filepath, include_eq=False, include_fi=False, include_cm=False,
                                                    include_fx=False)
        expected_key_no_assets = {}
        self.assertEqual(mkt_data_handler_no_assets.mkt_key, expected_key_no_assets)

# @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
# def test_get_mkt_returns(self, mock_read_excel_data):


class TestDataHandler(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_handler.MktDataHandler.__init__')
    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_init(self, mock_read_excel_data, mock_mkt_data_handler_init):
        mock_mkt_data_handler_init.return_value = None

        data_handler = DataHandler(index_data=True, freq_data=False, compute_agg=True,
                                   eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark')

        self.assertTrue(data_handler.index_data)
        self.assertFalse(data_handler.freq_data)
        self.assertTrue(data_handler.compute_agg)

        mock_mkt_data_handler_init.assert_called_with(eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark')

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_get_returns(self, mock_read_excel_data):
        mock_data = pd.DataFrame({'Column1': [1, 2, 3], 'Column2': [4, 5, 6]})
        mock_read_excel_data.return_value = mock_data

        data_handler = DataHandler(index_data=True, freq_data=False, compute_agg=True,
                                   eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark')

        data_handler.get_returns()

        # mock_read_excel_data.assert_called_with('test_filepath', sheet_name='returns')

        self.assertIsNotNone(data_handler.returns)
        self.assertEqual(data_handler.col_list, ['Column1', 'Column2'])

        self.assertEqual(list(data_handler.returns.columns), ['Column1', 'Column2'])

        self.assertEqual(data_handler.returns['Column1'].tolist(), [1, 2, 3])
        self.assertEqual(data_handler.returns['Column2'].tolist(), [4, 5, 6])

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_get_returns_with_freq_data(self, mock_read_excel_data):
        mock_data = pd.DataFrame({
            'Dates': ['2022-01-01', '2022-02-01', '2022-03-01'],
            'Monthly': [200, 600, 2400],
            'Quarterly': [500, 3000, 21000],
            'Yearly': [800, 4000, 15000]
        })
        mock_data['Dates'] = pd.to_datetime(mock_data['Dates'])
        mock_data.set_index('Dates', inplace=True)

        mock_read_excel_data.return_value = mock_data

        data_handler = DataHandler(index_data=True, freq_data=True, compute_agg=True,
                                   eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark')

        data_handler.get_returns()

        # mock_read_excel_data.assert_called_with('test_filepath', sheet_name='returns')

        self.assertTrue(data_handler.returns is not None)
        self.assertEqual(data_handler.col_list, ['Monthly', 'Quarterly', 'Yearly'])

        if isinstance(data_handler.returns, pd.DataFrame):
            self.assertEqual(list(data_handler.returns.columns), ['Monthly', 'Quarterly', 'Yearly'])
        elif isinstance(data_handler.returns, dict):
            expected_keys = ['Monthly', 'Quarterly', 'Yearly']
            actual_keys = list(data_handler.returns.keys())
            self.assertTrue(all(key in actual_keys for key in expected_keys),
                            f"Expected keys: {expected_keys}, Actual keys: {actual_keys}")

    @patch('EquityHedging.datamanager.data_handler.dm.filter_data_dict')
    @patch('EquityHedging.datamanager.data_handler.dm.get_freq_string')
    def test_update_mkt_returns_with_freq_data(self, mock_get_freq_string, mock_filter_data_dict):
        # Create a sample market returns data
        market_returns = {
            'Equity': pd.DataFrame({'Date': ['2022-01-01', '2022-01-02'], 'Return': [0.1, 0.2]}),
            'Fixed Income': pd.DataFrame({'Date': ['2022-01-01', '2022-01-02'], 'Return': [0.05, 0.03]})
        }
        data_handler = DataHandler(index_data=True, freq_data=True, compute_agg=True,
                                   eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark')

        data_handler.mkt_returns = market_returns

        # Mock the necessary functions
        mock_get_freq_string.return_value = 'Monthly'
        mock_filter_data_dict.return_value = {
            'Equity': pd.DataFrame({'Date': ['2022-01-01'], 'Return': [0.1]}),
            'Fixed Income': pd.DataFrame({'Date': ['2022-01-01'], 'Return': [0.05]})
        }

        # Call the method
        data_handler.update_mkt_returns()

        # Assertions
        self.assertTrue(mock_get_freq_string.called)
        mock_filter_data_dict.assert_called_once_with(market_returns, ['Return'])
        self.assertEqual(len(data_handler.mkt_returns['Equity']), 1)
        self.assertEqual(len(data_handler.mkt_returns['Fixed Income']), 1)
        self.assertEqual(list(data_handler.mkt_returns['Equity']['Return']), [0.1])
        self.assertEqual(list(data_handler.mkt_returns['Fixed Income']['Return']), [0.05])

    @patch('EquityHedging.datamanager.data_handler.di.ExcelImporter.read_excel_data')
    def test_get_mvs(self, mock_read_excel_data):
        # Mock data to be returned by read_excel_data
        mock_data = pd.DataFrame({
            'Strategy': ['A', 'B', 'C'],
            'Market Value': [100, 200, 300]
        })
        mock_read_excel_data.return_value = mock_data

        # Create DataHandler instance
        data_handler = DataHandler(file_path='test_file.xlsx')

        # Call the method
        data_handler.get_mvs()

        # Assertions
        mock_read_excel_data.assert_called_once_with(file_path='test_file.xlsx', sheet_name='market_values')
        self.assertIsNotNone(data_handler.mvs)
        self.assertEqual(data_handler.mvs['Strategy'].tolist(), ['A', 'B', 'C'])
        self.assertEqual(data_handler.mvs['Market Value'].tolist(), [100, 200, 300])

if __name__ == '__main__':
    unittest.main()
