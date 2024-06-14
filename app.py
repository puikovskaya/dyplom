import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import Label, Button
from PIL import Image, ImageTk
import data_process

# COLORS
COLOR_LIGHT_BLUE = "light blue"

# WINDOW SETTINGS
WINDOW_TITLE = "Узнай свою эмоцию по голосу"
WINDOW_RESOLUTION = "1200x500"
WINDOW_THEME = "classic"

# OPENSMILE SETTINGS
OPENSMILE_CONFIG_PATH = "C:/Job/Temp/opensmile-master/config/emobase/emobase.conf"

# PATHS
current_file_path = os.path.abspath(__file__)
current_folder_path = os.path.dirname(current_file_path)

assets_folder_path = current_folder_path + "/assets/"

runtime_folder_path = current_folder_path + "/runtime/"
results_folder_path = runtime_folder_path + "/results/"

# FILE
file = None


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Folder '{directory_path}' created.")


def emotions(df):
    global lbl_res

    emotion = df['class'][0]
    messages = {
        0: "Мы заметили, что вы счастливы. Это замечательно!\nПусть счастье всегда сопровождает вас и приносит радость в каждый день!",
        1: "Мы заметили, что вы грустите. Если вам нужно поговорить, не стесняйтесь обратиться за поддержкой. \nБудьте сильны. Грустные моменты временны, и впереди вас ждут лучшие дни!",
        2: "Ваш голос звучит нейтрально. Отлично! \nПродолжайте в том же духе. Спокойствие — это ключ к успеху!",
        3: "Мы заметили, что вы злитесь. Постарайтесь глубоко вдохнуть и выдохнуть, чтобы успокоиться. \nСохраняйте спокойствие и найдите способ выразить свои чувства конструктивно.",
        4: "Мы заметили, что вы испытываете отвращение. Возможно, лучше отложить этот разговор и вернуться к нему позже. \nСтарайтесь избегать неприятных ситуаций и окружать себя позитивными вещами.",
        5: "Мы заметили, что вы испуганы. Постарайтесь расслабиться и помните, что всё под контролем. \nБудьте спокойны и осторожны. Всё будет хорошо!",
        6: "Мы заметили, что вы удивлены. Надеемся, это приятный сюрприз! \nПусть ваш день будет наполнен приятными неожиданностями!"
    }
    lbl_res = Label(window, text=messages.get(emotion, "Эмоция не распознана"), font='Arial 15', background=COLOR_LIGHT_BLUE)
    lbl_res.pack()


def load_file():
    global file_choise
    global lbl_file, lbl_file1, btn1, lbl_res

    file_choise = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
    if file_choise:
        print(f"Выбранный файл: {file_choise}")
        lbl_file = Label(window, text="Файл загружен", font='Arial 15', background=COLOR_LIGHT_BLUE)
        lbl_file1 = Label(window, text='Если вы выбрали не тот файл, нажмите снова "загрузить"', font='Arial 15', background=COLOR_LIGHT_BLUE)
        lbl_file.pack()
        lbl_file1.pack()
        btn1 = Button(window, text="Показать результат", font='Arial 13', command=results)
        btn1.pack(pady=5)
        if lbl_res:
            lbl_res.pack_forget()


def resize_image(image, max_size=(100, 100)):
    original_size = image.size
    ratio = min(max_size[0]/original_size[0], max_size[1]/original_size[1])
    new_size = tuple([int(x*ratio) for x in original_size])
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    return resized_image


def results():
    global results_folder_path
    global file_choise, lbl_file, lbl_file1

    result_path = results_folder_path + f"{os.path.basename(file_choise)}.csv"
    data_process.analyse_file(file_choise, result_path, OPENSMILE_CONFIG_PATH)
    df = data_process.create_dataframe(file_choise, result_path)
    df = data_process.prediction(df)
    lbl_file.pack_forget()
    lbl_file1.pack_forget()
    btn1.pack_forget()
    df_new = df[['name', 'class']]
    emotions(df_new)


def create_window():
    global logo_path

    window = tk.Tk()
    window.title(WINDOW_TITLE)
    window.geometry(WINDOW_RESOLUTION)
    ttk.Style().theme_use(WINDOW_THEME)
    window["bg"] = COLOR_LIGHT_BLUE

    return window


def add_logo(window):
    global assets_folder_path
    
    logo_path = assets_folder_path + "logo1.png"

    if os.path.isfile(logo_path):
        logo_image = Image.open(logo_path)
        logo_image = resize_image(logo_image)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_icon = tk.Label(window, image=logo_photo)
        logo_icon.image = logo_photo
        logo_icon.pack(side=tk.LEFT, anchor="nw", padx=20, pady=20)   


def add_header(window):
    global header_label

    header_label = ttk.Label(window, text="Анализ эмоций", font="Arial 35", background=COLOR_LIGHT_BLUE)
    header_label.pack(pady=5)


def set_select_file_state(window):
    global select_file_label, load_file_button

    select_file_label = Label(window, text="Выберите файл с вашим голосом для определения эмоции", font='Arial 15', background=COLOR_LIGHT_BLUE)
    select_file_label.pack(pady=10)

    load_file_button = Button(window, text="Загрузить", font='Arial 13', command=load_file)
    load_file_button.pack(pady=5)


if __name__ == '__main__':
    ensure_directory_exists(runtime_folder_path)
    ensure_directory_exists(results_folder_path)
    
    window = create_window()
    add_logo(window)
    add_header(window)
    set_select_file_state(window)

    window.mainloop()