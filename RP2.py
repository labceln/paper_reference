import csv


def read_papercsv(filePaperPath:str,fileCourtPath:str):
    """csvから論文判例辞書を返す"""
    papers_dict={}

    #論文辞書
    with open(filePaperPath, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            version="、（"+row["version"]+"）" if row["version"]!="" else ""
            kwargs={"author_fam":row["author_fam"],"author_name":row["author_name"],
                    "author_etc":row["author_etc"],"F.name":row["F.name"],
                    "P.name":row["P.name"],"year":row["year"],
                    "title":row["title"],"album":row["album"],
                    "volume":row["volume"],"start_page":row["start_page"],
                    "publisher":row["publisher"],"version":version,
                    "editor":row["editor"],"series":row["series"],
                    "page":"",'Form':row['Form']}
            
            papers_dict[row["id"]]=kwargs

    #判例辞書
    with open(fileCourtPath, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:            
            papers_dict[row["id"]]=row

    return papers_dict

def make_PaperRef(id:str,papers_dict:dict,page:str)->str:
    """id,page,参考文献辞書から、論文判例表示形式を返す"""
    RefForm={"単行本":"{author_fam}{author_name}{author_etc}『{title}{version}』、{page}（{publisher}、{year}年）",
         "雑誌":"{author_fam}{author_name}{author_etc}「{title}」{album}{volume}{start_page}頁、{page}（{year}年）",
         "論文集":"{author_fam}{author_name}{author_etc}「{title}」、{editor}編『{album}{version}』{start_page}頁、{page}（{publisher}、{year}年）",
         "判批":"{author_fam}{author_name}{author_etc}「判批」、{album}{version}{volume}{start_page}頁、{page}（{year}年）",
         "判例":"{all} {title}"}
    tmp=papers_dict[id]
    tmp["page"]=page if not page else page+"、"
    return RefForm[papers_dict[id]["Form"]].format(**tmp)

                 
def exist_PaperRef(id:str,papers_dict:dict,page:str,footnoteNo:int)->str:
    """id,page,footnoteNo,参考文献辞書から、前掲表示形式を返す"""
    existPaper="{author_fam}.前掲注{No}、{page}"
    existCourt="前掲注{No}、{all} {title}"
    RefForm={"単行本":existPaper,"雑誌":existPaper ,"論文集":existPaper,
             "判批":existPaper,"判例":existCourt}
    
    tmp=papers_dict[id]
    tmp["page"]=page
    tmp["No"]=str(footnoteNo)
    return RefForm[papers_dict[id]["Form"]].format(**tmp)

def endPaper(paper_dict:dict):
    from collections import OrderedDict
    """論文については、著者の五十音順と出版年度でソート

    判例については、裁判所と判決と年度でソート
    """
    papers = OrderedDict()
    courts = OrderedDict()

    for key in paper_dict.keys():
        if paper_dict[key]["Form"] in ["単行本","雑誌","論文集","判批"]:
            papers[key]=paper_dict[key]
        if paper_dict[key]["Form"] in ["判例"]:
            courts[key]=paper_dict[key]

    print(sorted(papers.items(), key=lambda x: (x[1]["F.name"],x[1]["P.name"],x[1]["year"]), reverse=False))
    print(sorted(courts.items(), key=lambda x: (x[1]["year"],x[1]["id"]), reverse=False))


    
        
