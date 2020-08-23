import re
import logging

from .utils import generate_text, generate_talk_page, xml_from_url, GetLinks, run_from_links
from .bot import create_page


def create_content(url):
    xml = xml_from_url(url)

    bd1 = str(xml.find(class_="bd1"))
    hdtablefind = re.findall(
        "索  引  号：(.*)主题分类：(.*)发文机关：(.*)成文日期：(.*)年(.*)月(.*)日.*标　　题：(.*)发文字号：(.*)发布日期：(.*)",
        bd1, re.DOTALL)
    hdtable = [h.strip() for h in hdtablefind[0]]
    theme = hdtable[1]
    lawmaker = "中华人民共和国"+hdtable[2]
    date = hdtable[3:6]
    title = hdtable[6]
    tyfind = re.findall("(.*)关于.*的(.*)", title)
    ty = f"中华人民共和国{tyfind[0][0]}的{tyfind[0][1]}" if tyfind else ""
    no = hdtable[7]

    bd1 = xml.find(class_="b12c")
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
        },
        pd="PD-PRC-exempt"
    )
    talk_page = generate_talk_page(
        textinfo={
            'source': url,
            'edition': '中华人民共和国中央人民政府网站',
            'notes': '自国务院网站[[User:Njzjz/Njzjzwikibot|半自动导入]]'
        }
    )
    return title, main_page, talk_page


def create(site, url):
    title, main_page, talk_page = create_content(url)
    create_page(site, title, main_page, talk_page,
                r"[[User:Njzjz/Njzjzwikibot#国务院文件|自国务院网站导入国务院文件]]"
                )


class GetGuoLinks(GetLinks):
    URL_FORMAT = "http://sousuo.gov.cn/list.htm?t=paper&sort=publishDate&timetype=timeqb&n=100&p=%d"
    SUB_URL_PREFIX = "http://www.gov.cn/zhengce/content/"


def run(args):
    user = args.user
    password = args.password
    run_from_links(code='zh', fam='wikisource', user=user, password=password,
                   urls=GetGuoLinks(), create_func=create, max_try=10)

