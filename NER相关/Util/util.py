import sys
sys.path.append('./Util')
import os
import json
import re
from File_Util import get_json_info, get_log_config, get_text_from_txt
from pprint import pprint

PDF_DIR = './PDF_DIR'
PDF_TEST_DIR = './PDF_TEST'
# 保存结果
CORPUS_PATH = './Corpus_Path'
# 缩写映射
key_mapping_path = './Corpus_Path/key_mapping.json'
key_mapping = get_json_info(key_mapping_path)

# 将以及打好标记的词语进行分析，将每个字进行标记头部和尾部
def marking_character_tag(all_tag,text,dirpath):
    '''
    将以及打好标记的词语进行分析，将每个字进行标记头部和尾部
    :param all_tag: 所有打好标记的词语
    :param text: 原文本
    :param filepath: 文件夹目录
    :return:
    '''
    # 编码
    # 初始化标注列表
    tagged_text = ['O'] * len(text)

    # 更新标注信息
    for annotation in all_tag:
        for value, info in annotation.items():
            start, end, tag = info['start_index'], info['end_index'], info['tag']
            tagged_text[start] = 'B-' + tag  # 标记开始
            for i in range(start + 1, end + 1):
                tagged_text[i] = 'I-' + tag  # 标记内部

    # 生成最终的标注结果
    final_annotations = [[text[i], tagged_text[i]] for i in range(len(text))]
    # 打印结果
    # for item in final_annotations:
    #     print(f"{item[0]} {item[1]}")
    # tag 代表没有标注第几次经历下标和标注类别名字
    # tag_with_name 代表标注类别名字被标注
    # tag_with_idx 代表标注第几次经历下标
    # tag_wtih_idx_name 代表没有标注第几次经历下标和标注类别名字
    filepath = os.path.join(dirpath,'tag.txt')
    with open (filepath, 'w', encoding='utf-8') as f:
        for item in final_annotations:
            f.write(f"{item[0]} {item[1]}\n")
    print(f"标记已写入{filepath}")
    return final_annotations


# 给定标注好的json，将大段原始txt文本分为每一个词打标记
def marking_word_tag(json_text,txt_text,key_mapping=key_mapping,log_info="101",is_idx=False):
    """
    打标记
    :param json_text: 原始标注好的json文件
    :param txt_text: 原始文本
    :param key_mapping: 简写映射
    :param log_info: 日志文本
    :return:list类型，单个元素为
    """
    # from Util.util import get_index_by_automaton,get_log_config,get_text_tag
    all_tag_list = []
    # 遍历一级结构字典
    # pprint(json_text)
    for key, value in json_text.items():
        if isinstance(value, str):  # 如果字段值是字符串，则直接添加
            new_key = key_mapping[key]
            for split_tag in get_text_tag(value,new_key,txt_text,log_info):
                all_tag_list.append(split_tag)
        elif isinstance(value, list):
            # 遍历二级结构列表
            for (index,item) in enumerate(value):
                # 遍历字典
                for sub_key, sub_value in item.items():
                    if is_idx:
                        # 带idx的
                        new_key = key_mapping[key]+"_"+key_mapping[sub_key]+"_"+str(index)
                    else:
                        # 不带idx的
                        new_key = key_mapping[key]+"_"+key_mapping[sub_key]
                    split_tag_list = get_text_tag(sub_value,new_key,txt_text,log_info)
                    # pprint(split_tag_list)
                    # print(index,item)
                    for split_tag in split_tag_list:
                        all_tag_list.append(split_tag)
    return all_tag_list

# 一串字符串进行标注字段
def get_text_tag(search_string, tag, txt_text, log_info):
    """
    用于标注字段
    :param search_string:被查找的字符串,充当返回的key值，便于查找
    :param tag: 标注的标志
    :param txt_text: 大段文本内容
    :param loginfo: logging信息，文件名称便于定位错误信息
    :return:统一为list属性，取出时需遍历,单个元素为
    ”单个字“: {
        "start_index": start_idx,
        "end_index": end_idx,
        "tag": tag,
    }
    """
    log_config = get_log_config()
    # 变量初始化
    automaton_info = []
    # 若找得到文本
    if txt_text.find(search_string) != -1:
        start_idx = txt_text.find(search_string)
        end_idx = start_idx + len(search_string) - 1
        automaton_info = [{
            search_string: {
                "start_index": start_idx,
                "end_index": end_idx,
                "tag": tag,
            }
        }]
        log_config.info(f"{log_info}文件 {search_string} 标注为 {tag}")
        # print(automaton_info)
    # 找不到文本
    else:
        pattern = r'[、，。；：？！,.;:?!]'
        # 使用正则表达式分割文本
        segments = re.split(pattern, search_string)
        segments.pop()
        # print(segments)
        log_config.warning(f"{log_info}文件 {search_string} 标注为 :")
        log_config.error(f"{log_info}文件 {search_string} 未标注为 :")
        automaton_info = get_index_by_automaton(segments, tag, txt_text)
        # pprint(automaton_info)
    return automaton_info

# 通过自动机实例检索文本下标并带上标注
def get_index_by_automaton(segments, tag, txt_text):
    """
    通过自动机实例检索文本下标并带上标注
    :param segments: 列表文本
    :param tag: 标记
    :param txt_text: 大段文本
    :return:list属性，单个元素为
    “分词”: {
        "start_index": start_idx,
        "end_index": end_idx,
        "tag": tag,
    }
    """
    import ahocorasick
    log_config = get_log_config()
    # 创建 Aho-Corasick 自动机实例
    A = ahocorasick.Automaton()
    # 将列表中的每个文本项添加到自动机中作为模式
    for idx, pattern in enumerate(segments):
        A.add_word(pattern, (idx, pattern))
    # 构建自动机
    A.make_automaton()
    found_patterns = set()  # 用于存储找到的模式
    all_split_text = []
    # 遍历txt_text大段文字，查找列表中的文本
    for end_idx, (pattern_idx, pattern) in A.iter(txt_text):
        start_idx = end_idx - len(pattern) + 1
        split_text = {
            pattern: {
                "start_index": start_idx,
                "end_index": end_idx,
                "tag": tag,
            }
        }
        # print(split_text)
        log_config.warning(f"分词:{split_text} 标注为 {tag}")
        all_split_text.append(split_text)
        found_patterns.add(pattern)
    # 检查未找到的模式
    not_found_patterns = [pattern for pattern in segments if pattern not in found_patterns]
    # 处理未找到的模式
    for pattern in not_found_patterns:
        log_config.error(f"分词:{pattern} 未标注为 {tag}")
    return all_split_text


if __name__ == "__main__":
    pass




