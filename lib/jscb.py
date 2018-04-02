"""
get meanning from jscb, download URL of mp3.


"""
import re

from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep


def get_meaning(word, mdb):
    """search meanning from database firstly."""
    query = mdb.query(word)
    if query is not None:
        return query, True
    else:
        try:
            res = get_from_jscb(word)
        except UnicodeEncodeError:
            res = []
        mdb.add(word, res)
        return res, False

def get_resp(url):
    """try get resp from urlopen, until succeed."""
    try:
        resp = urlopen(url)
        return resp
    except ConnectionResetError:
        print("sleep for seconds.")
        sleep(3)
        return get_resp(url)


def get_from_jscb(word):
    """从金山词霸获取单词相关释义, 音标, 读音下载链接等内容"""
    url = "http://www.iciba.com/" + word
    resp = get_resp(url)
    html = resp.read()
    resp.close()
    soup = BeautifulSoup(html, 'lxml')
    results_static = []

    for div in soup.find_all('div'):
        if (['in-base-top', 'clearfix'] == div.get('class')):
            spans = div.find_all('span')
            for span in spans:
                text = span.get_text().strip()
                if ("英" in text and text not in results_static):
                    results_static.append(text)
                elif ("美" in text and text not in results_static):
                    results_static.append(text)
                try:
                    results_static.append(
                        span.i.get('ms-on-mouseover').split('\'')[1])
                except AttributeError:
                    pass
            if spans == []:
                try:
                    # 确认特殊网页排版时的释义为真.
                    if div.h1.get_text() == word:
                        results_static.append(div.div.get_text())
                except Exception:
                    pass
    for li in soup.find_all('li'):
        if (li.get('class') == ['clearfix']):
            for span in li.find_all('span'):
                results_static.append(span.get_text())
    return results_static


def light(word, sentence):
    """高亮例句中的单词"""
    cformat = "\033[4;94m{}\033[0m"
    patterns = [
        word + "s", word + "es", word[:-1] + "ies", word[:-1] + "ves",
        word + "ed", word[:-1] + "ied", word[:-1] + "ed", word + "ing",
        word[:-1] + "ing"
    ]
    for i in patterns:
        sentence = re.sub(i, cformat.format(i), sentence, flags=re.I)
    for i in reversed(list(re.finditer(word + r"[\W]", sentence, re.I))):
        sentence = sentence[:i.start()] + \
                cformat.format(word) + sentence[i.end() - 1:]
    return sentence


def get_sentence_from_source_page(source_page, word):
    """
    get sentences from jscb source_page.

    driver: str
        Example:
            >>> from driver import Webdriver
            >>> wdriver = Webdriver()
            >>> source_page = wdriver.source_page("hello")
            >>> get_sentence_from_source_page(source_page, "hello")
    word: str
        Example:
            "hello"
    """
    sen_ens, sen_cns, col_ens, col_cns = [], [], [], []
    if source_page is None:
        return {'sen_ens': [], 'sen_cns': [],
                'col_ens': [], 'col_cns': []}

    res_dic = {}
    sen_ens = [
        i for i in re.findall(
            '<p class="p-english family-english size-english">\s*?<span>(.*?)</span>',
            source_page) if i != ''
    ]
    sen_cns = [
        i for i in re.findall(
            '<p class="p-chinese family-chinese size-chinese">(.*?)</p>',
            source_page) if i != ''
    ]
    leng = min(len(sen_cns), len(sen_ens))
    sen_ens = sen_ens[:leng]
    sen_cns = sen_cns[:leng]
    sen_ens = [i.replace('<b>', '').replace('</b>', '') for i in sen_ens]
    sen_cns = [i.replace('<b>', '').replace('</b>', '') for i in sen_cns]
    for i, j, k in re.findall(
            'prep-order-icon">(.*?)<.*?family-chinese">\
(.*?)</span>.*?prep-en">(.*?)</span>',
            source_page,
            flags=re.S):
        col_ens.append(k)
        col_cns.append(j)
    res_dic['sen_ens'] = sen_ens
    res_dic['sen_cns'] = sen_cns
    res_dic['col_ens'] = col_ens
    res_dic['col_cns'] = col_cns

    return res_dic


def format_sentence(word, res_dic, lighten):
    """format sentences from dict."""
    if res_dic == [[], []]:
        res_dic = {'sen_ens': "", 'sen_cns': "", 'col_ens': "", 'col_cns': ""}
    """print res from res_dic"""
    # res = "\nexample sentences:\n\n"
    res = ""
    for ind, (en, cn) in enumerate(
            zip(res_dic['sen_ens'], res_dic['sen_cns'])):
        res += "{}: ".format(ind + 1) + en + " → " + cn + "\n"
    # res += "\nEnglish explanation:\n\n"
    res += "\n"
    for ind, (en, cn) in enumerate(
            zip(res_dic['col_ens'], res_dic['col_cns'])):
        res += "{}: ".format(ind + 1) + en + " → " + cn + "\n"

    if lighten is True:
        return light(word, res)
    else:
        return res


if __name__ == '__main__':
    
    from driver import Webdriver
    from sqlite import SenSqlite, MeanSqlite
    import sqlite3
    conn = sqlite3.connect("/home/zzp/program/release/dictionary/database/dic.db")
    sdb = SenSqlite(conn)
    mdb = MeanSqlite(conn)
    wd = Webdriver()

    for i in get_meaning("common", mdb):
        print(i)
    source_page = wd.source_page('common')
    res_dic = get_sentence_from_source_page(source_page, 'common')
    print(res_dic)
    print(format_sentence('common', res_dic, lighten=True))
    wd.quit()
