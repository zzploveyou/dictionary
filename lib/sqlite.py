import sqlite3
from time import sleep


class MeanSqlite(object):
    """
    meaning db handler(without commit).

    Members
    -------
    query(self, word)
        query meaning of word, return a list.
        if word not in db, return None.
    add(self, word, meaning)
        insert word, meaning into database.
    """

    def __init__(self, conn):
        """
        construct the class.

        Parameters
        ----------
        conn: sqlite3.Connection.
        """
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """query the existance of table."""
        sql = """select name from sqlite_master where type='table' and name='MEANING'"""
        if self.cursor.execute(sql).fetchall() == []:
            sql = """create table MEANING (word text unique, meaning text)"""
            self.cursor.execute(sql)
            self.conn.commit()

    def wordlist(self):
        sql = """select * from MEANING"""
        return set([i[0] for i in self.cursor.execute(sql).fetchall()])

    def query(self, word):
        """query meaning."""
        sql = "select * from MEANING where word=?"
        try:
            meaning = self.cursor.execute(sql, (word, )).fetchone()[1]
        except TypeError:
            return None
        return meaning.split("\n")

    def delete(self, word):
        """delete from table."""
        sql = """delete from MEANING where word=?"""
        try:
            self.cursor.execute(sql, (word, ))
        except Exception as e:
            print("Exception: {}".format(e))

    def add(self, word, meaning):
        """insert into db."""
        meaning = "\n".join(meaning)
        try:
            self.cursor.execute(
                "insert into MEANING (word, meaning) values(?, ?)",
                (word, meaning))
        except sqlite3.OperationalError:
            sleep(1)
            self.add(word, meaning)


class SenSqlite(object):
    """
    sentence db handler(without commit).

    Members
    -------
    query(self, word)
        query meaning of word, return a list.
        if word not in db, return None.
    add(self, word, sendic)
        insert word, meaning into database.
    """

    def __init__(self, conn):
        """
        construct the class.

        Parameters
        ----------
        conn: sqlite3.Connection.
        """
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """query the existance of table."""
        sql = """select name from sqlite_master where type='table' and name='SENTENCE'"""
        if self.cursor.execute(sql).fetchall() == []:
            sql = """create table SENTENCE (word text unique, sen_ens text, sen_cns text, col_ens text, col_cns text)"""
            self.cursor.execute(sql)
            self.conn.commit()

    def query(self, word):
        """query sentences."""
        try:
            word, sen_ens, sen_cns, col_ens, col_cns = self.cursor.execute(
                "select * from SENTENCE where word=?", (word, )).fetchone()
            sen_ens = sen_ens.split("\n")
            sen_cns = sen_cns.split("\n")
            col_ens = col_ens.split("\n")
            col_cns = col_cns.split("\n")
        except TypeError:
            return None
        return {
            'sen_ens': sen_ens,
            'sen_cns': sen_cns,
            'col_ens': col_ens,
            'col_cns': col_cns
        }

    def wordlist(self):
        sql = """select * from SENTENCE"""
        return set([i[0] for i in self.cursor.execute(sql).fetchall()])

    def delete(self, word):
        """delete from table."""
        sql = """delete from MEANING where word=?"""
        try:
            self.cursor.execute(sql, (word, ))
        except Exception as e:
            print("Exception: {}".format(e))

    def add(self, word, sendic):
        """insert into db."""
        sen_ens = "\n".join(sendic['sen_ens'])
        sen_cns = "\n".join(sendic['sen_cns'])
        col_ens = "\n".join(sendic['col_ens'])
        col_cns = "\n".join(sendic['col_cns'])
        self.cursor.execute(
            "insert into SENTENCE (word, sen_ens, sen_cns, col_ens, col_cns) values(?, ?, ?, ?, ?)",
            (word, sen_ens, sen_cns, col_ens, col_cns))
