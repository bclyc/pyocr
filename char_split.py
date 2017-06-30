# -*-coding:utf-8-*-
import os
import codecs
import tempfile
import sys
import time
import traceback

import numpy as np
import cv2
from PIL import Image

import getcharbox

def stdfilt(img, mask):
    n = mask.sum()
    n1 = n - 1
    c1 = cv2.filter2D(img**2, -1, mask / n1, borderType=cv2.BORDER_REFLECT)
    c2 = cv2.filter2D(img, -1, mask, borderType=cv2.BORDER_REFLECT)**2 / (n * n1)
    sig = np.sqrt(np.maximum(c1 - c2, 0))

    return sig


def localmean(img, mask):
    lm = cv2.filter2D(
        img, -1, mask / mask.sum(),
        borderType=cv2.BORDER_REPLICATE)

    return lm


def img_binary(img, w_size=3, w_sig=0.9, w_lm=0.9):
    if len(img.shape) != 2:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = img / 255.0
    mask = np.ones(w_size)

    sig = stdfilt(img, mask)
    if w_lm == 0:
        w_lm = 1
        lm = np.mean(img)
    else:
        lm = localmean(img, mask)

    img = 255 * ((img > sig * w_sig) & (img > w_lm * lm))

    return img


if __name__ == '__main__':
    imageName = "/usr/workspace/pyocr/tests/charboxtest/test2.jpg"
    handle = getcharbox.initTess()
    bbox = getcharbox.getCharBox(handle, imageName)

    t1 = time.time()
    img = cv2.imread(imageName)
    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.namedWindow("GrayImage")
    cv2.imshow("GrayImage", GrayImage)
    print time.time() - t1
    t1 = time.time()

    # th1 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
    #                             cv2.THRESH_BINARY, 3, 3)
    # th2 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                             cv2.THRESH_BINARY, 3, 3)
    th3 = cv2.adaptiveThreshold(cv2.medianBlur(GrayImage, 1, 3), 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                 cv2.THRESH_BINARY, 3, 3)
    # #th3 = cv2.adaptiveThreshold(cv2.GaussianBlur(GrayImage, (3, 5), 5), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, 3)
    # th4 = cv2.medianBlur(cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                             cv2.THRESH_BINARY, 3, 1), 3, 4)

    ret5, th5 = cv2.threshold(GrayImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)



    print time.time() - t1
    t1 = time.time()

    # cv2.namedWindow("1")
    # cv2.imshow("1", th1)
    # cv2.namedWindow("2")
    # cv2.imshow("2", th2)
    # cv2.namedWindow("3")
    # cv2.imshow("3", th3)
    # cv2.namedWindow("4")
    # cv2.imshow("4", th4)
    cv2.namedWindow("5")
    cv2.imshow("5", th5)

    charbox_rs = []

    for box in bbox[13:]:
        x1, y1, x2, y2 = box
        hwRate = (float(y2 - y1) / (x2 - x1) if x2 != x1 else 0)
        if hwRate>1:
            charbox_rs.append(box)
        else:
            cropImg = th5[y1:y2, x1:x2]
            cv2.namedWindow("crop")
            cv2.imshow("crop", cv2.resize(cropImg,(700,100)))

            # 创建一个空白图片(img.shape[0]为height,img.shape[1]为width)

            paintx = np.zeros(cropImg.shape, np.uint8)

            # 将新图像数组中的所有通道元素的值都设置为0
            cv2.cv.Zero(cv2.cv.fromarray(paintx))

            # 创建width长度都为0的数组
            w = [0] * cropImg.shape[1]

            tmp = cropImg.copy()

            print cropImg.shape[0]
            # 对每一行计算投影值
            for x in range(cropImg.shape[1]):
                for y in range(cropImg.shape[0]):
                    t = cv2.cv.Get2D(cv2.cv.fromarray(tmp), y, x)
                    if t[0] == 255:
                        w[x] += 1
                    # print ""

            # 绘制垂直投影图
            for x in range(cropImg.shape[1]):
                for y in range(w[x]):
                    # 把为0的像素变成白
                    cv2.cv.Set2D(cv2.cv.fromarray(paintx), y, x, (255, 255, 255, 0))

            cv2.namedWindow("projection")
            cv2.imshow("projection", cv2.resize(paintx,(700,100)))

            start_x = 0
            flag_start = 0
            black_shre = 1
            for x in range(cropImg.shape[1]):
                blackdots = cropImg.shape[0]-w[x]

                if blackdots<black_shre and flag_start==0:
                    continue
                elif blackdots >= black_shre and flag_start == 0:
                    start_x = x
                    flag_start = 1

                    for y in range(cropImg.shape[0]):
                        # fill with black
                        cv2.cv.Set2D(cv2.cv.fromarray(tmp), y, x, (0, 0, 0, 0))

                elif blackdots < black_shre and flag_start == 1:
                    charbox_rs.append([start_x, y1, x-1, y2])
                    flag_start = 0

                elif blackdots < black_shre+1 and (y2-y1) < 1.3*(x-start_x) and flag_start == 1:
                    charbox_rs.append([start_x, y1, x, y2])
                    flag_start = 0


                elif blackdots >= black_shre and flag_start == 1:
                    for y in range(cropImg.shape[0]):
                        # fill with black
                        cv2.cv.Set2D(cv2.cv.fromarray(tmp), y, x, (0, 0, 0, 0))
                    continue

            cv2.namedWindow("rs")
            cv2.imshow("rs", cv2.resize(tmp, (700, 100)))

            break




    # cv2.namedWindow("Image2")
    # cv2.imshow("Image2", th2)
    #
    # cv2.namedWindow("Image2b")
    # cv2.imshow("Image2b", th3)

    #cv2.imwrite("/usr/workspace/pyocr/tests/charboxtest/test66.jpg",th3)


    cv2.waitKey(0)
    #cv2.destroyAllWindows()

# threshold = 80
# # convert_table = []
# # for i in range(256):
# #     if i < threshold:
# #         convert_table.append(0)
# #     else:
# #         convert_table.append(1)
# #
# # img_binary = img.point(convert_table, "1")
# mask = np.ones(lineImage.size)
#
# sig = stdfilt(img, mask)
# if w_lm == 0:
#     w_lm = 1
#     lm = np.mean(img)
# else:
#     lm = localmean(img, mask)
#
# img = 255 * ((img > sig * w_sig) & (img > w_lm * lm))
# img_binary.show()
