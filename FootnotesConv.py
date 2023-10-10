from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
import os, zipfile
import shutil,datetime
import tkinter.simpledialog as simpledialog
from collections import OrderedDict
import traceback
import xml.etree.ElementTree as ET
import re
import RP2



#脚注番号と文献の辞書
#文献が前の脚注番号で現れていれば、「前掲」のように表示するため
#id->脚注番号
G_footnotes={}
G_paper_dict={}

def init0test(folderName:str):
    global G_paper_dict
    filePaperPath="D:\Python script\zip\論文リスト.csv"
    fileCourtPath="D:\Python script\zip\裁判例.csv"
    filePath="D:\Python script\zip\論文231009.docx"
    G_paper_dict=RP2.read_papercsv(filePaperPath,fileCourtPath)

    print(filePath)
    
    folderPath=expand2(filePath,folderName)
    print(folderPath)
    footnotePath=folderPath+os.sep+"word"+os.sep+"footnotes.xml"
    print(footnotePath)
    return footnotePath,folderPath,filePath

def init0(folderName:str):
    global G_paper_dict
    filePaperPath=selectFile1("論文リストを開く")
    fileCourtPath=selectFile1("判例リストを開く")
    G_paper_dict=RP2.read_papercsv(filePaperPath,fileCourtPath)

    filePath=selectFile1("ワードファイルを開く")
    print(filePath)
    
    folderPath=expand2(filePath,folderName)
    print(folderPath)
    footnotePath=folderPath+os.sep+"word"+os.sep+"footnotes.xml"
    print(footnotePath)
    return footnotePath,folderPath,filePath

def selectFile1(title):
    #展開するファイルを指定
    fTyp = [("", "*")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    file_abspath = askopenfilename(title=title,filetypes=fTyp, initialdir=iDir)
    #print(file_abspath)
    return file_abspath

def expand2(file_abspath:str,folderName:str):
    #zipファイルを展開
    zp = zipfile.ZipFile(file_abspath, "r")
    iDir = os.path.abspath(os.path.dirname(__file__))
    folder_abspath=iDir+os.sep+folderName
    zp.extractall(path=folder_abspath)
    #print(folder_abspath)
    return folder_abspath

def open_Convert3(file_abspath:str,sep:list[str]):
    """指定したfootnotes.xmlファイルを開いて
    断片した脚注を最初のもの以外""とする
    断片した脚注をすべて結合し最初の脚注に入力する
    """
    tree = ET.parse(file_abspath)
    root = tree.getroot()

    word_ns="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    xml_ns="{http://www.w3.org/XML/1998/namespace}"

    #脚注を検索
    for footnote in root.findall(word_ns+'footnote'):
        text=""
        first_txt=ET.Element("")
        for i,txt in enumerate(footnote.iter(word_ns+'t')):
            if i==0:
                first_txt=txt

            text+=txt.text#断片している場合に備えてテキストを結合する
            txt.text="" #断片している場合に備えてテキストをすべて削除する
        
        #最初のタグに変換した脚注のすべてを入力する
        footnoteNo=footnote.attrib[word_ns+"id"]
        first_txt.text=footnote_convert4(sep,text,footnoteNo)  

    tree.write(file_abspath)
    print(G_footnotes)

def footnote_convert4(sep:list[str],fnote:str,footnoteNo:str)->str:
    """
    1.脚注文字列fnoteから、**[paper_id][page]**の形式を抽出
    2.さらにpaper_id,pageの抽出
    3.paper_id,pageから参考文献を構成
    4.**[paper_id][page]**を参考文献に置換
    """
    trans_pair={'*': '\\*', '[': '\\[',']': '\\]','.':'\\.','+':'\\+'}
    trans_dict=str.maketrans(trans_pair)

    sep=[text.translate(trans_dict) for text in sep]

    ret,parse=paper_parse5(sep,fnote)
    if ret=="error":
        print(ret)
        return fnote
    
    #print(parse)
    for key in parse.keys():
        paper=find_paper6(parse[key]["id"],parse[key]["page"],footnoteNo)
        fnote=fnote.replace(key, paper)

    return fnote

def paper_parse5(sep:list[str],para:str)->(int,dict):
    """パターンから引数を抽出する.

    例:
    paraを"abc**[id][page]**def"とすると
    id,pageをdictとして抽出する。

    sep[0]=sep[1]="**"
    sep[2]="[",sep[3]="]"
    """
    # 非貪欲マッチ（最⼩マッチ）
    pat = '('+sep[0]+'.*?'+sep[1]+')' # 例(**.*?**)
    r = re.findall(pat,para)
   
    pat2 = sep[2]+'(.*?)'+sep[3] # 例 [(.*?)]
    parse={}
    for i in r:
        l=re.findall(pat2, i)
        if len(l)!=2:# 例 [id][page]の[]内を捉える
            return "error",parse
        parse[i]={"id":l[0],"page":l[1]}

    return "OK",parse

def find_paper6(id:str,page:str,footnoteNo:str)->str:
    
    """
    paper_id,pageから参考文献を構成
    論文判例表示形式を返す
    前掲なら前掲表示形式を返す
    """
    if G_footnotes.get(id)==None: #まだ参照していない
        G_footnotes[id]=footnoteNo
        return RP2.make_PaperRef(id,G_paper_dict,page)
    else:
        return RP2.exist_PaperRef(id,G_paper_dict,page,G_footnotes[id])

def compress9(file_abspath,folder_abspath,suffix):
    #展開したフォルダを圧縮してファイル名を変更
    basename_without_ext = os.path.splitext(os.path.basename(file_abspath))[0]
    print(basename_without_ext)
    docxfile_noext=basename_without_ext+suffix
    shutil.make_archive(docxfile_noext, format='zip', root_dir=folder_abspath)
    os.rename(docxfile_noext+".zip",docxfile_noext+".docx")

def folder_to_archive9():
    """指定したフォルダを、zipファイルに圧縮。
    その際、ファイル名を変更し、拡張子をdocxにする
    """
    iDir = os.path.abspath(os.path.dirname(__file__))
    dir_path = askdirectory(initialdir=iDir)
    inputdata = simpledialog.askstring("Input Box", "ファイル名を入力",)

    conv="_conv"
    shutil.make_archive(inputdata+conv, format='zip', root_dir=dir_path)
    os.rename(inputdata+conv+".zip",inputdata+conv+".docx")
    
    print(dir_path)
