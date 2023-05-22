import os
import re
import time
import errno
import pyautogui as pg
from pyautogui import ImageNotFoundException 
import subprocess 
import Config

def main():
    
    # iniファイルを読み込む
    ini_path = './config.ini'
    cfg = Config.Config(ini_path)
    
    midi_files = [f for f in os.listdir(cfg.midi_path) if os.path.isfile(os.path.join(cfg.midi_path, f))]
    tmp_dorico_files = [f for f in os.listdir(cfg.dorico_pj_path) if os.path.isfile(os.path.join(cfg.dorico_pj_path, f))]
    dorico_files = [f for f in tmp_dorico_files if re.search('^'+cfg.prefix_ignore_dorico, f) is None]
    done_dorico_files = [df for mf in midi_files for df in dorico_files if mf.startswith(df.replace('.dorico', ""))]
    
    # midiに変換されていないdoricoファイルはmidiに変換する
    convert_files = list(filter(lambda x: x not in done_dorico_files, dorico_files))
    
    midi_times = [os.path.getmtime(os.path.join(cfg.midi_path, f)) for f in midi_files]
    dorico_times = [os.path.getmtime(os.path.join(cfg.dorico_pj_path, f)) for f in done_dorico_files]
    
    # 更新日時がmidiファイルより新しいdoricoファイルは、midiファイルを再変換する
    convert_files = convert_files + [f for i,f in enumerate(done_dorico_files) if (dorico_times[i] - midi_times[i]) > 0]
    
    # doricoを起動
    subprocess.Popen(cfg.dorico_exe_path)
    
    # Dirico起動画面待機
    wait_show_img(pg, '.\img\stainberghub.png', 30)
    
    # midi変換
    with open('.\logfile.txt', 'a') as logfile:
        for df in convert_files:
            convertMidi(df, cfg.dorico_pj_path, cfg.midi_path, logfile, cfg.dorico_exe_path)

    print('midi変換が完了しました(' + str(len(convert_files)) + 'ファイル処理しました)')
    
# midi変換
def convertMidi(dorico_file, dorico_pj_path, midi_path, logfile, dorico_exe_path):
    
    #カンマを含む場合、一旦ファイル名を置換
    if ',' in dorico_file:
        dorico_file_org = dorico_file
        dorico_file = dorico_file.replace(",", "#comma#")
        os.rename(dorico_file_org, dorico_file)
    
    # dorico プロジェクトファイル起動
    subprocess.Popen([dorico_exe_path,os.path.join(dorico_pj_path,dorico_file)])
    
    # Dorico PJ画面待機
    try:
        wait_show_img(pg, '.\img\TopRightIcon.png', 10)
    except ImageNotFoundException as e:
        # ファイルが見つからない場合のエラーハンドリング
        while 1:
            try:
                # ファイルがエラーダイアログが表示された場合、ダイアログを閉じる
                wait_show_img(pg, '.\img\\notfound.png', 3)
                pg.press("enter")
            except ImageNotFoundException as e:
                # エラーが発生したファイル名をログに書込み、midi変換処理は行わずスキップする
                logfile.writelines(dorico_file+"\n")
                return
    
    # [メニュー]/[ファイル(Alt+F)]/[書き出し(E)]/MIDI...(↓↓)
    pg.hotkey("alt","f")
    wait_show_img(pg, '.\img\menu-file.png', 5)
    pg.press("e")
    pg.press("down")
    pg.press("down")
    pg.press("enter")
    time.sleep(0.5)

    #MIDIを書き出し画面待機
    wait_show_img(pg, "./img/writemidi.png", 5)

    
    # フォルダの選択画面を開く
    pg.hotkey("shift","tab")
    try:
        # 「ファイル書き出し用フォルダーを作成」チェックは外す
        wait_show_img(pg, "./img/makefolder.png", 1)
        pg.press("space")
    except ImageNotFoundException as e:
        # チェックが無い場合何もしない
        pass 
    pg.hotkey("shift","tab")
    pg.press("space")
    
    # フォルダの選択画面待機
    wait_show_img(pg, "./img/selectfolder.png", 5)

    # midiフォルダ指定
    pg.typewrite(midi_path)
    pg.press("enter")
    pg.press("enter")

    #MIDIを書き出し画面(...にフォーカスが当たっている状態)待機
    wait_show_img(pg, "./img/writemidi2.png", 5)
    
    # OKを押下し画面を閉じる
    pg.press("tab")
    pg.press("tab")
    pg.press("space")

    # 上書き確認ダイアログにOKで応答する
    try:
        wait_show_img(pg, "./img/overwrite.png", 2)
        pg.press("enter")
    except ImageNotFoundException as e:
        # 上書き確認ダイアログが表示されない場合何もしない
        pass

    ## Doricoを閉じる
    pg.hotkey("ctrl","shift", "w")

    #カンマを含む場合、置換したファイルを元に戻す
    if '#comma#' in dorico_file:
        os.rename(dorico_file, dorico_file_org)
        
        midi_files = [f for f in os.listdir(midi_path) if os.path.isfile(os.path.join(midi_path, f))]
        for  f in midi_files:
            if f.startswith(dorico_file.replace(".dorico", "")):
                os.rename(f, f.replace("#comma#", ","))

# 画像認識による操作完了待ち
def wait_show_img(pg, img, timeout):
    # 30秒でタイムアウト
    for i in range(timeout):
        time.sleep(1)
        p = pg.locateOnScreen(img)
        if p is not None:
            return pg.center(p)
        
    raise ImageNotFoundException(errno.ENOENT, os.strerror(errno.ENOENT), img)
    
# メイン関数
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)