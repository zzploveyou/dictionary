"""parse dic txt file."""
import os
import re


def parse_dic(filename):
    """获取单词对应文本库中内容, 返回一个单词到释义的映射"""
    dic = {}
    if os.path.exists(filename):
        content = open(filename, encoding="utf-8").read()
        # regex extract.
        for res in re.findall("#([^#]+?)\n([\s\S]*?)#|#([^#]+?)\n([\s\S]*)",
                              content):
            res = list(res)
            while "" in res:
                res.remove("")
            dic[res[0]] = res[1]
    return dic


def split_database(filename, num):
    """split database format file into several son files."""
    b, f = os.path.splitext(filename)
    dic = parse_dic(filename)
    keys = list(dic.keys())
    print(("before split: {} words".format(len(keys))))
    step = len(keys) / num
    total = 0
    for i in range(1, num + 1):
        son = b + "-{}".format(i) + f
        n = 0
        start = step * (i - 1)
        end = step * i
        if i == num:
            end = len(keys)
        with open(son, 'w') as fw:
            for word in keys[start:end]:
                n += 1
                fw.write("#" * 45 + "\n")
                fw.write("#{}\n".format(word))
                fw.write(dic[word])
        total += n
        print(("{}: {} words.".format(son, n)))
    print(("total: {}".format(total)))


if __name__ == '__main__':
    split_database("../database/IELTS2.txt", 30)
