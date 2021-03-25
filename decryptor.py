import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
 
private_key = "你生成的私钥"
encrypted   = "复制加密的内容过来"

# 应用秘钥对RSA类进行实例化
rsakey = RSA.importKey(private_key)
rsakey = PKCS1_OAEP.new(rsakey)

# 对编码文件Base64解码
chunk_size = 256
offset     = 0
decrypted  = ""
encrypted  = base64.b64decode(encrypted)

# 以256个字节为一块来解密数据
while offset < len(encrypted):
  decrypted += rsakey.decrypt(encrypted[offset:offset+chunk_size]) 
  offset    += chunk_size

# 将这些负载解压，因为之前是压缩过之后再加密处理的
plaintext = zlib.decompress(decrypted)
print plaintext
