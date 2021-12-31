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

def check_time(month,day,time): # 检验时间
    def change_num(c1,c2):
        if(c1<'0' or c1>'9'):
            return -1
        elif(c2<'0' or c2>'9'):
            return -1
        else:
            return int(c1)*10+int(c2)

    month_day=(31,28,31,30,31,30,31,31,30,31,30,31) # 月份及其对应的日期数
    if(month_day[month-1]<day):
        msg('err','错误','所选日期不存在，请重新选择！')
        return True
    if(len(time)!=11):
        msg('err','错误','所填时间格式错误，要求“HH:MM-HH:MM”！')
        return True
    h1=change_num(time[0],time[1])
    m1=change_num(time[3],time[4])
    h2=change_num(time[6],time[7])
    m2=change_num(time[9],time[10])
    if(time[2]!=':' or time[8]!=':' or time[5]!='-' or h1<0 or m1<0 or h2<0 or m2<0):
        msg('err','错误','所填时间格式错误，要求“HH:MM-HH:MM”！')
        return True
    if(h1>23 or m1>59 or h2>23 or m2>59):
        msg('err','错误','所填时间不存在，请重新输入！')
        return True
    if(h1>h2 or (h1==h2 and m1>m2)):
        msg('err','错误','起始时间大于结束时间，请重新输入！')
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

def rollback(): # 回溯
    conn.rollback()

def finish(flag): # 关闭连接
    if(flag):
        cursor.close()
        conn.close()


#------------------------- 登录界面 ---------------------------

def check(account, password):    # 登录检验
    res = (inspect(account,'int','账号栏', 8))
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
                        if(assign==None):
                            res = [state, account, name, sex, age, ('无','无')]
                            return res
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
            cursor.execute("insert into VISITOR_VOLUNTEER values('%s',0,'')" %(account))
            commit()
            msg('inf','提示','注册成功！您的账号为'+account+'。')
            return True
        except oracle.DatabaseError as e:
            msg('err','错误',str(e))
            rollback()
            return False

def apply_volunteer(account):
    try:
        cursor.execute("update VISITOR_VOLUNTEER set state=1 where account='%s'"%(account))
        commit()
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False


#----------------------------志愿管理部分-----------------------------------

def get_venue():        # 获取所有场馆信息
    try:
        cursor.execute("select vname from venue")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()

def new_assign(detail,venue):       # 创建志愿任务
    try:
        cursor.execute("select vno from venue where vname='%s'"%(venue))
        res=cursor.fetchone()[0]
        cursor.execute("insert into assign values(LPAD(q_ano.nextVal,8,0),'%s','%s')"%(detail,res))
        commit()
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False

def delete_assign(ano):             # 删除志愿任务
    try:
        cursor.execute("update VISITOR_VOLUNTEER set assign='' where assign='%s'"%(ano))
        cursor.execute("delete from assign where ano='%s'"%(ano))
        return False
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return True

def volunteer_list(*arg):                  # 获取申请者或志愿者列表
    try:
        cursor.execute("select a.account,uname,assign from visitor_volunteer a,users b where state =%s and a.account=b.account"%arg)
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()

def approve_volunteer(n,account):                     # 审批志愿者申请
    try:
        cursor.execute("update visitor_volunteer set state =%s where account = '%s'" %(n,account))
        return False
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return True

def assignment_list(*arg):                            # 获取所有志愿任务信息
    try:
        cursor.execute("select a.ano,vname,detail from assign a,venue b where a.venue=b.vno")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()

def allocate_assignment(account,ANo):                # 给志愿者分配任务
    try:
        cursor.execute("update visitor_volunteer set assign = '%s' where account = '%s'" %(ANo, account))
        commit()
        return False
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return True


# ------------------------- 票务信息部分 ------------------------------

def ticket_info(*arg):              # 获取票务信息
    try:
        cursor.execute("select mno, event, time, remain, price, vname from match, venue where match.venue = venue.vno")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()

def ticket_deal(tup, *arg):              # 购票结账
    try:
        sum = tup[1]
        account = tup[0]
        cursor.execute("insert into ticketdeal values (LPAD(q_dno.nextVal,8,0),sysdate,%d,'%s')"%(sum,account))
        for i in range (2, len(tup)):
            cursor.execute("insert into ticketsale values (LPAD(q_dno.currVal,8,0),'%s',%d,%d)"%(tup[i][0],tup[i][1],tup[i][2]))
            cursor.execute("select remain from match where mno ='%s'"%(tup[i][0]))
            remain = cursor.fetchone()[0]
            cursor.execute("update match set remain=%d where mno='%s'"%(remain-tup[i][1],tup[i][0]))
        commit()
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False


# ----------------- 查询历史记录相关 -------------------

def deal_data(n,account): # 查看历史记录
    try:
        if(n==1):
            cursor.execute("select dno,time,sum from ticketdeal where account='%s'"%(account))
        elif(n==2):
            cursor.execute("select dno,time,sum from itemdeal where account='%s'"%(account))
        res=cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()

def sale_data(n,dno): # 订单详情
    try:
        if(n==1):
            cursor.execute("select event,quantity,sum from match a,ticketsale b where a.mno=b.mno and dno='%s'"%(dno))
        elif(n==2):
            cursor.execute("select iname,quantity,sum from item a,itemsale b where a.ino=b.ino and dno='%s'"%(dno))
        res=cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()


# ------------------------- 商品信息部分 ------------------------------

def item_info(*arg):                            # 获取商品信息
    try:
        cursor.execute("select * from item")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        return ()

def item_deal(tup,*arg):                        # 购物结账
    try:
        sum = tup[1]
        account = tup[0]
        cursor.execute("insert into itemdeal values (LPAD(q_dno.nextVal,8,0),sysdate,%d,'%s')"%(sum,account))
        for i in range (2, len(tup)):
            cursor.execute("insert into itemsale values (LPAD(q_dno.currVal,8,0),'%s',%d,%d)"%(tup[i][0],tup[i][1],tup[i][2]))
            cursor.execute("select storage from item where ino='%s'"%(tup[i][0]))
            storage = cursor.fetchone()[0]
            cursor.execute("update item set storage=%d where ino='%s'"%(storage-tup[i][1],tup[i][0]))
        commit()
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False

def item_statistical(*arg):
    try:
        cursor.execute("select ino,iname, sum(quantity) from(select iname, itemsale.ino, quantity from itemsale ,item where item.ino=itemsale.ino) group by ino,iname order by sum(quantity) desc")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False


# ------------------- 票务和物品管理部分 ------------------


def supply_ticket(mno,total,remain):      # 补充门票数量
    try:
        cursor.execute("update match set total=%d where mno='%s'"%(total,mno))
        cursor.execute("update match set remain=%d where mno='%s'"%(remain,mno))
        commit()
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False

def add_new_item(iname,price,storage):          # 创建新商品
    try:
        if(inspect(price,'int','商品价格',0,1,5) or inspect(storage,'int','商品存量',0,1,5)):
            return False
        cursor.execute("insert into item values(LPAD(q_ino.nextVal,3,0),'%s',%s,%s)"%(iname,price,storage))
        commit()
        msg('inf','提示','商品新建成功！')
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False

def supply_item(ino,storage):         # 补充商品数量
    try:
        cursor.execute("update item set storage=%d where ino='%s'"%(storage,ino))
        commit()
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False


#---------------------------------赛事信息-------------------------------------------

def match_info(*arg):              # 获取票务信息
    try:
        cursor.execute("select mno, event, time, total, remain, price, vname from match, venue where match.venue = venue.vno")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return ()

def add_new_match(event,time,total,price,month,day,venue):                # 创建新的比赛
    try:
        if(inspect(price,'int','门票价格',0,1,5) or inspect(total,'int','门票总数',0,1,5)):
            return False
        if(check_time(int(month),int(day),time)):
            return False
        print(time)
        final_time=month+'月'+day+'日'+time
        cursor.execute("select vno from venue where vname='%s'"%(venue))
        res=cursor.fetchone()[0]
        cursor.execute("insert into match values(LPAD(q_mno.nextVal,3,0),'%s','%s',%s,%s,%s,'%s')"%(event,final_time,total,total,price,res))
        commit()
        msg('inf','提示','赛事新建成功！')
        return True
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False

def ticket_statistical(*arg):
    try:
        cursor.execute("select mno, event, total - remain as sold from match order by sold desc")
        res = cursor.fetchall()
        return res
    except oracle.DatabaseError as e:
        msg('err','错误',str(e))
        rollback()
        return False