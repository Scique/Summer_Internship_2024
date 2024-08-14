x = "hello"

def test():
    return 1+1

testvar = 1

exec("testvar = test()", locals())

print(testvar)

import datetime
print(str(datetime.datetime.now().time()))

y = {}
y.update({"hello": 1})