import cx_Oracle as oracle # 引入oracle数据库模块
#32位的Oracle系统可以通过安装instantclient并运行下面两行代码成功运行在64位的python环境，记得修改路径！
#import os
#os.environ['path'] =  r'D:/Codefield/CODE_python/instantclient_21_3'


# ------------------------ 通用函数 ----------------------

from tkinter import messagebox # 消息窗口
def msg(pattern,title,content): 
    if(pattern=='inf'):
        messagebox.showinfo(title=title,message=content)
    elif(pattern=='warn'):
        messagebox.showwarning(title=title,message=content)
    elif(pattern=='err'):
        messagebox.showerror(title=title,message=content)


# ----------------------- 数据库连接 ----------------------

def connect(): # 连接数据库
    try: 
        global conn,cursor
        conn=oracle.connect("s2020012856/DIDIDI147896325@166.111.68.220/dbta") 
        cursor=conn.cursor()    #获取数据库的操作游标
        return 1
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return 0


def commit(): # 提交修改
    conn.commit()


def finish(flag): # 关闭连接
    if(flag):
        cursor.close()
        conn.close()

#------------------------- 登录界面 ---------------------------

