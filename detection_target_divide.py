# -*-coding:utf-8-*-
import os
import shutil
import json


def target_task(s_path, d_path, step):
    img_lists = os.listdir(s_path)
    img_list = []
    for img in img_lists:
        if img.endswith("jpg"):
            img_list.append(img)
    step = int(step)
    s = len(img_list) // step

    for i in range(s):
        dicts = {}
        dicts["imgs"] = {}
        dicts["types"] = []
        i_li = img_list[i * step:(i + 1) * step]
        if not os.path.exists(os.path.join(d_path, str(i + 1))):
            os.makedirs(os.path.join(d_path, str(i + 1)))
        for j in i_li:
            shutil.copyfile(os.path.join(s_path, j), os.path.join(os.path.join(d_path, str(i + 1)), j))
            dicts["imgs"][j] = {}
            dicts["imgs"][j]["path"] = j
            dicts["imgs"][j]["objects"] = []
        with open(os.path.join(os.path.join(d_path, str(i + 1)), str(i + 1) + ".json"), 'w') as f:
            f.write(json.dumps(dicts))

    if s * step < len(img_list):
        if not os.path.exists(os.path.join(d_path, str(s + 1))):
            os.mkdir(os.path.join(d_path, str(s + 1)))
        dicts = {}
        dicts["imgs"] = {}
        dicts["types"] = []
        for j in img_list[s * step:]:
            shutil.copyfile(os.path.join(s_path, j), os.path.join(os.path.join(d_path, str(s + 1)), j))
            dicts["imgs"][j] = {}
            dicts["imgs"][j]["path"] = j
            dicts["imgs"][j]["objects"] = []
        with open(os.path.join(os.path.join(d_path, str(s + 1)), str(s + 1) + ".json"), 'w') as f:
            f.write(json.dumps(dicts))
