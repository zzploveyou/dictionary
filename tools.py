"""
several tools for this dictionary project.

Examples
------------------------------------------
1. delete null audio file.
2. download audio from sqlite db.
3. merge sqlite db.
4. pop null item from sqlite db.
5. get information of size of sqlite db.
6. retrieve word meanings from sqlite db.
------------------------------------------
"""
from urllib.request import urlretrieve
from urllib.error import HTTPError
import sqlite3
from glob import glob
import os
import argparse
import progressbar
from time import sleep
from lib.pre import audio_dir, database_dir
from lib.parser import parse_dic
from lib.jscb import get_meaning
from lib.sqlite import MeanSqlite

PATH = os.path.dirname(__file__)
DATABASE = os.path.join(PATH, database_dir, "dic.db")


def get_meanings_from_file(database, filename, tofile):
    conn = sqlite3.connect(database)
    mdb = MeanSqlite(conn)
    # read words list
    words_list = set()
    dic = parse_dic(filename)
    for i in dic:
        words_list.add(i)
    if words_list == set():
        with open(filename) as f:
            for line in f:
                words_list.add(line.strip())
    # write to tofile.
    bar = progressbar.ProgressBar()
    fw = open(tofile, 'a')
    for word in bar(words_list):
        results_static = get_meaning(word, mdb)[0]
        meanings = [i for i in results_static if not i.startswith("http:")]
        if meanings != []:
            fw.write("#" * 45 + "\n")
            fw.write("#" + word + "\n")
            for idx in range(len(meanings) - 1):
                fw.write("├── {}\n".format(meanings[idx]))
            fw.write("└── {}\n".format(meanings[-1]))
    conn.commit()
    conn.close()


def deletenull():
    """delete empty audio file."""
    global PATH
    for audio in glob(os.path.join(PATH, audio_dir, "*")):
        if os.path.getsize(audio) == 0:
            print("{} has been deleted since it's empty.".format(audio))
            os.remove(audio)


def download(database):
    """download mp3 from urls in sqlite db."""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    bar = progressbar.ProgressBar()

    def m1(word):
        return os.path.join(PATH, audio_dir, "{}-英.mp3".format(word))

    def m2(word):
        return os.path.join(PATH, audio_dir, "{}-美.mp3".format(word))

    mean = cursor.execute("select * from MEANING").fetchall()
    for word, rec in bar(mean):
        tag = 0
        for item in rec.split("\n"):
            if item.startswith("http:"):
                try:
                    if tag == 0:
                        if not os.path.exists(m1(word)):
                            urlretrieve(item, m1(word))
                        tag = 1
                    else:
                        if not os.path.exists(m2(word)):
                            urlretrieve(item, m2(word))
                except HTTPError:
                    sleep(10)
                except Exception:
                    pass


def size(cursor, head=""):
    "get size of table meaning and table sentence."
    print(head)
    num1, num2 = cursor.execute("select Count(*) from MEANING").fetchone(
    ), cursor.execute("select Count(*) from SENTENCE").fetchone()
    print("meanings : {}".format(num1))
    print("sentences: {}".format(num2))


def info(database):
    """print infomation of the specified db."""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    size(cursor, "size infomation:")
    conn.close()


def pop(database):
    """pop void value of the two table."""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    size(cursor, "before pop:")
    sql = """select name from sqlite_master where type='table' and name='SENTENCE'"""
    if cursor.execute(sql).fetchall() != []:
        sql = """delete from SENTENCE where sen_ens='' and sen_cns='' and col_ens='' and col_cns=''"""
        cursor.execute(sql)
    sql = """select name from sqlite_master where type='table' and name='MEANING'"""
    if cursor.execute(sql).fetchall() != []:
        sql = """delete from MEANING where meaning=''"""
        cursor.execute(sql)
    size(cursor, "after pop:")
    conn.commit()
    conn.close()


def res_database(database):
    """read whole content of db."""
    mean, sen = [], []
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    sql = """select name from sqlite_master where type='table' and name='MEANING'"""
    if cursor.execute(sql).fetchall() != []:
        sql = """select * from MEANING"""
        mean = cursor.execute(sql).fetchall()
    sql = """select name from sqlite_master where type='table' and name='SENTENCE'"""
    if cursor.execute(sql).fetchall() != []:
        sql = """select * from SENTENCE"""
        sen = cursor.execute(sql).fetchall()
    conn.close()
    return mean, sen


def merge(database):
    """merge other db to the specified db."""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    path = os.path.dirname(os.path.splitext(database)[0])
    add1, add2 = 0, 0
    for dbname in glob(os.path.join(path, "*.db")):
        if os.path.basename(dbname) != os.path.basename(database):
            print("merge {} into {}".format(dbname, database))
            mean, sen = res_database(dbname)
            for m in mean:
                try:
                    cursor.execute(
                        "insert into MEANING (word, meaning) values(?, ?)", m)
                    add1 += 1
                except sqlite3.IntegrityError:
                    pass
            for s in sen:
                try:
                    cursor.execute(
                        "insert into SENTENCE (word, sen_ens, sen_cns, col_ens, col_cns) values(?, ?, ?, ?, ?)",
                        s)
                    add2 += 1
                except sqlite3.IntegrityError:
                    pass
    print("Added item: {} of meanings, {} of sentences".format(add1, add2))
    num1, num2 = cursor.execute("select Count(*) from MEANING").fetchone(
    ), cursor.execute("select Count(*) from SENTENCE").fetchone()
    print("Now: {}, {}".format(num1, num2))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--database",
        type=str,
        default=DATABASE,
        help="specifty sqlite3 database name.")
    group = parser.add_argument_group("database")
    group.add_argument(
        "--pop", action='store_true', help="pop null item from '--database'.")
    group.add_argument(
        "--merge",
        action='store_true',
        help="merge other db to the '--database'.")
    group.add_argument(
        "--info",
        action='store_true',
        help="get size information of the '--database'.")
    group2 = parser.add_argument_group("audio")
    group2.add_argument(
        "--denull", action='store_true', help="delete null size mp3 file.")
    group2.add_argument(
        "--download_all_mp3",
        action='store_true',
        help="download all mp3 file from urls in '--database'.")
    group3 = parser.add_argument_group("retrieve words")
    group3.add_argument(
        "-i",
        "--input",
        dest="inputfile",
        help="input text file, each line is a word.")
    group3.add_argument(
        "-o",
        "--output",
        dest="outputfile",
        help="output text file, contains meanings of words in inputlist.")
    args = parser.parse_args()
    # print(vars(args))
    if args.pop \
            and args.database is not None:
        pop(args.database)
    if args.merge \
            and args.database is not None:
        merge(args.database)
    if args.info \
            and args.database is not None:
        info(args.database)
    if args.denull:
        deletenull()
    if args.download_all_mp3 \
            and args.database is not None:
        download(args.database)
    if args.inputfile is not None \
            and args.outputfile is not None \
            and args.database is not None:
        get_meanings_from_file(args.database, args.inputfile, args.outputfile)
