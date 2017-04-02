#coding=utf-8
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox

import os
import proc
import threading
import time
import traceback

from utils import holy_open

tk=Tk()
tk.title('vm01 - xm01 Visualizer')
tk.rowconfigure(0,weight=1)
tk.columnconfigure(2,weight=1)
tk.geometry('900x600')

fnvar=StringVar(value='选择文件……')
reloadvar=StringVar(value='on')
birthvar=StringVar(value='on')
msg=StringVar(value='就绪')

GAME01_TAGS={
    '-1': 'comment',
    '0': 'wally',
    '1': 'wallx',
    '3': 'shop',
    '4': 'birthplace',
}
walls=[]
birthplaces=[]
shops=[]
zoomrate=2.
item_ids={}

def _load_file(fn):
    with holy_open(fn) as f:
        if fn.endswith('.map.txt'):
            lines=proc.parse(f.read())
        else:
            lines=f.read()

    text.config({'state':'normal'})
    text.delete('1.0',END)
    walls.clear()
    birthplaces.clear()
    shops.clear()

    title,_,lines=lines.partition('\n')
    text.insert(END,' %s\n'%title,'title')

    for num,line in enumerate(lines.split('\n')):
        cmd,_,args=line.lstrip().partition(' ')
        tag=GAME01_TAGS.get(cmd,'useless')
        text.insert(END,' %s %s\n'%(cmd,args),tag)
        num+=2

        if tag=='wallx':
            l,r,y=args.split(' ')
            walls.append([num,int(l),-int(y),int(r),-int(y)])
        elif tag=='wally':
            l,r,x=args.split(' ')
            walls.append([num,int(x),-int(l),int(x),-int(r)])
        elif tag=='shop':
            x,y=args.split(' ')
            shops.append([num,int(x),-int(y)])
        elif tag=='birthplace':
            x,y=args.split(' ')
            birthplaces.append([num,int(x),-int(y)])

    text.config({'state':'disabled'})

last_path=os.path.expanduser('~/desktop')
last_filename=''
def select_file():
    global last_path
    global last_filename
    fn=filedialog.askopenfilename(
        title='打开地图...',
        filetypes=[('xm01 地图源文件','*.map.txt'),('Game01 地图', '*.dat')],
        initialdir=last_path,
    )
    if fn and os.path.isfile(fn):
        try:
            _load_file(fn)
            last_path=os.path.split(fn)[0]
            last_filename=fn
            fnvar.set(os.path.basename(fn))
            render(zoomrate)
        except Exception as e:
            messagebox.showerror('加载失败','%s\n\n%s'%(type(e),e))
            raise

def file_watcher():
    last_mod=None
    while True:
        if reloadvar.get()=='on' and os.path.isfile(last_filename):
            this_mod=os.stat(last_filename).st_mtime
            if this_mod!=last_mod:
                last_mod=this_mod
                try:
                    _load_file(last_filename)
                    render(zoomrate)
                except Exception as e:
                    messagebox.showerror('加载失败', '%s\n\n%s' % (type(e), e))
                    traceback.print_exc()
            time.sleep(.2)

def zoom(a,b,c,d):
    return a/zoomrate,b/zoomrate,c/zoomrate,d/zoomrate

def render(ratio):
    ratio=float(ratio)
    canvas.delete('item')
    canvas.delete('wall')
    item_ids.clear()

    if not walls:
        return #messagebox.showerror('渲染失败','地图缺少墙壁')

    ys=[x[2] for x in walls]+[x[4] for x in walls]+[x[2] for x in birthplaces]+[x[2] for x in shops]
    xs=[x[1] for x in walls]+[x[3] for x in walls]+[x[1] for x in birthplaces]+[x[1] for x in shops]
    xmin=min(xs)-100
    xmax=max(xs)+100
    ymin=min(ys)-50
    ymax=max(ys)+50
    global zoomrate
    zoomrate=ratio

    canvas.create_rectangle(*zoom(xmin,ymin,xmax,ymax),fill='white',outline='white',tags='item')
    canvas['scrollregion']=zoom(xmin,ymin,xmax,ymax)

    for num,x,y in shops:
        cid=canvas.create_rectangle(*zoom(x-50,y-75,x+50,y),fill='#aaaaff',outline='#aaaaff',tags='item')
        item_ids[num]=cid
    if birthvar.get()=='on':
        for num,x,y in birthplaces:
            cid=canvas.create_oval(*zoom(x-3*ratio,y-3*ratio,x+3*ratio,y+3*ratio),fill='#ffff00',tags='item')
            item_ids[num]=cid
    for num,x1,y1,x2,y2 in walls:
        cid=canvas.create_line(*zoom(x1,y1,x2,y2),tags='wall')
        item_ids[num]=cid

    canvas.lift('item')
    canvas.lift('wall')
    update_pos()

textf=Frame(tk)
textf.grid(row=0,column=0,columnspan=2,sticky='nswe')
textf.rowconfigure(0,weight=1)

text=Text(textf,font='consolas -14',width=25,state=['disabled'],wrap='none')
text.grid(row=0,column=0,sticky='ns')
sbar_text=Scrollbar(textf,orient=VERTICAL,command=text.yview)
text.configure(yscrollcommand=sbar_text.set)
sbar_text.grid(row=0,column=1,sticky='ns')

fill_bkp={}
def update_highlight(event):
    for k,v in fill_bkp.items():
        canvas.itemconfigure(k,fill=v,width=1)
    fill_bkp.clear()

    ranges=[int(x.string.partition('.')[0]) for x in text.tag_ranges('sel')]
    if ranges:
        begin,end=ranges
        for i in range(begin,end+1):
            if i in item_ids:
                fill_bkp[item_ids[i]]=canvas.itemcget(item_ids[i],'fill')
                canvas.itemconfigure(item_ids[i],fill='blue',width=3)

text.bind('<<Selection>>',update_highlight)

text.tag_config('title',foreground='white',background='blue',font='黑体')
text.tag_config('comment',foreground='black',background='yellow')
text.tag_config('wallx',foreground='blue')
text.tag_config('wally',foreground='red')
text.tag_config('shop',foreground='#880088')
text.tag_config('birthplace',foreground='#777700')
text.tag_config('useless',foreground='#aaaaaa')

text.tag_config('sel',foreground='white')
text.tag_raise('sel')

Button(tk,textvariable=fnvar,command=select_file).grid(row=1,column=0,sticky='we')
Checkbutton(tk,text='监视更改',variable=reloadvar,onvalue='on',offvalue='off').grid(row=1,column=1)

canvasf=Frame(tk)
canvasf.grid(row=0,column=2,sticky='nswe')
canvasf.rowconfigure(0,weight=1)
canvasf.columnconfigure(0,weight=1)

sbar_canvasy=Scrollbar(canvasf,orient=HORIZONTAL)
sbar_canvasx=Scrollbar(canvasf,orient=VERTICAL)
canvas=Canvas(canvasf,yscrollcommand=sbar_canvasx.set,xscrollcommand=sbar_canvasy.set,xscrollincrement='1',yscrollincrement='1')
#canvas.configure(background='#ffffff')
sbar_canvasy['command']=canvas.xview
sbar_canvasx['command']=canvas.yview
canvas.grid(column=0,row=0,sticky='nswe')
sbar_canvasy.grid(column=0,row=1,sticky='we')
sbar_canvasx.grid(column=1,row=0,sticky='ns')

def canvas_startmove(event):
    global movex
    global movey
    movex,movey=event.x,event.y

def canvas_moving(event):
    global movex
    global movey
    canvas.xview_scroll(movex-event.x,'units')
    canvas.yview_scroll(movey-event.y,'units')
    movex,movey=event.x,event.y

def update_pos(event=None):
    if event is None:
        x,y=0,0
    else:
        x=canvas.canvasx(event.x)*zoomrate
        y=canvas.canvasy(event.y)*zoomrate
    msg.set('Zoom = %.2f / X = %d / Y = %d'%(zoomrate,x,-y))

movex,movey=0,0
canvas.bind('<Button-1>',canvas_startmove)
canvas.bind('<B1-Motion>',canvas_moving)
canvas.bind('<Motion>',update_pos)

cmdf=Frame(tk)
cmdf.grid(row=1,column=2,sticky='we')
cmdf.columnconfigure(0,weight=1)

Label(cmdf,textvariable=msg).grid(row=0,column=0,sticky='we')
Checkbutton(cmdf,text='显示出生点',variable=birthvar,onvalue='on',offvalue='off',command=lambda:render(zoomrate))\
    .grid(row=0,column=1)
zoomscale=Scale(cmdf,length=100,from_=8,to=1,value=2,command=render)
zoomscale.grid(row=0,column=2)

threading.Thread(target=file_watcher,daemon=True).start()
mainloop()