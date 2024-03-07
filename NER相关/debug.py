from Util import util
from Util import File_Util
from pprint import pprint
import os

all_path = util.create_or_find_date_dir()
index = 0
for filename in os.listdir(all_path):
    # print(filename)
    major_path = os.path.join(all_path, filename)
    pdf_path = os.path.join(major_path,filename) + ".pdf"
    txt_path = os.path.join(major_path, filename) + ".txt"
    json_path = os.path.join(major_path, filename) + ".json"
    # print(file_pdf)
    if not os.path.exists(pdf_path):
        print("pdf不存在")
        continue
    text = File_Util.get_text_from_txt(txt_path,pdf_path)
    ner_json = File_Util.get_json_info(json_path)
    print(key_mapping)
    # 从标注好的json文件中映射原始文本索引
    json_index = util.marking_tag(ner_json,text,log_info=filename)
    pprint(json_index)
    # 标注好的json文件
    for key, value in ner_json.items():
        print(value)
    index = index + 1
    if index >= 1:
        break



# import torch
#
# model = torch.load('./Model_Save/latest_model.pth')
# print(model)

# from Util.Selenium_Util import Selenium_Edge
# edge_driver = Selenium_Edge(update=True)

import ahocorasick

# 假设 patterns 是您的文本列表，text 是您要搜索的大段文字

# import ahocorasick
#
# patterns = ['文本1', '文本2', '文本3']  # 待查找的文本列表
# text = "这里是一大段文字，包含了文本1和其他内容。"  # 大段待搜索的文字
#
# A = ahocorasick.Automaton()
#
# # 添加模式
# for pattern in patterns:
#     A.add_word(pattern, pattern)
#
# A.make_automaton()
#
# found_patterns = set()  # 用于记录找到的模式
#
# # 查找匹配
# for end_index, found_pattern in A.iter(text):
#     found_patterns.add(found_pattern)
#
# # 检查未找到的模式
# for pattern in patterns:
#     if pattern not in found_patterns:
#         print(f"'{pattern}' was not found in the text.")




# import json
#
# # 加载标注信息和源文本
# with open('./Corpus_Path/2024年03月03日15时01分/101/101.json', 'r', encoding='utf-8') as f:
#     annotations = json.load(f)
#
# with open('./Corpus_Path/all_tag.json', 'r', encoding='utf-8') as f:
#     tag_info = json.load(f)
#
# with open('./Corpus_Path/2024年03月03日15时01分/101/101.txt', 'r', encoding='utf-8') as f:
#     text = f.read()
#
# # 初始化标注数组，所有字符默认标注为O
# tags = ['O'] * len(text)
#
#
# # 根据annotations信息更新tags数组
# for entity in annotations['entities']:
#     start, end, label = entity['start'], entity['end'], entity['label']
#     tags[start] = 'B-' + tag_info.get(label, label)  # 使用all_tag.json中的简写（如果有的话）
#     for i in range(start + 1, end):
#         tags[i] = 'I-' + tag_info.get(label, label)
#     if start != end - 1:  # 如果实体不止一个字符
#         tags[end - 1] = 'L-' + tag_info.get(label, label)
#
# # 输出标注结果
# for char, tag in zip(text, tags):
#     print(f'{char} {tag}')





# import json
# with open('./Corpus_Path/Chinese_key_mapping.json', 'r', encoding='utf-8') as file:
#     tag_mapping = json.load(file)
# # 定义中文标签到英文缩写的映射
# print(tag_mapping)
# from Util.util import get_date_filename
#
# # 现在可以直接使用这个函数
# filename = get_date_filename('haha')
# print(filename)
# os.makedirs(new_file_name, exist_ok=True)

# from Util import util
#
# util.get_default_tags('104.pdf')

# tag_to_biname = {'姓名': 'name', '出生年月': 'bir', '性别': 'gend', '电话': 'tel', '最高学历': 'acad',
#                          '籍贯': 'nati', '落户市县': 'live', '政治面貌': 'poli', '毕业院校': 'unv', '工作单位': 'comp',
#                          '工作内容': 'work', '职务': 'post', '项目名称': 'proj', '项目责任': 'resp', '学位': 'degr',
#                          '毕业时间': 'grti', '工作时间': 'woti', '项目时间': 'prti'}
#
# biname_to_tag = {v: k for k, v in tag_to_biname.items()}
# print(biname_to_tag)
# import json
# biname_to_tag = json.dump(biname_to_tag)
# print(biname_to_tag)


