import pandas as pd
import numpy as np


def generate_normalization_curve(temperature, a, k):
    normalization_curve = [0] * len(temperature)
    if evoluteExponent:
        temperature_interval = temperature[0] - temperature[len(temperature) - 1]
        for i in range(len(temperature)):
            exp_ak_fraction = 1 / (1 + np.exp(0.32 * (temperature[i] - 50)))
            # exp_ak_fraction = (0 - 1) / temperature_interval * temperature[i] + ((1 + 0) - (0 - 1) / temperature_interval) / 2
            exp_AK_fraction = 1 - exp_ak_fraction
            normalization_curve[i] = exp_ak_fraction * (np.exp(a) * np.exp(k * temperature[i])) + exp_AK_fraction * (np.exp(A) * np.exp(K * temperature[i]))
    else:
        for i in range(len(temperature)):
            normalization_curve[i] = np.exp(a) * np.exp(k * temperature[i])
    return normalization_curve


def cut_data(data, from_to):
    T_interval = [int((from_to[0] - T[0]) / abs(T[1] - T[0]) + 2), int((from_to[1] - T[0]) / abs(T[1] - T[0]) + 2)]
    cuttedData = data[T_interval[0]:T_interval[1]]
    return cuttedData


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

    with pd.ExcelWriter('Processed/[processed]_' + file_signal + '.xlsx') as writer:
        excel_normSig_data = pd.read_excel('[norm]_' + file_normSignal + '.xlsx', sheet_name='dye')
        if normOnRealSignal:
            normSignal = excel_normSig_data['average'].tolist()
        else:
            normSignal = generate_normalization_curve(excel_normSig_data['T'].tolist(), A, K)

        for m in np.arange(sheet_name_num[0], sheet_name_num[1] + sheet_name_num[2], sheet_name_num[2]):
            sheet_name = sheet_name_body + str(m)
            excel_data = pd.read_excel('Raw/' + file_signal + '.xlsx', sheet_name=sheet_name)
            T = excel_data['T'].tolist()
            T_cut = cut_data(T, [T_cut_from, T_cut_to])

            for p in np.arange(col_name_num[0], col_name_num[1] + col_name_num[2], col_name_num[2]):
                # Get signal from specified file
                Signal_col_name = col_name_body + str(p)
                Signal = excel_data[Signal_col_name].tolist()

                # Calculate normalization exponent if needed
                if findExponentParameters:
                    T_info = excel_data['T interval ' + Signal_col_name].tolist()
                    if T_info[0] != 'None':
                        T_exp_determ_from = T_info[0]
                        T_exp_determ_to = T_info[1]
                        T_exp_determ_cut = cut_data(T, [T_exp_determ_from, T_exp_determ_to])
                        Signal_exp_determ_cut = cut_data(Signal, [T_exp_determ_from, T_exp_determ_to])
                        for k in range(len(Signal_exp_determ_cut)):
                            Signal_exp_determ_cut[k] = np.log(Signal_exp_determ_cut[k])
                        startRegionLinParameters = np.polyfit(T_exp_determ_cut, Signal_exp_determ_cut, 1)
                        a = startRegionLinParameters[1]
                        k = startRegionLinParameters[0]
                        normSignal = generate_normalization_curve(excel_normSig_data['T'].tolist(), a, k)
                    else:
                        pass

                nb_arg = int((maxBckgIntensity - minBckgIntensity) / step)
                # Lists of BckgIntensity 'B'
                B_values = [0] * int(nb_arg)
                B_abs_values = [0] * int(nb_arg)
                b = [0] * int(nb_arg)

                # Cut region at the end of melting curve
                normSignal_cut = cut_data(normSignal, [T_cut_from, T_cut_to])
                Signal_cut = cut_data(Signal, [T_cut_from, T_cut_to])
                Profile2check = [0] * len(T_cut)

                for j in range(nb_arg):
                    for i in range(len(T_cut)):
                        Profile2check[i] = (Signal_cut[i] + j * step + minBckgIntensity) / (normSignal_cut[i])

                    meltedRegionLinParameters = np.polyfit(T_cut, Profile2check, 1)
                    B_values[j] = j * step + minBckgIntensity
                    B_abs_values[j] = meltedRegionLinParameters[0] ** 2
                    b[j] = meltedRegionLinParameters[1]
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
