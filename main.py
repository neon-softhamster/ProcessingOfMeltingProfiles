import pandas as pd
import numpy as np


def dispersion(a, b, Y, T):
    disp = 0
    for q in range(len(Y)):
        disp = disp + (Y[q] - (a*T[q] + b)) ** 2
    return np.sqrt(disp)


if __name__ == '__main__':
    with open('task.txt') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        exec(lines[i])

    with pd.ExcelWriter('Processed/[processed]_' + file_name + '.xlsx') as writer:
        excel_normSig_data = pd.read_excel(file_normSignal + '.xlsx', sheet_name='dye')
        if normOnRealSignal:
            normSignal = excel_normSig_data['average'].tolist()
        else:
            T_norm = excel_normSig_data['T'].tolist()
            nbOfTPoints = len(T_norm)
            normSignal = [0] * nbOfTPoints
            for i in range(nbOfTPoints):
                normSignal[i] = np.exp(A) * np.exp(K * T_norm[i])

        for m in np.arange(sheet_name_num[0], sheet_name_num[1] + sheet_name_num[2], sheet_name_num[2]):
            sheet_name = sheet_name_body + str(m)
            excel_data = pd.read_excel('Raw/' + file_name + '.xlsx', sheet_name=sheet_name)

            for p in np.arange(col_name_num[0], col_name_num[1] + col_name_num[2], col_name_num[2]):
                col_name = col_name_body + str(p)
                T = excel_data['T'].tolist()
                col = excel_data[col_name].tolist()

                nb_arg = int((maxBckIntensity - minBckIntensity) / step)
                B_value = [0] * int(nb_arg)
                B_value_abs = [0] * int(nb_arg)
                b = [0] * int(nb_arg)
                cut = int((T_cut_less - T[0]) / abs(T[1] - T[0]) + 2)
                T_cut = T[cut:]
                normSig_cut = normSignal[cut:]
                col_cut = col[cut:]
                col2check = [0] * len(T_cut)

                for j in range(nb_arg):
                    for i in range(len(T_cut)):
                        col2check[i] = col_cut[i] / (normSig_cut[i] + j * step + minBckIntensity)

                    param = np.polyfit(T_cut, col2check, 1)
                    B_value[j] = j * step + minBckIntensity
                    B_value_abs[j] = param[0] ** 2
                    b[j] = param[1]
                    # dispers = dispersion(param[0], param[1], col2check, T_cut)

                indexOfLowestB = B_value_abs.index(min(B_value_abs))

                col_result = [0] * len(col)
                if normalizeToOne:
                    for i in range(len(col)):
                        col_result[i] = col[i] / (normSignal[i] + B_value[indexOfLowestB]) / b[indexOfLowestB]
                else:
                    for i in range(len(col)):
                        col_result[i] = col[i] / (normSignal[i] + B_value[indexOfLowestB])

                df = pd.DataFrame({'T': T})
                df.to_excel(writer, sheet_name=sheet_name, index=False, startcol=0)

                df = pd.DataFrame({col_name: col_result})
                df.to_excel(writer, sheet_name=sheet_name, index=False, startcol=(p - col_name_num[0]) / col_name_num[2] + 1)

                bckg_value = [0] * 2
                bckg_value[0] = B_value[indexOfLowestB]
                bckg_value[1] = b[indexOfLowestB]
                df = pd.DataFrame({col_name: bckg_value})
                df.to_excel(writer, sheet_name=sheet_name, index=False,
                            startcol=(p - col_name_num[0]) / col_name_num[2] + 2 + col_name_num[1] + col_name_num[2])

            bckg_legend = ['Background intensity',
                           'Melted probe/Dye',
                           'T_cut = ' + str(T_cut_less) + 'C',
                           'Normed to "' + file_normSignal + '"']
            df = pd.DataFrame({'Value': bckg_legend})
            df.to_excel(writer, sheet_name=sheet_name, index=False,
                        startcol=(col_name_num[1] - col_name_num[0]) / col_name_num[2] + 3)
