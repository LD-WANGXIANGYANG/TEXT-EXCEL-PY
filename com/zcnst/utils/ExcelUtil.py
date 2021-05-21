# coding=utf-8

'''
@project = data_source
@file = ExcelUtil 
@author = WANG-PC
@create_time = 2019/1/29 14:33
'''
import os
import datetime
import xlsxwriter as excel
import re

contentTypes = [("^((\d?)|([1-9]\d{1,13})|(\d{1,14}\.\d{1,11}))$", "numerical"),
                ("^(http|ftp|https)?://[\w\.\?=@#%&\*\/]+$", "url"),
                ("^TRUE|FALSE|true|false$", "bool"),
                ("^((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3})[-/\.](((0[13578]|1[02])[-/\.]"
                 "(0[1-9]|[12]\d|3[01]))|((0[469]|11)[-/\.](0[1-9]|[12]\d|30))|(02[-/\.](0[1-9]|[1]\d|2[0-8]))))|"
                 "(((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))[-/\.]02[-/\.]29)$",
                 "date")]


def isContentType(conten=str):
    if conten is not None:
        for reg in contentTypes:
            try:
                m = re.match(reg[0], conten)
                if m is not None:
                    return reg[1], m
            except:
                continue


class WorkBook(object):
    """
    自定义WorkBook工具类
    """

    def __init__(self, path, fileName, constant_memory: bool):
        file = self.__createFile(path, fileName, ".xlsx")
        self.__workBook = excel.Workbook(file, {'constant_memory': constant_memory, 'in_memory': not constant_memory,
                                                'default_date_format': 'yyyy/MM/dd'})

    def createSheet(self, sheetName):
        return self.__workBook.add_worksheet(sheetName)

    def finish(self):
        self.__workBook.close()

    def __createFile(self, pathStr, fileName, suffix):
        '''
        创建文件，如果文件存在则文件名追加“(副本)”进行再创建
        :param path: 创建文件的绝对路径
        :param fileName: 文件名称
        :param suffix: 文件后缀
        :return: 创建的文件
        '''
        if isinstance(pathStr, str):
            if not pathStr.endswith("/") and not pathStr.endswith("\\"):
                pathStr += "/"
        else:
            return None

        if not os.path.isabs(pathStr):
            return None

        if not os.path.exists(pathStr):
            os.makedirs(pathStr)

        pathFileName = pathStr + fileName + suffix
        if os.path.exists(pathFileName):
            return self.__createFile(pathStr, fileName + "(副本)", suffix)
        else:
            return pathFileName

    def paddingContent(self, sheet=excel.Workbook.worksheet_class, romNum=int, col=int, content=str):
        if sheet != None and col >= 0 and romNum >= 0 and content != "":
            typeObj = isContentType(content)
            if typeObj is None:
                sheet.write(romNum, col, content)
            else:
                isType = typeObj[0]
                isValue = typeObj[1].group()
                if isType == "numerical":
                    if re.search("[^\\x00-\\xff]", content) is not None:  # 判断是否为全角字符
                        sheet.write_string(romNum, col, content)
                    else:
                        sheet.write_number(romNum, col, eval(isValue))
                elif isType == "url":
                    if sheet.hlink_count < 65529:
                        sheet.write_url(romNum, col, content)
                    else:
                        sheet.write_string(romNum, col, content)
                elif isType == "bool":
                    sheet.write_boolean(romNum, col, isValue.lower() == "true")
                elif isType == "date":
                    isValue = re.sub("[-\.]", "/", isValue)
                    dateTimefmt = "%Y/%m/%d"
                    timeReg = re.search("([0-1]?[0-9]|2[0-3]):([0-5][0-9])$", content)
                    if timeReg is not None:
                        isValue += " " + timeReg.group()
                        dateTimefmt += " %H:%M"
                    sheet.write_datetime(romNum, col, datetime.datetime.strptime(isValue, dateTimefmt))
