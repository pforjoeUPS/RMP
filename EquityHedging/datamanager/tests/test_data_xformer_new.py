import unittest
from unittest.mock import patch, Mock, MagicMock
import numpy as np
import pandas as pd
from EquityHedging.datamanager.data_xformer_new import DataXformer, NexenDataXformer, NexenBmkDataXformer, \
    BbgDataXformer, InnocapDataXformer, VRRDataXformer, get_new_strategy_returns_data, get_new_strat_data, \
    get_data_dict, format_df, resample_df, PriceData, convert_freq

from EquityHedging.datamanager.data_importer import DataImporter, BbgDataImporter, InnocapDataImporter
from EquityHedging.datamanager.data_lists import NEXEN_DATA_COL_DICT, NEXEN_BMK_DATA_COL_DICT


class TestDataXformer(unittest.TestCase):
    @patch('EquityHedging.datamanager.data_importer.DataImporter')
    @patch('EquityHedging.datamanager.data_xformer_new.get_data_dict')
    # @patch('EquityHedging.datamanager.data_xformer_new.copy_data')
    def test_init(self, mock_get_data_dict, mock_data_importer):
        mock_data_import = {'M': pd.DataFrame({'A': [1, 2, 3]}), 'W': pd.DataFrame({'B': [4, 5, 6]})}
        mock_data_importer.return_value = Mock(data_import=mock_data_import, data_dict_bool=True)
        # mock_copy_data.return_value = {'M': pd.DataFrame({'A': [1, 2, 3]}), 'W': pd.DataFrame({'B': [4, 5, 6]})}
        mock_get_data_dict.return_value = {'M': pd.DataFrame({'A': [1, 2, 3]}), 'W': pd.DataFrame({'B': [4, 5, 6]})}

        xformer = DataXformer('test.xlsx', col_dict={'A': 'B'}, format_data=True)

        self.assertEqual(xformer.file_path, 'test.xlsx')
        self.assertEqual(xformer.sheet_name, 0)
        # self.assertEqual(xformer.data_source, 'custom')
        self.assertTrue(xformer.drop_na)
        self.assertFalse(xformer.index_data)
        self.assertTrue(xformer.format_data)
        self.assertEqual(xformer.col_dict, {'A': 'B'})
        self.assertEqual(xformer.data_import, mock_data_import)
        self.assertTrue(xformer.data_dict_bool)

        expected_df_M = pd.DataFrame({'A': [1, 2, 3]})
        expected_df_W = pd.DataFrame({'B': [4, 5, 6]})
        self.assertTrue(xformer.data_xform['M'].reset_index(drop=True).equals(expected_df_M))
        self.assertTrue(xformer.data_xform['W'].reset_index(drop=True).equals(expected_df_W))

    @patch('EquityHedging.datamanager.data_xformer_new.get_data_dict')
    def test_xform_data_dict(self, mock_get_data_dict):
        mock_data_import = {'M': pd.DataFrame({'A': [1, 2, 3]}), 'W': pd.DataFrame({'B': [4, 5, 6]})}
        mock_get_data_dict.return_value = {'M': pd.DataFrame({'A': [1, 2, 3]}), 'W': pd.DataFrame({'B': [4, 5, 6]})}

        with patch('pandas.read_excel', return_value=pd.DataFrame()):
            xformer = DataXformer(file_path='test.xlsx')

            result = xformer.xform_data()

            result_dict = {key: df.to_dict() for key, df in result.items()}
            mock_data_import_dict = {key: df.to_dict() for key, df in mock_data_import.items()}

            self.assertDictEqual(result_dict, mock_data_import_dict)

    @patch('EquityHedging.datamanager.data_importer.DataImporter')
    @patch('EquityHedging.datamanager.data_xformer_new.dm.get_freq')
    @patch('EquityHedging.datamanager.data_xformer_new.resample_df')
    def test_get_importer(self, mock_resample_data, mock_get_freq, mock_data_importer):
        mock_filepath = 'test.xlsx'
        mock_sheet_name = 0
        mock_data_source = 'custom'
        mock_col_dict = {'A': 'B'}
        mock_drop_na = True
        mock_index_data = False

        mock_data_importer_instance = Mock(DataImporter)
        mock_data_importer_instance.data_import = {
            'M': pd.DataFrame({'A': [1, 2, 3]}),
            'W': pd.DataFrame({'B': [4, 5, 6]})
        }
        mock_data_importer_instance.data_dict_bool = True

        mock_data_importer.return_value = mock_data_importer_instance

        xformer = DataXformer(file_path=mock_filepath, sheet_name=mock_sheet_name,
                              col_dict=mock_col_dict,
                              drop_na=mock_drop_na, index_data=mock_index_data)

        data_importer = xformer.get_importer()

        mock_data_importer.assert_called_with(file_path=mock_filepath, sheet_name=mock_sheet_name,
                                              col_dict=mock_col_dict,
                                              drop_na=mock_drop_na, index_data=mock_index_data)

        self.assertEqual(data_importer, mock_data_importer_instance)


class TestNexenDataXformer(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_importer.NexenDataImporter')
    def test_init(self, mock_nexen_data_importer):
        mock_nexen_data_importer_instance = Mock()
        mock_nexen_data_importer.return_value = mock_nexen_data_importer_instance

        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Name': ['Company1', 'Company2', 'Company3'],
            'Return': [0.1, 0.05, -0.02],
            'Market Value': [1000000, 2000000, 1500000]
        })
        mock_nexen_data_importer_instance.data_import = mock_data_import

        nexen_xformer = NexenDataXformer(file_path='test.xlsx')

        self.assertEqual(nexen_xformer.file_path, 'test.xlsx')
        # self.assertEqual(nexen_xformer.data_source, 'nexen')
        self.assertEqual(nexen_xformer.col_dict, NEXEN_DATA_COL_DICT)
        mock_nexen_data_importer.assert_called_once_with(file_path='test.xlsx', col_dict=NEXEN_DATA_COL_DICT)

    @patch('EquityHedging.datamanager.data_importer.NexenDataImporter')
    def test_get_importer(self, mock_nexen_data_importer):
        nexen_xformer = NexenDataXformer(file_path='test.xlsx', col_dict={'A': 'B'})

        importer = nexen_xformer.get_importer()

        mock_nexen_data_importer.assert_called_with(file_path='test.xlsx', col_dict={'A': 'B'})
        self.assertEqual(importer, mock_nexen_data_importer.return_value)

    @patch('EquityHedging.datamanager.data_importer.NexenDataImporter')
    def test_xform_data(self, mock_nexen_data_importer):
        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Name': ['Company1', 'Company2', 'Company3'],
            'Return': [10, 5, 8],
            'Market Value': [1000000, 2000000, 1500000]
        })

        mock_nexen_data_importer_instance = Mock()
        mock_nexen_data_importer.return_value = mock_nexen_data_importer_instance
        mock_nexen_data_importer_instance.data_import = mock_data_import

        nexen_xformer = NexenDataXformer(file_path='test.xlsx')

        nexen_xformer.data_import = mock_data_import

        transformed_data = nexen_xformer.xform_data()

        expected_returns_df = pd.DataFrame({
            'Company1': [0.1, np.NaN, np.NaN],
            'Company2': [np.NaN, 0.05, np.NaN],
            'Company3': [np.NaN, np.NaN, 0.08],
        }, index=['2024-01-01', '2024-01-02', '2024-01-03'])

        expected_market_values_df = pd.DataFrame({
            'Company1': [1000000.0, np.NaN, np.NaN],
            'Company2': [np.NaN, 2000000.0, np.NaN],
            'Company3': [np.NaN, np.NaN, 1500000.0],
        }, index=['2024-01-01', '2024-01-02', '2024-01-03'])

        self.assertTrue(expected_returns_df.equals(transformed_data['returns']))
        self.assertTrue(expected_market_values_df.equals(transformed_data['market_values']))


class TestNexenBmkDataXformer(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_importer.NexenDataImporter')
    def test_init(self, mock_nexen_data_importer):
        mock_nexen_data_importer_instance = Mock()
        mock_nexen_data_importer.return_value = mock_nexen_data_importer_instance

        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Benchmark Name': ['BMK1', 'BMK2', 'BMK3'],
            'Benchmark Return': [0.1, 0.05, -0.02],
        })
        mock_nexen_data_importer_instance.data_import = mock_data_import

        filepath = 'test_bmk.xlsx'
        col_dict = {'As Of Date\n': 'Dates', 'Benchmark Name\n': 'BMK', 'Benchmark Monthly Return\n': 'BMK Return'}

        expected_col_dict = {**NEXEN_DATA_COL_DICT, **NEXEN_BMK_DATA_COL_DICT, **col_dict}

        with patch.object(NexenBmkDataXformer, '__init__', return_value=None) as mock_init:
            nexen_bmk_xformer = NexenBmkDataXformer(file_path=filepath, col_dict=expected_col_dict)
            mock_init.assert_called_once_with(file_path=filepath, col_dict=expected_col_dict)

    @patch('EquityHedging.datamanager.data_importer.NexenDataImporter')
    def test_xform_data(self, mock_nexen_data_importer):
        mock_nexen_data_importer_instance = Mock()
        mock_nexen_data_importer.return_value = mock_nexen_data_importer_instance

        # Mock data import
        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Benchmark Name': ['BMK1', 'BMK2', 'BMK3'],
            'Benchmark Return': [10, 5, -2],  # These are in percentage
        })
        mock_nexen_data_importer_instance.data_import = mock_data_import

        # Mock col_dict
        col_dict = {'As Of Date\n': 'Dates', 'Benchmark Name\n': 'BMK', 'Benchmark Monthly Return\n': 'BMK Return'}

        # Create NexenBmkDataXformer instance
        nexen_bmk_xformer = NexenBmkDataXformer(file_path='test_bmk.xlsx')

        expected_transformed_data = pd.DataFrame({
            'BMK1': [0.1, None, None],
            'BMK2': [None, 0.05, None],
            'BMK3': [None, None, -0.02],
        }, index=['2024-01-01', '2024-01-02', '2024-01-03'])

        # Set the name of the index
        expected_transformed_data.index.name = 'Dates'

        # Reset the index name for columns
        expected_transformed_data.columns.name = 'Benchmark Name'

        transformed_data = nexen_bmk_xformer.xform_data()

        pd.testing.assert_frame_equal(transformed_data, expected_transformed_data)


class TestBbgDataXformer(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_importer.BbgDataImporter')
    def test_init(self, mock_bbg_data_importer):
        mock_data_importer_instance = Mock()
        mock_bbg_data_importer.return_value = mock_data_importer_instance

        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Return': [10, 5, 8],
        })
        mock_data_importer_instance.data_import = mock_data_import

        bbg_xformer = BbgDataXformer(file_path='test_bbg.xlsx', sheet_name='data')

        self.assertEqual(bbg_xformer.file_path, 'test_bbg.xlsx')
        self.assertEqual(bbg_xformer.sheet_name, 'data')
        # self.assertEqual(bbg_xformer.data_source, 'bbg')
        self.assertEqual(bbg_xformer.drop_na, True)
        self.assertEqual(bbg_xformer.index_data, True)
        self.assertEqual(bbg_xformer.format_data, True)

        mock_bbg_data_importer.assert_called_once_with(file_path='test_bbg.xlsx', sheet_name='data', drop_na=True)
        self.assertEqual(bbg_xformer.col_dict, mock_bbg_data_importer.return_value.col_dict)

    @patch('EquityHedging.datamanager.data_importer.BbgDataImporter')
    def test_get_importer(self, mock_bbg_data_importer):
        bbg_xformer = BbgDataXformer(file_path='test_bbg.xlsx', sheet_name='data')

        bbg_data_importer = bbg_xformer.get_importer()

        mock_bbg_data_importer.assert_called_with(file_path='test_bbg.xlsx', sheet_name='data', drop_na=True)
        self.assertIs(bbg_data_importer, mock_bbg_data_importer.return_value)


class TestInnocapDataXformer(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_importer.InnocapDataImporter')
    def test_init(self, mock_innocap_data_importer):
        mock_innocap_data_importer_instance = Mock()
        mock_innocap_data_importer.return_value = mock_innocap_data_importer_instance

        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Name': ['Company1', 'Company2', 'Company3'],
            'Return': [0.1, 0.05, -0.02],
            'Market Value': [1000000, 2000000, 1500000]
        })
        mock_innocap_data_importer_instance.data_import = mock_data_import

        innocap_xformer = InnocapDataXformer(file_path='test_innocap.xlsx')

        self.assertEqual(innocap_xformer.file_path, 'test_innocap.xlsx')
        # self.assertEqual(innocap_xformer.data_source, 'innocap')
        self.assertEqual(innocap_xformer.col_dict, {
            'Date': 'Dates',
            'Account Name': 'Name',
            'MTD Return': 'Return',
            'Market Value': 'Market Value'
        })
        mock_innocap_data_importer.assert_called_once_with(file_path='test_innocap.xlsx',
                                                           col_dict=innocap_xformer.col_dict)
#TODO : Fix this test
    @patch('EquityHedging.datamanager.data_importer.InnocapDataImporter')
    def test_get_importer(self, mock_innocap_data_importer):
        innocap_xformer = InnocapDataXformer(file_path='test_innocap.xlsx',
                                             col_dict={'Date': 'Dates', 'Account Name': 'Name', 'MTD Return': 'Return',
                                                       'Market Value': 'Market Value'})

        importer = innocap_xformer.get_importer()

        mock_innocap_data_importer.assert_called_with(file_path='test_innocap.xlsx',
                                                      col_dict={'Date': 'Dates', 'Account Name': 'Name',
                                                                'MTD Return': 'Return',
                                                                'Market Value': 'Market Value'})
        self.assertEqual(importer, mock_innocap_data_importer.return_value)
#TODO: Fix this test
    @patch('EquityHedging.datamanager.data_importer.InnocapDataImporter')
    def test_xform_data(self, mock_innocap_data_importer):
        # Mock data
        mock_data_import = pd.DataFrame({
            'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Name': ['Company1', 'Company2', 'Company3'],
            'Return': [10, 5, 8],
            'Market Value': [1000000, 2000000, 1500000]
        })

        mock_innocap_data_importer_instance = Mock()
        mock_innocap_data_importer.return_value = mock_innocap_data_importer_instance
        mock_innocap_data_importer_instance.data_import = mock_data_import

        innocap_xformer = InnocapDataXformer(file_path='test_innocap.xlsx',
                                             col_dict={'Date': 'Dates', 'Account Name': 'Name', 'MTD Return': 'Return',
                                                       'Market Value': 'Market Value'})

        innocap_xformer.data_import = mock_data_import

        transformed_data = innocap_xformer.xform_data()

        expected_returns_df = pd.DataFrame({
            'Company1': [0.1, np.NaN, np.NaN],
            'Company2': [np.NaN, 0.05, np.NaN],
            'Company3': [np.NaN, np.NaN, 0.08],
        }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))

        expected_market_values_df = pd.DataFrame({
            'Company1': [1000000.0, np.NaN, np.NaN],
            'Company2': [np.NaN, 2000000.0, np.NaN],
            'Company3': [np.NaN, np.NaN, 1500000.0],
        }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))

        print("Expected Returns DataFrame:")
        print(expected_returns_df)
        print("\nTransformed Returns DataFrame:")
        print(transformed_data['returns'])

        print("Expected Market Values DataFrame:")
        print(expected_market_values_df)
        print("\nTransformed Market Values DataFrame:")
        print(transformed_data['market_values'])

        self.assertTrue(expected_returns_df.equals(transformed_data['returns']))
        self.assertTrue(expected_market_values_df.equals(transformed_data['market_values']))


# class TestVRRDataXformer(unittest.TestCase):
#
#     @patch('EquityHedging.datamanager.data_xformer_new.get_data_dict')
#     def test_init(self, mock_get_data_dict):
#         # Mock data import with the expected structure
#         mock_data_import = {
#             'VRR': pd.DataFrame({'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'], 'VRR': [1, 2, 3]}),
#             'VRR 2': pd.DataFrame({'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'], 'VRR 2': [4, 5, 6]}),
#             'VRR Trend': pd.DataFrame({'Dates': ['2024-01-01', '2024-01-02', '2024-01-03'], 'VRR Trend': [7, 8, 9]})
#         }
#         mock_get_data_dict.return_value = mock_data_import
#
#         file_path = 'test_vrr.xlsx'
#         sheet_name = ["VRR", "VRR 2", "VRR Trend"]
#         index_data = True
#         drop_na = False
#
#         with patch('pandas.read_excel', return_value=pd.DataFrame()):
#             xformer = VRRDataXformer(file_path=file_path, sheet_name=sheet_name, index_data=index_data, drop_na=drop_na)
#
#             self.assertEqual(xformer.file_path, file_path)
#             self.assertEqual(xformer.sheet_name, sheet_name)
#             self.assertEqual(xformer.drop_na, drop_na)
#             self.assertEqual(xformer.index_data, index_data)
#
#             mock_get_data_dict.assert_called_once()
#             # Ensure mock_get_data_dict is called with correct parameters
#             mock_get_data_dict.assert_called_with(data_df=pd.DataFrame(), index_data=index_data)

class TestGetData(unittest.TestCase):

    @patch('pandas.read_excel')
    def test_get_new_strategy_returns_data(self, mock_read_excel):
        mock_data = {
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Strategy1': [0.1, 0.2, 0.3],
            'Strategy2': [0.2, 0.3, 0.4]
        }
        mock_df = pd.DataFrame(mock_data)

        mock_read_excel.return_value = mock_df

        result_df_default = get_new_strategy_returns_data(file_path='test.xlsx', sheet_name='data', freq='D')
        self.assertTrue(isinstance(result_df_default, pd.DataFrame))
        self.assertEqual(len(result_df_default), 3)
        self.assertEqual(list(result_df_default.columns), ['Date', 'Strategy1', 'Strategy2'])

        # Test with custom strategy_list
        result_df_custom = get_new_strategy_returns_data(file_path='test.xlsx', sheet_name='data', freq='D',
                                                         strategy_list=['Custom1', 'Custom2', 'Custom3'])
        self.assertTrue(isinstance(result_df_custom, pd.DataFrame))
        self.assertEqual(len(result_df_custom), 3)
        self.assertEqual(list(result_df_custom.columns), ['Custom1', 'Custom2', 'Custom3'])
#TODO : Needs through testing
    @patch('pandas.read_excel')
    def test_get_new_strat_data(self, mock_read_excel):
        mock_data = {
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Strategy1': [0.1, 0.2, 0.3],
            'Strategy2': [0.2, 0.3, 0.4]
        }
        mock_df = pd.DataFrame(mock_data)

        mock_read_excel.return_value = mock_df

        result_df_default = get_new_strat_data(file_path='test.xlsx')
        print(result_df_default)
        self.assertTrue(isinstance(result_df_default, pd.DataFrame))
        self.assertEqual(len(result_df_default), 1)  # Check number of rows
        self.assertEqual(list(result_df_default.columns), ['Date', 'Strategy1', 'Strategy2'])  # Check column names

        result_df_custom = get_new_strat_data(file_path='test.xlsx', sheet_name='data', freq='M', index_data=True)
        self.assertTrue(isinstance(result_df_custom, pd.DataFrame))
        self.assertEqual(len(result_df_custom), 0)  # Check number of rows
        self.assertEqual(list(result_df_custom.columns), ['Date', 'Strategy1', 'Strategy2'])  # Check column names


class TestResampleDF(unittest.TestCase):

    def test_resample_df(self):
        # Mock data for testing
        mock_data = {
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'Value': [100, 110, 105, 115]
        }
        mock_df = pd.DataFrame(mock_data)

        # Test resample to 'M'
        result_df = resample_df(mock_df, freq='M')

        self.assertTrue(isinstance(result_df, pd.DataFrame))

        # Check if index frequency is 'M'
        self.assertEqual(result_df.index.freqstr, 'M')

        expected_rows = 1
        self.assertEqual(len(result_df), expected_rows)

    def test_resample_df_daily(self):
        mock_data = {
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'Value': [100, 110, 105, 115]
        }
        mock_df = pd.DataFrame(mock_data)

        # Test resample to 'D' (daily)
        result_df = resample_df(mock_df, freq='D')

        # Check if result is a DataFrame
        self.assertTrue(isinstance(result_df, pd.DataFrame))

        expected_rows = 4
        self.assertEqual(len(result_df), expected_rows)


class TestFormatDF(unittest.TestCase):

    def setUp(self):
        data = {
            'date': ['2022-01-01', '2022-02-01', '2022-03-01', '2022-04-01'],
            'value': [100, 110, 120, 130]
        }
        self.df = pd.DataFrame(data)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.set_index('date')

        data_with_na = {
            'date': ['2022-01-01', '2022-02-01', '2022-03-01', '2022-04-01'],
            'value': [100, None, 120, 130]
        }
        self.df_with_na = pd.DataFrame(data_with_na)
        self.df_with_na['date'] = pd.to_datetime(self.df_with_na['date'])
        self.df_with_na = self.df_with_na.set_index('date')

    def test_format_df_monthly(self):
        expected_result = pd.DataFrame({'value': [0.1, 0.090909, 0.083333]},
                                       index=pd.to_datetime(['2022-02-28', '2022-03-31', '2022-04-30']))
        expected_result.index.name = 'date'
        expected_result.index.freq = 'M'
        result = format_df(self.df, freq='M', drop_na=True, drop_zero=False)
        pd.testing.assert_frame_equal(result, expected_result)

    def test_format_df_daily(self):
        # Test formatting with daily frequency
        expected_result = pd.DataFrame({'value': [0.1, 0.090909, 0.083333]},
                                       index=pd.to_datetime(['2022-02-01', '2022-03-01', '2022-04-01']))
        expected_result.index.name = 'date'

        result = format_df(self.df, freq='D', drop_na=True, drop_zero=False)

        pd.testing.assert_frame_equal(result, expected_result)

    def test_format_df_drop_na(self):
        expected_result = pd.DataFrame({'value': [0.0, 0.19999999999999996, 0.083333]},
                                       index=pd.to_datetime(['2022-02-28', '2022-03-31', '2022-04-30']))

        expected_result.index.name = 'date'
        expected_result.index.freq = 'M'
        result = format_df(self.df_with_na, freq='M', drop_na=False, drop_zero=False)
        pd.testing.assert_frame_equal(result, expected_result)


class TestPriceData(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_xformer_new.PriceData.get_price_data')
    def test_init(self, mock_get_price_data):
        returns_data = pd.Series([0.1, 0.05, -0.02])
        multiplier = 100

        mock_get_price_data.return_value = pd.DataFrame({
            'Dates': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01']),
            0: [100, 110, 115.5]
        })

        price_data = PriceData(multiplier=multiplier)
        # Assertions
        # self.assertEqual(price_data.returns_data.tolist(), returns_data.tolist())
        self.assertEqual(price_data.multiplier, multiplier)
        # self.assertIsInstance(price_data.price_data, pd.DataFrame)
        # pd.testing.assert_frame_equal(price_data.price_data, mock_get_price_data.return_value)

    @patch('EquityHedging.datamanager.data_xformer_new.PriceData.get_price_data')
    @patch('EquityHedging.datamanager.data_xformer_new.dm')
    def test_update_index_data(self, mock_dm, mock_get_price_data):
        returns_data = pd.Series([0.1, 0.05, -0.02])
        multiplier = 100

        mock_get_price_data.return_value = pd.DataFrame({
            'Dates': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01']),
            0: [100, 110, 115.5]
        })

        price_data = PriceData(multiplier=multiplier)

        price_data.price_data = pd.DataFrame({
            0: [100, 110, 115.5]
        }, index=pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01']))

        # Call the method to be tested
        updated_price_data = price_data.update_index_data(price_data.price_data)

        # Expected output
        expected_output = pd.DataFrame({
            0: [None, 100, 110, 115.5]
        }, index=pd.to_datetime(['2021-12-01', '2022-01-01', '2022-02-01', '2022-03-01']))

        updated_price_data.reset_index(drop=True, inplace=True)
        updated_price_data.set_index(expected_output.index, inplace=True)
        updated_price_data.columns = pd.Int64Index(updated_price_data.columns)
        pd.testing.assert_frame_equal(updated_price_data, expected_output)

    @patch.object(PriceData, 'update_index_data')
    def test_get_price_data(self, mock_update_index_data):
        returns_data = pd.Series([0.1, 0.05, -0.02])
        multiplier = 100

        mock_update_index_data.return_value = pd.DataFrame({
            'Dates': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01']),
            0: [100, 110, 115.5]
        })
        price_data_instance = PriceData(multiplier=multiplier)

        actual_output = price_data_instance.get_price_data(returns_data)

        expected_output = pd.Series([100, 110, 115.5])
        expected_output.name = 0

        actual_output = pd.Series(actual_output)
        self.assertEqual(actual_output.all(), expected_output.all())


if __name__ == '__main__':
    unittest.main()
