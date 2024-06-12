from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import tkinter as tk
import os
import test as data_process


conf = "D:/Diplom/opensmile-master/config/emobase/emobase.conf"
file = None
results_root_path = "D:/Diplom/results/"

def emotions(df):
    global lbl_res
    emotion = df['class'][0]
    if emotion == 1:
        lbl_res = Label(window, text="Мы заметили, что вы грустите. Если вам нужно поговорить, не стесняйтесь "
                                     "обратиться за поддержкой. \nБудьте сильны. Грустные моменты временны, и "
                                     "впереди вас ждут лучшие дни!", font='Arial 15', background="light blue")
        lbl_res.pack()
    elif emotion == 0:
        lbl_res = Label(window, text="Мы заметили, что вы счастливы. "
                                     "Это замечательно!\nПусть счастье всегда сопровождает вас "
                                     "и приносит радость в каждый день!", font='Arial 15', background="light blue")
        lbl_res.pack()
    elif emotion == 2:
        lbl_res = Label(window, text="Ваш голос звучит нейтрально. Отлично! \nПродолжайте в том же духе. "
                                     "Спокойствие — это ключ к успеху!", font='Arial 15', background="light blue")
        lbl_res.pack()
    elif emotion == 3:
        lbl_res = Label(window, text="Мы заметили, что вы злитесь. Постарайтесь глубоко вдохнуть и выдохнуть, "
                                     "чтобы успокоиться. \nСохраняйте спокойствие и найдите способ "
                                     "выразить свои чувства конструктивно.", font='Arial 15', background="light blue")
        lbl_res.pack()
    elif emotion == 4:
        lbl_res = Label(window, text="Мы заметили, что вы испытываете отвращение. Возможно, лучше отложить этот "
                                     "разговор и вернуться к нему позже. \nСтарайтесь избегать неприятных ситуаций "
                                     "и окружать себя позитивными вещами.", font='Arial 15', background="light blue")
        lbl_res.pack()
    elif emotion == 5:
        lbl_res = Label(window, text="Мы заметили, что вы испуганы. Постарайтесь расслабиться и помните, что всё под "
                                     "контролем. \nБудьте спокойны и осторожны. Всё будет хорошо!", font='Arial 15',
                        background="light blue")
        lbl_res.pack()
    elif emotion == 6:
        lbl_res = Label(window, text="Мы заметили, что вы удивлены. Надеемся, это приятный сюрприз! \nПусть ваш день "
                                     "будет наполнен приятными неожиданностями!", font='Arial 15',
                        background="light blue")
        lbl_res.pack()

def loaded_file():
    global file_choise
    global lbl_file, lbl_file1, btn1, lbl_res
    file_choise = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
    if file_choise:
        print(f"Выбранный файл: {file_choise}")
        lbl_file = Label(window, text="Файл загружен", font='Arial 15', background='light blue')
        lbl_file1 = Label(window, text='Если вы выбрали не тот файл, нажмите снова "загрузить"', font='Arial 15',
                          background='light blue')
        lbl_file.pack()
        lbl_file1.pack()
        btn1 = Button(window, text="Показать результат", font='Arial 13', command=results)
        btn1.pack(pady=5)
        lbl_res.pack_forget()


def resize_image(image, max_size=(100, 100)):
    original_size = image.size
    ratio = min(max_size[0]/original_size[0], max_size[1]/original_size[1])
    new_size = tuple([int(x*ratio) for x in original_size])
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    return resized_image


def results():
    global results_root_path
    global file_choise, lbl_file, lbl_file1
    files_ = os.path.basename(file_choise)
    files_to_analize = [files_[:-4]]
    directory_path = os.path.dirname(file_choise)
    directory_path += '/'
    data_process.analysis_for_opensmile(files_to_analize, conf, directory_path,
                                        results_root_path)
    df = (data_process.forming_dataframe(files_to_analize, results_root_path))
    df = data_process.prediction(df)
    print('Fineshed analysis!')
    lbl_file.pack_forget()
    lbl_file1.pack_forget()
    btn1.pack_forget()
    df_new = df[['name', 'class']]
    emotions(df_new)


window = Tk()
window.title("Узнай свою эмоцию по голосу")
window.geometry('1050x350')
ttk.Style().theme_use("classic")
style = ttk.Style()
window["bg"] = "light blue"

# Загрузка изображения логотипа
logo_path = "D:/Diplom/appemotion/logo1.png"
if os.path.isfile(logo_path):
    logo_image = Image.open(logo_path)
    logo_image = resize_image(logo_image)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(window, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.pack(side=tk.LEFT, anchor="nw", padx=20, pady=20)  # Изменение расположения на угол окна


name_window = ttk.Label(window, text="Анализ эмоций", font="Arial 35", background="light blue")
name_window.pack(pady=5)
lbl = Label(window, text="Выберите файл с вашим голосом для определения эмоции",
            font='Arial 15', background='light blue')
lbl.pack(pady=10)
btn = Button(window, text="Загрузить", font='Arial 13', command=loaded_file)
btn.pack(pady=5)

window.mainloop()
