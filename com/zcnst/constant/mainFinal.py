# 定义了全局变量

from PIL import Image, ImageTk
import os

'''
程序的标题名称
'''
WIN_TITLE_STR = "TXT 转 EXCEL"

'''
程序的图标
'''
WIN_ICON_PATH = ".\\source\\logo.ico"

'''
程序的图片
'''
WIN_APP_LOGO = ".\\source\\logo_64_64.png"

'''
背景图片
'''
WIN_BACK_IMG_PATH = "./source/backgareImage.png"

'''
最小化按钮图标
'''
WIN_MIN_IMG="./source/min.png"

'''
关闭按钮图标
'''
WIN_CLOSE_IMG = "./source/close.png"

'''
菜单图标
'''
WIN_MENU_IMG = "./source/menu.png"

'''
转换按钮图标
'''
WIN_RUN_IMG = "./source/run_txt.png"


def WIN_TITLE_BACK_IMG(image_path=None, width=-1, height=-1):
    if image_path is not None and os.path.exists(image_path) and os.path.isfile(image_path):
        suffix = os.path.splitext(image_path)[1].lower()
        if ".jpg" == suffix or ".png" == suffix or ".gif" == suffix:
            image = Image.open(image_path)
            if width != -1 and height != -1:
                image.resize((int(width), int(height)), Image.ANTIALIAS)
                return ImageTk.PhotoImage(image)


'''
输入项字段样式
'''
WIN_FIELD_STYLE = {"font": ("黑体", 12, "bold"), "fill": "#84D945"}

'''
输入框的样式
'''
WIN_ENTRY_STYLE = {"bg": "#E3D28D", "fg": "#778EAE", "highlightbackground": "green", "bd": 2, "relief": "flat", "highlightthickness": 2,
                   "highlightcolor": "#FFE300", "selectbackground": "#FFE300", "font": ("楷书", 11)}
