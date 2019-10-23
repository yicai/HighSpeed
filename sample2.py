import cv2 as cv
import os
import numpy as np

img_path = './Track1_Saliency/Images/'  # 图像路径
re_path = './Track1_Saliency/Results/'  # 图像路径

img_num = len(os.listdir(img_path))  # 计算目录下有多少图像

# 注：如果文件名不是顺序排列（1,2,3,4....n），可以用以下方式取文件
# img_list=os.listdir(img_path)
# re_list=os.listdir(re_path)

for i in range(1, img_num + 1):  #
    img_name = img_path + str(i) + '.png'  # 图像格式为“.png”
    re_name = re_path + str(i) + '.png'

    # 当文件名不是顺序排列时
    # img_name=img_path+img_list[i]
    # re_name=re_path+re_list[i]

    img = cv.imread(img_name)
    re = cv.imread(re_name)

    img = cv.resize(img, (512, 512))
    re = cv.resize(re, (512, 512))

    cv.namedWindow('Results', cv.WINDOW_AUTOSIZE)

    h_all = np.hstack((img, re))  # 参数（img,re）取决于你要横向排列的图像个数
    # v_all=np.vstack((img,re)) #纵向排列

    cv.imshow('Results', h_all)
    cv.waitKey(100)  # 0.1s后进行下轮循环
cv.destroyAllWindows()

'''
传入的参数是： 
1. 图片的集合 
2. 想显示到一张图片的大小 
3. 图片间隔大小。

如果图片太多，会自动省略多的图片。
'''

import argparse
import glob

import cv2
import numpy as np
import os


def show_in_one(images, show_size=(300, 300), blank_size=2, window_name="merge"):
    small_h, small_w = images[0].shape[:2]
    column = int(show_size[1] / (small_w + blank_size))
    row = int(show_size[0] / (small_h + blank_size))
    shape = [show_size[0], show_size[1]]
    for i in range(2, len(images[0].shape)):
        shape.append(images[0].shape[i])

    merge_img = np.zeros(tuple(shape), images[0].dtype)

    max_count = len(images)
    count = 0
    for i in range(row):
        if count >= max_count:
            break
        for j in range(column):
            if count < max_count:
                im = images[count]
                t_h_start = i * (small_h + blank_size)
                t_w_start = j * (small_w + blank_size)
                t_h_end = t_h_start + im.shape[0]
                t_w_end = t_w_start + im.shape[1]
                merge_img[t_h_start:t_h_end, t_w_start:t_w_end] = im
                count = count + 1
            else:
                break
    if count < max_count:
        print("ingnore count %s" % (max_count - count))
    cv2.namedWindow(window_name)
    cv2.imshow(window_name, merge_img)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demonstrate mouse interaction with images')
    parser.add_argument("-i", "--input", help="Input directory.")
    args = parser.parse_args()
    path = args.input
    if path is None:
        test_dir = "/home/android/Pictures/focus_cut"
        path = test_dir

    debug_images = []
    for infile in glob.glob(os.path.join(path, '*.*')):
        ext = os.path.splitext(infile)[1][1:]  # get the filename extenstion
        if ext == "png" or ext == "jpg" or ext == "bmp" or ext == "tiff" or ext == "pbm":
            print(infile)
            img = cv2.imread(infile)
            if img is None:
                continue
            else:
                debug_images.append(img)

    show_in_one(debug_images)
    cv2.waitKey(0)
    cv2.destroyWindow()

