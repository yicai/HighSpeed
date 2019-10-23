
#sys.path.append('/Users/chuxing/python/test');

import os
import sys
import argparse
import shutil
import stat

from ClsThresholdProc import Proc
from detection_target_divide import target_task


class Tools(object):
    def __init__(self):
        pass

# 从原始文件夹中，把各个散落文件夹中的图片归总到一个文件夹中去
def GetAllImgs(input, output, OnlyBiggerImg = True):
    if not os.path.exists(input):
        print('input path:%s in not exit!!\n' % input)
        sys.exit(1)
    if not os.path.exists(output):
        os.makedirs(output)

    img_cnt = 0
    for folder in os.walk(input):
        for file in folder[2]:
            file_path = os.path.join(folder[0], file)
            if file_path.endswith('.jpg'):
                # print(file_path)
                if OnlyBiggerImg :
                    if IsBiggestImg(file_path):
                        shutil.copy(file_path, output)
                    else:
                        print('Img is not biggest!  %s' % file_path)
                else:
                    shutil.copy(file_path, output)
                img_cnt += 1

    print('finish!!\nCopy Raw images:%d\n' % img_cnt)

def IsBiggestImg(img_name):
    img = cv2.imread(img_name)
    w, h, _ = img.shape
    if h == 6576 and w == 4384:
        return True
    else:
        return False

# 提取__ERROR__ 文件夹里面的图片
def GetErrorImgs(input, output):
    if not os.path.exists(input):
        print('input path:%s in not exit!!\n' % input)
        sys.exit(1)

    if os.path.exists(output):
        DeleteDir(output)

    os.makedirs(output)

    img_cnt = 0
    for folder in os.walk(input):
        if not folder[0].endswith('_ERROR_'):
            continue
        if str(folder[0]) == str(output):
            continue
        for file in folder[2]:
            file_path = os.path.join(folder[0], file)
            if file_path.endswith('.jpg'):
                # print(file_path)

                shutil.copy(file_path, output)
                img_cnt += 1

    print('finish!!\nCopy _ERROR_ images:%d\n' % img_cnt)

# 获取分类score阈值低于制定值得图片
# 根据阈值，把各类的图像进行分类
def GetLowThresholdImgs(input, output, cls_label_thred, cls_scores_path):

    scores = Proc(cls_path=cls_scores_path, cls_thrd_path=cls_label_thred)

    if not os.path.exists(output):
        os.makedirs(output)
        print('Make dir:%s' % output)

    #低质量图片目录
    low_score_imgs = os.path.join(output, 'LOW_SCORE')
    if not os.path.exists(low_score_imgs):
        os.mkdir(low_score_imgs)
    #高质量图片目录
    high_score_imgs = os.path.join(output, 'HIGH_SCORE')
    if not os.path.exists(high_score_imgs):
        os.mkdir(high_score_imgs)

    for dir in os.listdir(input):
        src_path = os.path.join(input, dir)
        if not os.path.isdir(src_path):
            print('Not Dir:%s', src_path)
            continue
        # 创建好图像的存储路径
        dest_path = os.path.join(high_score_imgs, dir)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        # Get the category`s threshold
        thred = float(scores.GetCategoryThreshold(int(dir)))
        if thred == -1:
            print('category:%d is not threshold!!' % int(dir))
            continue

        for file in os.listdir(os.path.join(input, dir)):
            if not file.endswith('.jpg'):
                print('Not a img:%s' % file)
                continue
            score = float(scores.GetImgClsScore(file))
            if score > thred:
                shutil.copy(os.path.join(src_path, file),
                            dest_path)
            else:
                shutil.copy(os.path.join(src_path, file),
                            low_score_imgs)

    print('Finish!!')

    # 获取标注完后，正确的图片（提出_ERROR_中的图片）
def GetCheckedImgs(input, output, top=1500):
    if not os.path.exists(input):
        print('Input path:%s is not exist!', input)
        sys.exit(1)

    if os.path.exists(output):
        DeleteDir(output)
    os.makedirs(output)

    for dir in os.listdir(input):
        src_dir = os.path.join(input, dir)
        if not os.path.isdir(src_dir):
            print('Src_Object:%s is not dir!' % src_dir)
            continue

        dest_dir = os.path.join(output, dir)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Get all the error imgs in the direction _ERROR_
        err_imgs = {}
        err_path = os.path.join(src_dir, '_ERROR_')
        if not os.path.exists(err_path):
            print('Path is not exist! : %s' % err_path)
            continue

        for img in os.listdir(err_path):
            err_imgs[img] = 1

        imgs = os.listdir(src_dir)
        imgs.sort()
        if len(imgs) > top:
            imgs = imgs[0:top]

        img_cnt = 0
        for img in imgs:
            if err_imgs.get(img, '0') == 1:
                continue

            if not img.endswith('.jpg'):
                print('unnormal img:%s' % img)
                continue

            shutil.copy(os.path.join(src_dir, img), dest_dir)
            img_cnt += 1

        print('Category:%s, exact %d good img!' % (str(dir), img_cnt))


    # 计算分类准确率，通过人工验证后
def GetClasscifyAccurate(input, top=1500):
    if not os.path.exists(input):
        print('Input path:%s is not exist!', input)
        sys.exit(1)

    for dir in os.listdir(input):
        src_dir = os.path.join(input, dir)
        if not os.path.isdir(src_dir):
            print('Src_Object:%s is not dir!' % src_dir)
            continue

        # Get all the error imgs in the direction _ERROR_
        err_imgs = {}
        err_path = os.path.join(src_dir, '_ERROR_')
        if os.path.exists(err_path):
            for img in os.listdir(err_path):
                if img.endswith('.jpg'):
                    err_imgs[img] = 1

        imgs = os.listdir(src_dir)
        imgs.sort()
        if (top > 0) and (len(imgs) > top):
            imgs = imgs[0:top]

        img_cnt = 0
        for img in imgs:
            if err_imgs.get(img, '0') == 1:
                continue

            if not img.endswith('.jpg'):
                #print('unnormal img:%s' % img)
                continue

            img_cnt += 1

        if len(err_imgs) == 0:
            acc_rate = 100.00
        else:
            acc_rate = float(img_cnt/float(img_cnt + len(err_imgs))) * 100

        print('category:%s\t%.2f\tcorrect:%d\terror:%d' % (dir, acc_rate, img_cnt, len(err_imgs)))


def RemoveFileInFirstDir(path):
    for file in os.listdir(path):
        target_file = os.path.join(path, file)
        if os.path.isfile(target_file):
            os.remove(target_file)

def DeleteDir(path):
    if os.path.exists(path):
        for filelist in os.walk(path):
            for file in filelist[2]:
                os.chmod(os.path.join(filelist[0], file), stat.S_IWRITE)
                os.remove(os.path.join(filelist[0], file))
            shutil.rmtree(path)
            print('deleted path:%s' % path)
    else:
        print('path:%s is not exit!' % path)

# 获取web分类工具分类图像
def ExtractClassifiedImgs(cls_log, src_imgs, dest_path):
    if not os.path.isfile(cls_log):
        print('cls_result file error:%s' % cls_log)
        raise Exception('Path Error!', cls_log)

    if not os.path.exists(src_imgs):
        raise Exception('Input path error!', src_imgs)

    if os.path.exists(dest_path):
        DeleteDir(dest_path)

    os.makedirs(dest_path)

    with open(cls_log, 'r') as f:
        for line in f:
            values = line.strip('\n').split('\t')
            if (len(values) != 4) or (not values[2].endswith('.jpg')):
                print('un-normal line:%s' % line)
                continue

            #print(src_imgs, values[2])
            #TODO: here is sth wrong  un-know  ,deal it later
            #src = os.path.join(src_imgs, str(values[2]))
            #print(src)
            subpath = values[2].split('/')
            src_path = os.path.join(src_imgs, subpath[2], subpath[3])
            #src_path = src_imgs + str(values[2])
            #print(src_path)
            dest = os.path.join(dest_path, values[3].strip('\n'))
            if not os.path.exists(dest):
                os.makedirs(dest)

            if not os.path.exists(src_path):
                print('src img is not exist:%s,  %s' % (src_path, line))
                continue

            shutil.copy(src_path, dest)

    f.close()
    print('finished extract classified images!!')

# TYPE : 6
# 将一个文件夹的图片，切分成几个文件夹
def SeperateImgsToDirs(src_path, dest_path, bag_sizes=2000, subdir_no=100):
    cnt = 1
    dir_no = subdir_no

    if not os.path.exists(src_path):
        raise Exception('Input path error!', src_path)

    dest = os.path.join(dest_path, str(dir_no))
    if not os.path.exists(dest):
        os.makedirs(dest)
    for img in os.listdir(input):
        if not img.endswith('.jpg'):
            print('not a img:%s' % img)
            continue
        if cnt > bag_sizes:
            dir_no += 1
            cnt = 1
            dest = os.path.join(output, str(dir_no))
            print('Init a net sub_dir:%s' % dest)
            if not os.path.exists(dest):
                os.makedirs(dest)
                print('create a new dir:%s' % dest)

        shutil.move(os.path.join(input, img), dest)
        cnt += 1

    print('finished! created sub_dirs:%d' % dir_no)

if __name__=='__main__':

    parse = argparse.ArgumentParser(description="Calculate the sub-class`s score threshold module!")
    parse.add_argument('-o', '--output_dir', type=str, default='/data2/highspeed/process', #RawImgs',
                       help='Input the classification result file name with path', required=False)
    parse.add_argument('-i', '--input_dir', type=str, default='/data2/highspeed/cls_pre',
                       help='The Dir of the sub-class to be calculated', required=False)
    parse.add_argument('-s', '--cls_scores', type=str, default='/data2/highspeed/cls_result.log',
                       help='input the classify result scores file path', required=False)
    parse.add_argument('-ls', '--cls_label_threshold', type=str, default='',
                       help='input the category label threshold config file!', required=False)
    parse.add_argument('-n', '--num', type=int, default=1,
                       help='input the num!', required=False)
    parse.add_argument('-t', '--process_type', type=int, default=1,
                       help='Decide what to do:\n' \
                            '1 -- merge classify result into detect result;\n' \
                            '2 -- compare two model`s result;\n' ,
                       required=True)
    args = parse.parse_args()


    #refresh the dir
    output = args.output_dir
    input = args.input_dir

    TYPE = args.process_type
    if TYPE == 1:
        # 获取标注完后，正确的图片（提取所有不在_ERROR_中的图片）
        GetCheckedImgs(input, output, 5000)

    elif TYPE == 2:
        # 获取分类后所有的 ERROR 文件夹中的图片
        GetErrorImgs(input, output)

    elif TYPE == 3:
        #从原始文件夹中，把各个散落文件夹中的图片归总到一个文件夹中去
        GetAllImgs(input, output)

    elif TYPE == 4:
        # 根据阈值，把各类的图像进行分类
        cls_label_thred = args.cls_l彻底abel_threshold
        cls_scores_path = args.cls_scores
        GetLowThresholdImgs(input, output, cls_label_thred=cls_label_thred, cls_scores_path= cls_scores_path)

    elif TYPE ==5:
        # 计算分类准确率，通过人工验证后
        num = args.num
        if num == 1:
            num = -1
        GetClasscifyAccurate(input, top=num)

    elif TYPE == 6:
        # 将一个文件夹的图片，按照cnt数量的图片，切分成几个文件夹
        cnt = args.num
        if cnt == 1:
            cnt = 500
        SeperateImgsToDirs(input, output, bag_sizes=cnt)

    elif TYPE == 7:
        # 提取人工分类的结果
        ExtractClassifiedImgs(args.cls_scores, input, output)

    elif TYPE == 8:
        # 按照指定的大小，生成指定的标注文件夹
        num = args.num
        if num == 1:
            num = 20

        target_task(input, output, num)

    else:
        raise Exception('Input Error!!', TYPE)

