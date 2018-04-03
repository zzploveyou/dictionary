"""
several tools for this dictionary project.

Examples
------------------------------------------
1. delete null audio file.
2. download audio from sqlite db.
3. merge sqlite db.
4. pop null item from sqlite db.
5. get information of size of sqlite db.
------------------------------------------
"""
from urllib.request import urlretrieve
from urllib.error import HTTPError
import sqlite3
from glob import glob
import os
import sys
import progressbar
from time import sleep
from lib.pre import audio_dir

PATH = os.path.dirname(__file__)


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
                except FileNotFoundError:
                    pass
                except HTTPError:
                    sleep(10)


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
    import argparse
    parser = argparse.ArgumentParser(
        description='''merge other database to a specified database,\n
        or pop null item from database.''')
    parser.add_argument(
        '-d', '--database', type=str, help='specify database name.')
    parser.add_argument(
        '--pop', action='store_true', help='pop null item from "--database".')
    parser.add_argument(
        '--info', action='store_true', help='show info of "--database".')
    parser.add_argument(
        '--merge',
        action='store_true',
        help='merge other database into "--database".')
    parser.add_argument(
        '--deleteEmptyAudio',
        action='store_true',
        help="delete empty audio file.")
    parser.add_argument(
        '--downloadAudio',
        action='store_true',
        help="download audio file according to urls in sqlite db.")
    args = parser.parse_args()
    if args.deleteEmptyAudio:
        deletenull()
        sys.exit(0)
    if args.database is None:
        print("Usage: python {} -h".format(__file__))
        sys.exit(1)
    if args.downloadAudio:
        download(args.database)
    if args.info:
        info(args.database)
    if args.merge:
        merge(args.database)
    if args.pop:
        pop(args.database)
