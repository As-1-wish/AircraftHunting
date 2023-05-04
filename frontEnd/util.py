import hashlib
from faker import Faker


# 加密字符串
def Encrypt(password):
    m = hashlib.md5()
    m.update(password.encode("utf8"))
    return m.hexdigest()


# 生成随机长度为6的字符串
def getRandomStr():
    return Faker().pystr()[0:6]

print(Encrypt('1111111'))


