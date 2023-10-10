import os
import FootnotesConv as FC
import csv,datetime
import RP2



if __name__ == '__main__':
    sep=["**","**","[","]"]
    dt_now = datetime.datetime.now()
    folderName=dt_now.strftime('%Y年%m月%d日 %H時-%M分-%S秒')+"_footnoted"
    footnotePath,folderPath,filePath=FC.init0test(folderName)
    FC.open_Convert3(footnotePath,sep)
    FC.compress9(filePath,folderPath,folderName)
    RP2.endPaper(FC.G_paper_dict)
    #print(FC.G_paper_dict)
    #print(FC.G_footnotes)
    
