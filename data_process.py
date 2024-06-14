import SMILEapi
import os
import pandas as pd
from joblib import load

openSmile = SMILEapi.OpenSMILE()

# UTILITY

def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return value


# CSV

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


# OPEN SMILE

def analyse_file(file_path, result_path, config_path):
    try:
        print(f"[DataProcess] | File ({file_path}) analyse started")
        openSmile.process(config_path, {"I": file_path, "O": result_path}, {}, [])
        print(f"[DataProcess] | File ({file_path}) analyse finished")
    except Exception as e:
        print(f"[DataProcess] | File ({file_path}) failed to analyse")


def create_dataframe(file_path, result_path):
    rows = []

    try:
        attribute_names, row_info = read_csv(result_path)
        row_info[0] = os.path.basename(file_path)
        rows.append(row_info)
    except Exception as e:
        print(f"[DataProcess] | Ошибка при обработке файла ({file_path}). Ошибка - {e}")

    if attribute_names is None:
        raise ValueError("[DataProcess] | Не удалось извлечь имена атрибутов из файлов.")

    return pd.DataFrame(rows, columns=attribute_names)


def prediction(df):
    svm_model = load('joblibs/svm_model.joblib')
    scaler = load('joblibs/scaler.joblib')
    x = df.drop(columns=['class', 'name']).values
    x = scaler.transform(x)
    y_pred = svm_model.predict(x)
    df['class'] = y_pred
    
    return df