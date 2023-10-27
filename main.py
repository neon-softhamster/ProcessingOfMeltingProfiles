import pandas as pd
import numpy as np


def cutData(Data, from_to):
    T_interval = [int((from_to[0] - T[0]) / abs(T[1] - T[0]) + 2), int((from_to[1] - T[0]) / abs(T[1] - T[0]) + 2)]
    cuttedData = Data[T_interval[0]:T_interval[1]]
    return cuttedData

def dispersion(a, b, Y, T):
    disp = 0
    for q in range(len(Y)):
        disp = disp + (Y[q] - (a*T[q] + b)) ** 2
    return np.sqrt(disp)


if __name__ == '__main__':
    # ------------------------------------------------------------------------------------------------------
    # This program allow to find out "BckgIntensity" in two ways with normalization factors:
    # 1.    N1(A, K, T) = 1 / (exp(A) * exp(K*T) + BckgIntensity)
    # 2.    N2(A, K, T) = 1 / (freeDyeSignal + BckgIntensity)
    # So the given section of the normalized function (Melt_Curve(T) + BckgIntensity)/Nx((A, K), T) at temperatures
    # higher than T_cut_less is horizontal.
    # !!! Locate your raw files in ../Raw folder !!!
    # ------------------------------------------------------------------------------------------------------

    # Files notation
    file_normSignal = 'cy3-T20-bhq2'
    # avaliable: 		cy3
    #			cy3-T20-bhq2
    #			ads14-ads14

    file_signal = 'ATPaptACmm + ads8-14'
    sheet_name_body = 'pH '
    sheet_name_num = [5.0, 8.5, 0.5]
    col_name_body = 'ads'
    col_name_num = [8, 14, 1]

    # Task
    normalizeToOne = True
    normOnRealSignal = False
    T_cut_from = 80
    T_cut_to = 95

    # Parameters exp(A) * exp(K*T) comes from experimental measurements of Cy3T8 intensity on temperature
    A = 12.70776
    K = -0.0371940

    # Range of background intensities checked sequentially with step (use int)
    maxBckgIntensity = 50000
    minBckgIntensity = -10000
    step = 20

    with open('task.txt') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        exec(lines[i])

    with pd.ExcelWriter('Processed/[processed]_' + file_signal + '.xlsx') as writer:
        excel_normSig_data = pd.read_excel('[norm]_' + file_normSignal + '.xlsx', sheet_name='dye')
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
            excel_data = pd.read_excel('Raw/' + file_signal + '.xlsx', sheet_name=sheet_name)
            T = excel_data['T'].tolist()
            T_cut = cutData(T, [T_cut_from, T_cut_to])

            for p in np.arange(col_name_num[0], col_name_num[1] + col_name_num[2], col_name_num[2]):
                Signal_col_name = col_name_body + str(p)
                Signal = excel_data[Signal_col_name].tolist()

                nb_arg = int((maxBckgIntensity - minBckgIntensity) / step)
                # Lists of BckgIntensity 'B'
                B_values = [0] * int(nb_arg)
                B_abs_values = [0] * int(nb_arg)
                b = [0] * int(nb_arg)

                # Cut region at the end of melting curve
                normSignal_cut = cutData(normSignal, [T_cut_from, T_cut_to])
                Signal_cut = cutData(Signal, [T_cut_from, T_cut_to])
                Profile2check = [0] * len(T_cut)

                for j in range(nb_arg):
                    for i in range(len(T_cut)):
                        Profile2check[i] = (Signal_cut[i] + j * step + minBckgIntensity) / (normSignal_cut[i])

                    linParam = np.polyfit(T_cut, Profile2check, 1)
                    B_values[j] = j * step + minBckgIntensity
                    B_abs_values[j] = linParam[0] ** 2
                    b[j] = linParam[1]
                    # dispers = dispersion(param[0], param[1], col2check, T_cut)

                indexOfLowestB = B_abs_values.index(min(B_abs_values))

                col_result = [0] * len(Signal)
                if normalizeToOne:
                    for i in range(len(Signal)):
                        col_result[i] = (Signal[i] + B_values[indexOfLowestB]) / (normSignal[i]) / b[indexOfLowestB]
                else:
                    for i in range(len(Signal)):
                        col_result[i] = (Signal[i] + B_values[indexOfLowestB]) / (normSignal[i])

                df = pd.DataFrame({'T': T})
                df.to_excel(writer, sheet_name=sheet_name, index=False, startcol=0)

                df = pd.DataFrame({Signal_col_name: col_result})
                df.to_excel(writer, sheet_name=sheet_name, index=False, startcol=(p - col_name_num[0]) / col_name_num[2] + 1)
                
                shiftResultsCol = 3
                bckg_value = [0] * 2
                bckg_value[0] = B_values[indexOfLowestB]
                bckg_value[1] = b[indexOfLowestB]
                df = pd.DataFrame({Signal_col_name: bckg_value})
                df.to_excel(writer, sheet_name=sheet_name, index=False,
                            startcol=(p - col_name_num[0]) / col_name_num[2] + (col_name_num[1] - col_name_num[0]) / col_name_num[2] + (shiftResultsCol + 1))

            bckg_legend = ['Background intensity',
                           'Melted probe/Dye',
                           'T_cut = ' + str(T_cut_from) + 'C',
                           'Normalized to "' + file_normSignal + '"']
            df = pd.DataFrame({'Value': bckg_legend})
            df.to_excel(writer, sheet_name=sheet_name, index=False,
                        startcol=(col_name_num[1] - col_name_num[0]) / col_name_num[2] + shiftResultsCol)
