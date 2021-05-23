# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 15:50:35 2021

@author: Powis Forjoe
"""

import pytest
import pandas as pd
import os
from ..import returns_stats as rs

#TODO: Separate test_data unto different files, easier to comprehend
RETURNS_DF = pd.read_excel('data/test_data.xlsx', sheet_name='Monthly', index_col=0)
INDEX_DF = pd.read_excel('data/test_data.xlsx', sheet_name='Index', index_col=0)

#TODO: add test cases for DD dates
#TODO: add test cases using other frequencies and strats

def test_cwd():
    result = os.getcwd()
    assert result == '//'

def test_ann_return():
    result = rs.get_ann_return(RETURNS_DF['SPTR'])
    assert result == pytest.approx(0.3148643),"Annualized Return should be 0.3148643"

def test_ann_vol():
    result = rs.get_ann_vol(RETURNS_DF['SPTR'])
    assert result == pytest.approx(0.1289242),"Annualized vol should be 0.1289242"

def test_max_dd():
    result = rs.get_max_dd(INDEX_DF['SPTR'])
    assert result == pytest.approx(-0.0635481),"Max DD should be -0.063481"

def test_max_1m_dd():
    result = rs.get_max_dd_freq(INDEX_DF['SPTR'])['max_dd']
    assert result == pytest.approx(-0.0635481),"Max 1M DD should be -0.0635481"

def test_max_3m_dd():
    result = rs.get_max_dd_freq(INDEX_DF['SPTR'],max_3m_dd=True)['max_dd']
    assert result == pytest.approx(-0.00669775),"Max 3M DD should be -0.0066978"

def test_avg_pos_neg():
    result = rs.get_avg_pos_neg(RETURNS_DF,'SPTR')
    assert result == pytest.approx(-0.91666901),"Avg Pos Neg should be -0.91666901"

def test_down_stddev():
    result = rs.get_down_stddev(RETURNS_DF,'SPTR')
    assert result == pytest.approx(0.116859687),"Downside deviation should be 0.116859687"

def test_sortino():
    result = rs.get_sortino_ratio(RETURNS_DF,'SPTR')
    assert result == pytest.approx(2.6943791),"Sortino Ratio should be 2.6943791"
