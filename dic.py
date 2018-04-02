"""
author: zzp
usage : quick dictionary in ubuntu.
"""
import argparse
import os
import sys
import threading
import urllib.request
import sqlite3

from lib.sqlite import MeanSqlite, SenSqlite
from lib.parser import parse_dic
from lib.jscb import (format_sentence, get_meaning,
                      get_sentence_from_source_page)
from lib.driver import Webdriver
from lib.play_wordmp3 import play_mp3
from lib.pre import (audio_dir, byebye, database_dir, myformat, order_clear,
                     order_logo_dic, other_dic_urls)


def parse():
    parser = argparse.ArgumentParser(
        description='description: translate words using jscb, \
            author: Zhaopeng Zhang')
    parser.add_argument(
        '-m',
        '--nosound',
        action='store_false',
        help='don\'t play audio if specified')
    parser.add_argument(
        '-g', '--logo', action='store_true', help='show logo if specified')
    parser.add_argument(
        '-e', '--expert', action='store_true', help='expert mode if specified')
    parser.add_argument(
        '-s',
        '--sentence',
        action='store_true',
        help='query sentences if specified')
    parser.add_argument('-w', '--word', type=str, help='query word in shell')
    parser.add_argument(
        '-d',
        '--database',
        default='default',
        type=str,
        help='default database name is "default", \
                        Review database in current dir if txt in database,\
                        Review database in database_dir if not')
    parser.add_argument(
        '-f',
        '--fromfile',
        type=str,
        help='get translations from file if specifed,\
                         please input realpath')
    parser.add_argument('--db', type=str, help='specify database name')
    parser.add_argument(
        '-u',
        '--url',
        action='store_true',
        help="print other dictionary urls.")
    args = parser.parse_args()
    if 'SSH_CLIENT' in os.environ:
        """don't play sound via ssh"""
        args.nosound = False
    return args


class Jscb:
    """金山词霸查单词"""

    def __init__(self):
        """初始化参数"""
        args = parse()
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.nosound = args.nosound
        self.logo = args.logo
        self.expert = args.expert
        self.sentence = args.sentence
        self.word = args.word
        self.fromfile = args.fromfile
        self.url = args.url
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
            if self.expert:
                word = input("\n").strip()
            else:
                word = input(
                    "input word to translate('q' or enter to exit):\n\n"
                ).strip()
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
                self.translate_from_jscb(word)
            except IOError as e:
                print("IOError:", e)
                sys.exit(byebye)
        else:
            # 在词库中，获取并发音
            for l in self.dic[word].split("\n"):
                print("  {:<}".format(l))
            print('\033[0m')
        if self.nosound == 1:
            play_mp3(
                self.path,
                word,
                show_tag=True,
                only_American_pronunciation=True)

    def sentences(self, word):
        """加入例句模块，尝试获取发音，重启获取功能"""
        if self.sentence:
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
        if self.url:
            other_dic_urls(word)

    def next_or_stop(self):
        """查词结束控制"""
        try:
            if self.expert:
                input()
            else:
                input("\nctrl+c to stop translate, enter to continue!")
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
        th = []
        th.append(threading.Thread(target=self.meaning(word)))
        th.append(threading.Thread(target=self.sentences(word)))
        # 多线程，释义发音与例句同步进行，减少因动态网页获取而增加的等待时间
        for t in th:
            t.start()
        for t in th:
            t.join()
        print('\033[0m', end='')
        self.conn.commit()
        self.conn.close()

    def getall_fromfile(self):
        words_list = set()
        dic = parse_dic(self.fromfile)
        for i in dic:
            words_list.add(i)
        if words_list == set():
            with open(self.fromfile) as f:
                for line in f:
                    words_list.add(line.strip())

        # meaning table
        words_list -= self.mdb.wordlist()
        words_list -= self.base_mdb.wordlist()
        import progressbar
        bar = progressbar.ProgressBar()
        num = 0
        bar_list = bar(words_list)
        for word in bar_list:
            num += 1
            if num % 50 == 0:
                self.conn.commit()
            results_static, tag_in = get_meaning(word, self.mdb)
            # write to note txt file and download mp3.
            # self.translate_from_jscb(word, results_static)

        # sentence table
        words_list -= self.sdb.wordlist()
        words_list -= self.base_sdb.wordlist()
        import progressbar
        bar = progressbar.ProgressBar()
        num = 0
        bar_list = bar(words_list)
        for word in bar_list:
            num += 1
            if num % 50 == 0:
                self.conn.commit()
            if self.wdriver is None:
                self.wdriver = Webdriver()
            res_dic = get_sentence_from_source_page(
                self.wdriver.source_page(word), word)
            self.sdb.add(word, res_dic)

        # commit
        self.conn.commit()
        self.conn.close()

    def translate(self):
        """查单词主函数"""
        self.get_words_already()
        # 从文件导入需要查询的单词
        if self.fromfile:
            self.getall_fromfile()
            sys.exit(0)
        while (1):
            word = self.prepare()
            th = []
            th.append(threading.Thread(target=self.meaning(word)))
            th.append(threading.Thread(target=self.sentences(word)))
            # 多线程，释义发音与例句同步进行，减少因动态网页获取而增加的等待时间
            for t in th:
                t.start()
            for t in th:
                t.join()
            self.next_or_stop()

    def translate_from_jscb(self, word, results_static=None):
        """获取单词在金山词霸上的释义，并格式化输出到屏幕，词库"""
        # 把需要的东西先抓下来
        if results_static is None:
            results_static, tag_in = get_meaning(word, self.mdb)
        if tag_in is True:
            """Already in local db."""
            print("[Local]")
        audio_path = os.path.join(self.path, audio_dir)
        num = 1
        dd = {1: "英", 2: "美", 3: "未知"}
        lines = ["#" * 45 + "\n", "#" + word + "\n"]

        if results_static != []:
            fayin = []
            for idx, i in enumerate(results_static):
                if "http" in i and "mp3" in i:
                    fayin.append(i)
                # 先打印音标与释义
                else:
                    if (idx + 1) != len(results_static):
                        if not self.fromfile:
                            print('  ├── %s' % (i))
                        lines.append('├── ' + i + "\n")
                    else:
                        if not self.fromfile:
                            print('  └── %s' % (i))
                        lines.append('└── ' + i + "\n")
            print('\033[0m')
            filenames = []
            for i in fayin:
                # 再进入发音模块
                filename_to = os.path.join(audio_path,
                                           word + "-" + dd[num] + ".mp3")
                num += 1
                # 下载音频文件
                if not os.path.exists(filename_to) or \
                        os.path.getsize(filename_to) == 0:
                    try:
                        urllib.request.urlretrieve(i, filename_to)
                    except Exception:
                        pass

            if filenames != []:
                print(
                    "\r %s" %
                    (" " *
                     (len("now playing: ") + max([len(fn)
                                                  for fn in filenames]))))
            else:
                print("\r %s" % (" " * 50))

        fw = open(self.notefile, 'a')
        if word not in self.words_already and len(lines) != 2:
            self.words_already.append(word)
            fw.writelines(lines)
        fw.close()

    def main(self):
        if self.word:
            """quick query for one word."""
            self.quick_dic()
        else:
            self.translate()


if __name__ == '__main__':
    j = Jscb()
    j.main()
