import tkinter
from tkinter import messagebox as dialog, filedialog as file_wm
import os
from typing import Dict, Any

from com.zcnst.constant import mainFinal
from com.zcnst.service import file_convert as convert
from  threading import Thread

def msgDialog(level: int, msg: str):
    '''
    消息对话框
    :param level: 消息级别
    :param msg: 消息
    :return:
    '''
    if level <= 0:
        dialog.showinfo("提示", msg)
    elif level == 1:
        dialog.showwarning("警告", msg)
    else:
        dialog.showerror("错误", msg)


def start_convert_event(wm, event, fileChoice=None, symbol=tkinter.Entry, encoding=str, coord=()):
    if convert.getConvertState():
        return
    convert.setConverted()

    files = fileChoice.get_files()
    del fileChoice
    symbol_text = symbol.get()
    if files.__len__() == 0:
        msgDialog(1, "请选择文本文件！")
    elif symbol_text == "":
        msgDialog(1, "请输入分割符！")
    else:
        convert.setConverting()
        progress = Progress(wm.getCanvas(), x1=coord[0], y1=coord[1], x2=coord[2], y2=coord[3], outline='#FFE300', backageColor='#2B9ADA', progressColor='#84D945')
        convert.ConvertThreading(event, files, encoding, symbol_text, progress, wm).start()
        wm.update()


class Window(tkinter.Tk):
    eventMode: Dict[Any, Dict[Any, Any]]
    _init_width, _init_height = 700, 400
    _main_wm = _progress = None

    def setCanvas(self, canvas=tkinter.Canvas):
        self._main_wm = canvas

    def getCanvas(self):
        return self._main_wm

    def __init__(self):
        super(Window, self).__init__()
        self.title(mainFinal.WIN_TITLE_STR)
        self.wm_iconname(mainFinal.WIN_TITLE_STR)
        self.wm_overrideredirect(True)  # 去掉标题栏
        self.wm_resizable(width=False, height=False)  # 禁止窗口最大化和拉伸
        self.wm_attributes("-topmost", True, "-alpha", 1)  # 置顶窗体，且透明度为80%
        self.wm_iconbitmap(bitmap=mainFinal.WIN_ICON_PATH)

        # 设置窗口的初始位置居中
        screen = self._get_vga()
        x = (screen["W"] - self._init_width) / 2
        y = (screen["H"] - self._init_height) / 2
        self.wm_geometry("%dx%d+%d+%d" % (self._init_width, self._init_height, x, y))

    # 改变背景色, kwargs 传入的是字典
    def changeBg(self, event, kwargs):
        event.widget.config(bg=kwargs["color"])

    # 最小化窗口
    def minimize(self, event, args):
        self.withdraw()
        self.wm_overrideredirect(False)
        self.state("iconic")

    # 最小化后恢复窗口
    def frame_mapped(self, event):
        self.wm_overrideredirect(True)
        self.deiconify()

    # 移动窗口事件
    def select_wid(self, event):
        self.x = event.x
        self.y = event.y

    def stop_wid(self, event):
        self.x = None
        self.y = None

    def moving_wid(self, event):
        new_x = (event.x - self.x) + self.winfo_x()
        new_y = (event.y - self.y) + self.winfo_y()
        self.wm_geometry("+%d+%d" % (new_x, new_y))

    # 关闭窗口
    def close(self, event, args):
        os._exit(0)

    # 鼠标悬浮，事件
    def hoverEvent(self, fun, event, **args):
        if "mode" in args and args["mode"] == "IN":
            self.eventMode = {event.widget._name: {"focus": True}}
        else:
            self.eventMode = None
        fun(event, args)

    # 鼠标单击事件
    def clickOn(self, fun, event, **kwargs):
        eventMode, widNmae = self.eventMode, event.widget._name
        if eventMode is not None:
            if widNmae in eventMode and eventMode[widNmae]["focus"]:
                fun(event, kwargs)

    def init_main_wm(self):
        """
         初始化自定义窗口背景
        :return:
        """

        # 添加背景图片
        global image
        image = mainFinal.WIN_TITLE_BACK_IMG(mainFinal.WIN_BACK_IMG_PATH, self._init_width, self._init_height)
        main_wm = tkinter.Canvas(self, width=self._init_width, height=self._init_height, bg="green", highlightthickness=0)
        main_wm.create_image((0, 0), anchor=tkinter.NW, image=image)
        main_wm.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=False)

        # 添加窗口图标
        global icon
        icon = mainFinal.WIN_TITLE_BACK_IMG(mainFinal.WIN_APP_LOGO, 64, 64)
        icon_label = tkinter.Label(self, width=60, height=60, bg="#042900", image=icon, borderwidth=0)
        main_wm.create_window((70, 35), window=icon_label, anchor=tkinter.NW)

        # 添加窗口标题
        main_wm.create_text((self._init_width / 2 - 108, 45), text=mainFinal.WIN_TITLE_STR, font=("黑体", 24, "bold"), fill="#1AFA29", anchor=tkinter.NW)

        # 添加菜单
        global imageMenu
        imageMenu = mainFinal.WIN_TITLE_BACK_IMG(mainFinal.WIN_MENU_IMG, 16, 16)
        self.codingVar = tkinter.StringVar()
        self.codingVar.set("UTF-8")
        mb = tkinter.Menubutton(self, name="menuCharCode", width=32, height=26, image=imageMenu, bd=0, bg="#3C3F41", fg="white", activebackground="red",
                                relief=tkinter.FLAT)
        filemenu = tkinter.Menu(mb, tearoff=False, bg="#3C3F41", bd=0, activebackground="red", font=("黑体", 10), fg="white", relief=tkinter.FLAT)
        for item in ["ANSI", "ASCII ", "UTF-8", "UTF-16", "UTF-32", "GBK", "GB2312", "GB18030", "BIG5", "ISO8859-1", "ISO8859-2",
                     "ISO8859-3", "ISO8859-4", "ISO8859-5", "ISO8859-6", "ISO8859-7", "ISO8859-15", "ISO8859-16"]:
            filemenu.add_radiobutton(label=item, command=None, variable=self.codingVar, value=item, selectcolor="white")
        mb.config(menu=filemenu)
        main_wm.create_window((self._init_width - 96, 0), window=mb, anchor=tkinter.NW)

        # 添加最小化
        global ImageMinimize
        ImageMinimize = mainFinal.WIN_TITLE_BACK_IMG(mainFinal.WIN_MIN_IMG, 16, 16)
        bt = tkinter.Button(self, name="minimize", width=32, height=24, image=ImageMinimize, bd=0, bg="#3C3F41", activebackground="red", relief=tkinter.FLAT)
        bt.bind("<Enter>", lambda event: self.hoverEvent(self.changeBg, event=event, color="red", mode="IN"))
        bt.bind("<Leave>", lambda event: self.hoverEvent(self.changeBg, event=event, color="#3C3F41"))
        bt.bind("<ButtonRelease-1>", lambda event: self.clickOn(self.minimize, event))
        main_wm.create_window((self._init_width - 64, 0), window=bt, anchor=tkinter.NW)

        # 最小化后显示窗口
        self.bind("<Map>", self.frame_mapped)

        # 移动窗口
        main_wm.bind("<Button-1>", self.select_wid)
        main_wm.bind("<ButtonRelease-1>", self.stop_wid)
        main_wm.bind("<B1-Motion>", self.moving_wid)

        # 添加窗口关闭按钮
        global imageClose
        imageClose = mainFinal.WIN_TITLE_BACK_IMG(mainFinal.WIN_CLOSE_IMG, 16, 16)
        bt = tkinter.Button(self, name="close", width=32, height=24, image=imageClose, bd=0, bg="#3C3F41", activebackground="red", relief=tkinter.FLAT)
        bt.bind("<Enter>", lambda event: self.hoverEvent(self.changeBg, event=event, color="red", mode="IN"))
        bt.bind("<Leave>", lambda event: self.hoverEvent(self.changeBg, event=event, color="#3C3F41"))
        bt.bind("<ButtonRelease-1>", lambda event: self.clickOn(self.close, event))
        main_wm.create_window((self._init_width - 32, 0), window=bt, anchor=tkinter.NW)

        self.setCanvas(main_wm)

    def init_component(self):
        """
        初始化组件
        :return:
        """
        main_wm = self.getCanvas()

        entryStartPosition = self._init_width / 2 - 180

        # 输入目录字段说明文字 及 输入控件
        field_style, entry_style = mainFinal.WIN_FIELD_STYLE, mainFinal.WIN_ENTRY_STYLE
        main_wm.create_text(35, 145, text="待转换的文件：", anchor=tkinter.NW, font=field_style["font"], fill=field_style["fill"])
        fileChoice = FileChoice(self, "请选择TXT文件 或 包含TXT文件夹!")
        fileChoice.set_relief(tkinter.FLAT).set_font(entry_style["font"]).set_bd(entry_style["bd"]).set_bg(entry_style["bg"]).set_fg(
            entry_style["fg"]).set_highlightbackground(entry_style["highlightbackground"]).set_selectbackground(
            entry_style["selectbackground"]).set_highlightcolor(entry_style["highlightcolor"])
        fileDialog = fileChoice.composition(takefocus=False, width=60, title="请选择TXT文件,可选择多个！", fileType=[("TXT文件", ".txt"),("CSV文件",".CSV")])
        main_wm.create_window(entryStartPosition, 140, window=fileDialog, anchor=tkinter.NW)

        # 输入分隔符字段说明文字 及 输入控件
        main_wm.create_text(35, 215, text="请输入分隔符：", anchor=tkinter.NW, font=field_style["font"], fill=field_style["fill"])
        decollatorValue = tkinter.StringVar(self, "|")
        decollator = tkinter.Entry(self, width=60, textvariable=decollatorValue, cnf=entry_style, takefocus=False)
        main_wm.create_window(entryStartPosition, 210, window=decollator, anchor=tkinter.NW)

        global runIco
        runIco = mainFinal.WIN_TITLE_BACK_IMG(mainFinal.WIN_RUN_IMG, 24, 24)
        runBut = tkinter.Button(text="开始转换 ", name="runConversion", image=runIco, bg="green", bd=0, highlightthickness=4, font=("黑体", 16, "bold"), \
                                fg="#EBEEEF", width=140, height=24, relief="flat", takefocus=False, activebackground="#FFE300", \
                                activeforeground="#84D945", compound=tkinter.RIGHT, highlightcolor="#FFE300")
        runBut.bind("<Enter>", lambda event: self.hoverEvent(self.changeBg, event=event, color="red", mode="IN"))
        runBut.bind("<Leave>", lambda event: self.hoverEvent(self.changeBg, event=event, color="green"))
        runFun = lambda event, kwargs: start_convert_event(self, event, fileChoice, decollator, self.codingVar.get(), kwargs["coord"])
        runBut.bind("<ButtonRelease-1>", lambda event: self.clickOn(runFun, event, coord=(35, 350, self._init_width - 35, 370)))

        main_wm.create_window(self._init_width / 2 - 80, 280, window=runBut, anchor=tkinter.NW)

    def show_windows(self):
        """
            显示程序
        :return:
        """
        self.init_main_wm()
        self.init_component()
        self.mainloop()

    def _get_vga(self):
        """
        获取屏幕的分辨率
        :return: 返回字典类型值；X, Y
        """
        return {"W": self.winfo_screenwidth(), "H": self.winfo_screenheight()}


class Progress:
    """
    进度条
    """

    def __init__(self, canvas=tkinter.Canvas, x1=int, y1=int, x2=int, y2=int, outline=str, backageColor=str, progressColor=str):
        """
        初始化进度条
        :param canvas:画布
        :param outline:边框颜色
        :param backageColor:进度条背景
        :param progressColor:进度色彩
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width, self.height = self.x2 - self.x1, self.y2 - self.y1
        self.progress_out = canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, outline=outline, fill=backageColor)
        self.progress_in = canvas.create_rectangle(self.x1, self.y1, self.x1, self.y2, outline=progressColor, fill=progressColor)
        self.canvas = canvas

        textValue = "0 %"
        text_x1 = (self.width / 2 + self.x1) - (textValue.__len__() * 10)
        font_size = int(self.height / 10 + 10)
        text_y1 = (self.height - font_size) / 2 + self.y1
        self.propress_txt = canvas.create_text(text_x1, text_y1, text=textValue, anchor=tkinter.NW, font=("宋体", font_size, "bold"), fill=outline)

    def update_progress(self, wm=tkinter.Tk, finish_rate=float):
        """
        更新进度条
        :param wm:父窗口
        :param finish_rate:完成率 0-1，1最大
        :return:
        """
        # (（x2-x2 【确定了进度条的长度】） * 完成率【增加的实际长度】)+x1=增加后的实际x2坐标
        new_x2 = (self.width * finish_rate) + self.x1
        self.canvas.coords(self.progress_in, (self.x1, self.y1, (self.x2 if new_x2 >= self.x2 else new_x2), self.y2))
        self.canvas.itemconfig(self.propress_txt, text="{:.0%}".format(finish_rate))
        wm.update()

    def clearProgress(self):
        """
        清除进度条
        :return:
        """
        self.canvas.delete(self.progress_in, self.progress_out, self.propress_txt)


class FileChoice(tkinter.Frame):
    """
    文件选择框
    """
    wm, path_choice, choice_but, hintMsg = None, None, None, None
    hintMsgStr = ""
    cnf, btcnf = {}, {}
    select_files = []

    def __init__(self, wm, hintMsg):
        self.wm = wm
        self.hintMsgStr = hintMsg
        super(FileChoice, self).__init__(self.wm)
        self.hintMsg = tkinter.StringVar(self.wm, hintMsg)

    def set_bg(self, color=str):
        if color.strip() != "":
            self.cnf["bg"] = color
        return self

    def set_fg(self, color=str):
        if color.strip() != "":
            self.cnf["fg"] = color
            self.btcnf["fg"] = color
        return self

    def set_highlightbackground(self, color=str):
        if color.strip() != "":
            self.cnf["highlightbackground"] = color
            self.btcnf["bg"] = color
            self.btcnf["activeforeground"] = color
        return self

    def set_highlightcolor(self, color=str):
        if color.strip() != "":
            self.cnf["highlightcolor"] = color
        return self

    def set_selectbackground(self, color=str):
        if color.strip() != "":
            self.cnf["selectbackground"] = color
            self.btcnf["activebackground"] = color
        return self

    def set_bd(self, value=int):
        if value > 0:
            self.cnf["bd"] = value
            self.cnf["highlightthickness"] = value
            self.btcnf["bd"] = 0
            self.btcnf["highlightthickness"] = value * 2 - 1
        return self

    def set_relief(self, value=str):
        if value.split() != "":
            self.cnf["relief"] = value
            self.btcnf["relief"] = value
        return self

    def set_font(self, font=()):
        if font.__len__() > 0:
            self.cnf["font"] = font
            self.btcnf["font"] = ("楷书", (font[1] - 1))
        return self

    def composition(self, takefocus=bool, width=int, title=None, fileType=[]):
        but_width = 10
        entry_width = width - but_width
        frame = tkinter.Frame(self.wm, width=width, highlightthickness=0, bd=0)
        self.path_choice = tkinter.Entry(frame, cnf=self.cnf, takefocus=takefocus, width=entry_width, textvariable=self.hintMsg)
        self.path_choice.bind("<ButtonRelease-1>", lambda event: self._buttonRelease_1(event, title, fileType))
        self.path_choice.pack(side=tkinter.LEFT, anchor=tkinter.W, expand="yes", fill=tkinter.BOTH, ipadx=0, ipady=0, padx=0, pady=0)
        self.choice_but = tkinter.Button(frame, cnf=self.btcnf, text="浏览...", width=but_width, takefocus=takefocus)
        self.choice_but.bind("<ButtonRelease-1>", lambda event: self._buttonRelease_1(event, title, fileType))
        self.choice_but.pack(side=tkinter.RIGHT, anchor=tkinter.E, expand="no", fill=tkinter.BOTH, padx=0, pady=0)

        return frame

    def get_files(self):
        return self.select_files.copy()

    def _buttonRelease_1(self, event, title=None, fileType=None):
        """
        点击 选择文件或文件框事件
        :param event: 监听事件的对象
        :param title: 文件选择框的对象
        :param fileType: 文件类型，为列表元组类型 [("文件类型描述","文件后缀,如“.txt”")]
        :return:
        """
        Thread(target=self._fileFiltrate, args=(event, title, fileType)).start()
        self.wm.focus_set()

    def _fileFiltrate(self, event, title, fileType):
        title = "请选择文件" if title == None else title
        fileType = [("请选择文件", "*")] if fileType == None and fileType.__len__() <= 0 else fileType
        widget = event.widget
        if isinstance(widget, tkinter.Entry):
            pathvalue = file_wm.askopenfilenames(title=title, filetypes=fileType)
        elif isinstance(widget, tkinter.Button):
            pathvalue = file_wm.askdirectory(title="请选择路径！", mustexist=True)

        if self.select_files.__len__() > 0:
            self.select_files.clear()

        if not pathvalue:
            self.hintMsg.set(value=self.hintMsgStr)
            return
        elif isinstance(pathvalue, tuple):
            self.select_files.extend(list(pathvalue))
        elif isinstance(pathvalue, str):
            for dir in os.listdir(pathvalue):
                tempStr = os.path.join(pathvalue, dir)
                if os.path.isfile(tempStr) and dir.endswith(fileType[0][1]):
                    self.select_files.append(tempStr)

        if len(self.select_files) == 1:
            self.hintMsg.set(value=self.select_files[0])
        else:
            filenamelist = []
            for file_path in self.select_files:
                filenamelist.append(os.path.split(file_path)[1])
            self.hintMsg.set(value=";".join(filenamelist))
