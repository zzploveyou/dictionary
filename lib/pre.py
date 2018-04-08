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

URLs = (("*Thesaurus", "https://www.freethesaurus.com/",
         "+"), ("*Idioms", "https://idioms.thefreedictionary.com/",
                "+"), ("Oxford",
                       "https://en.oxforddictionaries.com/definition/", "_"),
        ("Cambridge",
         "https://dictionary.cambridge.org/us/dictionary/english/", "-"),
        ("Collins", "https://www.collinsdictionary.com/dictionary/english/",
         "-"), ("Longman", "https://www.ldoceonline.com/dictionary/", "-"),
        ("Acronyms", "https://acronyms.thefreedictionary.com/",
         "+"), ("Encyclopedia", "https://encyclopedia2.thefreedictionary.com/",
                "+"), ("Wikipedia",
                       "https://encyclopedia.thefreedictionary.com/", "+"))


def url(url, word, rep):
    "return dic url(replace space with `rep`"
    url += word.replace(" ", rep)
    return "\033[36m {}\033[0m".format(url)


def other_dic_urls(word, verbose=False):
    """print other dictionary urls for the specified word."""
    print("+----------------------- other Online Dictionaries  \
---------------------------+")
    for dic_name, dic_url, dic_rep in URLs:
        if dic_name.startswith("*"):
            if verbose is False:
                print("{:<10s} >>> {}".format(dic_name,
                                            url(dic_url, word, dic_rep)))
        else:
            if verbose is True:
                print("{:>12s} >>> {}".format(dic_name,
                                            url(dic_url, word, dic_rep)))
    print()


if __name__ == "__main__":
    other_dic_urls("communicate")
    other_dic_urls("communicate", verbose=True)
