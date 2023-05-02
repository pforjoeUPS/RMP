import json
from datetime import datetime as dt

import numpy as np
import pandas as pd
import six

__all__ = ['reindex_dict_of_series', 'series_to_dict', 'dataframe_to_dict',
           'to_json_compatible_dict', 'to_json', 'strip_strings']


def reindex_dict_of_series(dictionary, index):
    for key in dictionary.keys():
        dictionary[key] = dictionary[key].reindex(index=index, method='ffill')


def series_to_dict(series, index_column='Date', data_column=None):
    if data_column is None:
        data_column = series.name if series.name is not None else 'Value'

    series.name = data_column
    series.index.name = index_column
    return list(series.reset_index().T.to_dict().values())


def dataframe_to_dict(df, index_column='Date'):
    df = df.reset_index()
    df.columns = [index_column if c == 'index' else c for c in df.columns]
    return list(df.T.to_dict().values())


def to_json_compatible_dict(obj):
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if obj is None or any([isinstance(obj, cls) for cls in [bool, int, float, str]]):
        return obj
    if isinstance(obj, dict):
        return {str(key): to_json_compatible_dict(obj[key]) for key in obj}
    if isinstance(obj, pd.DatetimeIndex):
        obj = obj.tolist()
    if isinstance(obj, list):
        return [to_json_compatible_dict(element) for element in obj]
    if any([isinstance(obj, cls) for cls in [pd.Timestamp, dt]]):
        obj = obj.date()
    return str(obj)


def to_json(obj):
    obj = to_json_compatible_dict(obj)

    return '{}'.format(json.dumps(obj, indent=4))


def strip_strings(obj):
    if isinstance(obj, (six.string_types, six.binary_type)):
        return obj.strip()
    if isinstance(obj, dict):
        return {strip_strings(key): strip_strings(obj[key]) for key in obj}
    if isinstance(obj, list):
        return [strip_strings(element) for element in obj]
    return obj
