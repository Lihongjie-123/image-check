import hashlib

def md5_convert(string):
    """
    计算字符串md5值
    :param string: 输入字符串
    :return: 字符串md5
    """
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()