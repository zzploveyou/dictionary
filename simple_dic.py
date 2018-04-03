# coding:utf-8
import os
import sqlite3
import argparse
import sys
from playsound import playsound

try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except Exception as e:
    pass


def play_audio(urls):
    """play audio mp3."""
    for url in urls:
        playsound(url)


def format_meaning(word, mean):
    """print meaning."""
    res = "\n"
    res += word + "\n"
    for idx in range(len(mean) - 1):
        res += "├── {}\n".format(mean[idx])
    res += "└── {}\n".format(mean[-1])
    return res


def format_sentence(word, res_dic):
    """format sentences from dict."""
    res = ""
    for ind, (en, cn) in enumerate(
            zip(res_dic['sen_ens'], res_dic['sen_cns'])):
        res += "{}: ".format(ind + 1) + en + " → " + cn + "\n"
    res += "\n"
    for ind, (en, cn) in enumerate(
            zip(res_dic['col_ens'], res_dic['col_cns'])):
        res += "{}: ".format(ind + 1) + en + " → " + cn + "\n"
    return res


def query(cursor, word):
    mean = cursor.execute("select * from MEANING where word=?",
                          (word, )).fetchone()[1]
    sen_ens, sen_cns, col_ens, col_cns = cursor.execute(
        "select * from SENTENCE where word=?", (word, )).fetchone()[1:]
    res_dic = {}
    res_dic['sen_ens'] = sen_ens.split("\n")
    res_dic['sen_cns'] = sen_cns.split("\n")
    res_dic['col_ens'] = col_ens.split("\n")
    res_dic['col_cns'] = col_cns.split("\n")
    meanings, urls = [], []
    for i in mean.split("\n"):
        if i.startswith("http:"):
            urls.append(i)
        else:
            meanings.append(i)
    print(format_meaning(word, meanings))
    print(format_sentence(word, res_dic))
    play_audio(urls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="quick query word from sqlite3 db.")
    parser.add_argument(
        '-d',
        '--database',
        type=str,
        default=os.path.join(os.path.dirname(__file__), "dic.db"),
        help="specify database name.")
    parser.add_argument('-w', '--word', type=str, help="specify word.")
    args = parser.parse_args()
    if args.database is None or args.word is None:
        sys.exit("exit since no auguments.")
    conn = sqlite3.connect(args.database)
    cursor = conn.cursor()
    query(cursor, args.word)
    conn.close()
