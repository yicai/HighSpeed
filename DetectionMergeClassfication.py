

import os, sys
import argparse
import json
import shutil

sys.path.append('/root/luyc/tools/HighSpeed')

from Tools import DeleteDir

def ParseArgv():
    parse = argparse.ArgumentParser(description="Merge the classification result into detection models!")
    parse.add_argument("-c", "--class_result", type=str,
                       help="input the classification result file path!",  required=False)
    parse.add_argument("-d", "--detection_result", type=str,
                       help="input the detection result file path!", required=False)
    parse.add_argument("-dd", "--detection_result_Dir", type=str,
                       help="input all the detection-result-file (json) together into Dir, path!", required=False)
    parse.add_argument("-o", "--output", type=str,
                       help="input the merge result file output path!", required=False)
    parse.add_argument('-i', '--input', type=str,
                       help='Input the path!')
    parse.add_argument('-t', '--process_type', type=int, default=1,
                       help='Decide what to do:\n' \
                            '1 -- merge classify result into detect result;\n' \
                            '2 -- compare two model`s result',
                       required=True)
    parse.add_argument('-r', '--cmp_result_root', type=str, default='',
                       help="input the compare two models result path for diff_img!")
    parse.add_argument('-tc', '--threshold_cls_score', type=float, default=0.8,
                       help='input the threshold of the classify score!')
    parse.add_argument('-td', '--threshold_detc_score', type=float, default=0.8,
                       help='input the threshold of the detect score!')
    parse.add_argument('-si', '--sub_img_path', type=str, default='',
                       help='input the processed-images path!')
    parse.add_argument('-crop', '--crop_imgs_dir', type=str, default='',
                       help="Corp images path")
    args = parse.parse_args()

    return args

def GenKey(img_name, id):
    #print(img_name, id)
    pre_name, aft_name = img_name.split('.')
    return pre_name+'_'+str(id)+'.'+aft_name

def UpdateItem(img_name, img_labels, obj):
    key = GenKey(img_name, obj['id'])
    #print(key)
    polygon = obj['polygon']
    bbox = obj['bbox'] # is a list
    bboxs = {
        'xmin':bbox[0],
        'ymin':bbox[1],
        'xmax':bbox[2],
        'ymax':bbox[3]
    }
    #category = img_labels[key]
    category = img_labels.get(key, '-1')
    if category == '-1':
        print('key:%s is not found!!' % key)
    id = obj['id']
    #score = obj['score']
    item = {'polygon': polygon,
            'bbox': bboxs,
            'category': category,
            'id': id}
            #'score': score}
    return item



# This func only merge the classify result into detect result,
# Without any process
def MergeResult(file, img_labels):
    new_json = []
    with open(file, 'rw') as f:
        fj = json.load(f)
        imgs = fj['imgs']
        for line in imgs:
            img_name = line
            items = []
            objects = imgs[line]['objects']
            for obj in objects:
                item = UpdateItem(img_name, img_labels, obj)
                items.append(item)
            new_json.append({img_name:items})
        json.dump(new_json, f)
    f.close()

def MergeResult_RW(file, img_labels, output):
    new_json = []
    with open(file, 'r') as f:
        fj = json.load(f)
        imgs = fj['imgs']
        for line in imgs:
            img_name = line
            items = []
            print(line)
            objects = imgs[line]['objects']
            print(line)
            for obj in objects:
                item = UpdateItem(img_name, img_labels, obj)
                items.append(item)
            new_json.append({img_name:items})
    f.close()

    with open(output, 'w') as o:
        json.dump(new_json, o)
        #json.dump(new_json, o, sort_keys=True, indent=5, separators=(',', ':'))
    o.close()

# Return a dict
# key: sub_img name
# value: category_score
def GetDetectionScore(file):
    if not os.path.isfile(file):
        print('detection result path is error:%s' % file)
        raise Exception('Path Error!', file)
        #return {}

    detc_score = dict()
    with open(file, 'r') as f:
        fj = json.load(f)
        imgs = fj['imgs']
        for img in imgs:
            img_name = img
            if not img_name.endswith('.jpg'):
                print('error detect result:%s' % img_name)
                continue
            objects = imgs[img]['objects']
            for obj in objects:
                if len(obj) == 0:
                    print('Img:%s no object!' % img_name)
                    continue
                id = obj['id']
                score = obj['score']
                category = obj['category']
                key = GenKey(img_name, id)
                value = str(category) + '_' + str(score)
                detc_score[key] = value
    f.close()
    return detc_score


def GetAllDetectionScore(results_dir):
    if not os.path.isdir(results_dir):
        print('detection-results Dir is error:%s ' % results_dir)
        raise Exception('Path Error!', results_dir)
        #return {}

    detc_scores = dict()
    for file in os.listdir(results_dir):
        print('Load file:%s ...' % file)
        scores = GetDetectionScore(os.path.join(results_dir, file))
        detc_scores.update(scores)
        # Other ways
        #detc_scores = dict(detc_scores.items() + scores.items())
        #detc_scores = dict(detc_scores, **scores)

    return detc_scores


# Return a dict
# key: sub_img name
# value: category_score
def GetClassificationScore(file):
    if not os.path.isfile(file):
        print('classification result path is error:%s' % file)
        return
    cls_score = dict()
    with open(file, 'r') as f:
        for line in f:
            labels, img, score, time = line.split('\t')
            if not img.endswith('.jpg'):
                print('error classify result:%s' % line)
                continue
            cls_score[img] = labels + '_' + score
    f.close()
    return cls_score

# Return a dict
# key: sub_img name
# value: category
def GetClassificationResult(file):
    f = open(file, 'r')
    img_labels = dict()
    for line in f:
        label, img, time, score = line.split('\t')
        img_labels[img] = label
        #TODO: score and time not process yet here!
    return img_labels


def ProcessLowScoreImg(args, img, category):
    root = args.cmp_result_root
    path = os.path.join(root, 'low_score', str(category))
    if not os.path.exists(path):
        os.makedirs(path)
    src_img = os.path.join(args.sub_img_path, img)
    shutil.move(src_img, path)

def  ProcessDiffImg(args, img, category):
    root = args.cmp_result_root
    path = os.path.join(root, 'diff_category', str(category))
    if not os.path.exists(path):
        os.makedirs(path)

    src_img = os.path.join(args.sub_img_path, img)
    shutil.move(src_img, path)

def CompareResult(args, cls_result, detc_result):
    cls_score = GetClassificationScore(cls_result)
    detc_score = GetDetectionScore(detc_result)

    while len(cls_score) > 0:
        item = cls_score.popitem()
        img = item[0]
        cls_category, cls_score = item[1].split('_')

        detc_value = detc_score.get(img, None)
        if detc_value == None:
            print('can`t found the value in detect result, img:%s' % img)
            continue

        category_detc, score_detc = detc_value.split('_')

        if cls_category == category_detc:
            #TODO: how to deal the score ?
            if float(cls_score) < args.threshold_cls_score or \
                    float(detc_score) < args.threshold_detc_score:
                ProcessLowScoreImg(args, img, category_detc)
        else:
            ProcessDiffImg(args, img, category_detc)

# 本函数用于比较，图像文件是否与Json中的数据一致
def CheckImgsDiff(args):
    dect_file = args.detection_result
    if not os.path.exists(dect_file):
        print('detection result file error:%s' % dect_file)
        return

    dect_result = dict()
    if os.path.isfile(dect_file):
        results = GetDetectionScore(dect_file)
    elif os.path.isdir(dect_file):
        results = GetAllDetectionScore(dect_file)
    else:
        print('Detection Result Input Error!!')
        return
    dect_result.update(results)
    print('\nLoad detect result!, Items:%d\n' % len(dect_result))

    crop_path = args.crop_imgs_dir
    if not os.path.isdir(crop_path):
        print('crop images path is error:%s' % crop_path)
        return

    checked_cnt = 0
    checked_err = 0
    for img in os.listdir(crop_path):
        if not img.endswith('.jpg'):
            print('img name error:%s' % img)
            continue
        value = dect_result.get(str(img), '0000')
        if value == '0000':
            print('Not result in Json:%s' % str(img))
            checked_err += 1
        else:
            checked_cnt += 1

    print('Finish check the diff, checked imgs:%d, un-normal:%d' % (checked_cnt, checked_err))


#Get the detect_result info from img_name
def GetImgDetectionInfo(img_name, detections):
    item = dict()
    infos = detections.get(str(img_name), '0000')
    if infos == '0000':
        return item;


def LineProcess(line):
    items = line.split('\t')
    if len(items) != 4:
        print('line format error!   %s' % line)
        return None

    label = items[0]
    sub_img = items[1]

    #TODO: Note here, is hard code to extract the img_name and obj_id, it`s heave depend on the format!!
    img = sub_img[0:-8]
    obj_no = sub_img[-7:-4]

    return [img, label, obj_no]


# 把分类的信息merge到检测结果中，并根据指定数量的图片进行文件夹切分，以便标注
# 分别生成标注包：配置文件 + 图片
def GenerateDetectionInnotation(args, bag_size=20):
    img_path = args.input
    cls_result = args.class_result
    dest_path = args.output
    if not os.path.exists(img_path):
        raise Exception('Input path is not exist!', img_path)
    if not os.path.exists(cls_result):
        raise Exception('Classfy result is not exist!', cls_result)

    if os.path.exists(dest_path):
        DeleteDir(dest_path)
    os.makedirs(dest_path)

    cls_results = GetClassificationResult(cls_result)

    dir_num = 1
    img_num = 1

    with open(args.detection_result, 'r') as f:
        fj = json.load(f)
        imgs = fj['imgs']
        new_json = dict()
        imgs_name = []
        items = dict()
        objs = []
        for line in imgs:
            items = {}
            objs = []
            objects = imgs[line]['objects']
            #new_json['path'] = line
            for obj in objects:
                if len(obj) == 0:
                    print('obj is empyt! img:%s' % line)
                    continue
                item = UpdateItem(line, cls_results, obj)
                objs.append(item)
            items['objects'] = objs
            items['path'] = line
            new_json[line] = items
            img_num += 1
            imgs_name.append(line)

            if img_num > bag_size:
                GeneratePakge(img_path, dest_path, dir_num, imgs_name, new_json)
                imgs_name = []
                new_json = {}
                img_num = 1
                dir_num += 1
        #TODO: store the least here
        if img_num > 1:
            GeneratePakge(img_path, dest_path, dir_num, imgs_name, new_json)
        print('last package generate:%d' % dir_num)
    f.close()

def GeneratePakge(img_path, dest_path, num, imgs, infos):
    dest_path = os.path.join(dest_path, str(num))
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    results = {'imgs': infos}
    results['types'] = []
    with open(os.path.join(dest_path, str(num) + '.json'), 'w') as f:
        f.write(json.dumps(results, ensure_ascii=False))
    f.close()

    for img in imgs:
        src_img = os.path.join(img_path, img)
        if not os.path.exists(src_img):
            print('Img is not exit!  %s' % src_img)
        shutil.copy(src_img, dest_path)



if __name__ == '__main__':
    args = ParseArgv()

    if args.process_type == 1:
        cls_labels = GetClassificationResult(args.class_result)
        #MergeResult(args.detection_result, cls_labels)
        MergeResult_RW(args.detection_result, cls_labels, args.output)
    elif args.process_type == 2:
        CompareResult(args, args.class_result, args.detection_result)
    elif args.process_type == 3:
        CheckImgsDiff(args)
    elif args.process_type == 4:
        GenerateDetectionInnotation(args, 30)
    else:
        print('this type is not support now!')



