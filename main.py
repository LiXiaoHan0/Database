from tkinter import *
from oracle import *
from tkinter import ttk # 树状表格

# 全局变量
flag=0 # 连接情况
power=0 # 权限等级
alter=0 # 是否修改
root=Tk() # 根窗口
screen_x=root.winfo_screenwidth() # 屏幕宽度
screen_y=root.winfo_screenheight() # 屏幕高度

# ------------------------- 全局类 -----------------------------
#我改了一下
#123123
class subform: # 输入框界面

    def __init__(self,father,title,que,submit): # 父容器，标题，标签及默认值
        l=len(que)
        self.submit_data=submit

        form=Toplevel(father)
        form.title(title)
        form.geometry("300x"+str(45*(l+1))+"+"+str((screen_x-300)//2)+"+"+str((screen_y-45*(l+1))//2))
        form.resizable(width=False, height=False)

        frm=Frame(form)
        str_v=[StringVar() for i in range(l)]
        str_e=[Entry(frm,fg='#A9A9A9',textvariable=str_v[i]) for i in range(l)]
        bool_e=[True for i in range(l)]
        
        self.flag=bool_e
        self.form=form
        self.edit=str_e

        def press_key(event,index):
            if(event.keycode==38): self.first_edit(event,(index-1)%l)
            elif(event.keycode==40): self.first_edit(event,(index+1)%l)
        
        for i,txt in enumerate(que):
            Label(frm,text=txt[0],font=('Arial',12)).grid(row=i, column=0,columnspan=2)
        for i,e in enumerate(str_e):
            e.insert(0,que[i][1]) # 默认值
            e.bind('<Button-1>',lambda event,_i=i:self.first_edit(event,_i)) # 初次编辑判定
            e.bind('<Return>',self.submit_data) # 绑定回车键
            e.bind('<Key>',lambda event,_i=i:press_key(event,_i+l)) # 绑定上下键
            e.grid(row=i,column=3,padx=5,pady=10,columnspan=4)
        Button(frm,width=8,text="退出",font=('Arial',12),command=self.exit_form).grid(row=l,column=1,pady=10,columnspan=2)
        Button(frm,width=8,text="提交",font=('Arial',12),command=self.submit_data).grid(row=l,column=5,pady=10)

        frm.pack()
        form.mainloop()

    def first_edit(self,event,index):
        if(self.flag[index]):
            self.edit[index].config(fg='#000000')
            self.edit[index].delete(0,END)
            self.flag[index]=False
        if(not self.edit[index].select_present()): self.edit[index].focus_set()

    def exit_form(self):
        self.form.destroy()


class table: # 自定义表格

    def __init__(self,father,num,heads,search,modify=False): # 初始化
        self.data=[]
        self.far=father
        self.heads=heads
        self.modify=modify
        self.search=search
        self.ybar=Scrollbar(father,orient='vertical')
        self.chart=ttk.Treeview(father,height=num,show="headings",columns=heads[0],yscrollcommand=self.ybar.set)
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
        if(self.modify):
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
    pass
    # global power
    # power=login_check(l_e1.get(),l_e2.get())
    # if(power!=0): login.destroy()


def sign_in(): # 注册界面

    class sign_subform(subform): # 继承

        def submit_data(self,*event):
            pass
            # edits=[self.edit[i].get() for i in range(3)]

            # if(inspect('' if self.flag[0] else edits[0],'str',0,1,15)): 
            #     self.first_edit(event,0)
            #     return
            # if(inspect('' if self.flag[1] else edits[1],'str',0,5,15)): 
            #     self.first_edit(event,1)
            #     return
            # if(inspect('' if self.flag[2] else edits[2],'str',0,5,15)): 
            #     self.first_edit(event,2)
            #     return

            # ans=signin(edits[0],edits[1],edits[2])
            # if(ans[0]):
            #     self.form.destroy()
            # else:
            #     self.edit[ans[1]].focus_set()

    sign_subform(login,'新用户注册',[('姓名：','请输入您的姓名'),('年龄：','请输入您的年龄'),('性别：','男/女'),('密码：','请设置登录密码'),('确认密码：','请再次输入密码')])


# ------------------------- 登录界面布局 -----------------------------

login=root
login.title("北京冬奥会信息管理系统")
login.geometry("450x250+"+str((screen_x-360)//2)+"+"+str((screen_y-200)//2))
login.resizable(width=False, height=False)

l_frm=Frame(login)
l_v1=StringVar()
l_v2=StringVar()

import tkinter # 引入图片
pic=tkinter.PhotoImage(file="dream.gif")

Label(l_frm,width=150,height=180,image=pic).grid(row=1,column=0,columnspan=2,rowspan=3,padx=5,pady=10)
Label(l_frm, text='账号：',font=('Arial',15)).grid(row=1, column=2,columnspan=2)
Label(l_frm, text='密码：',font=('Arial',15)).grid(row=2, column=2,columnspan=2)
l_e1=Entry(l_frm,font=('Arial',15),width=15,textvariable=l_v1)
l_e2=Entry(l_frm,font=('Arial',15),width=15,textvariable=l_v2,show='*')

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
Button(l_frm,text="登录",width=6,font=('Arial',15),command=check_login).grid(row=3,column=2,columnspan=3,pady=15,padx=5)
Button(l_frm,text="注册",width=6,font=('Arial',15),command=sign_in).grid(row=3,column=5,columnspan=2,pady=15,padx=5)
l_frm.pack(padx=20,pady=20)

# 设置程序图标
# login.iconbitmap(default="pic\homework.ico")

flag=connect() # 连接数据库
if(flag):login.mainloop()