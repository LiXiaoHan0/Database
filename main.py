from tkinter import *
from oracle import *
from tkinter import ttk # 树状表格


# 全局变量
flag=0 # 连接情况
debug=3 # 调试模式，可以跳过登录界面
user_data=(-1,'0','无','无',0,('无','无')) # 用户信息
# -1:账号不存在或密码错误；
# 0:未申请为志愿者；
# 1:申请成为志愿者；
# 2:已经成为志愿者；
# 3:管理员
# 示例 user_data=(2,'3','李晗','男','19岁',('冰立方','制冰'))

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
            e[0].grid(row=e[1],column=3,padx=5,pady=10,columnspan=4) # 确定位置
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

    def __init__(self,father,num,heads,method): # 初始化
        self.data=[]
        self.far=father
        self.son=Frame(father)
        self.heads=heads
        self.search=method
        xbar=Scrollbar(self.son,orient='horizontal')
        ybar=Scrollbar(self.son,orient='vertical')
        self.chart=ttk.Treeview(self.son,height=num,show="headings",columns=heads[0],xscrollcommand=xbar.set,yscrollcommand=ybar.set)
        xbar['command']=self.chart.xview
        ybar['command']=self.chart.yview
        for i,val in enumerate(heads[0]): # 设置表头
            tmp_width=heads[1][i+1]-heads[1][i]
            self.chart.column(val,width=tmp_width,minwidth=tmp_width,anchor="center")
            self.chart.heading(val,text=val,command=lambda _val=val:self.sort_column(_val,False))
        xbar.pack(side=BOTTOM,fill=X)
        ybar.pack(side=RIGHT,fill=Y)
        self.chart.pack(fill=BOTH,expand=True)

    def sort_column(self,col,way): # 表头排序
        tmp=self.chart
        try:
            que=[(int(tmp.set(k,col)),k) for k in tmp.get_children('')]
        except:
            que=[(tmp.set(k,col),k) for k in tmp.get_children('')]
        que.sort(reverse=way)
        for i,(val,k) in enumerate(que):
            tmp.move(k,'',i)
        tmp.heading(col,command=lambda:self.sort_column(col,not way))

    def delete_data(self,method=0): # 删除数据
        tmp=self.chart
        if(method==0):
            for k in tmp.get_children():
                tmp.delete(k) 
        elif(method==1):
            if(len(tmp.selection())==0):
                msg('err','提示','未选择任何数据！')
            else:
                for k in tmp.selection():
                    tmp.delete(k)

    def search_data(self,arg=0): # 获取数据
        for i in self.chart.get_children():
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

class order: # 自定义数量单

    def __init__(self,father,title,txt,number,method):
        form=Toplevel(father)
        form.title(title)
        form.geometry("300x"+str(45*(1+1)+20)+"+"+str((screen_x-300)//2)+"+"+str((screen_y-45*(1+1))//2))
        form.resizable(width=False, height=False)

        frm=Frame(form)
        Label(frm,text=txt,font=('SimHei',12)).grid(row=0,column=0,columnspan=2)
        str0=StringVar()
        Button(frm,width=8,text="取消",font=('SimHei',12),command=self.exit_form).grid(row=1,column=1,pady=10)
        Button(frm,width=8,text="确定",font=('SimHei',12),command=self.submit_data).grid(row=1,column=3,pady=10)
        spin=ttk.Spinbox(frm,from_=1,to=number,increment=1,textvariable=str0,font=('SimHei',12),state="readonly")
        spin.grid(row=0,column=2,columnspan=3,pady=15)
        spin.bind('<Return>',self.submit_data) # 绑定回车键
        frm.pack()

        self.num=str0
        self.form=form
        self.method=method
    
    def exit_form(self):
        self.form.destroy()

    def submit_data(self,*event):
        if(self.num.get()!=''):
            self.form.destroy()
            print(self.num.get())
            self.method(int(self.num.get()))
        else:
            msg('err','提示','未选择数量！')
            self.form.focus_set()
        


# ------------------------ 登录界面函数 ----------------------------

def check_login(*arg): # 登录检验
    global user_data
    if(debug>=0 and l_e1.get()==''): # 测试专用
        user_data=(debug,'00000000','测试账号','无','99',('宿舍','码代码'))
    else:
        tmp_data=check(l_e1.get(), l_e2.get())
        if(tmp_data!=-1):
            user_data=tmp_data
    if(user_data[0]!=-1): login.destroy()


def sign_data(): # 注册界面

    class sign_subform(subform): # 继承

        def submit_data(self,*event): # 提交数据
            self.get_data() # 刷新数据
            print(self.vars[0],self.vars[1],self.vars[2],self.vars[3],self.vars[4])
            if(sign_in(self.vars[0],self.vars[1],self.vars[4],self.vars[2],self.vars[3])):
                self.exit_form()
            else:
                self.form.focus_set()

    sign_subform(login,'新用户注册',[('姓名：','请输入姓名',0),('年龄：','请输入年龄',0),('性别：','请选择性别',1,('男','女')),('密码：','请设置20字符以内密码',0),('确认密码：','请再次输入密码',0)])


# ------------------------- 登录界面布局 -----------------------------

login=root
login.title("北京冬奥会信息管理系统：登录界面")
login.geometry("450x250+"+str((screen_x-450)//2)+"+"+str((screen_y-250)//2))
login.resizable(width=False, height=False)

l_frm=Frame(login)
l_v1=StringVar()
l_v2=StringVar()

import tkinter # 引入图片
pic=tkinter.PhotoImage(file="figures/dream.gif")

Label(l_frm,width=150,height=180,image=pic).grid(row=1,column=0,columnspan=2,rowspan=3,padx=5,pady=10)
Label(l_frm, text='账号：',font=('SimHei',15)).grid(row=1, column=2,columnspan=2)
Label(l_frm, text='密码：',font=('SimHei',15)).grid(row=2, column=2,columnspan=2)
l_e1=Entry(l_frm, font=('SimHei',15),width=15,textvariable=l_v1)
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
Button(l_frm,text="注册",width=6,font=('SimHei',15),command=sign_data).grid(row=3,column=5,columnspan=2,pady=15,padx=5)
l_frm.pack(padx=20,pady=20)

# 设置程序图标
# login.iconbitmap(default="pic\homework.ico")

flag=connect() # 连接数据库
if(flag):login.mainloop()


# ------------------------- 操作界面函数 -----------------------------

def clear(): # 清除页面布局
    global frm
    frm.destroy()

def deal_detail(father,n): # 历史订单信息

    def sale_detail(father,chart,n): # 订单详细信息
        if(len(chart.selection())==0):
            msg('err','提示','未选择任何订单！')
            father.focus_set()
        elif(len(chart.selection())>1):
            msg('err','提示','一次只能选择一个订单！')
            father.focus_set()
        else:
            dno=chart.set(chart.selection()[0],'订单编号')
            sum=chart.set(chart.selection()[0],'合计金额')
            form=Toplevel(father)
            form.title("订单详细信息")
            form.geometry("320x280")
            form.resizable(width=False, height=False)
            if(n==1):
                heads=[('比赛项目','购票数量','金额小计'),(0,100,160,240)]
            elif(n==2):
                heads=[('商品名称','购买数量','金额小计'),(0,100,160,240)]

            frm=Frame(form)
            i_table=table(frm,8,heads,lambda tmp:sale_data(n,dno))
            i_table.son.grid(row=0,column=0,columnspan=2,pady=10)
            Button(frm,text="关闭",width=10,font=('SimHei',12),command=form.destroy).grid(row=1,column=1,pady=5)
            Label(frm,text="合计金额："+sum,width=16,font=('SimHei',12)).grid(row=1,column=0,pady=5)
            frm.pack(pady=5,padx=5)
            i_table.search_data()

    form=Toplevel(father)
    text=('购票历史信息','购物历史信息')
    form.title(text[n-1])
    form.geometry("380x320")
    form.resizable(width=False, height=False)
    heads=[('订单编号','下单时间','合计金额'),(0,80,220,320)]

    frm=Frame(form)
    i_table=table(frm,10,heads,lambda tmp:deal_data(n,user_data[1]))
    i_table.son.grid(row=0,column=0,columnspan=2,pady=10)
    Button(frm,text="关闭",width=10,font=('SimHei',12),command=form.destroy).grid(row=1,column=0,pady=5)
    Button(frm,text="查看",width=10,font=('SimHei',12),command=lambda:sale_detail(father,i_table.chart,n)).grid(row=1,column=1,pady=5)
    frm.pack(pady=5,padx=5)
    i_table.search_data()


# ------- 个人信息页面 --------

def apply_volunteers(): # 申请成为志愿者
    if(user_data[0]==1):
        msg('inf','提示','申请已提交，请等待管理员审批通过！')
    elif(apply_volunteer(user_data[1])):
        user_data[0]=1
        call_info()
        msg('inf','提示','申请提交成功！')
    
def show_volunteer(): # 查看志愿任务分配
    if(user_data[5][0]!='无'):
        msg('inf','志愿任务查看','您分配到的场馆为'+user_data[5][0]+'，您负责的工作是'+user_data[5][1]+'。')
    else:
        msg('inf','提示','您还没有被分配具体任务，请等待管理员分配任务。')

def quit_account(form): # 退出登录
    form.destroy()


# ------- 订票业务页面 --------

def update_ticket(n,table1,table2,label):
    def clear_all():
        table1.search_data()
        table2.delete_data()
        label.configure(text="合计金额：0")
    if(n==1): # 清空门票信息
        print(table2.chart.get_children())
        if(len(table2.chart.get_children())==0):
            msg('err','提示','没有选择任何信息！')
        else:
            if(messagebox.askokcancel('提示', '确定要清空购物车信息吗？')):  
                clear_all()
    elif(n==2): # 刷新门票信息
        if(len(table2.chart.get_children())==0):
            clear_all()
        elif(messagebox.askokcancel('提示', '刷新会清空购物车信息，确定要继续吗？')):
            clear_all()
    elif(n==3): # 删除部分门票信息
        if(len(table2.chart.selection())==0):
            msg('err','提示','没有选择任何信息！')
        else:
            if(messagebox.askokcancel('提示', '确定要取消订购已选中的门票吗？')):  
                chart1=table1.chart
                chart2=table2.chart
                for i in chart1.get_children(): # 恢复
                    for j in chart2.selection():
                        if(chart1.set(i,"比赛编号")==chart2.set(j,"比赛编号")):
                            chart1.set(i,"门票剩余",int(chart1.set(i,"门票剩余"))+int(chart2.set(j,"购票数量")))
                table2.delete_data(1)
                global ans
                ans=0
                for i in chart2.get_children(): 
                    ans+=int(chart2.set(i,"金额小计"))
                label.configure(text="合计金额："+str(ans))

def select_ticket(table1,table2,label): # 选择票务信息
    chart1=table1.chart
    chart2=table2.chart
    if(len(chart1.selection())==0):
        msg('err','提示','未选择任何信息！')
    elif(len(chart1.selection())>1):
        msg('err','提示','一次只能选择一条信息！')
    elif(int(chart1.set(chart1.selection()[0],"门票剩余"))==0):
        msg('err','提示','该场次已没有余票！')
    else:
        def add_data(num):
            print('购票数量为：'+str(num))
            def update_sum(): # 计算总金额
                global ans
                ans=0 
                for i in chart2.get_children(): 
                    ans+=int(chart2.set(i,"金额小计"))
                label.configure(text="合计金额："+str("%.1d"%(ans)))

            chart1.set(choice,"门票剩余",int(chart1.set(choice,"门票剩余"))-num)
            for i in chart2.get_children():
                if(chart1.set(choice,"比赛编号")==chart2.set(i,"比赛编号")):
                    chart2.set(i,"购票数量",int(chart2.set(i,"购票数量"))+num)
                    chart2.set(i,"金额小计",int(chart2.set(i,"购票数量"))*int(chart1.set(choice,"门票价格")))
                    update_sum()
                    return
            selection=[chart1.set(choice,"比赛编号"),chart1.set(choice,"比赛项目"),num,num*int(chart1.set(choice,"门票价格"))]
            chart2.insert('',len(chart2.get_children()),values=selection)
            update_sum()
        choice=chart1.selection()[0]
        order(frm,'选择购票数量','购票数量：',int(chart1.set(choice,"门票剩余")),add_data)

def finish_ticket(chart2,label): # 开始结账
    global ans
    the_data=[user_data[1], ans]
    for i in chart2.get_children():
        the_data.append((chart2.set(i,"比赛编号"),int(chart2.set(i,"购票数量")),int(chart2.set(i,"金额小计"))))
    print(the_data)
    if(len(chart2.get_children())==0):
        msg('err','提示','未选择任何门票信息！')
    elif(ticket_deal(the_data)):
        msg('inf',"提示","购票成功！")
        label.configure(text="合计金额：0")
        call_ticket()
    else:
        msg('err',"提示","订单提交失败，请稍后重试！")
        call_ticket()


# --------- 购物页面 -----------

def update_item(n,table1,table2,label):
    def clear_all():
        table1.search_data()
        table2.delete_data()
        label.configure(text="合计金额：0")
    if(n==1): # 清空商品信息
        print(table2.chart.get_children())
        if(len(table2.chart.get_children())==0):
            msg('err','提示','没有选择任何信息！')
        else:
            if(messagebox.askokcancel('提示', '确定要清空购物车信息吗？')):  
                clear_all()
    elif(n==2): # 刷新商品信息
        if(len(table2.chart.get_children())==0):
            clear_all()
        elif(messagebox.askokcancel('提示', '刷新会清空购物车信息，确定要继续吗？')):
            clear_all()
    elif(n==3): # 删除部分商品信息
        if(len(table2.chart.selection())==0):
            msg('err','提示','没有选择任何信息！')
        else:
            if(messagebox.askokcancel('提示', '确定要取消订购已选中的商品吗？')):  
                chart1=table1.chart
                chart2=table2.chart
                for i in chart1.get_children(): # 恢复
                    for j in chart2.selection():
                        if(chart1.set(i,"商品编号")==chart2.set(j,"商品编号")):
                            chart1.set(i,"商品存量",int(chart1.set(i,"商品存量"))+int(chart2.set(j,"购买数量")))
                table2.delete_data(1)
                global ans
                ans=0
                for i in chart2.get_children(): 
                    ans+=int(chart2.set(i,"金额小计"))
                label.configure(text="合计金额："+str(ans))

def select_item(table1,table2,label): # 选择商品信息
    chart1=table1.chart
    chart2=table2.chart
    if(len(chart1.selection())==0):
        msg('err','提示','未选择任何信息！')
    elif(len(chart1.selection())>1):
        msg('err','提示','一次只能选择一条信息！')
    elif(int(chart1.set(chart1.selection()[0],"商品存量"))==0):
        msg('err','提示','该商品已售罄！')
    else:
        def add_data(num):
            print('购买数量为：'+str(num))
            def update_sum(): # 计算总金额
                global ans
                ans=0 
                for i in chart2.get_children(): 
                    ans+=int(chart2.set(i,"金额小计"))
                label.configure(text="合计金额："+str("%.1d"%(ans)))

            chart1.set(choice,"商品存量",int(chart1.set(choice,"商品存量"))-num)
            for i in chart2.get_children():
                if(chart1.set(choice,"商品编号")==chart2.set(i,"商品编号")):
                    chart2.set(i,"购买数量",int(chart2.set(i,"购买数量"))+num)
                    chart2.set(i,"金额小计",int(chart2.set(i,"购买数量"))*int(chart1.set(choice,"商品价格")))
                    update_sum()
                    return
            selection=[chart1.set(choice,"商品编号"),chart1.set(choice,"商品名称"),num,num*int(chart1.set(choice,"商品价格"))]
            chart2.insert('',len(chart2.get_children()),values=selection)
            update_sum()
        choice=chart1.selection()[0]
        order(frm,'选择购买数量','购买数量：',int(chart1.set(choice,"商品存量")),add_data)

def finish_item(chart2,label): # 开始结账
    global ans
    the_data=[user_data[1], ans]
    for i in chart2.get_children():
        the_data.append((chart2.set(i,"商品编号"),int(chart2.set(i,"购买数量")),int(chart2.set(i,"金额小计"))))
    print(the_data)
    if(len(chart2.get_children())==0):
        msg('err','提示','未选择任何商品信息！')
    elif(item_deal(the_data)):
        msg('inf',"提示","购买成功！")
        label.configure(text="合计金额：0")
        call_item()
    else:
        msg('err',"提示","订单提交失败，请稍后重试！")
        call_item()


# ------- 商品&票务管理 --------

def new_matchs(table):
    class match_subform(subform):

        def submit_data(self,*event): # 提交数据
            self.get_data() # 刷新数据
            print(self.vars)
            for i in range(7):
                if(self.vars[i]==''):
                    msg('err','提示','信息未填写完整！')
                    self.form.focus_set()
                    return
            if(add_new_match(self.vars[0],self.vars[1].replace('：',':'),self.vars[2],self.vars[3],self.vars[4],self.vars[5],self.vars[6])):
                table.search_data()
                self.exit_form()
            else:
                self.form.focus_set()

    match_subform(frm,'创建新的比赛项目',[('比赛项目','请输入比赛项目',0),('比赛月份','请选择比赛月份',1,list(range(1,13))),('比赛日期','请选择比赛日期',1,list(range(1,32))),('比赛时间','格式HH:MM-HH:MM',0),('门票数量','请输入门票数量',0),('门票单价','请输入门票单价',0),('比赛场馆','请选择比赛场馆',1,get_venue())])

def supply_tickets(table):
    chart=table.chart
    if(len(chart.selection())==0):
        msg('err','提示','未选择任何信息！')
    elif(len(chart.selection())>1):
        msg('err','提示','一次只能选择一条信息！')
    else:
        def add_tickets(n):
            total=int(chart.set(chart.selection()[0],'总门票数'))+n
            remain=int(chart.set(chart.selection()[0],'门票剩余'))+n
            if(supply_ticket(chart.set(chart.selection()[0],'比赛编号'),total,remain)):
                chart.set(chart.selection()[0],'总门票数',total)
                chart.set(chart.selection()[0],'门票剩余',remain)
        
        order(frm,'增加门票数量','增加数量：',99,add_tickets)

def new_items(table):
    class item_subform(subform):

        def submit_data(self,*event): # 提交数据
            self.get_data() # 刷新数据
            print(self.vars[0],self.vars[1],self.vars[2])
            if(add_new_item(self.vars[0],self.vars[1],self.vars[2])):
                table.search_data()
                self.exit_form()
            else:
                self.form.focus_set()

    item_subform(frm,'增加新的商品',[('商品名称','请输入商品名称',0),('商品价格','请输入商品价格',0),('商品存量','请输入现有商品存量',0)])

def supply_items(table):
    chart=table.chart
    if(len(chart.selection())==0):
        msg('err','提示','未选择任何信息！')
    elif(len(chart.selection())>1):
        msg('err','提示','一次只能选择一条信息！')
    else:
        def add_items(n):
            storage=int(chart.set(chart.selection()[0],'商品存量'))+n
            if(supply_item(chart.set(chart.selection()[0],'商品编号'),storage)):
                chart.set(chart.selection()[0],'商品存量',storage)
        
        order(frm,'补充商品数量','补充数量：',99,add_items)

def ticket_summary_data(*arg):
    #coding:utf-8
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False # 用来正常显示负号
    # 有中文出现的情况，需要u'内容'
    data1 = ticket_statistical()
    # data形式为（比赛编号，比赛名称，销量）
    # print(data[0][1])
    name_list1 = []
    sold_list1 = []
    for i in range (0,len(data1)):
        name_list1.append(data1[i][1])
        sold_list1.append(data1[i][2])
    fig1 = plt.bar(range(len(sold_list1)), sold_list1,tick_label = name_list1)
    
    # 添加数据标签 就是矩形上面的数值

    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height+0.01*height, '%.0f'%height, ha='center', va='bottom', fontsize=12, color='black')
            rect.set_edgecolor('black')
    add_labels(fig1)
    plt.title('门票销量统计图')
    plt.show()


def item_summary_data(*arg):
    #coding:utf-8
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False # 用来正常显示负号
    #有中文出现的情况，需要u'内容'
    data2 = item_statistical()
    # data形式为（比赛编号，比赛名称，销量）
    # print(data[0][1])
    name_list2 = []
    sold_list2 = []
    for i in range (0,len(data2)):
        name_list2.append(data2[i][1])
        sold_list2.append(data2[i][2])
    fig2 = plt.bar(range(len(sold_list2)), sold_list2,tick_label = name_list2)
    
    # 添加数据标签 就是矩形上面的数值

    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height+0.01*height, '%.0f'%height, ha='center', va='bottom', fontsize=12, color='black')
            rect.set_edgecolor('black')
    add_labels(fig2)
    plt.title('商品销量统计图')
    plt.show()

# ------- 志愿管理页面 --------

def check_volunteers(n,table1,table2): # 审批志愿者申请
    tmp_flag=True
    chart=table1.chart
    if(len(chart.selection())==0):
        msg('err',"提示","未选择任何申请者！")
    else:
        for i in chart.selection():
            if(approve_volunteer(n,chart.set(i,"用户账号"))):
                tmp_flag=False
                break
    if(tmp_flag):
        table1.delete_data(1)
        table2.search_data(2)
        commit()
    else:
        call_volunteer()

def allocate_assigns(table2,table3): # 分配志愿者任务
    chart2=table2.chart
    chart3=table3.chart
    if(len(chart3.selection())!=1):
        msg('err','提示','请选择一项任务进行分配！')
    elif(len(chart2.selection())==0):
        msg('err','提示','没有选择要分配的志愿者！')
    else:
        tmp_flag=True
        ano=chart3.set(chart3.selection()[0],'任务编号')
        for i in chart2.selection():
            if(allocate_assignment(chart2.set(i,'用户账号'),ano)):
                tmp_flag=False
                break
            else:
                chart2.set(i,"任务编号",ano)
        if(tmp_flag):
            commit()
            msg('inf','提示','分配成功！')
        else:
            call_volunteer() 

def new_assigns(table): # 创建新的志愿任务

    class assign_subform(subform): # 继承

        def submit_data(self,*event): # 提交数据
            self.get_data() # 刷新数据
            print(self.vars[0],self.vars[1])
            if(new_assign(self.vars[0],self.vars[1])):
                table.search_data()
                self.exit_form()
                msg('inf','提示','新建成功！')
            else:
                self.form.focus_set()
    assign_subform(form,'创建志愿任务',[('场馆：','请选择场馆',1,get_venue()),('详情：','请简述任务内容',0)])

def delete_assigns(table2,table3): # 删除志愿者任务
    chart3=table3.chart
    if(len(chart3.selection())==0):
        msg('err','提示','没有选择任何信息！')
        return
    tmp_flag=True
    if(messagebox.askokcancel('提示', '确定要删除该任务吗？相关信息也会被删除')):
        for i in chart3.selection():
            if(delete_assign(chart3.set(i,'任务编号'))):
                tmp_flag=False
                break
        if(tmp_flag):
            table2.search_data(2)
            table3.delete_data(1)
            commit()
            msg('inf','提示','删除成功！')
        else:
            call_volunteer()


# ------------------------- 操作界面子布局 -----------------------------

def call_info(): # 个人信息页面
    clear()
    global frm
    frm=Frame(form)
    form.geometry("480x270")
    power=['群众','群众','志愿者','管理员']

    Label(frm,width=160,height=160,image=user_pic).grid(row=0,column=0,rowspan=5,padx=40)
    for i,txt in enumerate(('账号：','姓名：','性别：','年龄：')):
        Label(frm,text=txt + str(user_data[i+1]),font=('SimHei',16),width=16,anchor=NW).grid(row=i,column=1,pady=3)          
    Label(frm,text="权限："+power[user_data[0]],font=('SimHei',16),width=16,anchor=NW).grid(row=4,column=1,pady=3)
    if(user_data[0]==0 or user_data[0]==1):
        Button(frm,text="申请成为志愿者",width=16,font=('SimHei',14),command=apply_volunteers).grid(row=5,column=0,pady=20)
    elif(user_data[0]==2):
        Button(frm,text="查看志愿任务分配",width=16,font=('SimHei',14),command=show_volunteer).grid(row=5,column=0,pady=20)
    Button(frm,text="退出登录",width=12,font=('SimHei',14),command=lambda:quit_account(form)).grid(row=5,column=1,pady=20)
    frm.pack(padx=20,pady=20)


def call_ticket(): # 票务页面
    clear()
    global frm
    frm=Frame(form)
    form.geometry("850x400")
    heads1=[('比赛编号','比赛项目','比赛时间','门票剩余','门票价格','比赛地点'),(0,60,140,260,320,380,500)]
    heads2=[('比赛编号','比赛项目','购票数量','金额小计'),(0,60,140,200,270)]
    t_table1=table(frm,12,heads1,ticket_info)
    t_table2=table(frm,8,heads2,lambda:())
    l_sum=Label(frm,text="合计金额：0",font=('SimHei',12))

    t_table1.son.grid(row=1,column=0,rowspan=3,columnspan=2,pady=5)
    t_table2.son.grid(row=1,column=3,columnspan=2,pady=5)
    l_sum.grid(row=2,column=3,pady=3)
    Label(frm,text="票务信息",font=('SimHei',16)).grid(row=0,column=0,columnspan=2)
    Label(frm,text="购物车",font=('SimHei',16)).grid(row=0,column=3,columnspan=3)
    Button(frm,text="确定购票",width=12,font=('SimHei',12),command=lambda:finish_ticket(t_table2.chart,l_sum)).grid(row=2,column=4,pady=3)
    Button(frm,text="清除选择",width=12,font=('SimHei',12),command=lambda:update_ticket(1,t_table1,t_table2,l_sum)).grid(row=3,column=4,pady=5)
    Button(frm,text="刷新票务信息",width=12,font=('SimHei',12),command=lambda:update_ticket(2,t_table1,t_table2,l_sum)).grid(row=4,column=0,pady=10)
    Button(frm,text="取消选择",width=12,font=('SimHei',12),command=lambda:update_ticket(3,t_table1,t_table2,l_sum)).grid(row=3,column=3,pady=5)
    Button(frm,text="加入购物车",width=12,font=('SimHei',12),command=lambda:select_ticket(t_table1,t_table2,l_sum)).grid(row=4,column=1,pady=10)
    Button(frm,text="查看订票历史",width=12,font=('SimHei',12),command=lambda:deal_detail(form,1)).grid(row=4,column=3,columnspan=2,pady=10)
    # t_table1.chart.bind('<Double-1>',lambda event:select_data(t_table1,t_table2,l_sum)) # 双击加入购物车
    # t_table2.chart.bind('<Double-1>',lambda event:update_ticket(3,t_table1,t_table2,l_sum)) # 双击清出购物车
    t_table1.search_data() # 初始化票务信息
    frm.pack(padx=20,pady=20)


def call_item(): # 商品页面
    clear()
    global frm
    frm=Frame(form)
    form.geometry("730x400")
    heads1=[('商品编号','商品名称','商品价格','商品存量'),(0,60,160,240,320)]
    heads2=[('商品编号','商品名称','购买数量','金额小计'),(0,60,160,240,320)]
    t_table1=table(frm,12,heads1,item_info)
    t_table2=table(frm,8,heads2,lambda:())
    l_sum=Label(frm,text="合计金额：0",font=('SimHei',12))

    t_table1.son.grid(row=1,column=0,rowspan=3,columnspan=2,pady=5)
    t_table2.son.grid(row=1,column=3,columnspan=2,pady=5)
    l_sum.grid(row=2,column=3,pady=3)
    Label(frm,text="商品信息",font=('SimHei',16)).grid(row=0,column=0,columnspan=2)
    Label(frm,text="购物车",font=('SimHei',16)).grid(row=0,column=3,columnspan=3)
    Button(frm,text="确定购买",width=12,font=('SimHei',12),command=lambda:finish_item(t_table2.chart,l_sum)).grid(row=2,column=4,pady=3)
    Button(frm,text="清除选择",width=12,font=('SimHei',12),command=lambda:update_item(1,t_table1,t_table2,l_sum)).grid(row=3,column=4,pady=5)
    Button(frm,text="刷新商品信息",width=12,font=('SimHei',12),command=lambda:update_item(2,t_table1,t_table2,l_sum)).grid(row=4,column=0,pady=10)
    Button(frm,text="取消选择",width=12,font=('SimHei',12),command=lambda:update_item(3,t_table1,t_table2,l_sum)).grid(row=3,column=3,pady=5)
    Button(frm,text="加入购物车",width=12,font=('SimHei',12),command=lambda:select_item(t_table1,t_table2,l_sum)).grid(row=4,column=1,pady=10)
    Button(frm,text="查看购物历史",width=12,font=('SimHei',12),command=lambda:deal_detail(form,2)).grid(row=4,column=3,columnspan=2,pady=10)
    # t_table1.chart.bind('<Double-1>',lambda event:select_data(t_table1,t_table2,l_sum)) # 双击加入购物车
    # t_table2.chart.bind('<Double-1>',lambda event:update_ticket(3,t_table1,t_table2,l_sum)) # 双击清出购物车
    t_table1.search_data() # 初始化票务信息
    frm.pack(padx=20,pady=20)


def call_manager(): # 票务&商品管理页面
    clear()
    global frm
    frm=Frame(form)
    form.geometry("930x400")
    heads1=[('比赛编号','比赛项目','比赛时间','总门票数','门票剩余','门票价格','比赛地点'),(0,60,160,280,340,400,460,580)]
    heads2=[('商品编号','商品名称','商品价格','商品存量'),(0,60,160,220,280)]
    t_table1=table(frm,12,heads1,match_info)
    t_table2=table(frm,12,heads2,item_info)

    t_table1.son.grid(row=1,column=0,columnspan=2,pady=5)
    t_table2.son.grid(row=1,column=4,columnspan=2,pady=5)
    Label(frm,text="赛事信息",font=('SimHei',16)).grid(row=0,column=0)
    Label(frm,text="商品信息",font=('SimHei',16)).grid(row=0,column=4)
    Button(frm,text="门票统计信息",width=12,font=('SimHei',12),command=ticket_summary_data).grid(row=0,column=1)
    Button(frm,text="商品统计信息",width=12,font=('SimHei',12),command=item_summary_data).grid(row=0,column=5)
    Button(frm,text="新建赛事",width=12,font=('SimHei',12),command=lambda:new_matchs(t_table1)).grid(row=2,column=0,pady=5)
    Button(frm,text="补充门票",width=12,font=('SimHei',12),command=lambda:supply_tickets(t_table1)).grid(row=2,column=1,pady=5)
    Button(frm,text="新建商品",width=12,font=('SimHei',12),command=lambda:new_items(t_table2)).grid(row=2,column=4,pady=5)
    Button(frm,text="补充商品",width=12,font=('SimHei',12),command=lambda:supply_items(t_table2)).grid(row=2,column=5,pady=5)
    # t_table1.chart.bind('<Double-1>',lambda event:supply_tickets(t_table1)) # 双击补充门票
    # t_table2.chart.bind('<Double-1>',lambda event:supply_items(t_table2)) # 双击补充物品
    t_table1.search_data() # 初始化票务信息
    t_table2.search_data() # 初始化票务信息
    frm.pack(padx=20,pady=20)


def call_volunteer(): # 志愿管理页面
    clear()
    global frm
    frm=Frame(form)
    form.geometry("800x400")
    heads1=[('用户账号','用户姓名'),(0,80,200)]
    heads2=[('用户账号','用户姓名','任务编号'),(0,80,160,240)]
    heads3=[('任务编号','任务地点','任务详情'),(0,80,160,260)]
    t_table1=table(frm,12,heads1,lambda n:volunteer_list(n))
    t_table2=table(frm,12,heads2,lambda n:volunteer_list(n))
    t_table3=table(frm,12,heads3,assignment_list)

    t_table1.son.grid(row=1,column=0,columnspan=2,pady=5)
    t_table2.son.grid(row=1,column=4,pady=5)
    t_table3.son.grid(row=1,column=7,columnspan=2,pady=5)
    Label(frm,text="申请人信息",font=('SimHei',16)).grid(row=0,column=0,columnspan=3)
    Label(frm,text="志愿者信息",font=('SimHei',16)).grid(row=0,column=4,columnspan=2)
    Label(frm,text="志愿任务信息",font=('SimHei',16)).grid(row=0,column=6,columnspan=3)
    Button(frm,text="审批通过",width=10,font=('SimHei',12),command=lambda:check_volunteers(2,t_table1,t_table2)).grid(row=2,column=0,pady=5)
    Button(frm,text="审批拒绝",width=10,font=('SimHei',12),command=lambda:check_volunteers(0,t_table1,t_table2)).grid(row=2,column=1,pady=5)
    Button(frm,text="分配任务",width=10,font=('SimHei',12),command=lambda:allocate_assigns(t_table2,t_table3)).grid(row=2,column=4,pady=5)
    Button(frm,text="新建任务",width=10,font=('SimHei',12),command=lambda:new_assigns(t_table3)).grid(row=2,column=7,pady=5)
    Button(frm,text="删除任务",width=10,font=('SimHei',12),command=lambda:delete_assigns(t_table2,t_table3)).grid(row=2,column=8,pady=5)
    t_table1.search_data(1)
    t_table2.search_data(2)
    t_table3.search_data()
    frm.pack(padx=20,pady=20)


# ------------------------- 操作界面主布局 -----------------------------

if(user_data[0]>=0):
    form=Tk()
    form.title("北京冬奥会信息管理系统：操作界面")
    form.geometry("480x280"+"+"+str((screen_x-600)//2)+"+"+str((screen_y-330)//2))
    form.resizable(width=False, height=False)

    frm=Frame(form) # 页面框架
    option=Menu(form) # 菜单栏
    user_pic=tkinter.PhotoImage(file="figures/user.gif") # 用户照片
    option.add_command(label =" 个人信息 ",command=call_info)
    if(user_data[0]!=3):
        option.add_command(label =" 订票服务 ",command=call_ticket)
        option.add_command(label =" 购买商品 ",command=call_item)
    else:
        option.add_command(label =" 志愿管理 ",command=call_volunteer)
        option.add_command(label =" 票务&商品管理 ",command=call_manager)
    form.config(menu=option)

    call_info()
    form.mainloop()

finish(flag) # 结束数据库连接