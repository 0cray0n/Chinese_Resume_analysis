import sys
sys.path.append('./Util')
from config import json_log_config
from datetime import datetime
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import json
from io import StringIO
from dateutil import parser
import os

PDF_DIR = './PDF_DIR'
PDF_TEST_DIR = './PDF_TEST'
# 保存结果
CORPUS_PATH = './Corpus_Path'
# 所有标签
all_tag_json_path = './Corpus_Path/all_tag.json'
# 英文全称映射缩写
key_mapping_path = './Corpus_Path/key_mapping.json'
# 简写标签映射序号
abbrtag_to_index_json_path = './Corpus_Path/Vocal/abbrtag_to_index.json'
index_to_abbrtag_json_path = './Corpus_Path/Vocal/index_to_abbrtag.json'
# 中文索引映射
chinese_to_idx_path = './Corpus_Path/Vocal/chinese_to_idx.json'
idx_to_chinese_path = './Corpus_Path/Vocal/idx_to_chinese.json'
# 测试时使用的已经人工标注好的json,算法标注好的每一个词
test_ner_json_path = './Corpus_Path/2024年03月03日15时01分/101/101.json'
test_tag_text_path = './Corpus_Path/2024年03月03日15时01分/101/tag.txt'

# 获取json文件信息
def get_json_info(json_path):
    '''
    获取json文件信息
    :param json_path:
    :return:
    '''
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            ner_json = json.load(f)
        print(f"从{json_path}读取成功")
    else:
        ner_json = ""
        print(f"json文件不存在{json_path}")
        json_log_config.error(f"json文件不存在{json_path}")
    return ner_json

# 英文全称映射缩写
key_mapping = get_json_info(key_mapping_path)
# 所有标签
all_tag_json = get_json_info(all_tag_json_path)
# 中文索引映射
chinese_to_idx_json = get_json_info(chinese_to_idx_path)
idx_to_chinese_json = get_json_info(idx_to_chinese_path)
# 测试时使用的已经人工标注好的json
test_ner_json = get_json_info(test_ner_json_path)
# 英文标记和简写的映射
abbrtag_to_index_json = get_json_info(abbrtag_to_index_json_path)
index_to_abbrtag_json = get_json_info(index_to_abbrtag_json_path)

# 从算法标注好的txt标签中，读取文本并转化为列表形式
def get_txt_tag(txt_path):
    '''
    :param txt_path:
    :return:list[[]],样例[['蔡', 'B-NM']]
    '''
    # 读取txt文件
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 将文本转化为二维列表
    data_list = [line.strip().split() for line in lines]
    return data_list
# 测试时使用的算法标注好的每一个词
test_tag_text = get_txt_tag(test_tag_text_path)

# 获取所有的标签简写并返回长度
def get_abbr_mapping(json_text=all_tag_json, key_mapping=key_mapping, is_idx=False, is_read=False):
    all_key_abbr = {}
    index = 0
    all_key_abbr["<start>"] = index
    index += 1
    # print(all_tag_json)
    if is_read:
        all_key_abbr = get_json_info(abbrtag_to_index_json_path)
    else:
        for key, value in json_text.items():
            if isinstance(value, str):  # 如果字段值是字符串，则直接添加
                new_key_B = "B-" + key_mapping[key]
                all_key_abbr[new_key_B] = index
                index += 1
                new_key_I = "I-" + key_mapping[key]
                all_key_abbr[new_key_I] = index
                index += 1
            elif isinstance(value, list):
                # 遍历二级结构列表
                for (idx, item) in enumerate(value):
                    # 遍历字典
                    for sub_key, sub_value in item.items():
                        if is_idx:
                            # 带idx的
                            new_key = key_mapping[key] + "_" + key_mapping[sub_key] + "_" + str(idx)
                            new_key_B = "B-" + new_key
                            new_key_I = "I-" + new_key
                        else:
                            # 不带idx的
                            new_key = key_mapping[key] + "_" + key_mapping[sub_key]
                            new_key_I = "I-" + new_key
                            new_key_B = "B-" + new_key
                        all_key_abbr[new_key_I] = index
                        index += 1
                        all_key_abbr[new_key_B] = index
                        index += 1
        all_key_abbr['<stop>'] = index
        index += 1
        all_key_abbr['O'] = index
        # with open(abbrtag_to_index_json_path, 'w', encoding='utf-8') as f:
        #     json.dump(all_key_abbr, f)
    # print(all_key_abbr)
    return all_key_abbr

# 更新json同时反写
def update_json_reverse(json_path,json_info,is_reverse=False,reverse_json_path=""):
    if len(json_info) == 0:
        print("json信息为空，请检查变量")
        return
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_info, f, ensure_ascii=False, indent=4)
    if is_reverse:
        reversed_data = {v: k for k, v in json_info.items()}
        with open(reverse_json_path, 'w', encoding='utf-8') as reverse_file:
            json.dump(reversed_data, reverse_file, ensure_ascii=False, indent=4)
    print(f"json成功写入{json_path},反写成功于{reverse_json_path}")

# 若txt路径存在并不为空从路径读取，不存在从pdf_path解析生成text并写入当前txt_path，
def get_text_from_txt(txt_path,pdf_path=""):
    '''
    若txt路径存在并不为空从路径读取，不存在从pdf_path解析生成text并写入当前txt_path，
    :param txt_path:
    :param pdf_path:
    :return: txt文本
    '''
    if not os.path.exists(txt_path):
        text = get_str_from_pdf(pdf_path)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"未解析pdf,txt已生成于目录{txt_path}")
    else:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        # 若读取出的txt文本为空则重新解析pdf
        if text == "":
            text = get_str_from_pdf(pdf_path)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"解析pdf,txt已生成于目录{txt_path}")
    return text

# 返回默认以时间为单位+filename命名的txt文件名称
def get_date_filename(filepath,suffix="txt",filename=""):
    """
    默认以时间为单位+filename命名的txt文件
    :param filepath: 文件路径
    :param suffix: 后缀
    :param filename: 添加的名字
    :return:
    """
    # 获取当前时间的时间戳
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
    print(current_time)
    # 新文件名
    new_file_name = filepath + "/" + current_time + "-" + filename + "."+ suffix
    return new_file_name

# 获取时间+文件名，若无文件名返回时间
def get_date_dir(filepath,filename=""):
    """
    默认以时间为单位命名的文件夹名称
    :param filepath:
    :param filename:
    :return:
    """
    # 获取当前时间的时间戳
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
    print(current_time)
    # 新文件名
    if filename != "":
        new_file_name = filepath + "/" + current_time + "-" + filename
    else:
        new_file_name = filepath + "/" + current_time
    return new_file_name

# 从PDF文件中提取文本内容
def get_str_from_pdf(pdf_path):
    """
    从PDF文件中提取文本内容
    :param pdf_path: pdf路径
    :return:
    """
    content = ''  # 初始化空字符串，用于累积提取的文本内容

    # 检查给定的文件路径是否指向一个PDF文件
    if pdf_path.endswith('.pdf'):
        # 创建PDF资源管理器，用于存储共享资源
        rsrcmgr = PDFResourceManager(caching=True)
        # 设置文本布局分析的参数
        laparams = LAParams()
        # 创建一个字符串流，用于临时存储提取的文本
        retstr = StringIO()
        # 创建一个文本转换器，结合资源管理器、字符串流和布局参数
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)

        # 以二进制读取模式打开PDF文件
        with open(pdf_path, 'rb') as fp:
            # 创建PDF页面解释器，需要资源管理器和转换设备作为参数
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            # 遍历PDF文件中的每一页
            for page in PDFPage.get_pages(fp, pagenos=set()):
                # 确保页面旋转角度有效
                page.rotate = page.rotate % 360
                # 用页面解释器处理当前页，提取文本
                interpreter.process_page(page)

        # 完成所有页面的处理后，关闭转换设备
        device.close()
        # 从字符串流中获取累积的文本内容
        content = retstr.getvalue()
    # 对提取的文本进行后处理：去除首尾空白、删除换行符、分割成单词、重新连接成字符串
    words = content.strip().replace('\n', '').split()
    ret = ''.join(words)
    # 返回处理和清理后的纯文本字符串
    return ret

# 寻找离当前时间最近的文件夹，或者创建由当前时间命名的文件夹
def create_or_find_date_dir(is_mkdir_date=False, corpus_path=CORPUS_PATH):
    """
    # 寻找离当前时间最近的文件夹，或者创建由当前时间命名的文件夹
    :param is_mkdir_date: 是否创建以当前日期时间命名的文件夹
    :param corpus_path: 父文件目录
    :return:
    """
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日%H时%M分")

    if is_mkdir_date:
        # 创建以当前日期时间命名的文件夹
        file_dir = os.path.join(corpus_path, date_str)
        os.makedirs(file_dir, exist_ok=True)
    else:
        # 查找最接近当前日期时间的文件夹
        closest_date = None
        closest_dir = None
        for dirname in os.listdir(corpus_path):
            try:
                dir_date = parser.parse(dirname, fuzzy=True)
                if closest_date is None or abs((now - dir_date).total_seconds()) < abs((now - closest_date).total_seconds()):
                    closest_date = dir_date
                    closest_dir = dirname
            except ValueError:
                # 如果文件夹名不能转换为日期，则忽略
                continue

        if closest_dir is not None:
            file_dir = os.path.join(corpus_path, closest_dir)
        else:
            # 如果没有找到接近的文件夹，创建一个新的
            file_dir = os.path.join(corpus_path, date_str)
            os.makedirs(file_dir, exist_ok=True)

    return file_dir

# 强制创建文件夹
def mkdir(url):
    if not os.path.exists(url):
        os.mkdir(url)
        print(f"{url}文件夹已创建")
    else:
        print(f"{url}文件夹已存在")


