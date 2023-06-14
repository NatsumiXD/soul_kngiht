import base64
import json
import os.path
from os import name
import re
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad


class File:
    def __init__(self) -> None:
        pass

    class Const:
        encryptedJsonGameFiles = ["battles.data", "battle.data"]  # 添加其他文件名到列表中

    # 加密文件
    def encrypt(self, data, file_name):
        result = data.encode('utf-8')
        if file_name == "battles.data" or file_name == "battle.data" or file_name in self.Const.encryptedJsonGameFiles:
            result = json.dumps(json.loads(data), separators=(',', ':')).encode('utf-8')
        if "item_data" in file_name or file_name == "task.data" or file_name == "setting.data" or "season_data" in file_name:
            result = self.encrypt_des(result, bytes([0x69, 0x61, 0x6d, 0x62, 0x6f, 0x0, 0x0, 0x0]))
        if file_name == "statistic.data":
            result = self.encrypt_des(result, bytes([0x63, 0x72, 0x73, 0x74, 0x31, 0x0, 0x0, 0x0]))
        if file_name == "game.data":
            result = self.xor(result)
        return result

    # 解密文件
    def decrypt(self, data, file_name):
        result = data.decode('utf-8')
        if ".xml" in file_name:
            attrs_regex = re.compile("(<.*?/>|<.*?</.*?>)")
            attrs_matcher = attrs_regex.finditer(data.decode('utf-8'))
            attrs = []
            final_xml = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n<map>"
            for attrs_match in attrs_matcher:
                for i in range(attrs_match.lastindex):
                    attrs.append(attrs_match.group(i))
            attrs.sort(key=lambda x: x.lower())
            attrs_arr = attrs
            for attr in attrs_arr:
                final_xml += "\n    " + attr
            final_xml += "\n</map>"
            result = final_xml
        if "item_data" in file_name or file_name == "task.data" or file_name == "setting.data" or "season_data" in file_name:
            result = self.decrypt_des(data, bytes([0x69, 0x61, 0x6d, 0x62, 0x6f, 0x0, 0x0, 0x0]))
        if file_name == "statistic.data":
            result = self.decrypt_des(data, bytes([0x63, 0x72, 0x73, 0x74, 0x31, 0x0, 0x0, 0x0]))
        if file_name == "game.data":
            result = self.xor(data)
        if file_name == "battles.data" or file_name == "battle.data" or file_name in self.Const.encryptedJsonGameFiles:
            result = json.dumps(json.loads(result), indent=4)
        return result

    @staticmethod
    def xor(data):
        key = bytes([115, 108, 99, 122, 125, 103, 117, 99, 127, 87, 109, 108, 107, 74, 95])
        output = bytearray(len(data))
        for i in range(len(data)):
            output[i] = key[i % 15] ^ data[i]
        return bytes(output)

    @staticmethod
    def decrypt_des(data, key):
        iv = bytes([0x41, 0x68, 0x62, 0x6f, 0x6f, 0x6c, 0x0, 0x0])
        cipher_bytes = base64.b64decode(data)
        cipher = DES.new(key, DES.MODE_CBC, iv)
        result_bytes = cipher.decrypt(cipher_bytes)
        result = unpad(result_bytes, DES.block_size).decode('utf-8')
        return result

    @staticmethod
    def encrypt_des(data, key):
        iv = bytes([0x41, 0x68, 0x62, 0x6f, 0x6f, 0x6c, 0x0, 0x0])
        cipher = DES.new(key, DES.MODE_CBC, iv)
        padded_data = pad(data, DES.block_size)
        result_bytes = cipher.encrypt(padded_data)
        result = base64.b64encode(result_bytes).decode('utf-8')
        return result


class Convert:
    File = File()
    FileName = ""

    def de_open(self):
        f = open(self.FileName, "rb")
        decode_data = self.decode(f.read())
        f.close()
        return decode_data

    def de_save(self):
        f = open(self.FileName, "rb")
        decode_data = self.decode(f.read())
        f.close()
        f = open(self.FileName + ".decode", "w")
        will_write = json.dumps(json.loads(decode_data), ensure_ascii=False, indent=4)
        f.write(will_write)
        f.close()
        return will_write

    def en_save(self):
        if not os.path.exists(self.FileName + ".decode"):
            print(
                "Cannot ind the file called " + self.FileName + ".Check if the file exists or use de_save() to create "
                                                                "it.")
            return "File Not Found."
        f = open(self.FileName + ".decode", "r")
        encode_data = json.dumps(json.loads(f.read()), ensure_ascii=False, separators=(',', ':'))

        encode_data = self.encode(encode_data)
        f.close()
        f = open(self.FileName + ".decode.encode", "w")
        will_write = encode_data
        f.write(will_write)
        f.close()
        return will_write

    def encode(self, data: str):
        byte = data
        return self.File.encrypt(byte, self.FileName)

    def decode(self, data: bytes):
        byte = data
        return self.File.decrypt(byte, self.FileName)
