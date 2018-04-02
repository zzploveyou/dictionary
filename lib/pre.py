'''
configs.
'''
myformat = '{0: <75}'
byebye = "\n^-^ byebye~~\n"
audio_dir = "audio"
database_dir = "database"

order_clear = "clear"
order_logo_dic = " ".join(["figlet", "Dic for God"])
order_logo_review = " ".join(["figlet", "Review for God"])


def url(url, word, rep):
    "return dic url(replace space with `rep`"
    url += word.replace(" ", rep)
    return ">>>\033[36m {}\033[0m".format(url)


def other_dic_urls(word):
    """print other dictionary urls for the specified word."""
    print(
        "+----------------------- other Online Dictionaries  \
---------------------------+"
    )
    print(url("https://dictionary.cambridge.org/us/dictionary/english/",
              word, rep="-"))
    print(url("https://en.oxforddictionaries.com/definition/",
              word, rep="_"))
    print(url("https://www.collinsdictionary.com/dictionary/english/",
              word, rep="-"))
    print()
