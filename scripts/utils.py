import os
import pygame
import tkinter
import tkinter.filedialog

BASE_IMG_PATH = 'assets/image/'

def load_image(path:str):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((255, 255, 255))
    return img

def load_images(path:str):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def h_col(h:str):
    return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def prompt_file(ftype, dir="~"):
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top,filetypes=ftype,initialdir=dir)
    top.destroy()
    return file_name

def prompt_save(data):
    top = tkinter.Tk()
    top.withdraw()  # hide window
    top.update()

    file = tkinter.filedialog.asksaveasfile(
        parent=top,
        initialfile="song.json",
        mode="w",
        defaultextension=".json",
        filetypes=[("JSON file","*.json")]
    )

    if not file is None:
        file.write(data)
        file.close()



