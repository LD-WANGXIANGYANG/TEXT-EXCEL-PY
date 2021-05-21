from com.zcnst.utils import ExcelUtil as excel
import os
from com.zcnst.view import window as wid
import threading

ROW_COUNT = 1000  # 每个线程读取的行数
start_row = -1  # 开始行号

# 转换完成标志
_isConverting = False


def next_rowNum():
    global start_row
    # lock.acquire()争抢该资源
    start_row += 1
    # lock.release()释放资源
    return start_row


def getConvertState() -> object:
    '''
    获取转换标志
    :return: True 转换中，False 未转换
    '''
    global _isConverting
    return _isConverting


def setConverting():
    '''
    更标志为转换中
    :return:
    '''
    global _isConverting
    _isConverting = True


def setConverted():
    '''
    更改标志为未转换
    :return:
    '''
    global _isConverting
    _isConverting = False


def convertFile(event, files, encoding, symbol_text, progress, wm):
    '''
    开始转换文件
    '''
    resultMsg = None
    x, span = 0, 100 / files.__len__() / 100
    for file in files:
        try:
            readLine(filePath=file, delimiter=symbol_text, encoding=encoding, progress_fun=progress.update_progress, wm=wm, progress_x=x, span=span)
        except FileNotFoundError as e:
            raise ConvertException(2, "文件【%s】不存在" % file)
        except UnicodeDecodeError as e:
            raise ConvertException(2, "用指定编码打开文件失败，请设置其他编码")
        except Exception as e:
            resultMsg = e
            if e.code > 1:  # 0 低级异常，1 中级异常，2 高级异常
                break
        else:
            resultMsg = ConvertException(0, "转换完成了")
        finally:
            x += span
    raise resultMsg


def readLine(filePath, delimiter, encoding, progress_fun, wm, progress_x, span):
    global start_row
    start_row = -1
    fileNames = os.path.split(filePath)
    fileAllName = fileNames[1]
    fileName = fileAllName[0:fileAllName.index(".")]
    with open(filePath, "rU", encoding=encoding, errors='ignore') as file:
        file_datas = file.readlines()
        lines_rows = file_datas.__len__()
        if lines_rows == 0:
            raise ConvertException(1, "文件【%s】为空文件" % fileName)
            
        workBook = excel.WorkBook(fileNames[0], fileName, (lines_rows > 50000))
        sheet = workBook.createSheet(fileName)
        
        while_count = (lines_rows / ROW_COUNT) if lines_rows % ROW_COUNT == 0 else (int(lines_rows / ROW_COUNT) + 1)
        seed_span = span / while_count
        for index in range(0, while_count):
            newList = file_datas[0:ROW_COUNT]
            file_datas = file_datas[ROW_COUNT:lines_rows - index * (len(newList))]
            if newList.__len__() > 0:
                try:
                    disposeData(newList, delimiter, workBook, sheet)
                    if index == (while_count - 1):
                        sheet.freeze_panes(1, 1, top_row=None, left_col=None, pane_type=0)
                        workBook.finish()
                except Exception as e:
                    raise ConvertThreading(2, "文件【%s】,%s" % (fileName, e))
                finally:
                    progress_x += seed_span
                    progress_fun(wm=wm, finish_rate=progress_x)


def disposeData(lineData=[], delimiter=str, workBook=excel.WorkBook, sheet=None):
    for line in lineData:
        if line.strip() != "":
            data = line.split("\t" if delimiter.count(" ") >=4 else delimiter)
            if data.__len__() > 0:
                row_num = next_rowNum()  # 多线程下获取写入行号
                for num in range(data.__len__()):
                    try:
                        workBook.paddingContent(sheet, row_num, num, data[num].strip())
                    except BaseException as e:
                        raise ConvertThreading(2, "第【%s】行转换出错" % row_num)


class ConvertThreading(threading.Thread):
    '''
    文件转换线程
    '''

    def __init__(self, event, files, encoding, symbol_text, progress, wm):
        threading.Thread.__init__(self)
        self.event, self.files, self.encoding, self.symbol_text, self.progress, self.vm = event, files, encoding, symbol_text, progress, wm

    def run(self):
        try:
            setConverting()
            convertFile(self.event, self.files, self.encoding, self.symbol_text, self.progress, self.vm)
        except Exception as e:
            result = e
        finally:
            setConverted()
            wid.msgDialog(result.code, result.msg)


class ConvertException(Exception):
    '''
    转换异常类
    '''
    code: int
    msg: str

    def __init__(self, code: int, msg: str):
        self.code, self.msg = code, msg
