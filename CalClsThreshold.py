import argparse
import os
import sys
from DetectionMergeClassfication import GetClassificationScore


if __name__=='__main__':
    parse = argparse.ArgumentParser(description="Calculate the sub-class`s score threshold module!")
    parse.add_argument('-ci', '--class_scores', type=str, default='/data2/highspeed/cls_result.log',
                       help='Input the classification result file name with path')
    parse.add_argument('-i', '--input_dir', type=str,
                       help='The Dir of the sub-class to be calculated', required=True)
    args = parse.parse_args()

    cls_scores = args.class_scores
    if not os.path.isfile(cls_scores):
        print('The file of classification result is error:%s' % cls_scores)
        sys.exit(1)
    scores = GetClassificationScore(cls_scores)

    path = os.path.join(args.input_dir, '_ERROR_')
    if not os.path.isdir(path):
        print('This sub-class path error or have no exception sample!:%s' % args.input_dir)
        sys.exit(1)


    print('Process the Dir....:%s\n' % path)
    img_cnt = 0
    img_scores = 0
    for item in os.listdir(path):
        if not item.endswith('.jpg'):
            print('Exception sample:%s' % item)
            continue

        value = scores.get(item, '-1')
        if value == '-1':
            print('Img:%s have not found!' % item)
            continue

        score = float(value.split('_')[1])
        img_cnt += 1
        img_scores += score

        print('img:%s,  score:%f' % (item, float(score)))

    print('Img:%d, Threshold:%f' % (img_cnt, float(img_scores/img_cnt)))
