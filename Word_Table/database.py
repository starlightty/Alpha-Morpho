import pandas as pd


def get_data(word):
    dic_re = {"word_table": [], "root_table": []}
    dataframe_original = pd.read_csv(r'expand_MophoLEX_set.csv')
    # 然后查询的话
    # word = 'sense'  # 这里传查询的单词
    df_word = dataframe_original[dataframe_original['word'] == word]  # 这里就是把word列的值 为 上面传过来的word字符串的 获取为列表（就相当于需求一是不）

    data_pd = pd.DataFrame(df_word, columns=["pos", "derivationa_prefix", "root",
                                             "derivational_suffix",
                                             "inflectional_type", "inflectional_suffix"])
    # print(data_pd)
    d_records = data_pd.to_dict('records')
    # print(d_records)
    dic_re["word_table"] = d_records

    # 查root
    data_pd_root = pd.DataFrame(df_word, columns=["root"])
    data_pd_root.drop_duplicates(['root'], keep='first', inplace=True)
    d_records_root = data_pd_root.to_dict('records')
    root_list = [item["root"] for item in d_records_root]
    df_word_root = dataframe_original[
        (dataframe_original['root'].isin(root_list)) & (dataframe_original['type'] == "base")]
    data_pd_root_sub = pd.DataFrame(df_word_root, columns=["word", "root"])
    d_records_root_sub = data_pd_root_sub.to_dict('records')
    # print(d_records_root_sub)
    dic_re["root_table"] = d_records_root_sub


    return dic_re


def to_none(value):
    if value == "nan":
        return None
    else:
        return value
