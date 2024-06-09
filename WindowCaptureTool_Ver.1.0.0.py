import tkinter
import pyautogui
from PIL import Image, ImageTk, ImageGrab
import wx
import wx.adv
import datetime
import csv
import os
import time
import sys
import subprocess
from pynput import keyboard
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

# トリミング範囲指定画像表示時の縮小率
RESIZE_RATIO = 3

# タイトルとアイコン画像指定
TRAY_TOOLTIP = 'Window Capture Tool Ver.1.0.0'
TRAY_ICON = ('./icon.png')

def Set_Capture_size():
    # ドラッグ開始時のイベント
    def start_point_get(event):
        global start_x, start_y

        canvas1.delete('rect1')
        canvas1.create_rectangle(event.x,
                                 event.y,
                                 event.x +1,
                                 event.y +1,
                                 outline = 'red',
                                 tag = 'rect1')
        start_x, start_y, = event.x, event.y

    # ドラッグ中のイベント
    def rect_drawing(event):

        # 指定範囲が画像サイズを超えた場合の処理
        if event.x < 0:
            end_x = 0
        else:
            end_x = min(img_resized.width, event.x)
        if event.y < 0:
            end_y = 0
        else:
            end_y = min(img_resized.height, event.y)

        canvas1.coords('rect1', start_x, start_y, end_x, end_y)

    # ドラッグ放した時のイベント
    def release_action(event):
        start_x, start_y, end_x, end_y = [round(n * RESIZE_RATIO) for n in canvas1.coords('rect1')]

        Set_Trim_Area = wx.MessageBox(
            u'表示されている枠を指定範囲に登録して問題無いですか？',
            u'連続キャプチャ指定範囲 確認',
            wx.CANCEL
            )
        if Set_Trim_Area == 4:
            global Fix_start_x
            global Fix_start_y
            global Fix_end_x
            global Fix_end_y
            Fix_start_x = start_x
            Fix_start_y = start_y
            Fix_end_x = end_x
            Fix_end_y = end_y

            root.destroy()

    # メイン処理
    # 表示する画像の取得
    img = pyautogui.screenshot()

    # スクリーンショットした画像は表示しきれないので画像リサイズ
    img_resized = img.resize(
        size=(
            int(img.width / RESIZE_RATIO),
            int(img.height / RESIZE_RATIO)),
            resample = Image.BILINEAR
        )

    root = tkinter.Tk()
    # root.attributes('-topmost', True)

    # tkinterで表示出来るように画像変換
    img_tk = ImageTk.PhotoImage(img_resized)

    # Canvasウィジェットの描画
    canvas1 = tkinter.Canvas(
        root,
        bg = 'black',
        width = img_resized.width,
        height = img_resized.height
        )

    # Canvasウィジェットに取得した画像を描画
    canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)

    # Canvasウィジェットを配置し、各種イベントを設定
    canvas1.pack()
    canvas1.bind('<ButtonPress-1>', start_point_get)
    canvas1.bind('<Button1-Motion>', rect_drawing)
    canvas1.bind('<ButtonRelease-1>', release_action)

    root.mainloop()

def ini_File_Write():
    settings_list = [
        ('Capture_Folder', Capture_Folder),
        ('Triming_Folder', Triming_Folder),
        ('Fix_start_x', Fix_start_x),
        ('Fix_start_y', Fix_start_y),
        ('Fix_end_x', Fix_end_x),
        ('Fix_end_y', Fix_end_y),
    ]

    with open('./settings.ini', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(settings_list)

def ini_File_Read():
    if os.path.isfile('./settings.ini') == False:
        wx.Messagebox(u'settings.iniが見つかりません。起動出来ませんでした。', u'ERROR', wx.ICON_ERROR)
        exit()
    else:
        global Capture_Folder
        global Triming_Folder
        global Fix_start_x
        global Fix_start_y
        global Fix_end_x
        global Fix_end_y

        Read_ini_File = open('./settings.ini', encoding='utf-8-sig')
        Reader = csv.reader(Read_ini_File)
        for row in Reader:

            if row[0] == 'Capture_Folder':
                Capture_Folder = row[1]
            elif row[0] == 'Triming_Folder':
                Triming_Folder = row[1]
            elif row[0] == 'Fix_start_x':
                Fix_start_x = row[1]
            elif row[0] == 'Fix_start_y':
                Fix_start_y = row[1]
            elif row[0] == 'Fix_end_x':
                Fix_end_x = row[1]
            elif row[0] == 'Fix_end_y':
                Fix_end_y = row[1]

def Get_File_Name_Date():
    Time_Now = datetime.datetime.now()
    File_Name_Date = (
        str(Time_Now.year) +
        str(Time_Now.month).zfill(2) +
        str(Time_Now.day).zfill(2) +
        str(Time_Now.hour).zfill(2) +
        str(Time_Now.minute).zfill(2) +
        str(Time_Now.second).zfill(2)
    )
    return File_Name_Date

def Get_Clipbord_Make_PNG():
    File_Name_Date = Get_File_Name_Date()
    File_Name = ('Clipbord_' + File_Name_Date + '.png')
    Capture_Image = ImageGrab.grabclipboard()
    Capture_Image.save(Capture_Folder + '/' + File_Name)

def Get_Capture_NoTrim():
    time.sleep(0.5)
    File_Name_Date = Get_File_Name_Date()
    File_Name = (File_Name_Date + '.png')

    Capture_Image = pyautogui.screenshot()
    Capture_Image.save(Capture_Folder + '/Capture_' + File_Name)

def Get_Capture_Trim():
    time.sleep(0.5)
    File_Name_Date = Get_File_Name_Date()
    File_Name = (File_Name_Date + '.png')

    Capture_Image = pyautogui.screenshot()
    Capture_Image.save(Capture_Folder + '/Capture_' + File_Name)

    Img_File = Image.open(Capture_Folder + '/Capture_' + File_Name)
    Trim_Img_File = Img_File.crop((int(Fix_start_x), int(Fix_start_y), int(Fix_end_x), int(Fix_end_y)))
    Trim_Img_File.save(Triming_Folder + '/Trim_' + File_Name)

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)

    return item

class TaskBarIcon(wx.adv.TaskBarIcon):

    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.on_Get_Clipbord_Make_PNG)

    def CreatePopupMenu(self):
        menu = wx.Menu()

        create_menu_item(menu, 'キャプチャ実行(トリミングあり)', self.on_Get_Capture_Trim)
        create_menu_item(menu, 'キャプチャ実行(トリミングなし)', self.on_Get_Capture_NoTrim)
        create_menu_item(menu, 'クリップボードの画像を保存', self.on_Get_Clipbord_Make_PNG)

        menu.AppendSeparator()
        create_menu_item(menu, 'トリムサイズセット', self.on_Trim_Size_Set)
        create_menu_item(menu, 'トリム範囲座標確認', self.on_Print_Trim_Area)

        submenu_Set_Folder = wx.Menu()
        create_menu_item(submenu_Set_Folder, 'トリム前フォルダ', self.on_Set_Capture_NoTrim_Save_Folder)
        create_menu_item(submenu_Set_Folder, 'トリム後フォルダ', self.on_Set_Capture_Trim_Save_Folder)
        menu.AppendSubMenu(submenu_Set_Folder, 'キャプチャ保存フォルダの指定')

        submenu_Open_Folder = wx.Menu()
        create_menu_item(submenu_Open_Folder, 'トリム前', self.on_Open_Capture_NoTrim_Save_Folder)
        create_menu_item(submenu_Open_Folder, 'トリム後', self.on_Open_Capture_Trim_Save_Folder)
        menu.AppendSubMenu(submenu_Open_Folder, 'キャプチャ保存フォルダを開く')

        menu.AppendSeparator()
        create_menu_item(menu, '設定保存', self.on_ini_File_Write)
        create_menu_item(menu, '終了', self.on_exit)

        return menu

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_Trim_Size_Set(self, event):
        #
        Set_Capture_size()

    def on_Print_Trim_Area(self, event):
        Trim_Area_Info = '開始座標：(' + str(Fix_start_x) + ',' + str(Fix_start_y) + ')¥n終了座標：(' + str(Fix_end_x) + ',' + str(Fix_end_y) + ')'
        wx.MessageBox(Trim_Area_Info, u'トリミング範囲')

    def on_Get_Capture_Trim(self, event):
        if Fix_start_x == 0 and Fix_start_y == 0 and Fix_end_x == 0 and Fix_end_y == 0:
            wx.MessageBox(u'トリミング範囲が指定されていません¥n範囲を指定してください', u'エラー', wx.ICON_ERROR)
        else:
            Get_Capture_Trim()

    def on_Get_Capture_NoTrim(self, event):
        Get_Capture_NoTrim()

    def on_Get_Clipbord_Make_PNG(self, event):
        Get_Clipbord_Make_PNG()

    def on_Set_Capture_Trim_Save_Folder(self, event):
        global Triming_Folder
        Folder_Select_Dialog = wx.DirDialog(None, 'トリム後 保存フォルダ')
        Folder_Select_Dialog.ShowModal()
        Triming_Folder = Folder_Select_Dialog.GetPath()

    def on_Set_Capture_NoTrim_Save_Folder(self, event):
        global Capture_Folder
        Folder_Select_Dialog = wx.DirDialog(None, u'トリム前 保存フォルダ')
        Folder_Select_Dialog.ShowModal()
        Capture_Folder = Folder_Select_Dialog.GetPath()

    def on_Open_Capture_NoTrim_Save_Folder(self, event):
        subprocess.Popen(['explorer', Capture_Folder], shell=True)

    def on_Open_Capture_Trim_Save_Folder(self, event):
        subprocess.Popen(['explorer', Triming_Folder], shell=True)

    def on_ini_File_Write(self, event):
        ini_File_Write()

    def on_exit(self, event):

        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)

        return True

class HotKey(wx.Frame):
    def __init__(self, parent, id, title):
        super(HotKey, self).__init__(None)
        self.RegisterHotKey(1234, wx.MOD_ALT, 44)
        self.Bind(wx.EVT_HOTKEY, self.Call_Hotkey)

    def Call_Hotkey(self, event):
        Get_Capture_NoTrim()

if __name__ == '__main__':
    ini_File_Read()
    app = App(False)
    HotKey(None, wx.ID_ANY, '')
    app.MainLoop()
