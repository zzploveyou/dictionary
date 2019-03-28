'''
review the words from database.
'''
import argparse
import os
import random
import re
import signal
import sys
import sqlite3
from lib.sqlite import MeanSqlite, SenSqlite
from lib.driver import Webdriver
from glob import glob
from lib.parser import parse_dic
from lib.jscb import format_sentence, get_sentence_from_source_page
from lib.play_wordmp3 import play_mp3
from lib.pre import (audio_dir, byebye, database_dir, myformat, order_clear,
                     order_logo_review, other_dic_urls)


def parse():
    parser = argparse.ArgumentParser(
        description='description: review words in database randomly.')
    parser.add_argument(
        '-m', '--mute', action='store_true', help='mute mode if specified.')
    parser.add_argument(
        '-g', '--logo', action='store_true', help=' show logo if specified.')
    parser.add_argument(
        '-i', '--info', action='store_true', help='print database infomation.')

    parser.add_argument(
        '-t',
        '--dictation',
        action='store_true',
        help='dictation mode if specified')
    parser.add_argument(
        '--nourl',
        action='store_false',
        help="don't print other dictionary urls.")
    parser.add_argument(
        '-n', '--number', default=1, type=int, help='review n words at once.')
    parser.add_argument(
        '-d',
        '--database',
        default='default',
        type=str,
        help='default database name is "default", \
                        Review database in current dir if txt in database name,\
                        Review database in database_dir if not.')
    args = parser.parse_args()
    if 'SSH_CLIENT' in os.environ:
        """don't play sound via ssh"""
        args.mute = True
    return args


class Review:
    """复习单词"""

    def __init__(self):
        """初始化"""
        args = parse()
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.mute = args.mute
        self.logo = args.logo
        if ".txt" not in args.database:
            self.database = os.path.join(self.path, database_dir,
                                         args.database + ".txt")
        else:
            self.database = args.database
        self.info = args.info
        self.number = args.number
        self.dictation = args.dictation
        self.nourl = args.nourl
        self.dic = {}
        self.temp_len = 0
        self.num_words = 0
        self.wdriver = None
        self.db = os.path.join(self.path, database_dir, "dic.db")
        self.conn = sqlite3.connect(self.db)
        self.sdb = SenSqlite(self.conn)
        self.mdb = MeanSqlite(self.conn)
        self.prepare()

    def ctrl_c(self, s, f):
        """
        必须两个参数，第一个是信号，第二个是signal模块下的frame object
        print '\nreceived signal: %s' % s
        """
        self.conn.commit()
        self.conn.close()
        try:
            input("\n")
        except RuntimeError:
            print()
            sys.exit(byebye)

    def prepare(self):
        """获取词库内容，与word对应词库的映射"""
        if self.info:
            dpath = os.path.join(self.path, database_dir)
            print(("database information in {}:\n".format(dpath)))
            filenames = []
            for fn, sf, fs in os.walk(dpath):
                for f in fs:
                    if ".txt" in f:
                        filenames.append(os.path.join(fn, f))
            for filename in sorted(filenames):
                size = len(re.findall("#[a-zA-Z].*?\n", open(filename).read()))
                print(("{}: {} words.".format(filename[len(dpath) + 1:],
                                              size)))
            sys.exit(byebye)
        self.dic = parse_dic(self.database)

    def delete_from_file(self, filename, word):
        """从词库删除单词,包括例句,读音"""
        try:
            # 获取词库内容
            dic = parse_dic(filename)
        except Exception:
            return
        # 从词库删除
        if word in list(dic.keys()):
            dic.pop(word)
        # 重新写入词库
        with open(filename, 'w') as f:
            for w in list(dic.keys()):
                f.write("#" * 45 + "\n")
                f.write("#" + w + "\n")
                f.write(dic[w])

    def delete_audio(self, word):
        # 删除读音
        for filename in glob(
                os.path.join(self.path, audio_dir, word + "-*.mp3")):
            os.remove(filename)

    def delete_sentence(self, word):
        # 删除例句
        self.mdb.delete(word)
        self.sdb.delete(word)

    def delete(self, filename, word):
        self.delete_from_file(filename, word)
        # self.delete_audio(word)
        # self.delete_sentence(word)

    def next(self, word):
        """输出结果后的操作, 可删除单词"""
        s = input()
        if s == 'd':
            # 删除单词
            self.delete(self.database, word)
            self.temp_len += 1
            self.num_words -= 1
        elif s == 's':
            """play sound again"""
            if not self.mute:
                play_mp3(self.path, word, show_tag=False)
                self.next(word)
        elif s == 'n':
            try:
                sen = self.sdb.query(word)['col_ens'][0]
            except Exception:
                sen = ""
            os.system('''notify-send "{}" "{}"'''.format(word, sen))
        elif s == 'v':
            self.next(word)
        elif s == 'm':
            other_dic_urls(word)
            input()
        elif s in ['h', 'help']:
            print((
                "-----------input choice -------------\n" + "{}\n" * 6).format(
                    "d: delete word from database.", "s: play sound again.",
                    "n: add word to notify-send.", "m: more dic urls.", "h: help.", "q: exit.",
                    "enter: next word."))
            print("input:", end="")
            self.next(word)
        elif s in ['q', 'exit']:
            print()
            sys.exit(byebye)
        else:
            pass

    def query(self, word, lighten=True):
        """获取释义与中英例句"""
        meanings = self.dic[word]
        query = self.sdb.query(word)
        if query is not None:
            res_dic = query
        else:
            if self.wdriver is None:
                self.wdriver = Webdriver()
            res_dic = get_sentence_from_source_page(
                self.wdriver.source_page(word), word)
            self.sdb.add(word, res_dic)
        res = format_sentence(word, res_dic, lighten=lighten)
        return meanings, res

    def print_thing(self, idx, word):
        meanings, sentences = self.query(word)
        """打印"""
        # 标题
        head = "[Review " + str(idx + 1 - self.temp_len) + \
            " of " + str(self.num_words) + " words]"
        if self.dictation:
            head += " - [dictation mode]"
        head += " - [{}]".format(
            os.path.basename(os.path.splitext(self.database)[0]))
        print(myformat.format(head))
        # 单词
        print()
        print('', end=' ')
        if not self.dictation:
            print(word)
        else:
            if not self.mute:
                play_mp3(self.path, word, show_tag=False)
            print("*" * len(word))
        # 释义
        for l in meanings.split("\n"):
            print("  {:<}".format(l))
        print('')

        temp = "lovezn"
        if self.dictation:
            try_t = 2
            while temp != word and try_t != 0:
                temp = input()
                try_t -= 1
                if temp.strip() == "":
                    try_t = 0
            print()
        if temp == word:
            print("~~~~ {:s} ~~~~\n".format("well done!"))
        elif temp == "lovezn":
            pass
        else:
            print("-->> {:s} <<--\n".format(word))
        if sentences == []:
            print('[*] cannot find sentence file of this word.')
        else:
            print(sentences)
        print()
        # play sound.
        if not self.mute and not self.dictation:
            play_mp3(self.path, word, show_tag=False)

    def review(self):
        """复习单词主函数"""
        # 设置信号中断
        signal.signal(signal.SIGINT, self.ctrl_c)
        # 打乱单词顺序
        keys = list(self.dic.keys())
        random.shuffle(keys)
        # 实时变动单词排序的临时变量
        self.temp_len = 0
        self.num_words = len(keys)
        k, N = 0, self.number
        while True:
            start = k * N
            if (k + 1) * N < len(keys):
                tmpkeys = keys[start:N * (k + 1)]
            else:
                tmpkeys = keys[start:]
            if tmpkeys == []:
                break
            ns, idxs, words = [], [], []
            if N != 1:
                os.system(order_clear)
                for idx, word in enumerate(tmpkeys):
                    print("{}: {}".format(idx, word))
                ns = input("\ninput:")
                if ns == '':
                    idxs, words = [], []
                elif ns == 'a':
                    idxs = [k * N + n for n in range(len(tmpkeys))]
                    words = tmpkeys
                else:
                    ns = ns.split()
                    ns = [int(n.strip()) for n in ns if n.strip().isdigit()]
                    idxs = [k * N + n for n in ns]
                    words = [tmpkeys[n] for n in ns]
            else:
                idxs = [k]
                words = [keys[k]]
            for idx, word in zip(idxs, words):
                os.system(order_clear)
                if self.logo:
                    os.system(order_logo_review)
                self.print_thing(idx, word)
                # 可执行发音，删除等命令
                self.next(word)
            k += 1
        print("[+] reivew completed, You get it.")
        sys.exit(byebye)


if __name__ == '__main__':
    r = Review()
    r.review()
