from tkinter import *
from types import BuiltinFunctionType
from oracle import *
from tkinter import ttk # 树状表格

# 全局变量
flag=0 # 连接情况
user_data=(0,'0','无',0,('无','无')) # 用户信息

root=Tk() # 根窗口
screen_x=root.winfo_screenwidth() # 屏幕宽度
screen_y=root.winfo_screenheight() # 屏幕高度

# ------------------------- 全局类 -----------------------------

class subform: # 输入框界面

    def __init__(self,father,title,que): # 父容器，标题，标签及默认值
        l=len(que)

        form=Toplevel(father)
        form.title(title)
        form.geometry("300x"+str(45*(l+1))+"+"+str((screen_x-300)//2)+"+"+str((screen_y-45*(l+1))//2))
        form.resizable(width=False, height=False)

        frm=Frame(form)
        str_v=[StringVar(frm) for i in range(l)]
        str_e=[] # 输入框
        str_l=[] # 下拉框
        for i,e in enumerate(que):
            if(e[2]==0):
                str_e.append([Entry(frm,fg='#A9A9A9',textvariable=str_v[i]),i])
            else:
                str_l.append([ttk.Combobox(frm,values=e[3],textvariable=str_v[i],width=17,state="readonly"),i])
        e_l=len(str_e)
        bool_e=[True for i in range(e_l)]

        self.flag=bool_e
        self.form=form
        self.edit=str_e
        self.list=str_l

        def press_key(event,index): # 上下键绑定
            if(event.keycode==38): self.first_edit(event,(index-1)%e_l)
            elif(event.keycode==40): self.first_edit(event,(index+1)%e_l)
        
        for i,txt in enumerate(que):
            Label(frm,text=txt[0],font=('SimHei',12)).grid(row=i, column=0,columnspan=2)
        for i,e in enumerate(str_e):
            e[0].insert(0,que[e[1]][1]) # 默认值
            e[0].bind('<Button-1>',lambda event,_i=i:self.first_edit(event,_i)) # 初次编辑判定
            e[0].bind('<Return>',self.submit_data) # 绑定回车键
            e[0].bind('<Key>',lambda event,_i=i:press_key(event,_i+e_l)) # 绑定上下键
            e[0].grid(row=e[1],column=3,padx=5,pady=10,columnspan=4)
        for e in str_l:
            e[0].bind('<Return>',self.submit_data) # 绑定回车键
            e[0].grid(row=e[1],column=3,padx=5,pady=10,columnspan=4) # 默认值
        Button(frm,width=8,text="退出",font=('SimHei',12),command=self.exit_form).grid(row=l,column=1,pady=10,columnspan=2)
        Button(frm,width=8,text="提交",font=('SimHei',12),command=self.submit_data).grid(row=l,column=5,pady=10)

        frm.pack()
        form.mainloop()

    def get_data(self,*event):
        self.vars=[i[0].get() for i in self.edit]
        for i in self.list:
            self.vars.append(i[0].get())

    def first_edit(self,event,index):
        if(self.flag[index]):
            self.edit[index][0].config(fg='#000000')
            self.edit[index][0].delete(0,END)
            self.flag[index]=False
        if(not self.edit[index][0].select_present()): self.edit[index][0].focus_set()

    def exit_form(self):
        self.form.destroy()


class table: # 自定义表格

    def __init__(self,father,num,heads,position,method): # 初始化
        self.data=[]
        self.far=father
        self.heads=heads
        self.search=method
        self.ybar=Scrollbar(father,orient='vertical')
        self.chart=ttk.Treeview(father,height=num,show="headings",columns=heads[0],yscrollcommand=self.ybar.set).grid(row=position[0],column=position[1],rowspan=position[2],columnspan=position[3],pady=position[4],padx=position[5])
        self.ybar['command']=self.chart.yview
        for i,val in enumerate(heads[0]): # 设置表头
            self.chart.column(val,width=heads[1][i+1]-heads[1][i],anchor="center")
            self.chart.heading(val,text=val,command=lambda _val=val:self.sort_column(_val,False))

    def sort_column(self,col,way): # 表头排序
        tmp=self.chart
        que=[(tmp.set(k,col),k) for k in tmp.get_children('')]
        que.sort(reverse=way)
        for i,(val,k) in enumerate(que):
            tmp.move(k,'',i)
        tmp.heading(col,command=lambda:self.sort_column(col,not way))

    def delete_data(self,method): # 删除数据
        tmp=self.chart
        if(len(tmp.selection())==0):
            msg('err','提示','未选择任何数据！')
        else:
            if(messagebox.askokcancel('提示', '相关信息也将被删除，确定要删除数据吗？')):
                global alter
                alter=1
                method([tmp.set(k,"课程号") for k in tmp.selection()])
                self.search_data(0)

    def search_data(self,*arg): # 获取数据
        for i in self.chart.get_children(''):
            self.chart.delete(i)
        self.data=self.search(arg)
        for i,val in enumerate(self.data):
            self.chart.insert('',i,values=val)

    def save_change(self,val,cn,rn,col,row): # 具体问题具体分析
        print(val,cn,rn,col,row)

    def change_data(self,event): # 修改数据
        tmp=self.chart
        col= tmp.identify_column(event.x) # 列节点
        row = tmp.identify_row(event.y) # 行节点
        cn=int(str(col).replace('#','')) # 获取列数
        rn=(event.y-6)//20 # 获取行数

        def finish_edit(event):
            if(edit.get()!=''):
                self.save_change(edit.get(),cn,rn,col,row)
            edit.destroy()

        if(len(self.data)>=rn and rn>0):
            Str_v=StringVar()
            edit=Entry(self.far,width=(self.heads[1][cn]-self.heads[1][cn-1])//8,textvariable=Str_v)
            edit.focus_set()
            edit.bind('<FocusOut>',finish_edit)
            # edit.bind('<Return>',self.save_change)
            edit.place(x=self.heads[1][cn-1]*15//16+self.heads[1][cn]//16,y=rn*20+16)

    def export_info(): # 导出数据
        pass

    def print_info(): # 打印数据
        pass



# ------------------------ 登录界面函数 ----------------------------

def check_login(*arg): # 登录检验
    print(l_e1.get(),l_e2.get()) # 所需数据
    global user_data
    user_data=(2,'3','李晗','男','19岁',('冰立方','制冰')) # 示例
    # !!! 需要返回用户信息，第一个是权限、第二个是账号
    # -1:账号不存在或密码错误
    # 0:未申请为志愿者；
    # 1:申请成为志愿者；
    # 2:已经成为志愿者；
    # 3:管理员
    if(user_data[0]!=-1): login.destroy()


def sign_in(): # 注册界面

    class sign_subform(subform): # 继承

        def submit_data(self,*event): # 提交数据
            self.get_data() # 刷新数据
            print(self.vars) # !!!

    sign_subform(login,'新用户注册',[('姓名：','请输入姓名',0),('年龄：','请输入年龄',0),('性别：','请选择性别',1,['男','女']),('密码：','请设置20以内密码',0),('确认密码：','请再次输入密码',0)])


# ------------------------- 登录界面布局 -----------------------------

login=root
login.title("北京冬奥会信息管理系统：登录界面")
login.geometry("450x250+"+str((screen_x-450)//2)+"+"+str((screen_y-250)//2))
login.resizable(width=False, height=False)

l_frm=Frame(login)
l_v1=StringVar()
l_v2=StringVar()

import tkinter # 引入图片
pic=tkinter.PhotoImage(file="dream.gif")

Label(l_frm,width=150,height=180,image=pic).grid(row=1,column=0,columnspan=2,rowspan=3,padx=5,pady=10)
Label(l_frm, text='账号：',font=('SimHei',15)).grid(row=1, column=2,columnspan=2)
Label(l_frm, text='密码：',font=('SimHei',15)).grid(row=2, column=2,columnspan=2)
l_e1=Entry(l_frm,font=('SimHei',15),width=15,textvariable=l_v1)
l_e2=Entry(l_frm,font=('SimHei',15),width=15,textvariable=l_v2,show='*')

# 绑定回车键&上下键
def e_press_key(event,index):
    if(event.keycode==38 or event.keycode==40):
        if(index==1): l_e2.focus_set()
        else: l_e1.focus_set()
l_e1.bind('<Return>',check_login)
l_e2.bind('<Return>',check_login)
l_e1.bind('<Key>',lambda event:e_press_key(event,1))
l_e2.bind('<Key>',lambda event:e_press_key(event,2))

# 组件定位
l_e1.grid(row=1,column=4,padx=5,pady=10,columnspan=3)
l_e2.grid(row=2,column=4,padx=5,pady=10,columnspan=3)
Button(l_frm,text="登录",width=6,font=('SimHei',15),command=check_login).grid(row=3,column=2,columnspan=3,pady=15,padx=5)
Button(l_frm,text="注册",width=6,font=('SimHei',15),command=sign_in).grid(row=3,column=5,columnspan=2,pady=15,padx=5)
l_frm.pack(padx=20,pady=20)

# 设置程序图标
# login.iconbitmap(default="pic\homework.ico")

flag=connect() # 连接数据库
if(flag):login.mainloop()


# ------------------------- 操作界面函数 -----------------------------

def clear(): # 清除页面布局
    global frm
    frm.destroy()

# ------- 个人信息页面 --------

def apply_volunteer(): # 申请成为志愿者
    print(user_data[1])
    if(True): # !!! 提供申请志愿者的账号，返回操作是否成功
        user_data[0]=1
        call_info()
    
def show_volunteer(): # 查看志愿任务分配
    if(user_data[5][0]!=''):
        msg('inf','志愿任务查看','您分配到的场馆为'+user_data[5][0]+'，您负责的工作是'+user_data[5][1]+'。')
    else:
        msg('inf','您还没有被分配具体任务！')

# ------- 订票业务页面 --------




# ------------------------- 操作界面子布局 -----------------------------

def call_info(): # 个人信息页面
    clear()
    global frm
    frm=Frame(form)
    power=['群众','群众','志愿者','管理员']

    # form.geometry("600x300")
    Label(frm,width=160,height=160,image=user_pic).grid(row=0,column=0,rowspan=4,padx=60)
    for i,txt in enumerate(('账号：','姓名：','性别：','年龄：')):
        Label(frm,text=txt+user_data[i+1],font=('SimHei',20),width=20,anchor=NW).grid(row=i,column=1,columnspan=2,pady=5)
    Label(frm,text="您的身份是："+power[user_data[0]],font=('SimHei',16)).grid(row=4,column=0,pady=30)
    if(user_data[0]==0):
        Button(frm,text="申请成为志愿者",width=16,font=('SimHei',16),command=apply_volunteer).grid(row=4,column=1,columnspan=2,pady=30,padx=20)
    elif(user_data[0]==1):
        Label(frm,text="志愿申请已提交",font=('SimHei',16)).grid(row=4,column=1,columnspan=2,pady=30,padx=20)
    elif(user_data[0]==2):
        Button(frm,text="查看志愿任务分配",width=16,font=('SimHei',16),command=show_volunteer).grid(row=4,column=1,columnspan=2,pady=30,padx=20)
        
    frm.pack(padx=20,pady=20)


def call_ticket(): # 票务页面
    clear()
    global frm
    frm=Frame(form)
    heads1=[('比赛项目','比赛时间','门票剩余','门票价格（元）'),(0,80,180,250,320)]
    heads2=[('比赛项目','购票数量','单项价格（元）'),(0,80,180,230,280)]

    
    Label(frm,text="票务信息",font=('SimHei',16)).grid(row=0,column=0,pady=30,padx=50)
    Label(frm,text="已选门票",font=('SimHei',16)).grid(row=0,column=0,pady=30,padx=50)
    table(frm,12,heads1,(1,0,5,1,20,20),clear)
    table(frm,6,heads2,(1,0,1,1,20,20),clear)
    Label(frm,text="合计金额：0",font=('SimHei',16)).grid(row=0,column=0,pady=30,padx=50)
    
    


def call_item(): # 商品页面
    clear()
    pass


def call_manager(): # 商品管理页面
    clear()
    pass


def call_volunteer(): # 志愿管理页面
    clear()
    pass


# ------------------------- 操作界面主布局 -----------------------------

if(user_data[0]>=0):
    form=Tk()
    form.title("北京冬奥会信息管理系统：操作界面")
    form.geometry("600x300"+"+"+str((screen_x-600)//2)+"+"+str((screen_y-300)//2))
    form.resizable(width=False, height=False)

    frm=Frame(form) # 页面框架
    option=Menu(form) # 菜单栏
    user_pic=tkinter.PhotoImage(file="user.gif") # 用户照片
    option.add_command(label ="个人信息",command=call_info)
    if(user_data[0]!=3):
        option.add_command(label ="订票服务",command=call_ticket)
        option.add_command(label ="购买商品",command=call_item)
    else:
        option.add_command(label ="商品管理",command=call_manager)
        option.add_command(label ="志愿管理",command=call_volunteer)
    form.config(menu=option)

    call_info()


    form.mainloop()
        
    # m_heads=[('课程号','课程名','学分','学时','先修要求'),(0,100,300,400,550,700)] # 表头及列宽

    # m_frm=Frame(form)
    # m_table=main_table(m_frm,15,m_heads)
    # m_table.chart.bind('<Double-1>',m_table.change_data)

    # # 组件定位
    # m_table.chart.grid(row=0,column=0,columnspan=12,pady=12)
    # m_table.ybar.grid(row=0,column=12,sticky='ns',pady=12)
    # Button(m_frm,text="获取",width=6,font=('Arial',12),command=lambda:m_table.search_data(0)).grid(row=1,column=1)
    # Button(m_frm,text="详情",width=6,font=('Arial',12),command=lambda:detail_info(m_table.chart)).grid(row=1,column=2)
    # Button(m_frm,text="新建",width=6,font=('Arial',12),command=lambda:add_info(m_table)).grid(row=1,column=5)
    # Button(m_frm,text="删除",width=6,font=('Arial',12),command=lambda:m_table.delete_data(delete)).grid(row=1,column=6)
    # # Button(m_frm,text="导出",width=6,font=('Arial',12),command=export_info).grid(row=1,column=7)
    # # Button(m_frm,text="打印",width=6,font=('Arial',12),command=print_info).grid(row=1,column=8)
    # Button(m_frm,text="保存",width=6,font=('Arial',12),command=save_all).grid(row=1,column=9)
    # Button(m_frm,text="退出",width=6,font=('Arial',12),command=exit_all).grid(row=1,column=10)
    # m_frm.pack(pady=10)
    # form.mainloop()

finish(flag) # 结束数据库连接