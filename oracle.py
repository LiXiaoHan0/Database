from tkinter.constants import CHAR, FALSE
import cx_Oracle as oracle # 引入oracle数据库模块
#32位的Oracle系统可以通过安装instantclient并运行下面两行代码成功运行在64位的python环境，记得修改路径！
# import os
# os.environ['path'] =  r'D:/Codefield/CODE_python/instantclient_21_3'


# ------------------------ 通用函数 ----------------------

from tkinter import messagebox # 消息窗口
def msg(pattern,title,content): 
    if(pattern=='inf'):
        messagebox.showinfo(title=title,message=content)
    elif(pattern=='warn'):
        messagebox.showwarning(title=title,message=content)
    elif(pattern=='err'):
        messagebox.showerror(title=title,message=content)


def inspect(txt,var,pre,length,*limit): # 输入格式判断 

    # 参数：文本，类型，前缀，定长值，*最短值，*最长值

    if(var=='int'):
        for i in txt:
            if(i<'0' or i>'9'): 
                msg('err','错误',pre+'只能输入数字！')
                return True
    l=len(txt)
    if(length!=0): 
        if(l!=length):
            msg('err','错误',pre+'应当输入%d个字符！'%(length))
            return True
    elif(l<limit[0]):
        msg('err','错误',pre+'至少输入%d个字符！'%(limit[0]))
        return True
    elif(l>limit[1]):
        msg('err','错误',pre+'至多输入%d个字符！'%(limit[1]))
        return True
    return False

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


def check(account, password):    # 登录检验
    res = (inspect(account,'账号栏','int', 8))
    if (res):
        return -1
    else:
        try:
            cursor.execute("select * from users where account = '%s' and password = '%s'" %(account,password))
            res = cursor.fetchone()
            if (res == None):
                msg('err', '错误', '账号不存在或密码错误！')
                return -1
            else:
                (name, age, sex, account, password) = res
                res = []
                cursor.execute("select state, assign from visitor_volunteer where account = '%s'" %account)
                tmp = cursor.fetchone()
                if (tmp == None):
                    #是管理员
                    res = [3, account, name, sex, age]
                    return res
                else:
                    #是visitor_volunteer
                    (state, assign) = tmp
                    if (state == 0 or state == 1):
                        res = [state, account, name, sex, age]
                        return res
                    else:
                        cursor.execute("select detail, venue from assign where ano = '%s'" %assign)
                        (detail, vno) = cursor.fetchone()
                        cursor.execute("select vname from venue where vno = '%s'" %vno)
                        (vname,) = cursor.fetchone()   # 保证返回正确形式的(vname, detail)元组
                        res = [state, account, name, sex, age, (vname, detail)]
                        return res
        except oracle.DatabaseError as e:
            msg('err', '错误', str(e))
            return -1


def sign_in(name, age, sex, password, confirm):      # 提交注册
    if (inspect(name,'str','姓名',0,1,18)):
        return False
    elif (inspect(age,'int','年龄',0,1,2)):
        return False
    elif (inspect(password,'str','密码',0,1,18)):
        return False
    elif (password != confirm):
        msg('err', '错误', '两次输入密码不一致！')
        return False
    else:
        try:
            default_account = '20210000'
            cursor.execute("select * from users")
            if (cursor.fetchall() == None):
                account = default_account
            else:
                cursor.execute("select max(account) from users")
                account = str(int(cursor.fetchone()[0]) + 1)
            # 设置一个默认初始值，空表插入用默认值作为账号，其他则用此账号依次加一
            cursor.execute("insert into users values('%s', %d, '%s', '%s', '%s')" %(name,int(age), sex, account, password))
            commit()
            msg('inf','提示','注册成功！您的账号为'+account+'。')
            return True
        except oracle.DatabaseError as e:
            msg('err','错误',str(e))
            return False


#----------------------------操作部分-----------------------------------
def volunteer_approval_list(*arg):                  # 点击管理员选项中的“志愿管理”和刷新都可以进入这一选项
    try:
        cursor.execute("select account from visitor_volunteer where state = 1")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return False

def approve_volunteer(account):                     # 审批同意，可以在点击“同意”按钮时调用
    try:
        cursor.execute("update visitor_volunteer set state = 2 where account = '%s'" %account)
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return False
        
def volunteer_list(*arg):                            # 获取所有已经是志愿者的人的信息
    try:
        cursor.execute("select account from visitor_volunteer where state = 2")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return False

def allocate_assignment(account, ANo):                # 给志愿者分配任务
    try:
        cursor.execute("update visitor_volunteer set assign = '%s' where account = '%s'" %(ANo, account))
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return False