#!/usr/bin/python3

import os
import sys
#import cv2

class Proc(object):
    def __init__(self, name='ClsThresholdProc', cls_path='', cls_thrd_path=''):
        self.cls_path_ = cls_path
        self.name_ = name
        self.score_cnt_ = None
        self.scores_ = None
        self.cls_dir_ = None
        self.labels_threhd_ = {}

        if cls_path != '':
            self.scores_ = self.__GetClsScore(cls_path)

        if cls_thrd_path != '':
            self.labels_threhd_ = self.__GetClsLabelThreshold(cls_thrd_path)


    def __GetClsScore(self, file):
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
            print('Load classify result:%s, Imgs:%d' % (file, len(cls_score)))
        f.close()
        return cls_score

    def __GetAvgScore(self, path):
        img_cnt = 0
        img_scores = 0
        for item in os.listdir(path):
            if not item.endswith('.jpg'):
                print('Exception sample:%s' % item)
                continue

            value = self.scores_.get(item, '-1')
            if value == '-1':
                print('Img:%s have not found!' % item)
                continue

            score = float(value.split('_')[1])
            img_cnt += 1
            img_scores += score
            #print('img:%s,  score:%f' % (item, float(score)))

        return img_cnt, img_scores

    def __GetClsLabelThreshold(self, path):
        if not os.path.isfile(path):
            print('Labels threshold file path is error:%s' % path)
            return
        labels_threhd = {}
        with open(path, 'r') as f:
            for line in f.readlines():
                Item = line.split(':')
                assert(len(Item) == 2)
                labels_threhd[int(Item[0])] = float(Item[1])
                print(Item[0], Item[1])
            print('Load category score threshold:%s, category:%d' % (path, len(labels_threhd)))
        f.close()
        return labels_threhd


    def SetClsScores(self, file):
        if os.path.isfile(file):
            #self.scores_ = GetClassificationScore(file)
            self.scores_ = self.__GetClsScore(file)
        else:
            print('Classification result file is error:%s' % file)

    def SetClsImgsDir(self, path):
        if os.path.isdir(path):
            self.cls_dir_ = path
        else:
            print('Classified img path is error:%s' % path)

    def GetClassAvgScore(self, class_no):
        if self.cls_dir_ is None:
            print('Cls_dir is empty, pls recall SetClsImgsDir first!')
            return

        path = os.path.join(self.cls_dir_, str(class_no))
        if not os.path.isdir(path):
            print('Class type:%s is not exit!' % str(class_no))
            return

        cnt, scores = self.__GetAvgScore(path)
        print('Img:%d, Avg_Score:%f\n' % (cnt, float(scores / cnt)))

    def GetAllClassAvgScore(self, class_no):
        if self.cls_dir_ is None:
            print('Cls_dir is empty, pls recall SetClsImgsDir first!')
            return

        path = os.path.join(self.cls_dir_, str(class_no))
        if not os.path.isdir(path):
            print('Class type:%s is not exit!' % str(class_no))
            return

        cnt, scores = self.__GetAvgScore(path)

        path = os.path.join('_ERROR_')
        if os.path.isdir(path):
            cnt_e, scores_e = self.__GetAvgScore(path)
            print('Img:%d, Avg_Score:%f; Img_e:%d, Avg_score:%f \n' %
                  ((cnt + cnt_e), float((scores+scores_e)/(cnt + cnt_e)),
                   cnt_e, float(scores_e/cnt_e)))
        else:
            print('Img:%d, Avg_Score:%f\n' % (cnt, float(scores / cnt)))

    def GetImgClsScore(self, img_name):
        assert self.scores_ != None
        return self.scores_[img_name].split('_')[1]

    def GetImgClsLabel(self, img_name):
        assert self.scores_ != None
        return self.scores_[img_name].split('_')[0]

    def GetCategoryThreshold(self, label):
        assert self.labels_threhd_ != None
        return self.labels_threhd_.get(label, -1)