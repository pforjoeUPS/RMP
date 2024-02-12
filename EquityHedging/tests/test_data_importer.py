import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
from EquityHedging.datamanager.data_importer import (
    DataImporter, InnocapDataImporter, BbgDataImporter, NexenDataImporter, NEXEN_DATA_COL_DICT
)


class BaseDataImporterTest(unittest.TestCase):
    def setUp(self):
        self.mock_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})

    def assert_data_importer_initialized_correctly(self, data_importer, filepath, sheet_name, index_col, skip_rows,
                                                   data_source, col_dict, drop_na, index_data, expected_data=None):
        self.assertEqual(data_importer.filepath, filepath)
        self.assertEqual(data_importer.sheet_name, sheet_name)
        self.assertEqual(data_importer.index_col, index_col)
        self.assertEqual(data_importer.skip_rows, skip_rows)
        self.assertEqual(data_importer.data_source, data_source)
        self.assertEqual(data_importer.col_dict, col_dict)
        self.assertEqual(data_importer.drop_na, drop_na)
        self.assertEqual(data_importer.index_data, index_data)
        if expected_data is not None:
            pd.testing.assert_frame_equal(data_importer.data_import, expected_data)
        else:
            self.assertTrue(data_importer.data_import.equals(self.mock_data))


class TestDataImporter(BaseDataImporterTest):
    @patch('EquityHedging.datamanager.data_importer.pd.read_excel')
    def test_read_excel_data(self, mock_read_excel):
        mock_data = {'row_1': [1, 2, 3], 'row_2': ['a', 'b', 'c']}
        mock_read_excel.return_value = mock_data

        result = DataImporter.read_excel_data('test_filepath.xlsx')

        self.assertEqual(result, mock_data)
        # mock_read_excel.assert_called_with('test_filepath.xlsx', 0, index_col=0, skiprows=[], usecols=None)

    @patch('EquityHedging.datamanager.data_importer.xlrd.open_workbook')
    def test_get_sheet_names_xls(self, mock_open_workbook):
        mock_workbook = MagicMock()
        mock_workbook.sheet_names.return_value = ['Sheet1', 'Sheet2']
        mock_open_workbook.return_value = mock_workbook

        result = DataImporter.get_excel_sheet_names('test_filepath.xls')

        self.assertEqual(result, ['Sheet1', 'Sheet2'])


class TestDataImporterInitialization(BaseDataImporterTest):
    @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
    def test_data_importer_init(self, mock_read_excel_data):
        mock_read_excel_data.return_value = self.mock_data

        data_importer = DataImporter('test_filepath.xlsx')
        self.assert_data_importer_initialized_correctly(data_importer, 'test_filepath.xlsx', 0, 0, [], 'custom', {},
                                                        False, False)

    @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
    def test_innocap_data_importer_init(self, mock_read_excel_data):
        mock_read_excel_data.return_value = self.mock_data

        innocap_data_importer = InnocapDataImporter('test_filepath.xlsx')
        self.assert_data_importer_initialized_correctly(
            innocap_data_importer, 'test_filepath.xlsx', 0, None, [0, 1], 'innocap', {}, False, False
        )

    @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
    @patch('EquityHedging.datamanager.data_importer.BbgDataImporter.get_col_dict')
    def test_bbg_data_importer_init(self, mock_get_col_dict, mock_read_excel_data):
        mock_read_excel_data.return_value = self.mock_data
        mock_get_col_dict.return_value = {'Index': 'Description'}

        bbg_data_importer = BbgDataImporter('test_filepath.xlsx')
        self.assert_data_importer_initialized_correctly(
            bbg_data_importer, 'test_filepath.xlsx', 0, 0, [0, 1, 2, 4, 5, 6], 'bbg', {'Index': 'Description'}, False,
            True
        )
        mock_get_col_dict.assert_called_once()

    @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
    def test_nexen_data_importer_init(self, mock_read_excel_data):
        mock_data = pd.DataFrame({
            'Name': ['John', 'Jane'],
            'Account Id': [1, 2],
            'Return Type': ['Type1', 'Type2'],
            'Dates': ['2022-01-01', '2022-01-02'],
            'Market Value': [100, 200],
            'Return': [0.01, 0.02]
        })
        mock_read_excel_data.return_value = mock_data

        nexen_data_importer = NexenDataImporter('test_filepath.xlsx')
        expected_data = mock_data[NEXEN_DATA_COL_DICT.values()]
        self.assert_data_importer_initialized_correctly(
            nexen_data_importer, 'test_filepath.xlsx', 0, None, [], 'nexen', NEXEN_DATA_COL_DICT, False, False,
            expected_data
        )


class TestDataImporterMethods(BaseDataImporterTest):

    @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
    @patch('EquityHedging.datamanager.data_importer.dm.drop_nas')
    @patch('EquityHedging.datamanager.data_importer.dm.rename_columns')
    def test_data_importer_import_data(self, mock_rename_columns, mock_drop_nas, mock_read_excel_data):
        mock_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_read_excel_data.return_value = mock_data
        mock_drop_nas.return_value = mock_data
        mock_rename_columns.return_value = mock_data

        data_importer = DataImporter(filepath='test_filepath.xlsx')
        result = data_importer.import_data()

        mock_read_excel_data.assert_called_with(filepath = 'test_filepath.xlsx', sheet_name = 0, index_col=0, skip_rows=[])
        # mock_drop_nas.assert_called_with(mock_data)

        if data_importer.col_dict:
            mock_rename_columns.assert_called_with(mock_data, col_dict={})
        else:
            mock_rename_columns.assert_not_called()

        self.assertTrue(result.equals(mock_data))

    @patch('EquityHedging.datamanager.data_importer.DataImporter.read_excel_data')
    def test_bbg_data_importer_get_col_dict(self, mock_read_excel_data):
        mock_keys_data = pd.DataFrame({'Index': ['A', 'B'], 'Description': ['DescA', 'DescB']})
        mock_read_excel_data.return_value = mock_keys_data

        bbg_data_importer = BbgDataImporter('test_filepath.xlsx')
        result = bbg_data_importer.get_col_dict()

        expected_result = {'A': 'DescA', 'B': 'DescB'}
        self.assertEqual(result, expected_result)
        mock_read_excel_data.assert_called_with(filepath='test_filepath.xlsx', sheet_name='key', index_col=None,
                                                use_cols='A:B')


if __name__ == '__main__':
    unittest.main()

# import unittest
# from unittest.mock import patch, MagicMock
#
# import pandas as pd
# from EquityHedging.datamanager.data_importer import (
#     read_excel_data, get_excel_sheet_names, DataImporter,
#     InnocapDataImporter, BbgDataImporter, NexenDataImporter, NEXEN_DATA_COL_DICT
# )
#
#
# class BaseDataImporterTest(unittest.TestCase):
#     def setUp(self):
#         self.mock_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
#
#     def assert_data_importer_initialized_correctly(self, data_importer, filepath, sheet_name, index_col, skip_rows,
#                                                    data_source, col_dict, index_data, expected_data=None):
#         self.assertEqual(data_importer.filepath, filepath)
#         self.assertEqual(data_importer.sheet_name, sheet_name)
#         self.assertEqual(data_importer.index_col, index_col)
#         self.assertEqual(data_importer.skip_rows, skip_rows)
#         self.assertEqual(data_importer.data_source, data_source)
#         self.assertEqual(data_importer.col_dict, col_dict)
#         self.assertEqual(data_importer.index_data, index_data)
#         # self.assertTrue(data_importer.data_import.equals(self.mock_data))
#         if expected_data is not None:
#             pd.testing.assert_frame_equal(data_importer.data_import, expected_data)
#         else:
#             self.assertTrue(data_importer.data_import.equals(self.mock_data))
#
#
# class TestDataImporter(BaseDataImporterTest):
#     @patch('EquityHedging.datamanager.data_importer.pd.read_excel')
#     def test_read_excel_data(self, mock_read_excel):
#         mock_data = {'row_1': [1, 2, 3], 'row_2': ['a', 'b', 'c']}
#         mock_read_excel.return_value = mock_data
#
#         result = read_excel_data('test_filepath.xlsx')
#
#         self.assertEqual(result, mock_data)
#         mock_read_excel.assert_called_once_with('test_filepath.xlsx', 0, index_col=0, skiprows=[], usecols=None)
#
#     @patch('EquityHedging.datamanager.data_importer.xlrd.open_workbook')
#     def test_get_sheet_names_xls(self, mock_open_workbook):
#         mock_workbook = MagicMock()
#         mock_workbook.sheet_names.return_value = ['Sheet1', 'Sheet2']
#         mock_open_workbook.return_value = mock_workbook
#
#         result = get_excel_sheet_names('test_filepath.xls')
#
#         self.assertEqual(result, ['Sheet1', 'Sheet2'])
#         mock_open_workbook.assert_called_once_with('test_filepath.xls')
#
#
# class TestDataImporterInitialization(BaseDataImporterTest):
#     @patch('EquityHedging.datamanager.data_importer.read_excel_data')
#     def test_data_importer_init(self, mock_read_excel_data):
#         mock_read_excel_data.return_value = self.mock_data
#
#         data_importer = DataImporter('test_filepath.xlsx')
#         self.assert_data_importer_initialized_correctly(data_importer, 'test_filepath.xlsx', 0, 0, [], 'custom', {},
#                                                         False)
#
#     @patch('EquityHedging.datamanager.data_importer.read_excel_data')
#     def test_innocap_data_importer_init(self, mock_read_excel_data):
#         mock_read_excel_data.return_value = self.mock_data
#
#         innocap_data_importer = InnocapDataImporter('test_filepath.xlsx')
#         self.assert_data_importer_initialized_correctly(
#             innocap_data_importer, 'test_filepath.xlsx', 0, None, [0, 1], 'innocap', {}, False
#         )
#
#     @patch('EquityHedging.datamanager.data_importer.read_excel_data')
#     @patch('EquityHedging.datamanager.data_importer.BbgDataImporter.get_col_dict')
#     def test_bbg_data_importer_init(self, mock_get_col_dict, mock_read_excel_data):
#         mock_read_excel_data.return_value = self.mock_data
#         mock_get_col_dict.return_value = {'Index': 'Description'}
#
#         bbg_data_importer = BbgDataImporter('test_filepath.xlsx')
#         self.assert_data_importer_initialized_correctly(
#             bbg_data_importer, 'test_filepath.xlsx', 0, 0, [0, 1, 2, 4, 5, 6], 'bbg', {'Index': 'Description'}, True
#         )
#         mock_get_col_dict.assert_called_once()
#
#     @patch('EquityHedging.datamanager.data_importer.read_excel_data')
#     def test_nexen_data_importer_init(self, mock_read_excel_data):
#         # Modify the mock data to include all columns from NEXEN_DATA_COL_DICT
#         mock_data = pd.DataFrame({
#             'Name': ['John', 'Jane'],
#             'Account Id': [1, 2],
#             'Return Type': ['Type1', 'Type2'],
#             'Dates': ['2022-01-01', '2022-01-02'],
#             'Market Value': [100, 200],
#             'Return': [0.01, 0.02]
#         })
#         mock_read_excel_data.return_value = mock_data
#
#         nexen_data_importer = NexenDataImporter('test_filepath.xlsx')
#         expected_data = mock_data[NEXEN_DATA_COL_DICT.values()]  # Select only the expected columns
#         expected_col_dict = NEXEN_DATA_COL_DICT
#         self.assert_data_importer_initialized_correctly(
#             nexen_data_importer, 'test_filepath.xlsx', 0, None, [], 'nexen', expected_col_dict, False, expected_data
#         )
#
#
# class TestDataImporterMethods(BaseDataImporterTest):
#
#     @patch('EquityHedging.datamanager.data_importer.read_excel_data')
#     @patch('EquityHedging.datamanager.data_importer.dm.drop_nas')
#     @patch('EquityHedging.datamanager.data_importer.dm.rename_columns')
#     def test_data_importer_import_data(self, mock_rename_columns, mock_drop_nas, mock_read_excel_data):
#         mock_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
#         mock_read_excel_data.return_value = mock_data
#         mock_drop_nas.return_value = mock_data
#         mock_rename_columns.return_value = mock_data
#
#         data_importer = DataImporter('test_filepath.xlsx')
#         result = data_importer.import_data()
#
#         mock_read_excel_data.assert_called_with('test_filepath.xlsx', 0, index_col=0, skip_rows=[])
#         mock_drop_nas.assert_called_with(mock_data)
#
#         # Check if rename_columns is called
#         if data_importer.col_dict:
#             mock_rename_columns.assert_called_with(mock_data, col_dict={})
#         else:
#             mock_rename_columns.assert_not_called()
#
#         self.assertTrue(result.equals(mock_data))
#
#     @patch('EquityHedging.datamanager.data_importer.read_excel_data')
#     def test_bbg_data_importer_get_col_dict(self, mock_read_excel_data):
#         mock_keys_data = pd.DataFrame({'Index': ['A', 'B'], 'Description': ['DescA', 'DescB']})
#         mock_read_excel_data.return_value = mock_keys_data
#
#         bbg_data_importer = BbgDataImporter('test_filepath.xlsx')
#         result = bbg_data_importer.get_col_dict()
#
#         expected_result = {'A': 'DescA', 'B': 'DescB'}
#         self.assertEqual(result, expected_result)
#         mock_read_excel_data.assert_called_with(filepath='test_filepath.xlsx', sheet_name='key', index_col=None,
#                                                 use_cols='A:B')
#
#
# if __name__ == '__main__':
#     unittest.main()
