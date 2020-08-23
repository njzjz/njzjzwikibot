import os
os.environ['PYWIKIBOT_NO_USER_CONFIG']='1'

import pywikibot

def login(code, fam, user, password):
    site = pywikibot.Site(
        code=code,
        fam=fam,
        user=user,
    )
    pywikibot.data.api.LoginManager(site=site,user=user,password=password).login()
    return site
    

def create_page(site, title, text, talktext, description=""):
    page = pywikibot.Page(site, title)

    if page.exists():
        raise RuntimeError("Page is not empty!")
    
    page.text = text
    page.save("[[User:Njzjz/Njzjzwikibot|半自动]]导入文献 "+ description)

    talk_page = page.toggleTalkPage()
    if not talk_page.exists():
        talk_page.text = talktext
        talk_page.save("[[User:Njzjz/Njzjzwikibot|半自动]]标明文献来源 "+description)