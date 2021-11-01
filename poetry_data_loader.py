import json
import re
import os
import time
import opencc


def poetry_load_func(file_path, item_getter):
    # 括号处理
    def _brackets_processor(item_list: list):
        return [re.sub(u"\\(.*?\\)", "", item) for item in item_list]

    # 书名号处理
    def _book_name_processor(item_list: list):
        return [re.sub(u"》", "", re.sub(u"《", "", item)) for item in item_list]

    # 句号处理
    def _full_stop_processor(item_list: list):
        _l = []
        for item in item_list:
            _l += item.rstrip(["。"]).split("。")
        return _l

    def _process(item_list: list):
        item_list = _brackets_processor(item_list)
        item_list = _book_name_processor(item_list)
        return item_list

    with open(file_path, "r", encoding="utf8") as fp:
        data = json.load(fp)
    return [_process(item_getter(item)) for item in data ]


def paper_load_func(file_path, converter):
    # 括号处理
    def _brackets_processor(item_list: list):
        return [re.sub(u"\\(.*?\\)", "", item) for item in item_list]

    # 书名号处理
    def _book_name_processor(item_list: list):
        return [re.sub(u"》", "", re.sub(u"《", "", item)) for item in item_list]

    # 引号
    def _co_processor(item_list: list):
        return [re.sub(u"》", "", re.sub(u"《", "", item)) for item in item_list]

    # 句号处理
    def _full_stop_processor(item_list: list):
        _l = []
        for item in item_list:
            _l += item.rstrip(["。"]).split("。")
        return _l

    def _process(item_list: list):
        item_list = _brackets_processor(item_list)
        item_list = _book_name_processor(item_list)
        return [converter(item) for item in item_list]

    def find_all_paragraphs(json, _l):
        if type(json) == list:
            if len(json) > 0:
                if type(json[0]) == dict:
                    for item in json:
                        find_all_paragraphs(item, _l)
        elif type(json) == dict:
            for key, value in json.items():
                if key == "paragraphs" and type(value) == list and len(value)>0 and type(value[0]) == str:
                    _l.append(value)
                else:
                    find_all_paragraphs(value, _l)

    with open(file_path, "r", encoding="utf8") as fp:
        data = json.load(fp)

    l = []
    find_all_paragraphs(data, l)
    return [_process(item_list) for item_list in l]


def get_loader():
    data_loader_map = {}

    # 曹操诗歌
    data_loader_map["caocaoshiji/caocao.json"] = lambda item: item["paragraphs"]

    # 楚辞
    data_loader_map["chuci/chuci.json"] = lambda item: item["content"]

    # 宋词
    for i in range(0,22):
        data_loader_map[f"ci/ci.song.{i*1000}.json"] = lambda item: item["paragraphs"]
    data_loader_map[f"ci/宋词三百首.json"] = lambda item: item["paragraphs"]

    # 论语
    # data_loader_map["lunyu/lunyu.json"] = lambda item: item["paragraphs"]

    # 诗经
    data_loader_map["shijing/shijing.json"] = lambda item: item["content"]

    # 五代诗歌
    for ch in [1, 2, 3, 4, 5, 6, 7, 8, 9, 'x']:
        data_loader_map[f"wudai/huajianji/huajianji-{ch}-juan.json"] = lambda item: item["paragraphs"]
    data_loader_map["wudai/nantang/poetrys.json"] = lambda item: item["paragraphs"]

    # 元曲
    data_loader_map["yuanqu/yuanqu.json"] = lambda item: item["paragraphs"]

    # 以下为繁体数据，需要转为简体
    converter = opencc.OpenCC("t2s.json")
    # 全唐诗
    for i in range(0, 58):
        data_loader_map[f"json/poet.tang.{i*1000}.json"] = lambda item: [converter.convert(line) for line in item["paragraphs"]]

    # 全宋诗
    for i in range(0, 255):
        data_loader_map[f"json/poet.song.{i*1000}.json"] = lambda item: [converter.convert(line) for line in item["paragraphs"]]

    data_dir = "data/chinese-poetry-master"
    data = []
    print("start processing...")
    for file_path, item_func in data_loader_map.items():
        start = time.time()
        data += poetry_load_func(os.path.join(data_dir, file_path), item_func)
        print(f"{file_path} finished, cost: {time.time() - start:.3f} ms")

    # 蒙学
    data += paper_load_func('data/chinese-poetry-master/mengxue/guwenguanzhi.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/qianjiashi.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/sanzijing-new.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/shenglvqimeng.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/tangshisanbaishou.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/youxueqionglin.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/zengguangxianwen.json', converter.convert)
    data += paper_load_func('data/chinese-poetry-master/mengxue/zhuzijiaxun.json', converter.convert)
    # print(paper_load_func('data/chinese-poetry-master/sishuwujing/daxue.json', converter.convert)[:10])
    # print(paper_load_func('data/chinese-poetry-master/sishuwujing/mengzi.json', converter.convert)[:10])
    # print(paper_load_func('data/chinese-poetry-master/sishuwujing/zhongyong.json', converter.convert)[:10])

    print(len(data))
    num = 0
    for _ in data:
        num += len(_)
    print(num)

if __name__ == "__main__":
    get_loader()