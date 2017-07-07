# -*-coding:utf-8-*-
import os
import codecs
import tempfile
import sys
import time
import traceback

from numpy import *
import numpy as np
import cv2
from PIL import Image,ImageDraw

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


def initTess():
    handle = getcharbox.initTess()
    return handle


def closeTess(handle):
    getcharbox.closeTess(handle)
    pass


def getTiderBox(img, x1,y1,x2,y2):
    ymin = -1
    ymax = -1
    for y in range(y1,y2):
        for x in range(x1,x2):
            if img[y,x]!=255:
                ymin = y
                break
        if ymin!=-1:
            break
    for y in reversed(range(y1,y2)):
        for x in range(x1,x2):
            if img[y,x]!=255:
                ymax = y
                break
        if ymax!=-1:
            break
    return x1, ymin, x2, ymax+1


def charSplit(img, handle):
    t1 = time.time()

    bbox = getcharbox.getCharBox(handle, img)

    t2 = time.time()

    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # #cv2.namedWindow("GrayImage")
    # cv2.imshow("GrayImage", GrayImage)

    # th1 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
    #                             cv2.THRESH_BINARY, 3, 3)
    # th2 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                             cv2.THRESH_BINARY, 3, 3)
    # th3 = cv2.adaptiveThreshold(cv2.medianBlur(GrayImage, 1, 3), 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                             cv2.THRESH_BINARY, 3, 3)
    # #th3 = cv2.adaptiveThreshold(cv2.GaussianBlur(GrayImage, (3, 5), 5), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, 3)
    # th4 = cv2.medianBlur(cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                             cv2.THRESH_BINARY, 3, 1), 3, 4)
    t3 = time.time()
    ret5, th5 = cv2.threshold(GrayImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    t4 = time.time()
    # cv2.namedWindow("5")
    # cv2.imshow("5", th5)

    charbox_rs = []

    for box in bbox:
        x1, y1, x2, y2 = box
        hwRate = (float(y2 - y1) / (x2 - x1) if x2 != x1 else 0)
        if hwRate > 1:
            charbox_rs.append(box)
        else:
            cropImg = th5[y1:y2, x1:x2]

            t5 = time.time()

            tmp = cropImg.copy()

            t6 = time.time()

            img_mat = mat(tmp)
            w = np.asarray(img_mat.sum(axis=0)/255)[0]

            # for x in range(cropImg.shape[1]):
            #     for y in range(cropImg.shape[0]):
            #         w[x] += tmp[y, x]
            #         t = cv2.cv.Get2D(cv2.cv.fromarray(tmp), y, x)
            #         if t[0] == 255:
            #             w[x] += 1
            #             print ""
            # print w

            # for x in range(cropImg.shape[1]):
            #     for y in range(w[x]):
            #         # 把为0的像素变成白
            #         cv2.cv.Set2D(cv2.cv.fromarray(paintx), y, x, (255, 255, 255, 0))

            # cv2.namedWindow("projection")
            # cv2.imshow("projection", cv2.resize(paintx, (700, 100)))
            t7 = time.time()
            start_x = 0
            flag_start = 0
            black_shre = 1
            for x in range(cropImg.shape[1]):
                blackdots = cropImg.shape[0] - w[x]

                if blackdots < black_shre and flag_start == 0:
                    continue
                elif blackdots >= black_shre and flag_start == 0:
                    start_x = x
                    flag_start = 1

                    # for y in range(cropImg.shape[0]):
                    #     # fill with black
                    #     cv2.cv.Set2D(cv2.cv.fromarray(tmp), y, x, (0, 0, 0, 0))

                elif blackdots < black_shre and flag_start == 1:
                    xt1,yt1,xt2,yt2 = getTiderBox(th5, x1+start_x, y1, x1+x, y2)
                    charbox_rs.append([xt1, yt1, xt2, yt2])
                    flag_start = 0

                elif blackdots < black_shre + 1 and (y2 - y1) < 1.1 * (x - start_x) and flag_start == 1:
                    xt1, yt1, xt2, yt2 = getTiderBox(th5, x1+start_x, y1, x1+x, y2)
                    charbox_rs.append([xt1, yt1, xt2, yt2])
                    flag_start = 0

                elif x == cropImg.shape[1]-1 and flag_start == 1:
                    xt1, yt1, xt2, yt2 = getTiderBox(th5, x1+start_x, y1, x1+x+1, y2)
                    charbox_rs.append([xt1, yt1, xt2, yt2])
                    flag_start = 0

                elif blackdots >= black_shre and flag_start == 1:
                    # for y in range(cropImg.shape[0]):
                    #     # fill with black
                    #     cv2.cv.Set2D(cv2.cv.fromarray(tmp), y, x, (0, 0, 0, 0))
                    continue

            # cv2.namedWindow("rs")
            # cv2.imshow("rs", cv2.resize(tmp, (700, 100)))
            # cv2.waitKey(0)
            # break
            t8 = time.time()
            #print "char split single line time:",  t8 - t7
    t9 = time.time()

    print "char split time:", t9 - t4
    #print "char split + line split time:", time.time()-t1
    return charbox_rs, th5


if __name__ == '__main__':
    imageName = "/usr/workspace/pyocr/tests/charboxtest/test12.jpg"
    t0=time.time()
    handle = getcharbox.initTess()
    print "Tess init time:", time.time()-t0
    img = cv2.imread(imageName)
    charbox_rs, th5 = charSplit(img, handle)

    pil = Image.fromarray(np.array(th5))
    inputImage = Image.open(imageName)
    imagedraw = ImageDraw.Draw(inputImage)

    count = 0
    for x1, y1, x2, y2 in charbox_rs:
        imagedraw.line((x1, y1, x1, y2), fill=(255, 0, 0), width=1)
        imagedraw.line((x1, y1, x2, y1), fill=(255, 0, 0), width=1)
        imagedraw.line((x1, y2, x2, y2), fill=(255, 0, 0), width=1)
        imagedraw.line((x2, y1, x2, y2), fill=(255, 0, 0), width=1)
        #imagedraw.text((x1, y1), str(count), fill=(255, 0, 0))
        count += 1

    #inputImage = inputImage.resize((1024, int(float(1024)/inputImage.size[0]*inputImage.size[1])))
    pil.show()
    inputImage.show()

    t1 = time.time()
    getcharbox.closeTess(handle)
    print "Tess close time:", time.time() - t1

