import json


def analyzeJson(jsonStr=str):
    """
    解析json字符串
    :param jsonStr:
    :return:
    """
    if not jsonStr is None and jsonStr.strip() != "":
        return json.load(jsonStr)
    return None


def analyzeJsonFile(filePath=str):
    """
    解析json文件
    :param filePath:
    :return:
    """
    import os
    if os.path.exists(filePath) and os.path.isfile(filePath) and filePath.lower().endswith(".json"):
        with open(filePath, "rU", encoding="utf-8") as read:
            return json.load(read)
    return None
