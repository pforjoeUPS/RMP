import pandas as pd
import os

CWD = os.getcwd()
print(CWD)
UPDATE_DATA_FP = CWD + '\\'

excel_files = ["SGMDV25T_Excess_Return_Track_2024_01_05.xlsx",
               "SGIXVR2U_Excess_Return_Track_2024_01_05.xlsx",
               "2024.01.05 - SGI VRR USD Official Chained Tracks.xlsx"
               ]

vrr_data_file = UPDATE_DATA_FP + "vrr_tracks_data - Copy.xlsx"
vrr_data_sheets = ['VRR', 'VRR 2', 'VRR Trend']

vrr_data = {sheet: pd.read_excel(vrr_data_file, sheet_name=sheet, skiprows=1) for sheet in vrr_data_sheets}

for i, df in enumerate([pd.read_excel(UPDATE_DATA_FP + file, sheet_name='Track', header=None, skiprows=4) for file in excel_files]):
    dates, index_name, excess_returns = df.iloc[1:, 1].tolist(), df.iloc[0, 2], df.iloc[1:, 3].tolist()
    vrr_sheet_name = {'SGMDV25T Index': 'VRR', 'SGIXVR2U Index': 'VRR 2', 'SGBVVRRU Index': 'VRR Trend'}.get(index_name)

    if vrr_sheet_name:
        last_date_col_name = vrr_data[vrr_sheet_name].columns[0]
        last_date_vrr = vrr_data[vrr_sheet_name][last_date_col_name].iloc[-1]
        last_date_df_index = dates.index(last_date_vrr)
        last_date_df_index, new_dates, new_excess_returns = dates.index(last_date_vrr), dates[
                                                                                        last_date_df_index + 1:], excess_returns[
                                                                                                                  last_date_df_index + 1:]

        with pd.ExcelWriter(vrr_data_file, engine='openpyxl', mode='a') as writer:
            existing_data = pd.read_excel(writer, sheet_name=vrr_sheet_name)
            existing_data[existing_data.columns[0]] = pd.to_datetime(
                existing_data[existing_data.columns[0]]).dt.strftime('%m/%d/%Y')

            new_data = pd.DataFrame({'Date': new_dates, existing_data.columns[1]: new_excess_returns})
            combined_data = pd.concat([existing_data, new_data], axis=0, ignore_index=True)

            writer.book.remove(writer.book[vrr_sheet_name])
            combined_data.to_excel(writer, sheet_name=vrr_sheet_name, index=False)

print("Data appended and saved successfully.")
