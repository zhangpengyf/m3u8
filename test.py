# -*- coding:utf-8 -*-  
import os
import sys
import requests
import datetime
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
 
reload(sys)
sys.setdefaultencoding('utf-8')

def read_file(name):
    with open(name, "r") as f:  # 打开文件
        data = f.read()  # 读取文件
    return data

def merge_ts(url):
    download_path = os.getcwd() + "/download"
    if os.path.exists(download_path):
        os.removedirs(download_path)
        
    #新建日期文件夹
    #download_path = os.path.join(download_path, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    #print download_path
    os.mkdir(download_path)
        
    all_content = read_file(url)  #读取M3U8文件内容
    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的链接")
 
 
    file_line = all_content.split("\n")
 
    unknow = True
    key = ""
    for index, line in enumerate(file_line): # 第二层
        if "#EXT-X-KEY" in line:  # 找解密Key
            method_pos = line.find("METHOD")
            comma_pos = line.find(",")
            method = line[method_pos:comma_pos].split('=')[1]
            print "Decode Method：", method
            
            uri_pos = line.find("URI")
            quotation_mark_pos = line.rfind('"')
            key_path = line[uri_pos:quotation_mark_pos].split('"')[1]
            
            key_url = url.rsplit("/", 1)[0] + "/" + key_path # 拼出key解密密钥URL
            key = read_file(key_url)
            print "key：" , key
            
        if "EXTINF" in line: # 找ts地址并下载
            unknow = False
            pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1] # 拼出ts片段的URL
            #print pd_url
            
            res = read_file(pd_url)
            c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
            print len(key)
            if len(key): # AES 解密
                cryptor = AES.new(key, AES.MODE_EAX, key)
                with open(os.path.join(download_path, c_fule_name + ".mp4"), 'ab') as f:
                    print res
                    f.write(cryptor.decrypt(res))
                # with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                #     print res
                #     f.write(cryptor.decrypt(res))
            else:
                with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                    f.write(res.content)
                    f.flush()
    if unknow:
        raise BaseException("未找到对应的下载链接")
    else:
        print "下载完成"
    merge_file(download_path)
 
def merge_file(path):
    os.chdir(path)
    cmd = "copy /b * new.tmp"
    os.system(cmd)
    os.system('del /Q *.ts')
    os.system('del /Q *.mp4')
    os.rename("new.tmp", "new.mp4")
    
if __name__ == '__main__': 
    url = "./5f913e952b2f9eba82a7464c1c29f72f_2/5f913e952b2f9eba82a7464c1c29f72f_2.m3u8"
    merge_ts(url)
