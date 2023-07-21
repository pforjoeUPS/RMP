import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import EquityHedging.analytics.util as ut
import EquityHedging.analytics.hedge_metrics as hm
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary 
import openpyxl
from openpyxl.drawing.image import Image
import io

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False

returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

#get notional weights

notional_weights = dm.get_notional_weights(returns['Monthly'])
returns = dm.create_vrr_portfolio(returns,notional_weights)
notional_weights[4:6] = [notional_weights[4] + notional_weights[5]]

df_weights = ut.get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)
returns_df = returns['Daily']

#get weighted strats and weighted hedges
r = summary.get_weighted_data(returns_df, notional_weights)

# Step 3: Compute hedge metrics, this line causes an error for some reason but the rest of it runs fine. 
df_hedge_metrics = hm.get_hedge_metrics(r,freq = "1D", full_list=True)

# Step 4: Select specific metrics for spider chart
metrics_to_plot = df_hedge_metrics.transpose()
metrics = metrics_to_plot[["Benefit Cum", "Convexity Cum", "Cost Cum", "Downside Reliability", "Decay Days (25% retrace)"]]

# Step 5: Normalize the hedge metrics
normalized_data = ut.get_normalized_data(metrics)

# Get the strategy names
strategies = normalized_data.index

# Get the values for each strategy
values = normalized_data.values

# Create a radar chart for each strategy
for i in range(len(strategies)):
    # Get the values for the current strategy
    strategy_values = values[i].tolist()
    strategy_values.append(strategy_values[0])  # Close the loop
    
    # Create a new figure and polar axis for the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    # Set the angles and plot the strategy values
    angles = np.linspace(0, 2 * np.pi, len(metrics.columns), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    ax.plot(angles, strategy_values)
    
    # Set the labels for each angle
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics.columns)
    
    # Set the title as the strategy name
    ax.set_title(strategies[i])
    
    # Show the plot
    plt.show()

# Creates an excel file with the normalized_data Dataframe
excel_file_path = r'C:\Users\mxm6sft\Documents\GitHub\RMP\EquityHedging\reports\Radar_Chart.xlsx'
    
writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

normalized_data.to_excel(writer, sheet_name='Normalized_Data', startcol=1, index=False)

workbook = writer.book
worksheet = writer.sheets['Normalized_Data']

cell_format = workbook.add_format({'bold': True, 'border': 1})
worksheet.write('A1', 'Index')

for i, column in enumerate(normalized_data.columns):
    column_width = max(normalized_data[column].astype(str).map(len).max(), len(column)) + 2
    worksheet.set_column(i + 1, i + 1, column_width)

first_column_width = max(normalized_data.index.astype(str).map(len).max(), len('Strategy')) + 2
worksheet.set_column(0, 0, first_column_width + 5)

for i, strategy_name in enumerate(normalized_data.index):
    worksheet.write(i + 1, 0, strategy_name)

writer.save()

# Creates graphs in the excel file
wb = openpyxl.load_workbook(excel_file_path)
sheet = wb['Normalized_Data']

for i, strategy_name in enumerate(normalized_data.index):
    # Get the values for the current strategy
    strategy_values = sheet[f'B{i+2}:F{i+2}'][0]
    strategy_values = [cell.value for cell in strategy_values]

    # Create a new figure and polar axis for the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})

    # Set the angles and plot the strategy values
    angles = np.linspace(0, 2 * np.pi, len(metrics.columns), endpoint=False).tolist()
    ax.plot(angles, strategy_values)

    # Set the labels for each angle
    ax.set_xticks(angles)
    ax.set_xticklabels(metrics.columns)

    # Set the title as the strategy name
    ax.set_title(strategy_name)

    # Save the radar chart to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Add some spacing between radar charts
    x_offset = 15
    y_offset = 10 + i * 120

    # Convert the buffer image to an openpyxl Image
    img = Image(buffer)
    img.width = 400
    img.height = 400

    # Insert the Image to the worksheet
    sheet.add_image(img, f'A{i+15}')

    # Close the buffer
    buffer.close()

# Save the modified Excel file
wb.save(excel_file_path)