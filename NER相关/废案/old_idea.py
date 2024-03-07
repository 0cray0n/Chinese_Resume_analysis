import logging
import json
import os

def build_json_from_old_one(old_json_path, new_json_path):
    # 打开旧的JSON文件并加载其内容
    with open(old_json_path, 'r') as old_json:
        old_data = json.load(old_json)
    # 初始化新的数据字典，用于存储处理后的数据
    new_data = {}
    # 遍历旧数据字典中的每一项
    for name, info in old_data.items():
        # 初始化新信息字典，用于存储当前项处理后的信息
        new_info = {}
        # 再次遍历当前项的信息字典
        for key, value in info.items():
            # 如果key不是特定的三个类别之一，则直接复制到新信息字典中
            if key not in {'教育经历', '工作经历', '项目经历'}:
                new_info[key] = value
            else:
                # 如果key是特定的三个类别之一，需要进一步处理
                for d in value:  # 遍历包含多个字典的列表，每个字典代表一条记录
                    for k, v in d.items():  # 遍历记录中的每个键值对
                        if k not in new_info:
                            # 如果新信息字典中还没有这个键，初始化为一个空列表
                            new_info[k] = []
                        # 将值添加到对应键的列表中
                        new_info[k].append(v)
        # 将处理后的信息字典与其标识符一起存储到新数据字典中
        new_data[name] = new_info
    # 将新数据字典保存到新的JSON文件中
    with open(new_json_path, 'w', encoding='utf-8') as new_json:
        json.dump(new_data, new_json, ensure_ascii=False)


# 初始标注信息
def tagging2txt(pdf_dir='PDF_DIR', tag_file_path='Corpus_Path/Chinese_key_mapping.json', txt_path='Corpus_Path/Txt'):
    # 配置日志记录，便于调试和追踪
    logging.basicConfig(level=logging.INFO, filename='../Document/log.txt', format='%(message)s')
    from Util import util
    txt_path = util.get_date_filename(txt_path)
    # 获取PDF目录下所有文件的列表
    pdf_path_list = os.listdir(pdf_dir)
    # 打开语料库文件夹并读取包含标签信息的JSON文件,
    with open(tag_file_path, 'r', encoding='utf-8') as file:
        tag_to_biname = json.load(file)
    # 遍历目录中的每个PDF文件
    for p in pdf_path_list:
        if p.endswith('.pdf'):  # 确保处理的是PDF文件
            pdf_name = p[:-4]  # 移除文件扩展名，获取PDF文件名
            pdf_path = os.path.join(pdf_dir, p)  # 构建完整的PDF文件路径
            # 提取PDF文件中的文本内容
            content = util.get_str_from_pdf(pdf_path)
            # 初始化文本标注数组，初始值为'o'，表示其他/未标注
            con_to_tag = ['o'] * len(content)
            # 遍历标签信息，将标签应用到文本上
            for tag, keywords in tag_to_biname.items():
                for keyword in keywords:  # 直接遍历关键词列表
                    start_idx = content.find(keyword)
                    while start_idx != -1:  # 找到关键词
                        # 应用开始标签和内部标签
                        con_to_tag[start_idx] = 'b-' + tag
                        for i in range(start_idx + 1, start_idx + len(keyword)):
                            con_to_tag[i] = 'i-' + tag
                        # 继续查找下一个匹配项
                        start_idx = content.find(keyword, start_idx + 1)
            # 确保文本长度和标注数组长度一致
            assert len(content) == len(con_to_tag)
            # 将标注好的文本写入文件，每个字符及其标注为一行
            with open(txt_path, 'w',encoding='utf-8') as txt_file:
                for i in range(len(content)):
                    txt_file.write(content[i] + ' ' + con_to_tag[i] + '\n')
                txt_file.write('\n')  # 不同PDF文件的内容之间添加空行分隔
tagging2txt()



def marking_tag(json_text,txt_text,key_mapping=key_mapping,log_info="101",is_idx=False):
    """
    打标记
    :param json_text: 原始标注好的json文件
    :param txt_text: 原始文本
    :param key_mapping: 简写映射
    :param log_info: 日志文本
    :return:
    """
    import re
    from Util.util import get_index_by_automaton,get_log_config,get_text_index
    from pprint import pprint
    log_config = get_log_config()
    all_tag_list = []
    # 遍历一级结构字典
    # pprint(json_text)
    for key, value in json_text.items():
        if isinstance(value, str):  # 如果字段值是字符串，则直接添加
            new_key = key_mapping[key]
            for split_tag in get_text_index(value,new_key,txt_text,log_info):
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
                    split_tag_list = get_text_index(sub_value,new_key,txt_text,log_info)
                    pprint(split_tag_list)
                    # print(index,item)
                    for split_tag in split_tag_list:
                        all_tag_list.append(split_tag)
    return all_tag_list
all_tag = marking_tag(ner_json,text)
from pprint import pprint
pprint(all_tag)
