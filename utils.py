#coding=utf-8

# fuck you, gbk
def holy_open(*args,**kwargs):
    f=open(*args,encoding='utf-8',**kwargs)
    try:
        f.read()
    except UnicodeDecodeError:
        f.close()
        return open(*args,encoding='gbk',**kwargs)
    else:
        f.seek(0)
        return f