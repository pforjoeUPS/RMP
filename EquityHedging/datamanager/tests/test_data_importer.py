import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
from EquityHedging.datamanager.data_importer import (
    ExcelImporter, DataImporter,
    InnocapDataImporter, BbgDataImporter, NexenDataImporter
)

class BaseDataImporterTest(unittest.TestCase):
    def setUp(self):
        self.mock_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})

    def assert_data_importer_initialized_correctly(self, data_importer, filepath, sheet_name, index_col, skip_rows,
                                                   data_source, col_dict, index_data, expected_data=None):
        self.assertEqual(data_importer.file_path, filepath)
        self.assertEqual(data_importer.sheet_name, sheet_name)
        self.assertEqual(data_importer.index_col, index_col)
        self.assertEqual(data_importer.skip_rows, skip_rows)
        self.assertEqual(data_importer.data_source, data_source)
        self.assertEqual(data_importer.col_dict, col_dict)
        self.assertEqual(data_importer.index_data, index_data)
        if expected_data is not None:
            pd.testing.assert_frame_equal(data_importer.data_import, expected_data)
        else:
            self.assertTrue(data_importer.data_import.equals(self.mock_data))


class TestDataImporter(BaseDataImporterTest):
    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_read_excel_data(self, mock_read_excel):
        mock_data = {'row_1': [1, 2, 3], 'row_2': ['a', 'b', 'c']}
        mock_read_excel.return_value = mock_data

        result = ExcelImporter('test_filepath.xlsx').read_excel_data()

        self.assertEqual(result, mock_data)
        mock_read_excel.assert_called_once()

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.get_excel_sheet_names')
    def test_get_sheet_names_xls(self, mock_get_sheet_names):
        mock_get_sheet_names.return_value = ['Sheet1', 'Sheet2']

        result = ExcelImporter('test_filepath.xls').get_excel_sheet_names()

        self.assertEqual(result, ['Sheet1', 'Sheet2'])
        mock_get_sheet_names.assert_called_once()

class TestDataImporterInitialization(BaseDataImporterTest):
    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_data_importer_init(self, mock_read_excel_data):
        mock_read_excel_data.return_value = self.mock_data

        data_importer = DataImporter('test_filepath.xlsx')
        self.assert_data_importer_initialized_correctly(data_importer, 'test_filepath.xlsx', 0, 0, [], 'custom', {},
                                                        False)

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_innocap_data_importer_init(self, mock_read_excel_data):
        mock_read_excel_data.return_value = self.mock_data

        innocap_data_importer = InnocapDataImporter('test_filepath.xlsx')
        self.assert_data_importer_initialized_correctly(
            innocap_data_importer, 'test_filepath.xlsx', 0, None, [0, 1], 'innocap', {}, False
        )

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    @patch('EquityHedging.datamanager.data_importer.BbgDataImporter.get_col_dict')
    def test_bbg_data_importer_init(self, mock_get_col_dict, mock_read_excel_data):
        mock_read_excel_data.return_value = self.mock_data
        mock_get_col_dict.return_value = {'Index': 'Description'}

        bbg_data_importer = BbgDataImporter('test_filepath.xlsx')
        self.assert_data_importer_initialized_correctly(
            bbg_data_importer, 'test_filepath.xlsx', 0, 0, [0, 1, 2, 4, 5, 6], 'bbg', {'Index': 'Description'}, True
        )
        mock_get_col_dict.assert_called_once()

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
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
        expected_data = mock_data[['Name', 'Account Id', 'Return Type', 'Dates', 'Market Value', 'Return']]
        expected_col_dict = {}
        self.assert_data_importer_initialized_correctly(
            nexen_data_importer, 'test_filepath.xlsx', 0, None, [], 'nexen', expected_col_dict, False, expected_data
        )


class TestDataImporterMethods(BaseDataImporterTest):

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    @patch('EquityHedging.datamanager.data_importer.dm.drop_nas')
    @patch('EquityHedging.datamanager.data_importer.dm.rename_columns')
    def test_data_importer_import_data(self, mock_rename_columns, mock_drop_nas, mock_read_excel_data):
        mock_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_read_excel_data.return_value = mock_data
        mock_drop_nas.return_value = mock_data
        mock_rename_columns.return_value = mock_data

        data_importer = DataImporter('test_filepath.xlsx')
        result = data_importer.import_data()

        mock_read_excel_data.assert_called()


        # Check if rename_columns is called
        if data_importer.col_dict:
            mock_rename_columns.assert_called_with(mock_data, col_dict={})
        else:
            mock_rename_columns.assert_not_called()

        self.assertTrue(result.equals(mock_data))

    @patch('EquityHedging.datamanager.data_importer.ExcelImporter.read_excel_data')
    def test_bbg_data_importer_get_col_dict(self, mock_read_excel_data):
        mock_keys_data = pd.DataFrame({'Index': ['A', 'B'], 'Description': ['DescA', 'DescB']})
        mock_read_excel_data.return_value = mock_keys_data

        bbg_data_importer = BbgDataImporter('test_filepath.xlsx')
        result = bbg_data_importer.get_col_dict()

        expected_result = {'A': 'DescA', 'B': 'DescB'}
        self.assertEqual(result, expected_result)
        mock_read_excel_data.assert_called_with()


if __name__ == '__main__':
    unittest.main()
