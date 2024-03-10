# 汉字转索引编码
from File_Util import chinese_to_idx_json,chinese_to_idx_path
# 索引转汉字解码
from File_Util import idx_to_chinese_json,idx_to_chinese_path
# 标签转索引编码
from File_Util import abbrtag_to_index_json
from File_Util import update_json_reverse
from config import json_log_config
start_idx = 0
start_key = '<start>'
stop_idx = 10000000
stop_key = '<stop>'

# 对每个字进行编码
def encode_word(all_text_tag,chinese_to_idx_json=chinese_to_idx_json,abbrtag_to_index_json=abbrtag_to_index_json,
                chinese_to_idx_path=chinese_to_idx_path,idx_to_chinese_path=idx_to_chinese_path):
    '''
    对汉字和标签进行编码
    :param all_text_tag: list[[]]类型，单个元素为[字，标签]
    :param chinese_to_idx_json: 汉字转索引编码
    :param abbrtag_to_index_json:  简写标签转索引编码
    :param chinese_to_idx_path: 汉字转索引编码路径
    :param idx_to_chinese_path: 索引转汉字编码路径，用于纠错时反写更新词典
    :return: list[[]]类型，单个元素为[字对映的映射，标签对映的映射]
    '''
    word_tag_idx_list = []
    # 对每个句子进行编码
    for text_tag in all_text_tag:
        text = text_tag[0]
        tag = text_tag[1]
        word_tag_idx = list(range(1, 3))
        try:
            # 汉字转索引
            text_index = chinese_to_idx_json[text]
        except Exception:
            # 未找到对应字典时，纠错
            # 将字典转换为包含键值对的列表
            dict_items = list(chinese_to_idx_json.items())
            # 获取列表的最后一个元素（即字典的最后一个键值对）
            last_dict_item = dict_items[-1]
            text_index = last_dict_item[1]
            # 字典变量更新
            chinese_to_idx_json[text] = text_index + 1
            print(f"{text}解码有误，已将汉字{text}添加到字典中，对应索引为{text_index+1}")
            json_log_config.error(f"{text}解码有误，已将汉字{text}添加到字典中，对应索引为{text_index+1}")
            # 本地词典同步更新
            update_json_reverse(chinese_to_idx_path,chinese_to_idx_json,True,idx_to_chinese_path)
        try:
            # 标签转索引
            tag_index = abbrtag_to_index_json[tag]
        except Exception:
            print(f"标签{tag}解码有误")
            json_log_config.error(f"标签{tag}解码有误")
        word_tag_idx[0] = text_index
        word_tag_idx[1] = tag_index
        word_tag_idx_list.append(word_tag_idx)
    # print(word_to_idx)
    return word_tag_idx_list
# 对每个字进行解码
def decode_word(word_to_idx, is_test = True):
    # 加载预训练的Tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
    # word_to_idx : word : tag 测试时为 word : idx
    # idx_to_word : tag : word 测试时为 idx : word，测试出来的word和后面的word相同证明成功
    idx_to_word = {v: k for k, v in word_to_idx.items() if k in word_to_idx}
    decoded_sentences = {}
    print(idx_to_word)
    for idx,word in idx_to_word.items():
        if idx == start_idx :
            decoded_text = start_key
        elif idx == stop_idx:
            decoded_text = stop_key
        else:
            decoded_text = tokenizer.decode([idx-1])
            if decoded_text != word:
                print(f"第{idx}号解码有误，应解析为{word},实解析为{decoded_text}")
        decoded_sentences[decoded_text] = word
    return decoded_sentences





