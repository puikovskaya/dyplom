import SMILEapi
import csv
import pandas as pd
import os


openSmile = SMILEapi.OpenSMILE()


def getLastRowData(file):
    with open(file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            last_row = row
    return last_row


def convert_to_float(element):
    try:
        return float(element)
    except ValueError:
        return element


def delete_logs(files_to_analize, results_root_path):
    csv_files_to_delete = [os.path.join(results_root_path, f"{base_name}.csv")
                           for base_name in files_to_analize]
    for file_path in csv_files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)


def opensmile_analysis(files_to_analize, conf, audiofiles_root_path,
                       results_root_path):
    options = {}
    metadata = []
    for file in files_to_analize:
        openSmile.process(conf, {"I": audiofiles_root_path + file + '.wav',
                                 "O": results_root_path + file + '.csv'},
                          options, metadata)


def reading_csv(file_path):
    attribute_names = []
    data_section = False  # Флаг, чтобы знать, когда начинается секция данных
    with open(file_path, 'r') as file:
        for line in file:
            if '@data' in line:
                data_section = True  # Найден момент начала раздела с данными
                continue
            if not data_section:
                # До секции '@data', обрабатываем атрибуты
                if '@attribute' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        attribute_names.append(parts[1])
            else:
                # После нахождения '@data', начинаем сбор данных
                row_info = line.strip()
    row_info = row_info.split(sep=',')
    info = [convert_to_float(item) for item in row_info]
    # Возврат значений может быть полезен для дальнейшего использования
    return attribute_names, info


def forming_dataframe(files_to_analize, results_root_path):
    rows = []
    for file in files_to_analize:
        attribute_names, row_info = reading_csv(results_root_path + file
                                                + '.csv')
        row_info[0] = file
        rows.append(row_info)
    df = pd.DataFrame(rows, columns=attribute_names)
    # Удалить логи?
    delete_logs(files_to_analize, results_root_path)
    return df


def get_wav_files(audiofiles_root_path):
    # Получить названия файлов .wav из директории
    all_files = os.listdir(audiofiles_root_path)
    return [f[:-4] for f in all_files if f.endswith('.wav')]


def main():
    audiofiles_root_path = "opensmile-master/example-audio/"
    results_root_path = "results/"
    conf = "opensmile-master/config/emobase/emobase.conf"

    files_to_analize = get_wav_files(audiofiles_root_path)

    opensmile_analysis(files_to_analize, conf, audiofiles_root_path,
                       results_root_path)
    df = (forming_dataframe(files_to_analize, results_root_path))
    df.to_csv('output.csv', index=False)
    print(df)


if __name__ == '__main__':
    main()
