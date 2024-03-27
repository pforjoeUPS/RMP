import pandas as pd
from Sams_Projects import Marginal_Analysis as marg

df_index_prices =  pd.read_excel("C:\\Users\\PCR7FJW\\Documents\\RMP\\Sams_Projects\\spx_mxwdim_index_data.xlsx", index_col=0, sheet_name='price')
df_index_returns = pd.read_excel("C:\\Users\\PCR7FJW\\Documents\\RMP\\Sams_Projects\\spx_mxwdim_index_data.xlsx", index_col=0, sheet_name='returns')

bmk_index = pd.DataFrame(data=df_index_prices['SPX'], index=df_index_prices.index)
strat_index = pd.DataFrame(data=df_index_prices['MXWDIM'], index=df_index_prices.index)
bmk='SPX'
strat='MXWDIM'
weights=[.01, .02, .03, .04, .05, .06, .07, .08, .09, .1, .11, .12, .13, .14, .15]
test = marg.get_returns_analysis(bmk_index, strat_index, bmk=bmk, strat=strat, freq = 'D', weights=weights)
marg.show_sharpe_cvar(test, bmk, strat, weights)

#TODO: Check if excess return ( R_p - R_b ) is same as rolling(excess_ret)


with pd.ExcelWriter('C:\\Users\\PCR7FJW\\Documents\\RMP\\Sams_Projects\\test.xlsx', engine='openpyxl') as writer:
    test.to_excel(writer, sheet_name='Sheet1', index=False)

    # Get the ExcelWriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Data']

    # Add the plot to the worksheet
    chart = workbook.create_chart({'type': 'column'})
    chart.add_series({'values': '=Data!$B$2:$B$5', 'categories': '=Data!$A$2:$A$5'})
    chart.set_title({'name': 'Age Distribution'})
    chart.set_x_axis({'name': 'Name'})
    chart.set_y_axis({'name': 'Age'})
    chart.set_legend({'none': True})
    worksheet.add_chart(chart, 'D2')

plt.show()