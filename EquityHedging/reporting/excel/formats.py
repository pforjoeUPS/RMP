# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

def set_worksheet_format(workbook):
    """
    Format sheet
    
    Parameters:
    workbook
    """

    cell_format = workbook.add_format()
    cell_format.set_font_name('Calibri')
    cell_format.set_font_size(11)
    cell_format.set_bg_color('#FFFFFF')
    cell_format.set_align('center')
    cell_format.set_align('vcenter')
    return cell_format

def set_title_format(workbook):
    """
    Format title
    
    Parameters:
    workbook
    """
    title_format = workbook.add_format()
    title_format.set_bold()
    title_format.set_font_color('#000000')
    title_format.set_font_name('Calibri')
    title_format.set_font_size(14)
    return title_format

def set_number_format(workbook,num_format, bold=False):
    """
    Format numbers
    
    Parameters:
    workbook
    num_format
    bold -- boolean
    """

    num_format = workbook.add_format({'num_format': num_format, 'bold':bold})
    return num_format
