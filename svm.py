import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from joblib import dump, load


read_csv = pd.read_csv('output.csv', sep=',')
df = pd.DataFrame(read_csv)

# Присвоение значений class
def classify(name):
    if 'Happy' in name:
        return 0
    elif 'Sad' in name:
        return 1
    elif 'Neutral' in name:
        return 2
    elif 'Angry' in name:
        return 3
    elif 'Disgusted' in name:
        return 4
    elif 'Fearful' in name:
        return 5
    elif 'Suprised' in name:
        return 6
    else:
        return 100


df['class'] = df['name'].apply(classify)

# Разделение на признаки (x) и целевой столбец (y)
x = df.drop(columns=['class', 'name']).values
y = df['class']

# Преобразование меток классов в числовые значения
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Разделение на тренировочные и тестовые данные
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

# Нормализация данных
scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)


param_grid = {
    'C': [0.1, 1, 10, 100],  # Значения параметра регуляризации
    'gamma': [1, 0.1, 0.01, 0.001],  # Значения параметра gamma для ядра 'rbf'
    'kernel': ['linear', 'rbf', 'poly']  # Различные ядра
}

# Создание экземпляра SVC
svm = SVC()

# Объект GridSearchCV
grid_search = GridSearchCV(svm, param_grid, refit=True, verbose=2, cv=5)

# Запуск поиска наилучших гиперпараметров
grid_search.fit(x_train, y_train)
print(grid_search.best_params_)

# Предсказание с использованием лучшей модели
y_pred = grid_search.predict(x_test)

def get_model_results(model):
    Y_pred = model.predict(x_test)

    accuracy = accuracy_score(y_test, Y_pred)
    precision = precision_score(y_test, Y_pred, average='weighted')
    recall = recall_score(y_test, Y_pred, average='weighted')
    f1 = f1_score(y_test, Y_pred, average='weighted')
    conf_matrix = confusion_matrix(y_test, Y_pred)
    class_report = classification_report(y_test, Y_pred)

    print("Правильность (Accuracy):", accuracy)
    print("Точность (Precision):", precision)
    print("Полнота (Recall):", recall)
    print("F1-Score:", f1)
    print("Матрица ошибок (Confusion Matrix):\n", conf_matrix)
    print("Отчет о классификации (Classification Report):\n", class_report)

#accuracy = accuracy_score(y_test, y_pred)

#print(f"Точность: {accuracy*100}%")
get_model_results(grid_search)
print(y_pred)

# Сохранение модели
dump(grid_search, 'svm_model.joblib')

# Сохранение стандартизатора
dump(scaler, 'scaler.joblib')
