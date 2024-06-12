import SMILEapi
import csv
import os
import pandas as pd
from joblib import load

openSmile = SMILEapi.OpenSMILE()


def getLastRowData(file):
    with open(file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            last_row = row
    return last_row


def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return value


def delete_logs(files_to_analyze, results_root_path):
    log_file_names = set(f"{filename}.csv" for filename in files_to_analyze)  # Создание множества имен файлов журналов
    for filename in os.listdir(results_root_path):
        if filename in log_file_names:  # Проверка, есть ли имя файла в множестве
            file_path = os.path.join(results_root_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)  # Удаление файла, если он существует


def analysis_for_opensmile(files_to_analize, conf, audiofiles_root_path, results_root_path):
    options = {}
    metadata = []
    print(audiofiles_root_path, files_to_analize)
    for file in files_to_analize:
        try:
            openSmile.process(conf, {"I": audiofiles_root_path + file + '.wav', "O": results_root_path + file + '.csv'},
                              options, metadata)
        except Exception as e:
            print(f"Ошибка1 при обработке файла {file}: {e}")


def read_csv(file_path):
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
    return attribute_names, info


def forming_dataframe(files_to_analise, results_root_path):
    if not files_to_analise:
        raise ValueError("Список файлов для анализа пуст.")

    rows = []
    for file in files_to_analise:
        try:
            attribute_names, row_info = read_csv(results_root_path + file + '.csv')
            row_info[0] = file
            rows.append(row_info)
        except Exception as e:
            print(f"Ошибка при обработке файла {file}: {e}")
            continue

        if attribute_names is None:
            raise ValueError("Не удалось извлечь имена атрибутов из файлов.")

    df = pd.DataFrame(rows, columns=attribute_names)
    delete_logs(files_to_analise, results_root_path)
    return df


def get_file_names(audiofiles_root_path):
    filenames = []
    for filename in os.listdir(audiofiles_root_path):
        if os.path.isfile(os.path.join(audiofiles_root_path, filename)):
            filenames.append(filename)
    return [f[:-4] for f in filenames if f.endswith('.wav')]


def prediction(df):
    svm_model = load('svm_model.joblib')
    scaler = load('scaler.joblib')
    x = df.drop(columns=['class', 'name']).values
    x = scaler.transform(x)
    y_pred = svm_model.predict(x)
    df['class'] = y_pred
    print(df)
    return df


def main():
    audiofiles_root_path = "D:/Diplom/Emotions/"
    results_root_path = "D:/Diplom/results/"
    conf = "D:/Diplom/opensmile-master/config/emobase/emobase.conf"
    files_to_analise = get_file_names(audiofiles_root_path)
    analysis_for_opensmile(files_to_analise, conf, audiofiles_root_path, results_root_path)
    df = (forming_dataframe(files_to_analise, results_root_path))
    df.to_csv('output.csv', index=False)
    prediction(df)


if __name__ == '__main__':
    main()
