# 安装
>
1. ```pip3 install -r requirements.txt```
2. 需要firefox --headless及geckodriver的支持，如无，则修改lib/driver.py并运行lib/jscb.py通过测试也可。
3. database/dic.db[下载地址](https://pan.baidu.com/s/1L1XwrMZxEuJ7HWOeASChfw)   **n841**

---

# 简介

**author**: Zhaopeng Zhang

**usage**: 

从金山词霸网站爬取单词释义, 例句等内容，并存入单词库

1. 单词释义等存入指定单词库文本文件
2. 单词发音mp3文件存入音频文件夹
3. 单词例句及英文释义例句存入database/dic.db

查询单词
>
1. 音标
2. 词性
3. 释义
4. 发音
5. 例句

复习单词
>
1. 默写

---

# 注意

```
alias 'dic'='python dic.py'
alias 'review'='python review.py'

or

alias 'dic'='python dic.py -esu
alias 'review'='python review.py -esu'
```

# 用法

## 查询单词

```
# 有例句且专家模式
dic -es

# 查询单个单词
dic -w hello

#进入查询模式
dic

# 指定存入词库查询
dic -d TOEFL/list01

# 创建单词库的方法
ls *.txt | parallel -j 4 "python3 dic.py -es -d {}.txt -f {} --db {}.db"
```

## 复习单词
```
# 复习default database
review

# 指定词库复习，database下存在TOEFL/list01.txt
review -d TOEFL/list01

# 听写模式
review -t

更多用法python review.py -h / review -h
```
