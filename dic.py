"""
author: zzp
usage : quick dictionary in ubuntu.
"""
import argparse
import os
import sys
from urllib.request import urlretrieve
import sqlite3
import socket

from lib.sqlite import MeanSqlite, SenSqlite
from lib.parser import parse_dic
from lib.jscb import (format_sentence, get_meaning,
                      get_sentence_from_source_page)
from lib.driver import Webdriver
from lib.play_wordmp3 import play_mp3
from lib.pre import (audio_dir, byebye, database_dir, myformat, order_clear,
                     order_logo_dic, other_dic_urls)


socket.setdefaulttimeout(30)


def parse():
    parser = argparse.ArgumentParser(
        description='description: dictionary crawed from http://www.iciba.com')
    parser.add_argument(
        '-g', '--logo', action='store_true', help='show logo if specified.')
    parser.add_argument(
        '-m', '--mute', action='store_true', help='mute mode if specified.')
    parser.add_argument(
        '-w', '--word', type=str, help='query word in shell directly.')
    parser.add_argument('--db', type=str, help='specify sqlite db.')
    parser.add_argument(
        '--nourl',
        action='store_false',
        help="don't print other dictionary urls.")
    parser.add_argument(
        '-d',
        '--database',
        default='default',
        type=str,
        help='default database name is "default", \
                        query word using database in current dir if txt in database name,\
                        use database in database_dir if not.')
    args = parser.parse_args()
    if 'SSH_CLIENT' in os.environ:
        """don't play sound via ssh"""
        args.mute = True
    return args


class Jscb:
    """金山词霸查单词"""

    def __init__(self):
        """初始化参数"""
        args = parse()
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.mute = args.mute
        self.logo = args.logo
        self.word = args.word
        self.nourl = args.nourl
        if args.db is not None:
            self.db = os.path.join(self.path, database_dir, args.db)
        else:
            self.db = os.path.join(self.path, database_dir, 'dic.db')
        if ".txt" not in args.database:
            self.notefile = os.path.join(self.path, database_dir,
                                         args.database + ".txt")
        else:
            self.notefile = args.database
        self.conn = sqlite3.connect(self.db)
        self.sdb = SenSqlite(self.conn)
        self.mdb = MeanSqlite(self.conn)
        self.base_db = os.path.join(self.path, database_dir, 'dic.db')
        self.base_conn = sqlite3.connect(self.base_db)
        self.base_sdb = SenSqlite(self.base_conn)
        self.base_mdb = MeanSqlite(self.base_conn)
        self.words_already = []
        self.words_keys = []
        self.dic = {}
        self.wdriver = None

    def get_words_already(self):
        """获取词库中已有单词信息"""
        if (os.path.exists(self.notefile)):
            for line in open(self.notefile):
                if line.count('#') == 1 and line[0] == '#':
                    self.words_already.append(line.strip()[1:])
            self.dic = parse_dic(self.notefile)
        self.words_keys = list(self.dic.keys())[:]

    def prepare(self):
        """打印logo与词库单词个数信息"""
        os.system(order_clear)
        if (self.logo):
            os.system(order_logo_dic)
        try:
            print(
                myformat.format(
                    "[" + os.path.basename(os.path.splitext(self.notefile)[0])
                    + " - " + str(len(self.words_keys)) + " words]"))
            print("\033[32m", end=" ")
            word = input("\n").strip()
        except KeyboardInterrupt:
            print()
            sys.exit(byebye)

        if (word in ['q', 'quit', 'exit', '']):
            sys.exit(byebye)
        # 记录下加入一个单词，提供给显示信息
        if (word not in self.words_keys):
            self.words_keys.append(word)
        else:
            print("[existed]")
        return word

    def meaning(self, word):
        """获取释义并发音, 若在词库中直接显示,若否,则在线查询"""
        if word not in self.dic:
            # 不在词库中或指定强制重新查询，则联网获取释义，发音
            try:
                self.retrieve_meaning(word)
            except IOError as e:
                print("IOError:", e)
                sys.exit(byebye)
        else:
            for l in self.dic[word].split("\n"):
                print("  {:<}".format(l))
            print('\033[0m')

    def sound(self, word):
        """play sound."""
        if self.mute is not True:
            play_mp3(
                self.path,
                word,
                show_tag=False,
                only_American_pronunciation=True)

    def sentences(self, word):
        """加入例句模块，尝试获取发音，重启获取功能"""
        try_time = 2
        success = 0
        while try_time != 0:
            query = self.sdb.query(word)
            if query is not None:
                res_dic = query
            else:
                if self.wdriver is None:
                    self.wdriver = Webdriver()
                res_dic = get_sentence_from_source_page(
                    self.wdriver.source_page(word), word)
                self.sdb.add(word, res_dic)
            res = format_sentence(word, res_dic, lighten=True)
            if res != "":
                print(res)
                success = 1
                break
            else:
                # print "retry to get sentence of this words..."
                pass
            try_time -= 1
        if not success:
            print("[*] cannot get sentences of this word.\033[0m")

    def urls(self, word):
        """print urls of other dic."""
        if self.nourl:
            other_dic_urls(word)

    def next_or_stop(self):
        """查词结束控制"""
        try:
            input()
        except KeyboardInterrupt:
            self.conn.commit()
            self.conn.close()
            sys.exit(byebye)

    def quick_dic(self):
        """命令行快速查词"""
        print('\033[0m', end=' ')
        self.get_words_already()
        word = self.word
        print('\033[32m', end=' ')
        print("\n{:s}".format(word))
        if word in self.words_already:
            print("[existed]")
        # several parts.
        self.meaning(word)
        self.sentences(word)
        self.urls(word)
        self.sound(word)
        print('\033[0m', end='')
        # close connect.
        self.conn.commit()
        self.conn.close()

    def translate(self):
        """查单词主函数"""
        self.get_words_already()
        while True:
            word = self.prepare()
            # several parts.
            self.meaning(word)
            self.sentences(word)
            self.urls(word)
            self.sound(word)
            self.next_or_stop()

    def retrieve_meaning(self, word, results_static=None):
        """获取单词在金山词霸上的释义，并格式化输出到屏幕，词库"""
        # 把需要的东西先抓下来
        tag_in = False
        if results_static is None:
            results_static, tag_in = get_meaning(word, self.mdb)
        if tag_in is True:
            """Already in local db."""
            print("[Local]")
        fayin, meanings = [], []
        if results_static != []:
            for item in results_static:
                if item.startswith("http:"):
                    fayin.append(item)
                else:
                    meanings.append(item)
        res = ""
        if meanings != []:
            for idx in range(len(meanings) - 1):
                res += "  ├── {}\n".format(meanings[idx])
            res += "  └── {}\n".format(meanings[-1])
        for tag, url in zip(["英", "美"], fayin):
            try:
                urlretrieve(url,
                            os.path.join(self.path, audio_dir,
                                         "{}-{}.mp3".format(word, tag)))
            except Exception as e:
                print(e)
        print(res)
        print("\033[0m")
        if word not in self.words_already and meanings != []:
            with open(self.notefile, 'a') as f:
                f.write("#" * 45 + "\n")
                f.write("#" + word + "\n")
                f.write(res)
            self.words_already.append(word)

    def main(self):
        if self.word:
            """quick query for one word."""
            self.quick_dic()
        else:
            self.translate()


if __name__ == '__main__':
    j = Jscb()
    j.main()
