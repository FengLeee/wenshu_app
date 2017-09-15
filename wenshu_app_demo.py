# -*- coding: utf-8 -*-
# author__ = "lyao"
# version__ = "1.0.1"
# Date: 2017/09/06 19:18
import base64
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import re
import json
import requests

headers = {
    'Content-Type':'application/json',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1; MX4 Build/LMY47I)',# 使用手机ＵＡ
}
url='http://wenshuapp.court.gov.cn/MobileServices/GetLawListData'
# condition是查询条件
form_data = '{"dicval":"asc","condition":"/CaseInfo/案/@案件类型=1","reqtoken":"BE6B6AFBACC7B49EA79307E6663A0457","skip":"20","limit":"20","dickey":"/CaseInfo/案/@法院层级"}'

response = requests.post(url,data=form_data,headers=headers)
b = base64.b64decode(response.text) #unicode 经过base64解密
he = b2a_hex(b)# 2进制的16进制表示法

class prpcrypt():
    def __init__(self, key):
        '''
        :param key: 解密秘钥
        '''
        self.key = key
        self.mode = AES.MODE_CBC
    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            # \0 backspace
            text = text + ('\0' * add)
        elif count > length:
            add = (length - (count % length))
            text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text),)
        return plain_text

if __name__ == '__main__':
    t = prpcrypt(u'lawyeecourtwensh')
    c = t.decrypt(he)
    # print c
    obj = re.match(u'.*?(:.*])',c)# 返回的不是json格式的文件 通过正则拼凑
    obj = '[{"案件类型"'+obj.group(1)
    data_list = json.loads(obj)
    for data in data_list:
        docID = data[u'文书ID']
        anhao = data[u'案号']
        fymc = data[u'法院名称']
        zjmc = data[u'案件名称']
        print docID,anhao,fymc,zjmc