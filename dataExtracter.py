import pandas as pd
import numpy as np


if __name__ == '__main__':
    # file notation
    src_file_name = 'Untitled_data'
    src_sheet_name = 'Multicomponent Data'
    src_col_name = 'CY3'

    sheet_name_body = 'ads'
    sheet_name_num = [8, 19, 1]
    col_name_body = 'pH '
    col_name_num = [5.0, 8.5, 0.5]

    T_init = 5
    T_final = 95
    T_step = 0.3

    nb_steps = int((T_final-T_init) / T_step) + 1
    col_T = np.linspace(T_init, T_final, num=nb_steps, endpoint=True)

    excel_data = pd.read_excel(src_file_name + '.xls', sheet_name=src_sheet_name)
    allData = excel_data[src_col_name].tolist()
    col = [0] * nb_steps

    with pd.ExcelWriter(src_file_name + '_processed.xlsx') as writer:
        for m in np.arange(sheet_name_num[0], sheet_name_num[1] + sheet_name_num[2], sheet_name_num[2]):
            for p in np.arange(col_name_num[0], col_name_num[1] + col_name_num[2], col_name_num[2]):
                for i in range(len(col)):
                    col[i] = allData[96*i + 12*int((p-col_name_num[0])/col_name_num[2]) + int((m-sheet_name_num[0])/sheet_name_num[2])]

                # writing to .xls
                df = pd.DataFrame({'T': col_T})
                df.to_excel(writer, sheet_name=sheet_name_body + str(m), index=False, startcol=0)
                df = pd.DataFrame({col_name_body + str(p): col})
                df.to_excel(writer, sheet_name=sheet_name_body + str(m), index=False, startcol=(p - col_name_num[0]) / col_name_num[2] + 1)

        pass

