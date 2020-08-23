import requests
from bs4 import BeautifulSoup
import re
import logging
import sys

from .bot import login

def generate_template(name, kwargs=None):
    if kwargs is None:
        kwargs = {}
    buff = [r"{{", name]
    for key, value in kwargs.items():
        buff.append("\n")
        buff.append(f"| {key} = {value}")
    if len(kwargs):
        buff.append("\n")
    buff.append("}}")
    return ''.join(buff)


def generate_text(text, header: dict, pd):
    header['edition'] = 'yes'
    header['notes'] = r"{{Textquality|50%}}"
    return "".join((
        generate_template('Header', header),
        "\n\n",
        "<onlyinclude>",
        str(text),
        "</onlyinclude>",
        "\n\n",
        generate_template(pd),
    ))

def generate_talk_page(textinfo):
    textinfo['proofreaders'] = '<!-- 校对者 -->'
    textinfo['contributors'] = r'{{subst:Currentuser}}'
    textinfo['progress'] = '[[File:50%.svg|15px]]'
    return generate_template("Textinfo", textinfo)



def xml_from_url(url):
    r = requests.get(url.strip())
    r.encoding = 'utf-8'
    return XML(BeautifulSoup(r.text, 'lxml'))


class XML:
    def __init__(self, xml):
        self.xml = xml

    def find(self, *args, **kwargs):
        return XML(self.xml.find(*args, **kwargs))
    
    def replace_with(self, *args, **kwargs):
        self.xml.replace_with(*args, **kwargs)

    def find_all(self, *args, **kwargs):
        return XMLlist(self.xml.find_all(*args, **kwargs))

    def __str__(self):
        return self.xml.get_text().strip()

    def insert(self, before=None, after=None):
        if str(self):
            self.xml.string = str(self)
            if before is not None:
                self.xml.insert_before(before)
            if after is not None:
                self.xml.insert_after(after)

    def replace_bold(self):
        self.find_all(
            style=lambda value: value and "font-weight: bold;" in value.lower()).insert("<b>", "</b>")
        self.find_all('b').insert("<b>", "</b>")
        self.find_all('strong').insert("<b>", "</b>")

    def replace_center(self):
        self.find_all(
            style=lambda value: value and "text-align: center;" in value.lower()).insert(r"{{c|", r"}}")
        self.find_all("p", align='center').insert(r"{{c|", r"}}")

    def replace_larger(self):
        self.find_all(style=lambda value: value and "font-size: 18pt;" in value.lower()
                          ).insert(r"{{x-larger block|", r"}}")

    def replace_kaiti(self):
        self.find_all(
            style=lambda value: value and "font-family: 楷体, 楷体_GB2312;" in value.lower()).insert(r'{{楷体|', r'}}')
        self.find_all("font", face="楷体_GB2312").insert(r'{{楷体|', r'}}')

    def replace_right(self):
        self.find_all(
            style=lambda value: value and "text-align: right;" in value.lower()).insert(r'{{right|', r'}}')

    def replace_gap(self):
        self.find_all(
            style=lambda value: value and "text-indent: 2em;" in value.lower()).insert(r'{{gap}}')

    def replace_breakline(self):
        self.find_all("br").insert("\n")

    def replace_table(self):
        for subdiv in self.find_all('table'):
            wikitable = ["\n{| class=\"wikitable\"\n"]
            for tr in subdiv.find_all('tr'):
                wikitable.append("|-\n")
                for td in tr.find_all(['th', 'td']):
                    wikitable.append("|")
                    if td.xml.get('colspan') is not None:
                        wikitable.extend((
                            "colspan=",
                            str(td.xml['colspan']),
                            " ",
                        ))
                    if td.xml.get('rowspan') is not None:
                        wikitable.extend((
                            "rowspan=",
                            str(td.xml['rowspan']),
                            " ",
                        ))
                    wikitable.extend((
                        "| ",
                        str(td),
                        " \n",
                    ))
            wikitable.append("|}\n")
            subdiv.replace_with("".join(wikitable))
    
    def replace_all(self):
        self.replace_bold()
        self.replace_center()
        self.replace_larger()
        self.replace_kaiti()
        self.replace_right()
        self.replace_gap()
        self.replace_breakline()
        self.replace_table()
    
    @staticmethod
    def remove_breakline(text):
        return re.sub('\n+', '\n\n', text)

    @staticmethod
    def add_link(text):
        def format_link(s):
            raw_text = s.group(0).strip("《》")
            if '〈' in raw_text:
                real_text = raw_text.replace('〈', '《').replace('〉', '》')
                raw_text = "%s|%s"%(real_text, raw_text)
            return "《[[%s]]》" % raw_text
        return re.sub('《(.*?)》', format_link, text)

    def get_text(self, remove_breakline=False, add_link=False):
        text = str(self)
        if remove_breakline:
            text = self.remove_breakline(text)
        if add_link:
            text = self.add_link(text)
        return text

class XMLlist:
    def __init__(self, xmllist: list):
        self.xmllist = [XML(x) for x in xmllist]

    def insert(self, *args, **kwargs):
        for xml in self.xmllist:
            xml.insert(*args, **kwargs)

    def __getitem__(self, key):
        return self.xmllist[key]


class GetLinks:
    URL_FORMAT = "%d"
    SUB_URL_PREFIX = ""

    def __init__(self):
        self.urls = []
        self.ii = 0

    def __iter__(self):
        self.jj = 0
        return self

    def __next__(self):
        retry = 0
        while self.jj >= len(self.urls):
            self.get_more_urls()
            retry += 1
            if retry > 3:
                raise RuntimeError("Cannot get the urls.")
        url = self.urls[self.jj]
        self.jj += 1
        return url
    
    def get_more_urls(self):
        url = self.URL_FORMAT % self.ii
        xml = xml_from_url(url)
        for link in xml.find_all('a', target="_blank"):
            l = link.xml['href']
            if l.startswith(self.SUB_URL_PREFIX):
                self.urls.append(l)
        self.ii += 1

def run_from_links(code, fam, user, password, urls, create_func, max_try=10):
    site = login(code, fam, user, password)
    failed = 0
    will_exit = False
    for url in urls:
        try:
            create_func(site, url)
        except KeyboardInterrupt:
            logging.warning("The program will stop after this article")
            will_exit = True
        except Exception:
            logging.exception("Failed on %s" % url)
            failed += 1
            if failed > max_try:
                will_exit = True
        else:
            failed = 0
        if will_exit:
            sys.exit()