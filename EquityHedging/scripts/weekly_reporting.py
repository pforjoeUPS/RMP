import openpyxl

def copy_cells(source_file, destination_file, source_sheet, destination_sheet, cell_mappings):
    # Load the source workbook
    source_workbook = openpyxl.load_workbook(source_file, data_only=True)
    source_ws = source_workbook[source_sheet]
    
    # Load the destination workbook
    destination_workbook = openpyxl.load_workbook(destination_file)
    destination_ws = destination_workbook[destination_sheet]
    
    # Copy cells from source to destination
    for source_cell, destination_cell in cell_mappings.items():
        if ':' in source_cell and ':' in destination_cell:
            source_range = source_ws[source_cell]
            destination_range = destination_ws[destination_cell]
            
            for source_row, destination_row in zip(source_range, destination_range):
                for source_cell, destination_cell in zip(source_row, destination_row):
                    destination_cell.value = source_cell.value
        else:
            source_value = source_ws[source_cell].value
            destination_ws[destination_cell].value = source_value
    
    # Save the destination workbook
    destination_workbook.save(destination_file)
    print("Cells copied successfully!")

# Dollar Returns

source_file = r'C:\Users\HQP6CBS\Documents\Weekly Reporting\July28\NISA - Total Program Dollar Returns - 07-28-2023.xlsx'
destination_file = r'C:\Users\HQP6CBS\Documents\Weekly Reporting\July28\Weekly Strategy Report for IC - 07-28-2023.xlsx'

source_sheet = 'Dollar Returns'
destination_sheet = 'Dollar Returns'

# Specify the cell mappings in the format {'source_cell/range': 'destination_cell/range'}
cell_mappings = {
    'B3:D22': 'K3:M22',
    'C26:C45':'Q3:Q22'
}

copy_cells(source_file, destination_file, source_sheet, destination_sheet, cell_mappings)

#Currencies

source_file = r'C:\Users\HQP6CBS\Documents\Weekly Reporting\July28\UPS Profit-Loss Daily Update - July 28, 2023.xlsx'

source_sheet = 'UPS Summary'
destination_sheet = 'Currencies'

cell_mappings = {
    'H50:H51': 'E5:E6',
    'I50:I51': 'G5:G6',
    'H52:H55': 'M5:M8',
    'I52:I55': 'O5:O8',
    'H58' : 'M9',
    'I58' : 'O9'
}
copy_cells(source_file, destination_file, source_sheet, destination_sheet, cell_mappings)

#ART

source_file = r'C:\Users\HQP6CBS\Documents\Weekly Reporting\July28\NISA - UPS ART Program Holdings - 07-28-2023.xlsx'

#destination_file = r'C:\Users\HQP6CBS\Documents\Weekly Reporting\June23\Weekly Strategy Report for IC - 06-23-2023.xlsx'
source_sheet = 'Program Overview'
source_sheet2 = 'Volatility'
destination_sheet = 'ART'

cell_mappings = {
    'D8:E16': 'H6:I14',
    'G7:G16': 'K5:K14'
}
cell_mappings2 = {
    'H58' : 'H5',
    'G58' : 'I5'
}
copy_cells(source_file, destination_file, source_sheet, destination_sheet, cell_mappings)
copy_cells(source_file, destination_file, source_sheet2, destination_sheet, cell_mappings2)


