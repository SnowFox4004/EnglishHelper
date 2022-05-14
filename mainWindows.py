from myClasses import *
import init
import sys
from datetime import datetime

print('sys.argvL:', sys.argv)
my_path = sys.argv[0].split('\\')
if len(my_path) == 1:
    my_path = my_path[0].split('/')

my_path = my_path[:-1]
MY_PATH = ''
for i in my_path:
    MY_PATH += i + '\\'
MY_PATH = MY_PATH[:-1]
if MY_PATH == '':
    MY_PATH = '.'
    print('本程序路径空')
load = None
flag = False
if len(sys.argv) >= 2:
    try:
        load = {}
        for i in range(1, len(sys.argv)):
            ev = open(sys.argv[i], 'r', encoding='utf-8').read()
            try:
                load.update(eval(ev))
            except:
                pass
    except Exception as err:
        print(err)


else:
    load = None
init.StartPlatinum(MY_PATH, 'fine')
win = myWindow(MY_PATH)
if not load is None:
    try:
        win.UpdateAll(load)
    except Exception as err:
        print(err)
        x = input()
win.win.mainloop()
print('本程序路径：', MY_PATH)
filename = fr"{MY_PATH}\errors\{str(datetime.now()).replace('.', '').replace(' ', '').replace(':', '')}"
print('错误日志文件名：', filename)
if len(win.tsl.logs['error']) > 0:
    open(filename + '.log', 'w+').write(filename.split('\\')[-1] + '\n' + str(win.tsl.logs['error']))
print('---程序结束---')
