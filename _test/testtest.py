import os

# Получение пути к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получение директории, в которой находится текущий файл
current_dir = os.path.dirname(current_file_path)

print(f"Путь к файлу: {current_file_path}")
print(f"Директория: {current_dir}")