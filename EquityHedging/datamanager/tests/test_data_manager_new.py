import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime
from EquityHedging.datamanager.data_manager_new import merge_dicts_list, merge_dicts, merge_df_lists, get_min_max_dates, \
    switch_freq_string, format_date_index, get_freq, get_freq_string, get_freq_data, drop_nas, convert_to_freq2, \
    get_freq_ratio, rename_columns, get_first_valid_index, get_last_valid_index, replace_value_with_nan, get_date_offset


class TestMergeDictsList(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_manager_new.merge_dicts')
    def test_merge_dicts_list(self, mock_merge_dicts):
        dict_list = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]
        mock_merge_dicts.return_value = {'a': 1, 'b': 3, 'c': 4}

        from EquityHedging.datamanager.data_manager_new import merge_dicts_list
        merged_dict = merge_dicts_list(dict_list)

        expected_dict = {'a': 1, 'b': 3, 'c': 4}
        self.assertEqual(merged_dict, expected_dict)

    @patch('EquityHedging.datamanager.data_manager_new.merge_dicts')
    def test_merge_dicts_list_with_drop_na(self, mock_merge_dicts):
        dict_list = [{'a': 1, 'b': 2, 'c': None}, {'b': 3, 'c': 4}]
        mock_merge_dicts.return_value = {'a': 1, 'b': 3, 'c': 4}

        from EquityHedging.datamanager.data_manager_new import merge_dicts_list
        merged_dict = merge_dicts_list(dict_list, drop_na=True)

        expected_dict = {'a': 1, 'b': 3, 'c': 4}
        self.assertEqual(merged_dict, expected_dict)

    @patch('EquityHedging.datamanager.data_manager_new.merge_dicts')
    def test_merge_dicts_list_with_fillzeros(self, mock_merge_dicts):
        dict_list = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]
        mock_merge_dicts.return_value = {'a': 1, 'b': 3, 'c': 4}

        from EquityHedging.datamanager.data_manager_new import merge_dicts_list
        merged_dict = merge_dicts_list(dict_list, fillzeros=True)

        expected_dict = {'a': 1, 'b': 3, 'c': 4}
        self.assertEqual(merged_dict, expected_dict)


class TestMergeDFLists(unittest.TestCase):
    @patch('EquityHedging.datamanager.data_manager_new.merge_dfs')
    def test_merge_df_lists(self, mock_merge_dfs):
        df1 = MagicMock()
        df2 = MagicMock()

        merged_df = MagicMock()

        mock_merge_dfs.return_value = merged_df

        result = merge_df_lists([df1, df2])

        mock_merge_dfs.assert_called_with(main_df = df1, new_df = df2, drop_na = True, fillzeros =False, how = 'outer')

        self.assertEqual(result, merged_df)

# class TestGetMinMaxDates(unittest.TestCase):
#     def test_get_min_max_dates(self):
#         index_values = [datetime(2022, 1, 1), datetime(2022, 1, 2), datetime(2022, 1, 3)]  # Example timestamps
#         mock_df = MagicMock(index=MagicMock(values=index_values))
#
#         result = get_min_max_dates(mock_df)
#
#         expected_dates = {'start': datetime(2022, 1, 1), 'end': datetime(2022, 1, 3)}
#
#         self.assertEqual(result, expected_dates)

class TestSwitchFreqString(unittest.TestCase):

    def test_switch_freq_string_daily(self):
        self.assertEqual(switch_freq_string('D'), 'Daily')

    def test_switch_freq_string_weekly(self):
        self.assertEqual(switch_freq_string('W'), 'Weekly')

    def test_switch_freq_string_monthly(self):
        self.assertEqual(switch_freq_string('M'), 'Monthly')

    def test_switch_freq_string_quarterly(self):
        self.assertEqual(switch_freq_string('Q'), 'Quarterly')

    def test_switch_freq_string_yearly(self):
        self.assertEqual(switch_freq_string('Y'), 'Yearly')

    def test_switch_freq_string_default(self):
        self.assertEqual(switch_freq_string('Z'), 'Daily')  # Default value for unknown input is 'Daily'
class TestFormatDateIndex(unittest.TestCase):

    def test_format_date_index_yearly(self):
        # Test for yearly frequency
        data_df = pd.DataFrame(data=[1, 2, 3], index=pd.date_range(start='2022-01-01', periods=3, freq='Y'))
        formatted_df = format_date_index(data_df, freq='Y')
        self.assertEqual(formatted_df.index.tolist(), [2022, 2023, 2024])

    def test_format_date_index_quarterly(self):
        # Test for quarterly frequency
        data_df = pd.DataFrame(data=[1, 2, 3], index=pd.date_range(start='2022-01-01', periods=3, freq='Q'))
        formatted_df = format_date_index(data_df, freq='Q')
        self.assertEqual(formatted_df.index.tolist(), ['Q1 2022', 'Q2 2022', 'Q3 2022'])

    def test_format_date_index_monthly(self):
        # Test for monthly frequency
        data_df = pd.DataFrame(data=[1, 2, 3], index=pd.date_range(start='2022-01-01', periods=3, freq='M'))
        formatted_df = format_date_index(data_df, freq='M')
        self.assertEqual(formatted_df.index.tolist(), ['Jan 2022', 'Feb 2022', 'Mar 2022'])

    def test_format_date_index_no_freq(self):
        # Test for default behavior (no frequency specified)
        data_df = pd.DataFrame(data=[1, 2, 3], index=pd.date_range(start='2022-01-01', periods=3))
        formatted_df = format_date_index(data_df)  # No frequency specified
        self.assertEqual(formatted_df.index.tolist(), ['Jan 2022', 'Jan 2022', 'Jan 2022'])

class TestGetFreq(unittest.TestCase):

    def test_get_freq_daily(self):
        # Test for daily frequency
        returns_df = MagicMock()
        returns_df.index = pd.date_range(start='2022-01-01', periods=10, freq='D')
        self.assertEqual(get_freq(returns_df), 'D')

    def test_get_freq_weekly(self):
        # Test for weekly frequency
        returns_df = MagicMock()
        returns_df.index = pd.date_range(start='2022-01-01', periods=10, freq='W')
        self.assertEqual(get_freq(returns_df), 'W')

    def test_get_freq_monthly(self):
        # Test for monthly frequency
        returns_df = MagicMock()
        returns_df.index = pd.date_range(start='2022-01-01', periods=10, freq='M')
        self.assertEqual(get_freq(returns_df), 'M')

    def test_get_freq_quarterly(self):
        # Test for quarterly frequency
        returns_df = MagicMock()
        returns_df.index = pd.date_range(start='2022-01-01', periods=10, freq='Q')
        self.assertEqual(get_freq(returns_df), 'Q')

    def test_get_freq_business_daily(self):
        # Test for business daily frequency
        returns_df = MagicMock()
        returns_df.index = pd.date_range(start='2022-01-01', periods=10, freq='B')
        self.assertEqual(get_freq(returns_df), 'D')

    def test_get_freq_no_freq(self):
        # Test for no frequency (returns None)
        returns_df = MagicMock()
        returns_df.index = pd.date_range(start='2022-01-01', periods=10)
        self.assertEqual(get_freq(returns_df), 'D')

class TestGetFreqFunctions(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_manager_new.get_freq', return_value='M')  # Mocking get_freq function to return 'M'
    def test_get_freq_string_monthly(self, mock_get_freq):
        self.assertEqual(get_freq_string(MagicMock()), 'Monthly')

    @patch('EquityHedging.datamanager.data_manager_new.get_freq', return_value='W')  # Mocking get_freq function to return 'W'
    def test_get_freq_string_weekly(self, mock_get_freq):
        self.assertEqual(get_freq_string(MagicMock()), 'Weekly')

    @patch('EquityHedging.datamanager.data_manager_new.get_freq', return_value='Q')  # Mocking get_freq function to return 'Q'
    def test_get_freq_data_quarterly(self, mock_get_freq):
        expected_data = {'freq': 'Q', 'freq_string': 'Quarterly', 'freq_int': 4}
        self.assertEqual(get_freq_data(MagicMock()), expected_data)

    @patch('EquityHedging.datamanager.data_manager_new.get_freq', return_value='D')  # Mocking get_freq function to return 'D'
    def test_get_freq_data_daily(self, mock_get_freq):
        expected_data = {'freq': 'D', 'freq_string': 'Daily', 'freq_int': 252}
        self.assertEqual(get_freq_data(MagicMock()), expected_data)

class TestDropNas(unittest.TestCase):

    def test_drop_nas_dataframe(self):
        # Test for DataFrame input
        data_df = MagicMock()
        data_df.dropna.return_value = data_df
        result = drop_nas(data_df)
        data_df.dropna.assert_called_once_with(inplace=True, axis=0)
        self.assertIs(result, data_df)

    def test_drop_nas_dict(self):
        # Test for dictionary of DataFrames input
        data_dict = {'A': MagicMock(), 'B': MagicMock()}
        for df in data_dict.values():
            df.dropna.return_value = df
        result = drop_nas(data_dict)
        for df in data_dict.values():
            df.dropna.assert_called_once_with(inplace=True, axis=0)
        self.assertIs(result, data_dict)
class TestGetFreqRatio(unittest.TestCase):

    @patch('EquityHedging.datamanager.data_manager_new.switch_freq_int', side_effect=lambda x: {'D': 252, 'W': 52}.get(x, 252))  # Mocking switch_freq_int
    def test_get_freq_ratio_daily_to_weekly(self, mock_switch_freq_int):
        self.assertEqual(get_freq_ratio('D', 'W'), 252 // 52 +1)

    @patch('EquityHedging.datamanager.data_manager_new.switch_freq_int', side_effect=lambda x: {'M': 12, 'W': 52}.get(x, 252))  # Mocking switch_freq_int
    def test_get_freq_ratio_monthly_to_weekly(self, mock_switch_freq_int):
        self.assertEqual(get_freq_ratio('M', 'W'), 12 // 52)

    @patch('EquityHedging.datamanager.data_manager_new.switch_freq_int', side_effect=lambda x: {'Q': 4, 'D': 252}.get(x, 252))  # Mocking switch_freq_int
    def test_get_freq_ratio_quarterly_to_daily(self, mock_switch_freq_int):
        self.assertEqual(get_freq_ratio('Q', 'D'), 4 // 252)

    @patch('EquityHedging.datamanager.data_manager_new.switch_freq_int', side_effect=lambda x: {'D': 252, 'D': 252}.get(x, 252))  # Mocking switch_freq_int
    def test_get_freq_ratio_same_freq(self, mock_switch_freq_int):
        self.assertEqual(get_freq_ratio('D', 'D'), 1)
class TestConvertToFreq2(unittest.TestCase):
    @patch('EquityHedging.datamanager.data_manager_new.get_freq_ratio', return_value=5)
    def test_convert_to_freq2_example(self, mock_get_freq_ratio):
        # Expected result = round(arg / ratio) = round(10 / 5) = round(2) = 2
        self.assertEqual(convert_to_freq2(10, 'D', 'W'), 2)

    @patch('EquityHedging.datamanager.data_manager_new.get_freq_ratio', return_value=12)
    def test_convert_to_freq2_other_example(self, mock_get_freq_ratio):
        # Expected result = round(arg / ratio) = round(10 / 12) = round(0.83333) = 1
        self.assertEqual(convert_to_freq2(10, 'M', 'W'), 1)
class TestRenameColumns(unittest.TestCase):
    def test_rename_columns_dataframe(self):
        data_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        col_dict = {'A': 'X', 'B': 'Y'}
        expected_df = pd.DataFrame({'X': [1, 2, 3], 'Y': [4, 5, 6]})
        renamed_df = rename_columns(data_df, col_dict)
        pd.testing.assert_frame_equal(renamed_df, expected_df)

    def test_rename_columns_dict(self):
        data_dict = {'df1': pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
                     'df2': pd.DataFrame({'C': [7, 8, 9], 'D': [10, 11, 12]})}
        col_dict = {'A': 'X', 'B': 'Y', 'C': 'Z'}
        expected_dict = {'df1': pd.DataFrame({'X': [1, 2, 3], 'Y': [4, 5, 6]}),
                         'df2': pd.DataFrame({'Z': [7, 8, 9], 'D': [10, 11, 12]})}
        renamed_dict = rename_columns(data_dict, col_dict)
        for key in renamed_dict.keys():
            pd.testing.assert_frame_equal(renamed_dict[key], expected_dict[key])


class TestDataSeriesIndices(unittest.TestCase):

    def test_get_first_valid_index(self):
        data_series = pd.Series([None, 1, 2, None, 4, 5])

        first_valid_idx = MagicMock(return_value=1)
        data_series.first_valid_index = first_valid_idx

        result = get_first_valid_index(data_series)

        self.assertEqual(result, 1)

    def test_get_last_valid_index(self):
        data_series = pd.Series([None, 1, 2, None, 4, 5])

        last_valid_idx = MagicMock(return_value=4)
        data_series.last_valid_index = last_valid_idx

        result = get_last_valid_index(data_series)

        self.assertEqual(result, 4)

class TestDataManipulation(unittest.TestCase):

    def test_get_date_offset(self):
        # Test for each valid frequency
        self.assertEqual(get_date_offset('D'), pd.DateOffset(days=1))
        self.assertEqual(get_date_offset('W'), pd.DateOffset(weeks=1))
        self.assertEqual(get_date_offset('M'), pd.DateOffset(months=1))
        self.assertEqual(get_date_offset('Q'), pd.DateOffset(months=3))
        self.assertEqual(get_date_offset('Y'), pd.DateOffset(years=1))


    def test_replace_value_with_nan(self):

        data = {
            'A': [0, 1, 2, 0, 4],
            'B': [0, 0, 0, 3, 0],
            'C': [0, 1, 0, 0, 5]
        }
        index = pd.date_range('2022-01-01', periods=5, freq='D')
        data_df = pd.DataFrame(data, index=index)

        result = replace_value_with_nan(data_df, value=0)

        expected_data = {
            'A': [np.NAN, 1, 2, np.NaN, 4],
            'B': [np.NaN, np.NaN, np.NaN, 3, np.NaN],
            'C': [np.NaN, 1, np.NaN, np.NaN, 5]
        }
        expected_df = pd.DataFrame(expected_data, index=index)
        expected_df.index.name = 'Dates'
        for col in result.columns:
            for idx in result.index:
                expected_value = expected_df.loc[idx, col]
                result_value = result.loc[idx, col]
                # Check if both values are NaN
                if pd.isna(expected_value) and pd.isna(result_value):
                    continue
                self.assertEqual(result_value, expected_value)

if __name__ == '__main__':
    unittest.main()