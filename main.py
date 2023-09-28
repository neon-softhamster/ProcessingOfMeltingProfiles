# This program allow to find out "BckIntensity" in
# N(A, K, T) = 1 / (exp(A) * exp(K*T) + BckIntensity) normalization factor
# in such a way that the given section of the normalized function
# Melt_Curve(T) / N(A, K, T)
# (at high temperatures) is horizontal

import pandas as pd
import numpy as np


def dispersion(a, b, Y, T):
    disp = 0
    for q in range(len(Y)):
        disp = disp + (Y[q] - (a*T[q] + b)) ** 2
    return np.sqrt(disp)


if __name__ == '__main__':
    # file notation
    file_name = 'ATPaptACmm+4ATP'
    sheet_name_body = 'MM ATP '
    sheet_name_num = [1, 4, 1]
    col_name_body = 'pH '
    col_name_num = [5.0, 8.5, 0.5]

    # Parameters exp(A) * exp(K*T) comes from experimental measurements of Cy3T8 intensity on temperature
    A = 12.70776
    K = -0.0371940

    # cut
    cut = 252

    # Range of background intensities checked sequentially with step
    maxBckIntensity = 15000
    minBckIntensity = -10000
    step = 20
    nb_arg = int((maxBckIntensity - minBckIntensity) / step)

    with pd.ExcelWriter(file_name + '_processed.xlsx') as writer:
        for m in np.arange(sheet_name_num[0], sheet_name_num[1] + sheet_name_num[2], sheet_name_num[2]):
            sheet_name = sheet_name_body + str(m)
            excel_data = pd.read_excel(file_name + '.xlsx', sheet_name=sheet_name)
            for p in np.arange(col_name_num[0], col_name_num[1] + col_name_num[2], col_name_num[2]):
                col_name = col_name_body + str(p)
                T = excel_data['T'].tolist()
                col = excel_data[col_name].tolist()

                B_abs = [0] * int(nb_arg)
                B_data = [0] * int(nb_arg)
                b = [0] * int(nb_arg)
                T_cut = T[cut:]
                col_cut = col[cut:]
                col2check = [0] * len(T_cut)

                for j in range(nb_arg):
                    for i in range(len(T_cut)):
                        col2check[i] = col_cut[i] / (np.exp(A) * np.exp(K * T_cut[i]) + j * step + minBckIntensity)

                    param = np.polyfit(T_cut, col2check, 1)
                    B_data[j] = j * step + minBckIntensity
                    B_abs[j] = param[0] ** 2
                    b[j] = param[1]
                    # dispers = dispersion(param[0], param[1], col2check, T_cut)

                indexOfLowestB = B_abs.index(min(B_abs))

                col_result = [0] * len(col)
                for i in range(len(col)):
                    col_result[i] = col[i] / (np.exp(A) * np.exp(K * T[i]) + B_data[indexOfLowestB]) / b[indexOfLowestB]

                df = pd.DataFrame({'T': T})
                df.to_excel(writer, sheet_name=sheet_name, index=False, startcol=0)
                df = pd.DataFrame({col_name: col_result})
                df.to_excel(writer, sheet_name=sheet_name, index=False, startcol=(p - col_name_num[0]) / col_name_num[2] + 1)

    pass

