import ttkbootstrap as ttk
# import tkinter.tk as ottk
import tkinter as tk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import Radiobutton
from tkinter import messagebox

from translater import get_translate, get_translate2, get_voice2
import random as rnd
import pyttsx3 as tts
import WordCloudMaker
import Dependencies
from datetime import datetime
from Output_Maker import *
import os
import xlwt
from playsound import playsound

import easygui as g


def Make_Sheet(data, filename, GLOBAL_PATH):
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('Sheet1')
    col = 0
    for k, v in data.items():
        sheet.write(0, col, label=k)
        for i in range(len(v)):
            sheet.write(i + 1, col, label=v[i])
        col += 1
    wb.save(r"{0}\excels\{1}.xls".format(GLOBAL_PATH, filename))


def better_length(x):
    if len(x) < 25:
        return x
    else:
        ret = ''
        for i in range(len(x)):
            if i % 25 == 0 and i > 1:
                ret += '\n'
            ret += x[i]
    return ret


class myWindow():
    def __init__(self, program_path):
        self.icon_path = f'{program_path}/Star_Transparent.ico'

        self.lastsave = '暂无'
        self.askFlag = False
        self.global_path = program_path

        self.win = ttk.Window(themename='litera')
        # self.win = tk.Tk()
        self.win.title('生词查询 & 记忆')
        # self.win.resizable(0, 0)
        self.win.iconbitmap(self.icon_path)
        # self.win.geometry('1672x1320')

        self.style = ttk.Style()
        # self.style.configure('lefttab.TNotebook', tabposition='wn', bootstyle='success')
        # self.style.configure('TNotebook', tabposition='wn')
        # self.notebook = tk.Notebook(self.win, style='TNotebook-info', width=500,height=500)

        self.notebook = ttk.Notebook(self.win, style='warning', width=500, height=500, )
        self.Separator = ttk.Separator(self.win, orient=VERTICAL, bootstyle='default')

        self.tsl = translating(self)
        self.Frame1 = self.tsl.fm

        self.rmb = remember(self.tsl.EnglishWords, self)
        self.wrt = writing(self.tsl.EnglishWords, self)
        self.data = Datas(self.rmb, self.tsl, self.wrt)
        self.Menu = myMenu(self)

        # self.notebook.add(self.tsl.fm, text='英文翻译')
        self.notebook.add(self.rmb.fm, text='单词速记', )
        self.notebook.add(self.wrt.fm, text='单词默写', )
        self.notebook.add(self.data.fm, text='正确率', )

        self.Frame1.pack(side=LEFT, padx=10, pady=3, anchor='nw')
        self.Separator.pack(side=LEFT, fill=Y, pady=5)
        self.notebook.pack(padx=10, pady=3, fill=BOTH, expand=True)

        self.updateForrmb(self.tsl.EnglishWords)
        self.win.config(menu=self.Menu.menu)

        self.win.protocol('WM_DELETE_WINDOW', self.askQuit)

        # self.winfo()

    def winfo(self):
        print(self.win.winfo_height(), self.win.winfo_width())
        self.win.after(1000, self.winfo)

    def askQuit(self):
        if self.askFlag:
            ask = messagebox.askyesno(title='退出', message='您是否要退出', default='no', detail=f'上次保存时间:{self.lastsave}')
            if ask is True:
                self.win.destroy()
            elif ask is False:
                pass
        else:
            self.win.destroy()

    def updateForrmb(self, EnglishWords):
        self.rmb.EnglishWord = EnglishWords

    def UpdateAll(self, EnglishWords: dict):
        self.rmb.EnglishWord.update(EnglishWords)
        self.tsl.EnglishWords.update(EnglishWords)
        self.wrt.Englishword.update(EnglishWords)
        messagebox.showinfo('更新成功', '词库已刷新')


class translating():
    def __init__(self, fatherwin):
        self.fm = ttk.Frame()
        self.frame1 = ttk.Frame(self.fm)
        self.entry1 = ttk.Entry(self.frame1, width=20)
        self.btn1 = ttk.Button(self.frame1, text='翻译', command=self.translate, width=5, bootstyle='link-danger')
        self.btn2 = ttk.Button(self.frame1, text='朗读', command=self.speak, bootstyle='outline')
        self.txt = ttk.Text(self.frame1, height=40, width=35)
        self.scroll = ttk.Scrollbar(self.frame1)
        self.txtvar = ttk.StringVar()

        self.scroll.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.scroll.set)
        self.entry1.bind('<Return>', self.translate)

        self.frame1.pack()
        self.entry1.grid(row=0, column=0, padx=10)
        self.btn1.grid(row=0, column=1)
        self.btn2.grid(row=0, column=2)
        self.txt.grid(row=1, column=0, columnspan=3, sticky=(N, S))
        self.scroll.grid(row=1, column=3, sticky='ns')

        self.logs = {'error': []}
        self.EnglishWords = {}
        self.fatherwin = fatherwin
        self.lasttrans = None
        # self.colorlist=self.fatherwin.win.style.colors

    def speak(self):
        content = self.entry1.get()
        if content == '':
            messagebox.showerror('朗读内容为空', '请输入需朗读的内容')
        else:
            try:
                filename = get_voice2(content)
                if filename == '-1':
                    raise Exception('没有网')
                print(self.fatherwin.global_path.replace('\\', '/') + filename.replace('./', '/'))
                playsound(self.fatherwin.global_path.replace('\\', '/') + filename.replace('./', '/'))
                # os.startfile(get_voice2(content).replace('/', '\\'))
            except Exception as err:
                print(type(err), err)
                tts.speak(content)

    def clean(self, lst, format=tuple):
        copy_lst = list(lst).copy()
        copy_lst = [i.replace('\n', '').strip() for i in copy_lst if i]
        copy_lst = [i for i in copy_lst if i]
        copy_lst = set(copy_lst)
        return format(copy_lst)

    def updateWords(self, result):
        rtype = result['type']
        try:
            rtype = rtype.split('2')

            zindex = rtype.index('zh-CHS')
            key = result['translateResult'][0][0]['tgt']
            value = result['translateResult'][0][0]['src']
            # 此处 value是输入 key是返回

            if zindex == 0:
                # 中文翻译为其他
                try:
                    entries = result["smartResult"]['entries']
                    entries = [i.replace('\r', '').replace('\n', '') for i in entries if i]
                    key = tuple(entries + [key])
                except Exception as err:
                    self.logs['error'].append(str(type(err)) + str(err))
                if type(key) != tuple:
                    pass
                    # self.EnglishWords.update({(key,): [value]})
                else:
                    # print({key,value})
                    key = (i for i in key if i)
                    key = tuple(key)
                    # self.EnglishWords.update({key: [value]})
            else:
                # 其他翻译为中文
                key, value = value, key
                try:
                    entries = result["smartResult"]['entries']
                    entries = [i.replace('\r', '').replace('\n', '') for i in entries if i]
                    value = entries + [value]
                except Exception as err:
                    self.logs['error'].append(str(type(err)) + str(err))
                if type(value) != list:
                    value = [value]
                # self.EnglishWords.update({(key,): value})

        except Exception as err:

            self.logs['error'].append(str(type(err)) + str(err))
            key = result['translateResult'][0][0]['tgt']
            value = result['translateResult'][0][0]['src']
            # self.EnglishWords.setdefault(key, [])
            # self.EnglishWords[key].append(value)

            pass
        print(key)
        if type(key) == str:
            key = (key,)
        else:
            key = tuple(key)
        if type(value) == str:
            value = [value]
        elif type(value) == tuple:
            value = list(value)
        value = self.clean(value, list)
        sml = self.findsimilar(key, value)
        if sml[0]:
            new_key = self.clean(list(key) + list(sml[1]), tuple)
            ori = self.EnglishWords.pop(sml[1])
            self.EnglishWords[new_key] = value + ori
            self.EnglishWords[new_key] = self.clean(self.EnglishWords[new_key], list)
        else:
            key = self.clean(key, tuple)
            self.EnglishWords.update({key: value})
        self.fatherwin.updateForrmb(self.EnglishWords)

    def findsimilar(self, key, value):
        for k in self.EnglishWords.keys():
            if key[0] in k:
                return True, k
        return False, None

    def translate(self, *args):
        self.TransType = 1
        # print(*args)
        if self.entry1.get() == self.lasttrans:
            return False
        self.lasttrans = self.entry1.get()

        if self.TransType == 2:
            result = get_translate2(self.entry1.get())
        elif self.TransType == 1:
            result = get_translate(self.entry1.get())
        result = eval(result)
        if result['errorCode'] == -1:
            self.txt.insert(END, '网络错误，请检查网络状况\n')
            return False
        elif result['errorCode'] == -2:
            self.txt.insert(END, '别用中文啊\n')
            return False
        elif result['errorCode'] == 40:
            self.txt.delete('1.0', END)
            self.txt.insert(END, self.entry1.get())
            return False

        if result['errorCode'] != 0:
            return False
        ret = result["translateResult"][0][0]['tgt'] + '\n'
        self.updateWords(result)
        try:
            entries = result["smartResult"]['entries']
            ret += '其他意义: \n'
            if self.TransType == 2:
                entries = entries
            # print(entries)
            for i in entries:
                # print(i)
                if i:
                    ret += i.replace('；', ' / ').replace('\n', ' ').replace('\t', '') + '\n'
        except BaseException as err:
            self.logs['error'].append(str(type(err)) + ' ' + str(err))
        self.logs[self.entry1.get()] = result

        self.txt.delete('1.0', END)
        self.txt.insert('1.0', ret)

        return ret


class remember():
    def __init__(self, EnglishWords, Father):
        self.Father = Father

        self.fm = ttk.Frame(width=1200)
        if True:
            # 左半边布局
            self.leftFrame = ttk.Frame(self.fm, height=1000, width=600)
            self.frame1 = ttk.LabelFrame(self.leftFrame, text='请根据中文释义选取正确的英文单词')
            self.Label1 = ttk.Label(self.frame1, text='')

            self.frame2 = ttk.LabelFrame(self.leftFrame, text='请选择')
            self.choice = ttk.IntVar()
            self.RadioB = [Radiobutton(self.frame2, variable=self.choice, text=f'选项{i}', value=i, anchor='center') for i
                           in \
                           range(4)]

            self.default_color = self.RadioB[0]['bg']
            for i in self.RadioB:
                i.pack(pady=20, fill=X)
            self.submitButton = ttk.Button(self.frame2, text='开始', command=self.start)

            self.submitButton.pack(padx=10)
            self.frame1.pack(side=TOP, fill=X, )
            self.frame2.pack(side=TOP, fill=BOTH, expand=True)
            self.Label1.pack()
            self.leftFrame.pack(side=LEFT, fill=BOTH, expand=True)

            # self.leftFrame.pack_propagate(0)
        # if True:
        #     # 右半边布局
        #     self.rightFrame = tk.LabelFrame(self.fm, height=1000, width=600)
        #     self.rframe1 = tk.Frame(self.rightFrame)
        #     self.Labels = [tk.Label(self.rightFrame, text=f'解析{i}', anchor='center') for i in range(4)]
        #
        #     for i in self.Labels:
        #         i.pack(pady=20, fill=X, anchor='center', side=BOTTOM)
        #     self.rframe1.pack(fill=BOTH, expand=True)
        #     self.rightFrame.pack(side=RIGHT, fill=Y)
        #
        #     self.rightFrame.pack_propagate(0)
        self.EnglishWord = EnglishWords

        self.All = 0
        self.right = 0
        self.wrongs = []

    def submit(self):
        self.All += 1
        choose = self.choice.get()
        self.Answers = [self.find_English(i) for i in self.ChooseText]
        print(self.Answers)
        for i in range(len(self.Answers)):
            tempString='\n'.join(self.Answers[i])
            self.Answers[i]=tempString

        for i in range(len(self.Answers)):
            Dependencies.Create_tips(self.RadioB[i], self.Answers[i])
        for i in range(len(self.RadioB)):
            if i == self.answer:
                self.RadioB[i].config(bg='lightgreen')
            else:
                self.RadioB[i].config(fg='red')
        if choose == self.answer:
            self.right += 1
            self.Label1.config(text=self.Label1['text'] + '\n恭喜你答对了！')
            playsound(r'C:\Windows\Media\Windows Proximity Notification.wav')
            print('对了')

        else:
            self.wrongs.append(self.question[0])
            self.Label1.config(text=self.Label1['text']+'\n很遗憾答错了可以将鼠标移动到选项上查看解析')
            playsound(r'C:\Windows\Media\Windows Critical Stop.wav')
            print('错了')
        self.submitButton.config(command=self.start, text='下一题')
        self.Father.data.Update()

    def findin(self, choice, already):
        for v in self.EnglishWord.values():
            if (choice in v):
                for i in already:
                    if i in v:
                        return True
        return False

    def get_Chooses(self, x, already):
        ret = []
        already = already.copy()
        # print(already)
        for i in range(x):
            c = rnd.choice(list(self.EnglishWord.values()))
            c = rnd.choice(c)
            while self.findin(c, already):
                c = rnd.choice(list(self.EnglishWord.values()))
                if self.findin(c, already):
                    continue
                c = rnd.choice(c)

            ret.append(better_length(c))
            already.append(c)
        return ret

    def find_English(self, x):
        print(x)
        for v in self.EnglishWord.values():
            if x.replace('\n','') in v:
                return self.value_to_key(v)

    def value_to_key(self, v):
        for i in self.EnglishWord.keys():
            if v == self.EnglishWord[i]:
                return i

    def start(self):
        if len(self.EnglishWord.keys()) < 4:
            self.Label1.config(text='词库新词数量不足\n请使用翻译功能添加新学习词语或选择预设词库')
            return

        for i in range(len(self.RadioB)):
            self.RadioB[i].config(fg='black')
            self.RadioB[i]['bg'] = self.default_color
            Dependencies.Decreate_tips(self.RadioB[i])
        self.question = rnd.choice(list(self.EnglishWord.keys()))
        self.answer = rnd.choice(self.EnglishWord[self.question])
        self.Label1.config(text=f'请选出{self.question[0]}的中文意思')

        self.ChooseText = [better_length(self.answer)] + self.get_Chooses(3, [self.answer])
        rnd.shuffle(self.ChooseText)
        for i in range(len(self.ChooseText)):
            self.RadioB[i].config(text=self.ChooseText[i])
        self.answer = self.ChooseText.index(better_length(self.answer))
        self.submitButton.config(text='确认', command=self.submit)


class Datas():
    def __init__(self, rmb, tsl, wrt):
        self.rmb = rmb
        self.tsl = tsl
        self.wrt = wrt
        self.fm = ttk.Frame()

        # 答题正确率的初始化
        # 答题正确率
        if True:
            self.frame1 = ttk.LabelFrame(self.fm, text='答题正确率')

            try:
                t = self.rmb.right / self.rmb.All * 100
                t = str(t)[:5] + '%'
            except:
                t = '暂无数据'
            self.Label1 = ttk.Label(self.frame1,
                                    text=f'正确个数 {self.rmb.right}\n\n错误个数 {self.rmb.All - self.rmb.right}\n\n总个数 {self.rmb.All}\n\n正确率 {t}')

            self.btn1 = ttk.Button(self.frame1, text='查看错误率词云', command=lambda: self.makeWC(self.rmb.wrongs))
            self.Label1.pack(anchor='nw', padx=5)
            self.btn1.pack(anchor='w', padx=5, pady=5)
            self.frame1.pack(fill=BOTH, expand=True)

        # 填空正确率
        if True:

            self.frame2 = ttk.LabelFrame(self.fm, text='默写正确率')
            try:
                t = self.wrt.right / self.wrt.all * 100
                t = str(t)[:5] + '%'
            except:
                t = '暂无数据'
            self.Label2 = ttk.Label(self.frame2,
                                    text=f'正确个数 {self.wrt.right}\n\n错误个数 {self.wrt.all - self.wrt.right} \n\n总个数 {self.wrt.all}\n\n正确率 {t}')
            self.btn2 = ttk.Button(self.frame2, text='查看错误率词云', command=lambda: self.makeWC(self.wrt.wrong))
            self.Label2.pack(anchor='nw', padx=5)
            self.btn2.pack(anchor='w', padx=5, pady=5)
            self.frame2.pack(fill=BOTH, expand=True)
        self.fm.pack()

    def Update(self):
        try:
            t = self.rmb.right / self.rmb.All * 100
            t = str(t) + '%'
        except:
            t = '暂无数据'
        self.Label1.config(
            text=f'正确个数 {self.rmb.right}\n错误个数 {self.rmb.All - self.rmb.right}\n总个数 {self.rmb.All}\n正确率 {t}')

        try:
            t = self.wrt.right / self.wrt.all * 100
            t = str(t)[:5] + '%'
        except Exception as err:

            t = '暂无数据'
        self.Label2.config(
            text=f'正确个数 {self.wrt.right}\n\n错误个数 {self.wrt.all - self.wrt.right} \n\n总个数 {self.wrt.all}\n\n正确率 {t}')

    def makeWC(self, words):
        try:
            WordCloudMaker.make_wordcloud(words)
        except Exception as err:
            messagebox.showerror('你还没有错误词语', '您目前的错误率是0%！')


class writing():
    def __init__(self, EnglishWords, father):
        self.Father = father

        self.fm = ttk.Frame()
        self.frame1 = ttk.LabelFrame(self.fm, text='请根据所给中文默写出英文单词')
        self.frame2 = ttk.LabelFrame(self.fm)

        self.Label1 = ttk.Label(self.frame1)
        self.entry1 = ttk.Entry(self.frame2)
        self.btn1 = ttk.Button(self.frame2, text='开始', command=self.makeQuestion)

        self.entry1.bind('<Return>', self.makeQuestion)

        self.frame1.pack(fill=X, side=TOP)
        self.frame2.pack(fill=BOTH, side=TOP, expand=True)
        self.Englishword = EnglishWords
        self.entry1.pack(anchor='n')
        self.btn1.pack(anchor='n')
        self.Label1.pack(fill=X)

        self.right = 0
        self.all = 0
        self.wrong = []

    def submit(self, *args):
        answer = self.entry1.get()
        checkanswer = list(self.answer)
        for i in range(len(checkanswer)):
            repl = checkanswer[i].replace(' ', '').replace('\n', '').title()
            if repl != '':
                checkanswer[i] = repl
        print(checkanswer)
        canswer = answer.replace(' ', '').replace('\n', '').title()
        print(canswer)
        self.btn1.config(command=self.makeQuestion, text='下一题')

        self.entry1.delete(0, END)
        self.entry1.bind('<Return>', self.makeQuestion)
        self.entry1.config(state='disable')
        self.all += 1
        if canswer in checkanswer:
            self.right += 1
            messagebox.showinfo('回答正确', f'你的回答{answer}是正确的！ ')
        else:
            self.wrong.append(self.answer[0].replace(' ', ''))
            rightans = ''
            for i in self.answer:
                rightans += i + ' \n'
            messagebox.showerror('回答错误', f'你的回答 {answer} 是错的\n正确答案是: {rightans} \n其中之一 ')

        self.Father.data.Update()

    def makeQuestion(self, *args):
        if len(self.Englishword.keys()) < 1:
            messagebox.showerror('词库数量不足', '词库没有足够生词，请查询后使用')
            return False
        self.entry1.config(state='normal')
        self.entry1.focus_set()
        self.answer = rnd.choice(list(self.Englishword.keys()))
        self.question = self.Englishword[self.answer]
        self.question = rnd.choice(self.question)
        self.question = better_length(self.question)
        self.Label1.config(text=f'请写出 {self.question} 的英文')
        self.entry1.bind('<Return>', self.submit)
        self.btn1.config(command=self.submit, text='提交')


class myMenu():
    def __init__(self, father: myWindow):
        self.father = father
        self.menu = ttk.Menu(father.win)
        self.file = ttk.Menu(self.menu, tearoff=False)
        self.help = ttk.Menu(self.menu, tearoff=False)
        self.filesub = ttk.Menu(self.file, tearoff=False)

        self.menu.add_cascade(label='文件(F)', menu=self.file, underline=3, )
        self.menu.add_command(label='帮助(H)', underline=3, command=self.HelpDocx)
        self.file.add_command(label='导入词库 (I)', command=self.impPack, underline=6)
        self.filesub.add_command(label='导出为 词库', command=lambda: self.Output('.ff2'))
        self.filesub.add_command(label='导出为 HTML', command=lambda: self.Output('.html'))
        self.filesub.add_command(label='导出为 Excel', command=lambda: self.Output('.xls'))
        self.file.add_cascade(label='导出 (O)', menu=self.filesub, underline=4)

    def HelpDocx(self):
        if os.path.exists(r'{0}\help.html'.format(self.father.global_path)):
            os.startfile(r'{0}\help.html'.format(self.father.global_path))
        else:
            path = os.path.abspath(r'{0}\help.html'.format(self.father.global_path))
            messagebox.showerror('找不到帮助文档', f'找不到{path}')

    def impPack(self):
        self.load_ff2()
        print('导入成功力')
        # messagebox.showinfo('?', '正在开发中')

    def Output(self, format, *args):
        self.format = format
        words = self.Choose_words()

        # messagebox.showwarning('?', '在做了在做了')

    def Make_Choices(self, EnglishWord):
        words = []
        chn = []
        eng = []
        ml = 0
        for k, v in EnglishWord.items():
            chn.append(v[0].split('；')[0])
            eng.append(k[0])
            ml = max(ml, len(chn[-1]))

        for index in range(len(chn)):
            sep = abs(ml - len(chn[index])) * 2.5 + 1.5
            sep = ' ' * int(sep)
            add = chn[index] + sep + eng[index]
            words.append(add)
        return words

    def all_y(self):
        for i in range(self.lb.size()):
            self.lb.selection_set(i)

    def all_n(self):
        self.lb.selection_clear(0, END)

    def Choose_words(self, ):
        self.tpl = ttk.Toplevel()

        self.tpl.title('选取导出的单词')

        self.EnglishWord = self.father.tsl.EnglishWords

        words = self.Make_Choices(self.EnglishWord)
        print(words)
        self.lb = tk.Listbox(self.tpl, selectmode=MULTIPLE)

        all_yes = ttk.Button(self.tpl, text='全选', command=self.all_y)
        all_no = ttk.Button(self.tpl, text='全不选', command=self.all_n)
        btn1 = ttk.Button(self.tpl, text='确认')
        if self.format == '.html':
            btn1.config(command=self.submit_html)
        elif self.format == '.ff2':
            btn1.config(command=self.submit_ff2)
        elif self.format == '.xls':
            btn1.config(command=self.submit_xls)
        for i in words:
            self.lb.insert(END, i)

        self.lb.pack(fill=X)
        all_yes.pack(side=LEFT, padx=10, anchor='nw')
        all_no.pack(side=RIGHT, padx=10, anchor='nw')
        btn1.pack(padx=10, pady=10, anchor='center')

    def submit_ff2(self):
        select = self.lb.curselection()
        self.indexs = []
        for i in select:
            self.indexs.append(i)
        self.realSelect = {}
        cnt = 0
        for k, v in self.EnglishWord.items():
            if cnt in self.indexs:
                self.realSelect.update({k: v})
            cnt += 1
        if len(self.realSelect) == 0:
            messagebox.showerror('未选择', '您的选择单词数为 0 ')
            self.tpl.destroy()
            return False
        filename = f"{str(datetime.now()).replace('.', '').replace(' ', '').replace(':', '')}"
        self.tpl.destroy()
        Make_ff2(self.realSelect, filename, self.father.global_path)
        messagebox.showinfo('保存成功', '文件已成功保存')
        os.startfile(r'{0}\ff2'.format(self.father.global_path))

    def submit_html(self):
        selected = self.lb.curselection()
        self.indexs = []
        for i in selected:
            self.indexs.append(i)

        self.realSelect = []
        cnt = 0
        for k, v in self.EnglishWord.items():
            if cnt in self.indexs:
                add = '<span>'
                for j in k:
                    if j.replace(' ', '') == '':
                        continue
                    add += j + ', '
                add += '</span>' + ' ' * 10 + '<span<ASPACE>class="orange">'
                for j in v:
                    if j.replace(' ', '') == '':
                        continue
                    add += j + ' '
                add += '</span>\n'
                self.realSelect.append(add)
            cnt += 1
        if len(self.realSelect) == 0:
            messagebox.showerror('未选择', '您的选择单词数为 0 ')
            self.tpl.destroy()
            return False
        self.tpl.destroy()
        self.saveFilename = f"{str(datetime.now()).replace('.', '').replace(' ', '').replace(':', '')}"
        Make_html(self.realSelect, self.saveFilename, self.father.global_path)
        messagebox.showinfo('保存成功！', '文件已成功保存')
        os.startfile(r'{0}\htmls\{1}.html'.format(self.father.global_path, self.saveFilename))

    def submit_xls(self):
        select = self.lb.curselection()
        self.indexs = []
        for i in select:
            self.indexs.append(i)
        self.realSelect = {'中文': [], '译文': []}
        cnt = 0
        for k, v in self.EnglishWord.items():
            if cnt in self.indexs:
                self.realSelect['译文'].append(rnd.choice(k))
                self.realSelect['中文'].append(rnd.choice(v))
            cnt += 1
        if len(self.realSelect['中文']) == 0:
            messagebox.showerror('未选择', '您的选择单词数为 0 ')
            self.tpl.destroy()
            return False
        filename = f"{str(datetime.now()).replace('.', '').replace(' ', '').replace(':', '')}"
        self.tpl.destroy()
        Make_Sheet(self.realSelect, filename, self.father.global_path)
        messagebox.showinfo('保存成功', '文件已成功保存')
        os.startfile(r'{0}\excels\{1}.xls'.format(self.father.global_path, filename))

    def submit_load(self):
        select = self.lb.curselection()
        self.indexs = []
        for i in select:
            self.indexs.append(i)
        self.realAdd = {}
        cnt = 0
        print(self.Loadwords)
        for k, v in self.Loadwords.items():
            if cnt in self.indexs:
                self.realAdd.update({k: v})
            cnt += 1
        if len(self.realAdd) == 0:
            messagebox.showerror('未选择', '您的选择单词数为 0 ')
            self.tpl.destroy()
            return False
        self.father.UpdateAll(self.realAdd)
        self.tpl.destroy()

    def load_ff2(self):
        loading = filedialog.askopenfilename(title='选择要导入的词库', filetypes=[('ff2词库文件', '*.ff2'), ('任何文件', '*.*')])
        print('选择的文件路径', loading)
        try:
            self.Loadwords = eval(open(loading, 'r', encoding='utf-8').read())
            print(self.Loadwords)
            choices = self.Make_Choices(self.Loadwords)
        except FileNotFoundError as err:
            messagebox.showerror(str(type(err)), '你没有选择任何文件' + str(err))
            return False
        except SyntaxError as err:
            messagebox.showerror(str(type(err)), '文件损坏或内容无法识别' + str(err))
            return False
        except UnicodeDecodeError as err:
            messagebox.showerror(str(type(err)), '内容无法识别' + str(err))
            return False
        self.tpl = ttk.Toplevel()
        self.lb = tk.Listbox(self.tpl, selectmode=MULTIPLE)
        all_yes = ttk.Button(self.tpl, text='全选', command=self.all_y)
        all_no = ttk.Button(self.tpl, text='全不选', command=self.all_n)
        btn1 = ttk.Button(self.tpl, text='确认', command=self.submit_load)
        for i in choices:
            self.lb.insert(END, i)
        self.lb.pack(fill=X)
        all_yes.pack(side=LEFT, padx=10, anchor='nw')
        all_no.pack(side=RIGHT, padx=10, anchor='ne')
        btn1.pack(pady=5, padx=5, anchor='center')
        self.lb.pack(fill=X)


if __name__ == '__main__':
    win = myWindow('D:\ForEnglishPrograms\EnglishHelper\EnglishHelper')
    win.win.mainloop()
    print(win.rmb.EnglishWord)
    x = input()
    print(win.tsl.logs['error'])
