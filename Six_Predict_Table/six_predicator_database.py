import os
# import spacy
import re
import pandas as pd
import numpy as np
from typing import List
from collections import Counter


def get_morpheme(list, dicts):
    """

    @rtype: object
    """
    number_of_nonexisted_words = 0
    affixlist = []
    wordlist = []
    for word in list:
        for dict in dicts:
            if word == dict['word']:
                for prefix in dict['prefix'].split(';'):
                    if prefix != "":
                        affixlist.append(prefix)
                        wordlist.append(word)
                for root in dict['root'].split(';'):
                    if root != "":
                        affixlist.append(root)
                        wordlist.append(word)
                for suffix in dict['suffix'].split(';'):
                    if suffix != "":
                        affixlist.append(suffix)
                        wordlist.append(word)
    j = 0
    dictofmorpheme = {}
    while j < len(affixlist):
        if affixlist[j] not in dictofmorpheme.keys():
            wordlist_of_same_affix = []
            k = 0
            while k < len(wordlist):
                if affixlist[k] == affixlist[j]:
                    wordlist_of_same_affix.append(wordlist[k])
                k += 1
            dictofmorpheme.setdefault(affixlist[j], []).extend(wordlist_of_same_affix)
        j += 1
    hapax = []
    PTMF = {}
    sum_token_frequency = {}
    wordfamily = {}
    P = {}
    PP = {}
    n_of_all_hapax = 0
    for values in dictofmorpheme.values():
        if len(values) == 1:
            n_of_all_hapax += 1
    for keys, values in dictofmorpheme.items():
        n_of_hapax_of_morpheme = 0
        if len(values) == 1:
            hapax.append(values)
            n_of_hapax_of_morpheme += 1
        sum_token_frequency[keys] = len(values)
        wordfamily[keys] = len((set(values)))
        P[keys] = n_of_hapax_of_morpheme / len(values)
        if n_of_all_hapax != 0:
            PP[keys] = n_of_hapax_of_morpheme / n_of_all_hapax
        word_freq = {}
        for word in values:
            word_freq[word] = word_freq.get(word, 0) + 1
        list_of_word_family = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        PT = 0
        i = 0
        word = ''
        if len(list_of_word_family) > 1:
            while i < len(list_of_word_family):
                if i == 0:
                    PT += (i - 1) / (len(values) - 1)
                if i > 0:
                    PT += list_of_word_family[i - 1][1] / (len(values) - 1)
                i += 1
        PTMF[keys] = PT
    all = []
    for keys in sum_token_frequency:
        six_predictors = {
            'keys': keys,
            'morpheme': dictofmorpheme[keys],
            'sum_token_frequency': sum_token_frequency[keys],
            'wordfamily': wordfamily[keys],
            'P': P[keys],
            'P*': PP[keys],
            'PTMF': PTMF[keys]
        }
        all.append(six_predictors)

    return all


def divide_morphemes(df, type):
    condition = df[type].str.contains(';')
    df1 = df[~condition]
    df = df[condition]
    df2 = pd.DataFrame(columns=['word', type])
    for (_, r) in df.iterrows():
        prefix_list = r[type].split(';')
        for prefix in prefix_list:
            word = r['word']
            newR = pd.DataFrame(data={'word': [word], type: [prefix]})
            df2 = pd.merge(df2, newR, how='outer')
    df2.reset_index()
    df = pd.merge(df1, df2, how='outer')
    return df


def unique_word(df, hapax_frame, n_all_hapax):
    """
    @df:每个prefix分组后的dataframe
    """
    word_list = df['word'].tolist()
    sum_token_frequency = df['word'].count()
    df["sum_token_frequency"] = sum_token_frequency
    df['word_family'] = df['word'].nunique()
    list = np.unique(word_list, return_counts=True)[1]
    PMPF = 0
    for x in list:
        PMPF += (x - 1) / (sum_token_frequency - 1)
    df['PMPF'] = PMPF
    hapax_word_in_word_list = pd.merge(df, hapax_frame, how="inner")
    df["hapax_word_in_word_list"] = hapax_word_in_word_list['word'].count()
    df["P"] = df["hapax_word_in_word_list"] / sum_token_frequency
    df["P*"] = df["hapax_word_in_word_list"] / n_all_hapax
    # df['new_rt_mean'] = df['rt_mean'].mean()
    return df


def count_morpheme(list):
    newlist = []
    for morpheme in list:
        # 不能为空
        if str(morpheme) != 'nan':
            for m in str(morpheme).split(';'):
                newlist.append(m)
    res = pd.DataFrame.from_dict(dict(Counter(newlist)), orient='index')
    res.columns = ['pre_frequency']
    res['pre_affix'] = res.index
    res.loc[:, ['affix', 'frequency']] = res[['pre_affix', 'pre_frequency']].values
    res = res.drop(labels=['pre_frequency', 'pre_affix'], axis=1)
    return res


def combine_dataframe(dataframe, type):
    '''

    :param dataframe:
    :param type: 'derivational_prefix'
    :return:
    '''
    affix = dataframe[type].tolist()
    frequency_of_affix = count_morpheme(affix)
    word_of_affix = divide_morphemes(dataframe[['word', type]].dropna(),
                                     type).groupby(type).apply(
        lambda x: set(x['word'].tolist()))
    word_of_affix = word_of_affix.reset_index()
    word_of_affix.columns = ['affix', 'word']
    res_affix = pd.merge(frequency_of_affix, word_of_affix, how='right')
    return res_affix


def get_wordlist_sole(file: str) -> pd.DataFrame:
    """
    函数的功能……
    :param target_dir:
    :param files:
    :return:dataframe
    """

    BNCwordlist = []
    file_in = open(file, "r", encoding="utf-8")
    for line in file_in.readlines():
        for word in line.strip().split(" "):
            word1 = re.sub(r"[^a-zA-Z\s]+", "", word)
            BNCwordlist.append(word1)
    wordlist = pd.DataFrame({"word": BNCwordlist})
    return wordlist

def data_base(file):
    dataframe_original = pd.read_csv(r'expand_MophoLEX_set.csv')
    d_re_six = {"count_sub_list": [], "res_prefix_list": [], "res_root_list": [],
                "res_suffix_list": [], "all_frame_list": []}
    count_sub_list = []
    res_prefix_list = []
    res_root_list = []
    res_suffix_list = []
    all_frame_list = []

    dataframe = pd.merge(get_wordlist_sole(file), dataframe_original, how='left')
    count_all = dataframe['word'].count()
    # # root 为空值的地方筛选排除
    dataframe = dataframe.loc[dataframe['root'].notnull(), :]
    # # 获得该词表对文本的覆盖率
    count_sub = dataframe['word'].count()
    coverage = count_sub / count_all
    count = {"count_sub": count_sub, "count_all": count_all, "coverage": '{:.2%}'.format(coverage)}
    count_sub_list.append(count)
    d_re_six["count_sub_list"] = count_sub_list
    # print("覆盖词数", count_sub, "总词数", count_all, "覆盖率", '{:.2%}'.format(coverage))
    # 显示所有前缀、词根、后缀 频率及对应词
    res_prefix = combine_dataframe(dataframe, 'derivationa_prefix')
    d_res_prefix = res_prefix.to_dict('records')
    res_prefix_list.append(d_res_prefix)
    d_re_six["res_prefix_list"] = res_prefix_list
    # print("前缀对应频率词汇", d_res_prefix)
    res_root = combine_dataframe(dataframe, 'root')
    d_res_root = res_root.to_dict('records')
    res_root_list.append(d_res_root)
    d_re_six["res_root_list"] = res_root_list
    # print("词根对应频率词汇", d_res_root)
    res_suffix = combine_dataframe(dataframe, 'derivational_suffix')
    d_res_suffix = res_suffix.to_dict('records')
    res_suffix_list.append(d_res_suffix)
    d_re_six["res_suffix_list"] = res_suffix_list
    # print("后缀对应频率词汇", d_res_suffix)
    # 获得所有罕见词(frequency = 1)
    frequency_frame = pd.DataFrame(dataframe['word'].value_counts()).reset_index()
    frequency_frame.columns = ['word', 'frequency']
    hapax_frame = frequency_frame.loc[(frequency_frame['frequency'] == 1)]
    n_all_hapax = hapax_frame['word'].count()
    # group by 获得新列表
    prefix_frame = dataframe.loc[:, ['word', 'derivationa_prefix']]
    condition = prefix_frame['derivationa_prefix'].notnull()
    prefix_frame = prefix_frame[condition]
    prefix_frame = divide_morphemes(prefix_frame, 'derivationa_prefix')
    prefix_frame = prefix_frame.groupby('derivationa_prefix').apply(unique_word, hapax_frame, n_all_hapax)
    prefix_frame["affix_length"] = prefix_frame['derivationa_prefix'].str.len()
    prefix_frame = prefix_frame.drop('word', axis=1)
    prefix_frame = prefix_frame.drop_duplicates(subset='derivationa_prefix')
    prefix_frame['type'] = 'prefix'
    prefix_frame.columns = ["morpheme", "sum_token_frequency", "word_family", "PMPF", "hapax_word_in_word_list",
                            "P", "P*", "affix_length", "type"]
    '输出prefix 六项指标'
    suffix_frame = dataframe.loc[:, ['word', 'derivational_suffix']]
    condition = suffix_frame['derivational_suffix'].notnull()
    suffix_frame = suffix_frame[condition]
    suffix_frame = divide_morphemes(suffix_frame, 'derivational_suffix')
    suffix_frame = suffix_frame.groupby('derivational_suffix').apply(unique_word, hapax_frame, n_all_hapax)
    suffix_frame["affix_length"] = suffix_frame['derivational_suffix'].str.len()
    # suffix_frame["new_rt_mean"] = suffix_frame['rt_mean'].mean()
    suffix_frame = suffix_frame.drop('word', axis=1)
    suffix_frame = suffix_frame.drop_duplicates(subset='derivational_suffix')
    suffix_frame['type'] = 'suffix'
    suffix_frame.columns = ["morpheme", "sum_token_frequency", "word_family", "PMPF", "hapax_word_in_word_list",
                            "P", "P*", "affix_length", "type"]
    '输出suffix六项指标'
    affix_frame = pd.concat([prefix_frame, suffix_frame], axis=0, join='outer')
    root_frame = dataframe.loc[:, ['word', 'root']]
    root_frame = divide_morphemes(root_frame, 'root')
    root_frame = root_frame.groupby('root').apply(unique_word, hapax_frame, n_all_hapax)
    root_frame["affix_length"] = root_frame['root'].str.len()
    root_frame = root_frame.drop('word', axis=1)
    root_frame = root_frame.drop_duplicates(subset='root')
    root_frame['type'] = 'root'
    root_frame.columns = ["morpheme", "sum_token_frequency", "word_family", "PMPF", "hapax_word_in_word_list", "P",
                          "P*", "affix_length", "type"]
    '输出root 六项指标'
    all_frame = pd.concat([affix_frame, root_frame], axis=0, join='outer')
    d_all_frame = all_frame.to_dict('records')
    all_frame_list.append(d_all_frame)
    d_re_six["all_frame_list"] = all_frame_list
    # print('morphological complexity')
    # print(d_all_frame)
    # print('返回值')
    # print(d_re_six)
    return d_re_six


if __name__ == '__main__':
    path= ""
    data_base(path)
