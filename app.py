import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import Label, Button, Frame, font
from PIL import Image, ImageTk
import data_process
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# COLORS
COLOR_WHITE = "#ffffff"
COLOR_GRAY = "#2f2f2f"
COLOR_LIGHT_GRAY = "#4f4f4f"

# WINDOW PARAMETERS
WINDOW_TITLE = "Узнай свою эмоцию по голосу"
WINDOW_RESOLUTION = "1000x850"
WINDOW_THEME = "classic"

# FRAMES PARAMETERS
FILE_FRAME_WIDTH = 350
FILE_FRAME_HEIGHT = 150

RESULTS_FRAME_WIDTH = 710
RESULTS_FRAME_HEIGHT = 600

# OPENSMILE PARAMETERS
OPENSMILE_CONFIG_PATH = "C:/Job/Temp/opensmile-master/config/emobase/emobase.conf" # Необходимо поменять на путь к конфигу 

# PATHS
current_file_path = os.path.abspath(__file__)
current_folder_path = os.path.dirname(current_file_path)

assets_folder_path = current_folder_path + '\\assets\\'

runtime_folder_path = current_folder_path + '\\runtime\\'
recordings_folder_path = runtime_folder_path + 'recordings\\'
results_folder_path = runtime_folder_path + '\\results\\'

# FILE
file = None

# Параметры записи
samplerate = 44100  # Частота дискретизации
channels = 2  # Количество каналов (стерео)

# Переменная для хранения записи
recording = []
stream = None


def stop_recording_and_show_results():
    stop_recording_and_save()
    show_results()


def start_recording():
    global recording, stream, record_file_button
    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recording.append(indata.copy())

    # Начинаем запись
    print("Запись началась...")
    stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback)
    stream.start()

    record_file_button.config(text="Остановить запись", command=stop_recording_and_show_results)


def stop_recording_and_save():
    global recording, stream, file_choise, record_file_button

    if (stream == None):
        return
    
    filename='recorded_audio.wav'
    file_path = recordings_folder_path + filename
    file_choise = file_path

    stream.stop()
    print("[App] | Запись остановлена.")
    
    recording = np.concatenate(recording, axis=0)
    
    wav.write(file_path, samplerate, recording)
    print(f"[App] | Запись сохранена в файл. Путь к файлу - ({file_path})")

    record_file_button.config(text="Начать запись", command=start_recording)


def resize_image(image, max_size=(80, 80)):
    original_size = image.size
    ratio = min(max_size[0]/original_size[0], max_size[1]/original_size[1])
    new_size = tuple([int(x*ratio) for x in original_size])
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    return resized_image


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Folder '{directory_path}' created.")


def emotions(df):
    global results_label

    emotion = df['class'][0]
    messages = {
        0: "Мы заметили, что вы счастливы.\nЭто замечательно!\nПусть счастье всегда сопровождает вас и приносит радость в каждый день!",
        1: "Мы заметили, что вы грустите.\nЕсли вам нужно поговорить, не стесняйтесь обратиться за поддержкой.\nБудьте сильны. Грустные моменты временны, и впереди вас ждут лучшие дни!",
        2: "Ваш голос звучит нейтрально. Отлично!\nПродолжайте в том же духе. Спокойствие — это ключ к успеху!",
        3: "Мы заметили, что вы злитесь.\nПостарайтесь глубоко вдохнуть и выдохнуть, чтобы успокоиться.\nСохраняйте спокойствие и найдите способ выразить свои чувства конструктивно.",
        4: "Мы заметили, что вы испытываете отвращение.\nВозможно, лучше отложить этот разговор и\nвернуться к нему позже. Старайтесь избегать\nнеприятных ситуаций и окружать себя позитивными вещами.",
        5: "Мы заметили, что вы испуганы.\nПостарайтесь расслабиться и помните, что всё под контролем.\nБудьте спокойны и осторожны. Всё будет хорошо!",
        6: "Мы заметили, что вы удивлены.\nНадеемся, это приятный сюрприз!\nПусть ваш день будет наполнен приятными неожиданностями!"
    }

    results_label.config(text=messages.get(emotion, "Эмоция не распознана, попробуйте еще раз"))


def load_file_and_show_results():
    load_file()
    show_results()


def load_file():
    global file_choise

    file_choise = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])


def show_results():
    global results_folder_path, file_choise

    if (not file_choise):
        return

    result_path = results_folder_path + f"{os.path.basename(file_choise)}.csv"

    data_process.analyse_file(file_choise, result_path, OPENSMILE_CONFIG_PATH)
    df = data_process.create_dataframe(file_choise, result_path)
    df = data_process.prediction(df)

    df_new = df[['name', 'class']]
    emotions(df_new)
    draw_spectrogram()


def load_logo():
    global assets_folder_path, logo_icon
    
    logo_path = assets_folder_path + "logo1.png"

    if os.path.isfile(logo_path):
        logo_image = Image.open(logo_path)
        logo_image = resize_image(logo_image)

        logo_icon = ImageTk.PhotoImage(logo_image)


spectrogram_canvas = None
spectrogram_figure = None
spectrogram_colorbar = None
ax = None
def draw_spectrogram():
    global results_frame, spectrogram_canvas, spectrogram_figure, spectrogram_colorbar, ax

    rate, data = wav.read(file_choise)
    
    if data.ndim > 1:
        data_mono = data[:, 0]
    else:
        data_mono = data
    
    if spectrogram_figure is None:
        spectrogram_figure = Figure(figsize=(8, 4))
        ax = spectrogram_figure.add_subplot(111)
        ax.set_xlabel('Время [сек]')
        ax.set_ylabel('Частота [Hz]')
        ax.set_title('Спектрограма')
    
    spectrum, freqs, t, im = ax.specgram(data_mono, Fs=rate, NFFT=1024, cmap='viridis')

    if spectrogram_colorbar is not None:
        spectrogram_colorbar.remove()
    
    spectrogram_colorbar = spectrogram_figure.colorbar(im, ax=ax)
    
    # Создание холста для вставки в tkinter
    if (spectrogram_canvas == None):
        spectrogram_canvas = FigureCanvasTkAgg(spectrogram_figure, master=results_frame)
        spectrogram_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    spectrogram_canvas.draw()
    spectrogram_canvas.flush_events()


def create_window():
    window = tk.Tk()
    window.title(WINDOW_TITLE)
    window.geometry(WINDOW_RESOLUTION)
    ttk.Style().theme_use(WINDOW_THEME)
    window["bg"] = COLOR_GRAY

    return window


def create_and_add_header(window):
    global header_frame, logo_icon

    header_frame = Frame(window, background=COLOR_LIGHT_GRAY, borderwidth=2, relief="groove", pady=10)

    logo_label = Label(header_frame, image=logo_icon, background=COLOR_LIGHT_GRAY)
    logo_label.pack(side="left", padx=10)

    header_label = Label(header_frame, text="Анализ эмоций", font="Arial 28", background=COLOR_LIGHT_GRAY, foreground=COLOR_WHITE)
    header_label.pack(side="right", padx=10)

    header_frame.pack(pady=10)


def create_and_add_files_frame(window):
    global files_frame

    files_frame = Frame(window, width=FILE_FRAME_WIDTH*2, height=FILE_FRAME_HEIGHT, background=COLOR_GRAY)
    files_frame.pack()


def create_and_add_load_file_frame(window):
    global select_file_label, load_file_button, assets_folder_path
    
    load_file_frame = Frame(window, width=FILE_FRAME_WIDTH, height=FILE_FRAME_HEIGHT, background=COLOR_LIGHT_GRAY, borderwidth=1, relief="solid")
    load_file_frame.pack_propagate(False)
    load_file_frame.pack(side="left", padx=5)

    header_label = Label(load_file_frame, text="Выбор файла", font='Arial 18', background=COLOR_LIGHT_GRAY, foreground=COLOR_WHITE)
    header_label.pack(pady=10)

    load_file_button = Button(load_file_frame, text="Загрузить", font='Arial 15', command=load_file_and_show_results)
    load_file_button.pack(pady=10)


def create_and_add_record_file_frame(window):
    global record_file_button

    record_file_frame = Frame(window, width=FILE_FRAME_WIDTH, height=FILE_FRAME_HEIGHT, background=COLOR_LIGHT_GRAY, borderwidth=1, relief="solid")
    record_file_frame.pack_propagate(False)
    record_file_frame.pack(side="left", padx=5)

    header_label = Label(record_file_frame, text="Запись голоса", font='Arial 18', background=COLOR_LIGHT_GRAY, foreground=COLOR_WHITE)
    header_label.pack(pady=10)

    record_file_button = Button(record_file_frame, text="Начать запись", font='Arial 15', command=start_recording)
    record_file_button.pack(pady=10)


def create_and_add_results_frame(window):
    global results_frame, results_label

    results_frame = Frame(window, width=RESULTS_FRAME_WIDTH, height=RESULTS_FRAME_HEIGHT, background=COLOR_LIGHT_GRAY, borderwidth=1, relief="solid")
    results_frame.pack_propagate(False)
    results_frame.pack(pady=10)

    header_label = Label(results_frame, text="Результаты", font='Arial 18', background=COLOR_LIGHT_GRAY, foreground=COLOR_WHITE)
    header_label.pack(pady=10)

    results_label = Label(results_frame, text="Загрузите файл или запишите голос,\nчтобы проанализировать эмоции", font='Arial 14', background=COLOR_LIGHT_GRAY, foreground=COLOR_WHITE)
    results_label.pack(pady=10)


if __name__ == '__main__':
    ensure_directory_exists(runtime_folder_path)
    ensure_directory_exists(results_folder_path)
    ensure_directory_exists(recordings_folder_path)

    window = create_window()
    load_logo()
    create_and_add_header(window)
    create_and_add_files_frame(window)
    create_and_add_load_file_frame(files_frame)
    create_and_add_record_file_frame(files_frame)
    create_and_add_results_frame(window)

    window.mainloop()