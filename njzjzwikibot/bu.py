import re
import logging

from .utils import generate_text, generate_talk_page, xml_from_url, GetLinks, run_from_links
from .bot import create_page


def create_content(url):
    xml = xml_from_url(url)
    bd1 = str(xml.find(class_="policyLibraryOverview_header"))
    hdtablefind = re.findall(
        "标.*题：(.*)发文机关：(.*)发文字号：(.*)来.*源：(.*)主题分类：(.*)公文种类：(.*)成文日期：(.*)年(.*)月(.*)日.*发布日期：(.*)",
        bd1, re.DOTALL)
    hdtable = [h.strip() for h in hdtablefind[0]]
    theme = hdtable[4]
    lawmaker = hdtable[1]
    date = hdtable[6:9]
    title = hdtable[0]
    ty = "中华人民共和国"+hdtable[1]+"的"+hdtable[5]
    no = hdtable[2]
    source = hdtable[3]

    bd1 = xml.find(class_="pages_content")
    bd1.replace_all()
    content = bd1.get_text(remove_breakline=True, add_link=True)

    main_page = generate_text(
        text=content,
        header={
            "title": title,
            "year": int(date[0]),
            "month": int(date[1]),
            "day": int(date[2]),
            "发文字号": no,
            "发布者": lawmaker,
            "type": ty,
            "theme": theme,
            "notes": source,
        },
        pd="PD-PRC-exempt"
    )
    talk_page = generate_talk_page(
        textinfo={
            'source': url,
            'edition': '中华人民共和国中央人民政府网站',
            'notes': '自国务院网站[[User:Njzjz/Njzjzwikibot#国务院部门文件|半自动导入]]'
        }
    )
    return title, main_page, talk_page


def create(site, url):
    title, main_page, talk_page = create_content(url)
    create_page(site, title, main_page, talk_page,
                r"[[User:Njzjz/Njzjzwikibot#国务院部门文件|自国务院网站导入国务院部门文件]]"
                )


class GetBuLinks(GetLinks):
    URL_FORMAT = "http://sousuo.gov.cn/column/47995/%d.htm"
    SUB_URL_PREFIX = "http://www.gov.cn/zhengce/zhengceku/"


def run(args):
    user = args.user
    password = args.password
    run_from_links(code='zh', fam='wikisource', user=user, password=password,
                   urls=GetBuLinks(), create_func=create, max_try=10)
