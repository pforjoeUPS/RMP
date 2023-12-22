# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, Zach Wells
"""

import pandas as pd
from .import formats

def set_analysis_sheet(writer, data_dict, sheet_name, spaces=3,include_fi=False):
    """
    Create excel sheet with:
    Correlation Matrices
    Portfolio Weightings
    Return Statistics
    Hedge Metrics

    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    df_list = data_dict['df_list']
    title_list = data_dict['title_list']
    
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    jump=0
    if include_fi:
        jump=2
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')
    #currency format
    currency_fmt = formats.set_number_format(workbook,num_format='$##0.0')
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='d mmmm yyyy')
    
    int_fmt = formats.set_number_format(workbook, num_format='0')
        
    for n in range(0,len(df_list)):
        try:
            row_dim = row + df_list[n].shape[0]
            col_dim = col + df_list[n].shape[1]
            worksheet.write(row-1, 1, title_list[n], title_format)
            
            #write data into worksheet
            df_list[n].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
        except AttributeError:
            pass
        #format for correlation matrices
        if n<(jump+3):
            #format numbers to digits
            worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'duplicate',
                                      'format':digits_fmt})
            #format matrics using 3 color scale
            worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'3_color_scale'})
        
        #format for weights
        elif n==(jump+3):
            if len(df_list[n]) != 0:
                #format notional weights to currency
                worksheet.conditional_format(row+1,col+1, row+1, col_dim,{'type':'no_blanks',
                                          'format':currency_fmt})
                #format pct and strategy weights to percent
                worksheet.conditional_format(row+2,col+1, row_dim, col_dim,{'type':'no_blanks',
                                          'format':pct_fmt})
            
        #format for return stats
        elif n==(jump+4):
            #format ann. ret and ann. vol to percent
            worksheet.conditional_format(row+1,col+1, row+2, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            #format ret/vol to digits
            worksheet.conditional_format(row+3,col+1, row+3, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            #format max_dd to percent
            worksheet.conditional_format(row+4,col+1, row+4, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            #format ret/dd to digits
            worksheet.conditional_format(row+5,col+1, row+5, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            #format max_1m_dd to percent
            worksheet.conditional_format(row+6,col+1, row+6, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            #format max_1m_dd date to date
            #TODO: figure mout way to format date to short date
            worksheet.conditional_format(row+7,col+1, row+7, col_dim,{'type':'no_blanks',
                                      'format':date_fmt})
            #format ret_max1m_dd to digita
            worksheet.conditional_format(row+8,col+1, row+8, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            
            #format max_3m_dd to percent
            worksheet.conditional_format(row+9,col+1, row+9, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            #format max_3m_dd date to date
            
            #TODO: figure mout way to format date to short date
            worksheet.conditional_format(row+10,col+1, row+10, col_dim,{'type':'no_blanks',
                                      'format':date_fmt})

            #format ret_max1q_dd to digit
            worksheet.conditional_format(row+11,col+1, row+11, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            
            #format skew to digits and avg_pos_ret/avg_neg_ret to digits
            worksheet.conditional_format(row+12,col+1, row+13, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            
            #format downside dev to percent
            worksheet.conditional_format(row+14,col+1, row+14, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            #format sortino to digits
            worksheet.conditional_format(row+15,col+1, row+15, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            
            
        #format for hedge metrics
        else:
            #format benefit count to int
            worksheet.conditional_format(row+1,col+1, row+1, col_dim,{'type':'no_blanks',
                                      'format':int_fmt})
            #format benefit mean and median to percent
            worksheet.conditional_format(row+2,col+1, row+3, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format benefit cumulitive to percent
            worksheet.conditional_format(row+4,col+1, row+4, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format reliability up and down to digits
            worksheet.conditional_format(row+5,col+1, row+6, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
            #format convexity count to int
            worksheet.conditional_format(row+7,col+1, row+7, col_dim,{'type':'no_blanks',
                                      'format':int_fmt})
            #format convexity mean and median to percent
            worksheet.conditional_format(row+8,col+1, row+9, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format convexity cumulitive to percent
            worksheet.conditional_format(row+10,col+1, row+10, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            #format cost count to int
            worksheet.conditional_format(row+11,col+1, row+11, col_dim,{'type':'no_blanks',
                                      'format':int_fmt})
            
            #format cost mean and median to percent
            worksheet.conditional_format(row+12,col+1, row+13, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format cost cumulitive to percent
            worksheet.conditional_format(row+14,col+1, row+14, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format decay days to int
            worksheet.conditional_format(row+15,col+1, row+17, col_dim,{'type':'no_blanks',
                                      'format':int_fmt})
            
        row = row_dim + spaces + 1
    
    return 0

def set_ret_stat_sheet(writer, ret_stat_df, sheet_name='Returns Statistics', spaces=3,include_fi=False, include_bmk=False):
    """
    Create excel sheet with:
    Return Statistics
    

    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    
    jump_0 = 0
    jump_1 = 0
    jump_2 = 0
    jump_3 = 0
    jump_4 = 0
    if include_bmk and include_fi:
        jump_0 = 1
        jump_1 = jump_0+2
        jump_2 = jump_1+4
        jump_3 = jump_2+2
        jump_4 = jump_3+2
    elif include_fi:
        jump_1 = jump_0+1
        jump_2 = jump_1+3
        jump_3 = jump_2
        jump_4 = jump_3
    elif include_bmk:
        jump_0 = 1
        jump_1 = jump_0+1
        jump_2 = jump_1+1
        jump_3 = jump_2+2
        jump_4 = jump_3+2

    if include_bmk:
        worksheet.freeze_panes(row+2, col+1)
    else:
        worksheet.freeze_panes(row+1, col+1)
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')
       
    try:
        row_dim = row + ret_stat_df.shape[0]
        col_dim = col + ret_stat_df.shape[1]
        worksheet.write(row-1, 1, sheet_name, title_format)
        
        #write data into worksheet
        ret_stat_df.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
    except AttributeError:
        pass
    #format for return stats
    #format (ann_ret, excess_ret, alphas) to percent
    worksheet.conditional_format(row+1+jump_0,col+1, row+2+jump_1, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format betas to digits
    worksheet.conditional_format(row+3+jump_1,col+1, row+5+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    
    #format returns (med, avg) to percent
    worksheet.conditional_format(row+6+jump_2,col+1, row+9+jump_2, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format avg_pos_ret to avg_neg_ret ratio to digits
    worksheet.conditional_format(row+10+jump_2,col+1, row+10+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    #format min, max, vols to percent
    worksheet.conditional_format(row+11+jump_2,col+1, row+17+jump_3, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format up/dwn dev ratio, skew, kurt to digits
    worksheet.conditional_format(row+18+jump_3,col+1, row+20+jump_3, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    #format max_dd to percent
    worksheet.conditional_format(row+21+jump_3,col+1, row+21+jump_3, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format ret/vol, ir, sortino, ret/dd ratios to digits
    worksheet.conditional_format(row+22+jump_3,col+1, row+24+jump_4, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    #format mctr to percent
    worksheet.conditional_format(row+25+jump_4,col+1, row+25+jump_4, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    
    return 0

def set_ret_stat_sheet_fi(writer, ret_stat_df, sheet_name='Returns Statistics', spaces=3):
    """
    Create excel sheet with:
    Return Statistics
    

    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 18.29, cell_format)
    row = 2
    col = 0
    
    jump_1=0
    jump_2 = 0
    # worksheet.freeze_panes(row+jump_1, col+1)
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')
       
    try:
        row_dim = row + ret_stat_df.shape[0]
        col_dim = col + ret_stat_df.shape[1]
        worksheet.write(row-1, 1, sheet_name, title_format)
        
        #write data into worksheet
        ret_stat_df.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    except AttributeError:
        pass
    #format for return stats
    #format ret to percent
    worksheet.conditional_format(row+1,col+1, row+4+jump_1, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format ratio to digits
    worksheet.conditional_format(row+5+jump_1,col+1, row+9+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    
    worksheet.conditional_format(row+10+jump_2,col+1, row+13+jump_2, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    return 0

def set_ret_stat_sheet_fi_1(writer, ret_stat_df, sheet_name='Returns Statistics', spaces=3):
    """
    Create excel sheet with:
    Return Statistics
    

    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 18.29, cell_format)
    row = 2
    col = 0
    jump_1=0
    jump_2 = 0
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')
       
    try:
        row_dim = row + ret_stat_df.shape[0]
        col_dim = col + ret_stat_df.shape[1]
        worksheet.write(row-1, 1, sheet_name, title_format)
        
        #write data into worksheet
        ret_stat_df.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    except AttributeError:
        pass
    #format for return stats
    #format ret to percent
    worksheet.conditional_format(row+3,col, row+6+jump_1, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format ratio to digits
    worksheet.conditional_format(row+7+jump_1,col, row+11+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    
    worksheet.conditional_format(row+12+jump_2,col, row+15+jump_2, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    
    return 0

def set_ret_stat_sheet_1(writer, ret_stat_df, sheet_name='Returns Statistics', spaces=3,include_fi=True):
    """
    Create excel sheet with:
    Return Statistics
    

    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    
    jump_1 = 0
    jump_2 = jump_1
    jump_3 = jump_2+1
    jump_4 = jump_3+1
    
    if include_fi:
        jump_1 = 1
        jump_2 = jump_1+3
        # jump_3 = jump_2+1
        # jump_4 = jump_3+1
        
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')
       
    try:
        row_dim = row + ret_stat_df.shape[0]
        col_dim = col + ret_stat_df.shape[1]
        worksheet.write(row-1, 1, sheet_name, title_format)
        
        #write data into worksheet
        ret_stat_df.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
    except AttributeError:
        pass
    #format for return stats
    #format (ann_ret, excess_ret, alphas) to percent
    worksheet.conditional_format(row+3,col+1, row+5+jump_1, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format betas to digits
    worksheet.conditional_format(row+5+jump_1,col+1, row+9+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    
    #format returns (med, avg) to percent
    worksheet.conditional_format(row+10+jump_2,col+1, row+13+jump_2, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format avg_pos_ret to avg_neg_ret ratio to digits
    worksheet.conditional_format(row+14+jump_2,col+1, row+14+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    #format avg_pos_ret to avg_neg_ret ratio to pct
    worksheet.conditional_format(row+15+jump_2,col+1, row+23+jump_2, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format up_down_dev ratio, skew, kurt to digits
    worksheet.conditional_format(row+24+jump_2,col+1, row+26+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    #format max_dd to percent
    worksheet.conditional_format(row+27+jump_2,col+1, row+27+jump_2, col_dim,{'type':'no_blanks',
                              'format':pct_fmt})
    #format ret/vol, ir, sortino, ret/dd ratios to digits
    worksheet.conditional_format(row+28+jump_2,col+1, row+32+jump_2, col_dim,{'type':'no_blanks',
                              'format':digits_fmt})
    
    return 0

def set_corr_sheet(writer, corr_dict, sheet_name='Correlation Analsysis', spaces=3,include_fi=False):
    """
    Create excel sheet with:
    Correlation Matrices
    

    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
     
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    
    worksheet.freeze_panes(row+1, col+1)
        
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
        
    for key in corr_dict:
        try:
            row_dim = row + corr_dict[key][0].shape[0]
            col_dim = col + corr_dict[key][0].shape[1]
            worksheet.write(row-1, 1, corr_dict[key][1], title_format)
            
            #write data into worksheet
            corr_dict[key][0].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
        except AttributeError:
            pass
        #format for correlation matrices
        #format numbers to digits
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
                                  'format':digits_fmt})
        #format matrics using 3 color scale
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'3_color_scale'})
        
        
        row = row_dim + spaces + 1
    
    return 0

def set_normal_sheet(writer, data_dict, sheet_name='Hedgging Framework Metrics', spaces=3):
    """
    Create excel sheet with:
    
    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    df_list = data_dict['df_list']
    title_list = data_dict['title_list']
     
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')

    int_fmt = formats.set_number_format(workbook, num_format='0')
        
    for n in range(0,len(df_list)):
        try:
            row_dim = row + df_list[n].shape[0]
            col_dim = col + df_list[n].shape[1]
            worksheet.write(row-1, 1, title_list[n], title_format)
            
            #write data into worksheet
            df_list[n].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
        except AttributeError:
            pass
        
        if n==1:
            #format all the normalized data to 2 decimals
            worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
                                      'format':digits_fmt})
        else:
 
            #format benefit cumulitive to percent
            worksheet.conditional_format(row+1,col+1, row_dim, col+1,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format reliability up and down to digits
            worksheet.conditional_format(row+1,col+2, row_dim, col+3,{'type':'no_blanks',
                                      'format':digits_fmt})
            
            #format convexity cumulitive to percent
            worksheet.conditional_format(row+1,col+4, row_dim, col+4,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format cost cumulitive to percent
            worksheet.conditional_format(row+1,col+5, row_dim, col+5,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format decay days to int
            worksheet.conditional_format(row+1,col+6, row_dim, col+6,{'type':'no_blanks',
                                      'format':int_fmt})
            

            row = row_dim + spaces + 1
    
    return 0

def set_grouped_data_sheet(writer, quintile_df, decile_df, sheet_name = 'Grouped Data', spaces = 3):
    
    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    df_list = [quintile_df, decile_df]
    title_list = ['Quintile', 'Decile']
     
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')

    
           
    for n in range(0,len(df_list)):
        try:
            row_dim = row + df_list[n].shape[0]
            col_dim = col + df_list[n].shape[1]
            worksheet.write(row-1, 1, title_list[n], title_format)
            
            #write data into worksheet
            df_list[n].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
        except AttributeError:
            pass
        
        if n==1:
            #format all the normalized data to 2 decimals
            worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})
        else:
            #format all the normalized data to 2 decimals
            worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
                                      'format':pct_fmt})     
            row = row_dim + spaces + 1
    
    return 0

def set_mv_sheet(writer,df_returns,sheet_name='Market Values'):
    """
    Create excel sheet for historical returns
    
    Parameters:
    writer -- excel writer
    df_returns -- dataframe
    sheet_name -- string
    """

    workbook = writer.book
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 21, cell_format)
    worksheet.freeze_panes(1, 1)
    row = 0
    col = 0
    #    title_format = set_title_format(workbook)
    
    #currency format
    currency_fmt = formats.set_number_format(workbook,num_format='$#,##0.00')
    
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='mm/dd/yyyy')
        
    row_dim = row + df_returns.shape[0]
    col_dim = col + df_returns.shape[1]
    #    worksheet.write(row-1, 1, sheet_name, title_format)
    df_returns.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    # worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
    #                               'format':pct_fmt})
    worksheet.conditional_format(row,col, row_dim, col,{'type':'no_blanks',
                                  'format':date_fmt})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
                              'format':currency_fmt})
    return 0

    
def set_hist_return_sheet(writer,df_returns,sheet_name='Daily Historical Returns',freeze=True):
    """
    Create excel sheet for historical returns
    
    Parameters:
    writer -- excel writer
    df_returns -- dataframe
    sheet_name -- string
    """

    workbook = writer.book
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 21, cell_format)
    row = 0
    col = 0
    if freeze:
        worksheet.freeze_panes(row+1, col+1)
    #    title_format = set_title_format(workbook)
    
    #percent format
    pct_fmt_pos = formats.set_number_format(workbook,num_format='0.00%')
    #percent format with dark red text.
    pct_fmt_neg = workbook.add_format({'num_format': '0.00%',
                                    'bold':False,
                                    'font_color': '#9C0006'})
    
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='mm/dd/yyyy')
        
    row_dim = row + df_returns.shape[0]
    col_dim = col + df_returns.shape[1]
    #    worksheet.write(row-1, 1, sheet_name, title_format)
    df_returns.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    # worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
    #                               'format':pct_fmt})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '<',
                                  'value': 0,
                                  'format':pct_fmt_neg})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '>',
                                  'value': 0,
                                  'format':pct_fmt_pos})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '=',
                                  'value': 0,
                                  'format':pct_fmt_pos})
    worksheet.conditional_format(row,col, row_dim, col,{'type':'no_blanks',
                                  'format':date_fmt})
    return 0
      
def set_sgi_vrr_sheet(writer,df, sheet_name):
    """
    Create excel sheet for vrr returns
    
    Parameters:
    writer -- excel writer
    df_returns -- dataframe
    sheet_name -- string
    """

    workbook = writer.book
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 21, cell_format)
    row = 0
    col = 0
    #title_format = set_title_format(workbook)
    
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.000000')
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='mm/dd/yyyy')
    int_fmt = formats.set_number_format(workbook, num_format='0')
       
    row_dim = row + df.shape[0]
    col_dim = col + df.shape[1]
    #worksheet.write(row-1, 1, sheet_name, title_format)
    df.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    worksheet.conditional_format(row+1,col+1, row_dim, col+3,{'type':'no_blanks',
                                  'format':digits_fmt})
    worksheet.conditional_format(row+1,col+4, row_dim, col+4,{'type':'no_blanks',
                                  'format':int_fmt})
    worksheet.conditional_format(row+1,col+5, row_dim, col_dim,{'type':'no_blanks',
                                  'format':digits_fmt})
    worksheet.conditional_format(row,col, row_dim, col,{'type':'no_blanks',
                                  'format':date_fmt})
    return 0

#TODO: Edit comments
def set_hist_sheet(writer, df_hist, title = 'Historical Sell-offs', freeze=False):
    """
    Create excel sheet for historical selloffs
    
    Parameters:
    writer -- excel writer
    df_hist -- dataframe
    """
    #create worksheet
    
    workbook = writer.book
    # title = 'Historical Sell-offs'
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=title, startrow=0, startcol=0)
    worksheet = writer.sheets[title]
    worksheet.set_column(0, 1000, 30, cell_format)
    row = 2
    col = 1
    if freeze:
        worksheet.freeze_panes(row+1, col+4)
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='d mmmm yyyy')
    
    #percent format
    pct_fmt = formats.set_number_format(workbook,num_format='0.00%')
    
    #percent format with dark red text.
    pct_fmt1 = workbook.add_format({'num_format': '0.00%',
                                    'bold':False,
                                    'font_color': '#9C0006'})
    
    #percent format with dark green text.
    pct_fmt2 = workbook.add_format({'num_format': '0.00%',
                                    'bold':False,
                                    'font_color': '#006100'})
    
    row_dim = row + df_hist.shape[0]
    col_dim = col + df_hist.shape[1]
    worksheet.write(row-1, 1, title, title_format)
    
    #write data into worksheet
    df_hist.to_excel(writer, sheet_name=title, startrow=row , startcol=1)   
    
    #format for dates
    worksheet.conditional_format(row+1,col+1, row_dim, col+2,{'type':'no_blanks',
                              'format':date_fmt})
    #format equity returns
    worksheet.conditional_format(row+1,col+3, row_dim, col+3,{'type':'no_blanks',
                              'format':pct_fmt})
    #format strat returns
    worksheet.conditional_format(row+1,col+4, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '<',
                                  'value': 0,
                                  'format':pct_fmt1})
    worksheet.conditional_format(row+1,col+4, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '>',
                                  'value': 0,
                                  'format':pct_fmt2})
    return 0

def set_dd_stat_sheet(writer, dd_df, title = 'Drawdown Statistics'):
    """
    Create excel sheet for historical selloffs
    
    Parameters:
    writer -- excel writer
    df_hist -- dataframe
    """
    #create worksheet
    
    workbook = writer.book
    # title = 'Historical Sell-offs'
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=title, startrow=0, startcol=0)
    worksheet = writer.sheets[title]
    worksheet.set_column(0, 1000, 30, cell_format)
    row = 2
    col = 1
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='d mmmm yyyy')
    
    #percent format with dark red text.
    pct_fmt = workbook.add_format({'num_format': '0.00%',
                                    'bold':False,
                                    'font_color': '#9C0006'})
    
    int_fmt = formats.set_number_format(workbook, num_format='0')
    
    row_dim = row + dd_df.shape[0]
    col_dim = col + dd_df.shape[1]
    worksheet.write(row-1, 1, title, title_format)
    
    #write data into worksheet
    dd_df.to_excel(writer, sheet_name=title, startrow=row , startcol=1,index=False)   
    
    #format for dates
    worksheet.conditional_format(row+1,col, row_dim, col+2,{'type':'no_blanks',
                              'format':date_fmt})
    #format dd 
    worksheet.conditional_format(row+1,col+3, row_dim, col+3,{'type':'no_blanks',
                              'format':pct_fmt})
    #format length and recovery
    worksheet.conditional_format(row+1,col+4, row_dim, col_dim,{'type':'no_blanks',
                                  'format':int_fmt})
    #format for dates
    # worksheet.conditional_format(row+1,col+1, row_dim, col+3,{'type':'no_blanks',
    #                           'format':date_fmt})
    # #format equity returns
    # worksheet.conditional_format(row+1,col+4, row_dim, col+4,{'type':'no_blanks',
    #                           'format':pct_fmt})
    # #format strat returns
    # worksheet.conditional_format(row+1,col+5, row_dim, col_dim,{'type':'no_blanks',
    #                               'format':int_fmt})
    return 0

def set_corr_rank_sheet(writer,corr_pack,dates):
    """
    """
    #create excel sheet
    data_range = str(dates['start']).split()[0] + ' to ' + str(dates['end']).split()[0]
    header = 'Data from ' + data_range
    title_list = []
    corr_list = []
    
    #unpack corr_rank_data
    for i in corr_pack:
        title_list.append(corr_pack[str(i)][1])
        corr_list.append(corr_pack[str(i)][0])
    
    sheet_name = 'Correlations Ranks'
    spaces = 3
    
    workbook = writer.book
    #format background color of worksheet to white
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 19, cell_format)
    row = 3
    col = 1
    
    #get formats for worksheet
    #title format
    title_format = formats.set_title_format(workbook)
    #digits format
    digits_fmt = formats.set_number_format(workbook,num_format='0.00')
    
    worksheet.write(0, 0, header, title_format)
    for n in range(0,len(corr_list)):
        row_dim = row + corr_list[n].shape[0]
        col_dim = col + corr_list[n].shape[1]
        worksheet.write(row-1, 1, title_list[n], title_format)
        
        #write data into worksheet
        corr_list[n].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
        
        #format for correlation matrices
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'duplicate',
                                      'format':digits_fmt})
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'3_color_scale'})
        
        row = row_dim + spaces + 1
    return 0

def set_ratio_sheet(writer,df_returns,sheet_name='Sortino', freeze=True):
    """
    Create excel sheet for historical returns
    
    Parameters:
    writer -- excel writer
    df_returns -- dataframe
    sheet_name -- string
    """

    workbook = writer.book
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 21, cell_format)
    if freeze:
        worksheet.freeze_panes(1, 1)
    row = 0
    col = 0
    #    title_format = set_title_format(workbook)
    
    #currency format
    number_fmt = formats.set_number_format(workbook,num_format='0.00')
    
    #date format
    date_fmt = formats.set_number_format(workbook, num_format='mm/dd/yyyy')
        
    row_dim = row + df_returns.shape[0]
    col_dim = col + df_returns.shape[1]
    #    worksheet.write(row-1, 1, sheet_name, title_format)
    df_returns.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    # worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
    #                               'format':pct_fmt})
    worksheet.conditional_format(row,col, row_dim, col,{'type':'no_blanks',
                                  'format':date_fmt})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,{'type':'no_blanks',
                              'format':number_fmt})
    return 0

def set_mtd_ytd_sheet(writer,df_returns,sheet_name='MTD-YTD'):
    """
    Create excel sheet for historical returns
    
    Parameters:
    writer -- excel writer
    df_returns -- dataframe
    sheet_name -- string
    """

    workbook = writer.book
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 10.67, cell_format)
    row = 1
    col = 0
    #    title_format = set_title_format(workbook)
    
    #percent format
    pct_fmt_pos = formats.set_number_format(workbook,num_format='0.00%')
    #percent format with dark red text.
    pct_fmt_neg = workbook.add_format({'num_format': '0.00%',
                                    'bold':False,
                                    'font_color': '#9C0006'})
    
    
    #title format
    title_format = formats.set_title_format(workbook)
       
    try:
        row_dim = row + df_returns.shape[0]
        col_dim = col + df_returns.shape[1]
        worksheet.write(row-1, 0, 'Return History', title_format)
        
        #write data into worksheet
        df_returns.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)  
    except AttributeError:
        pass  
    
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '<',
                                  'value': 0,
                                  'format':pct_fmt_neg})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '>',
                                  'value': 0,
                                  'format':pct_fmt_pos})
    worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                 {'type':'cell',
                                  'criteria': '=',
                                  'value': 0,
                                  'format':pct_fmt_pos})
    # worksheet.conditional_format(row,col, row_dim, col,{'type':'no_blanks',
    #                               'format':date_fmt})
    return 0


def set_mtd_ytd_sheet_1(writer,data_dict,sheet_name='MTD-YTD'):
    """
    Create excel sheet for historical returns
    
    Parameters:
    writer -- excel writer
    df_returns -- dataframe
    sheet_name -- string
    """

    workbook = writer.book
    cell_format = formats.set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 10.67, cell_format)
    row = 1
    col = 0
    spaces = 2
    #    title_format = set_title_format(workbook)
    
    #percent format
    pct_fmt_pos = formats.set_number_format(workbook,num_format='0.00%')
    #percent format with dark red text.
    pct_fmt_neg = workbook.add_format({'num_format': '0.00%',
                                    'bold':False,
                                    'font_color': '#9C0006'})
    #pull out lists from data_dict
    # df_list = data_dict['df_list']
    # title_list = data_dict['title_list']
    
    #title format
    title_format = formats.set_title_format(workbook)
       
    for key in data_dict:
        try:
            row_dim = row + data_dict[key].shape[0]
            col_dim = col + data_dict[key].shape[1]+1
            worksheet.write(row-1, 0, f'{key} Return History', title_format)
            #
            #write data into worksheet
            data_dict[key].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col) 
        except AttributeError:
            pass
    # for n in range(0,len(df_list)):
    #     try:
    #         row_dim = row + df_list[n].shape[0]
    #         col_dim = col + df_list[n].shape[1]+1
    #         worksheet.write(row-1, 0, f'{title_list[n]} History', title_format)
    #         #
    #         #write data into worksheet
    #         df_list[n].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
    #     except AttributeError:
    #         pass
        
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                     {'type':'cell',
                                      'criteria': '<',
                                      'value': 0,
                                      'format':pct_fmt_neg})
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                     {'type':'cell',
                                      'criteria': '>',
                                      'value': 0,
                                      'format':pct_fmt_pos})
        worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                     {'type':'cell',
                                      'criteria': '=',
                                      'value': 0,
                                      'format':pct_fmt_pos})
        
       
        row = row_dim + spaces + 1
        
    return 0