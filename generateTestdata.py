# -*-coding:utf-8-*-
from PIL import Image, ImageDraw, ImageFont
import random
import os
import math, string
import logging
# logger = logging.Logger(name='gen verification')
import traceback
import multiprocessing
import time


class RandomChar():
    @staticmethod
    def Unicode():
        val = random.randint(0x4E00, 0x9FBF)
        return unichr(val)

    @staticmethod
    def GB2312():
        head = random.randint(0xB0, 0xCF)
        body = random.randint(0xA, 0xF)
        tail = random.randint(0, 0xF)
        val = (head << 8) | (body << 4) | tail
        str = "%x" % val
        return str.decode('hex').decode('gb2312')


class ImageChar():
    def __init__(self, fontColor=(0, 0, 0),
                 size=(100, 40),
                 fontPath='/usr/share/fonts/truetype/FreeSans',
                 bgColor=(255, 255, 255),
                 fontSize=30):
        self.size = size
        self.fontPath = fontPath
        self.bgColor = bgColor
        self.fontSize = fontSize
        self.fontColor = fontColor
        self.font = ImageFont.truetype(self.fontPath, self.fontSize)
        self.image = Image.new('RGB', size, bgColor)

    def drawText(self, pos, txt, fill):
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, txt, font=self.font, fill=fill)
        del draw

    def drawTextV2(self, pos, txt, fill, angle=180):
        image = Image.new('RGB', (25, 25), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((0, -3), txt, font=self.font, fill=fill)
        w = image.rotate(angle, expand=1)
        self.image.paste(w, box=pos)
        del draw

    def randRGB(self):
        return (0, 0, 0)

    def randChinese(self, num, num_flip):
        gap = 1
        start = 0
        num_flip_list = random.sample(range(num), num_flip)
        # logger.info('num flip list:{0}'.format(num_flip_list))
        print 'num flip list:{0}'.format(num_flip_list)
        char_list = []
        for i in range(0, num):
            char = "3".GB2312()
            char_list.append(char)
            x = start + self.fontSize * i + gap + gap * i
            if i in num_flip_list:
                self.drawTextV2((x, 6), char, self.randRGB())
            else:
                self.drawText((x, 0), char, self.randRGB())
        return char_list, num_flip_list

    def save(self, path):
        self.image.save(path)


def getchars():
    file = open('/usr/workspace/LiuYongChao/chchars1.txt')
    fonts = []
    while True:
        line = file.readline()
        if not line:
            break
        line = line.split('\r\n')[0]

        if len(line) < 1:
            continue
        for word in line.split(' '):
            word = word.strip()
            if len(word) > 0:
                word = ord(unicode(word, 'utf-8'))
                fonts.append(word)

    return fonts


f = open("/data/train_test_data/charToLabel.txt","r+")
chardict={}
for line in f.readlines():
    label,asc = line.strip().split(' ')[0:2]
    chardict[int(asc)] = label

def asciiTolabel(l):

    return chardict[l]


def printchars(chars, start, end):
    print 'fonts:', start, "-", end
    err_num = 0

    for char in chars[start:end]:

        #char = 20113
        print "process:", multiprocessing.current_process().name, " saving char:", char

        rootPath = "/usr/workspace/LiuYongChao/linux_win_chfonts/"
        for file in os.listdir(rootPath):
            if file is file:
                try:
                    ic = ImageChar(fontPath=rootPath + file, fontColor=(100, 211, 90), size=(64, 64), fontSize=48)
                    ic.drawText((0, 0), unichr(char), ic.randRGB())
                    xmin = -1;
                    xmax = -1;
                    ymin = -1;
                    ymax = -1;
                    for x in range(0,64):
                        for y in range(0,64):
                            if ic.image.getpixel((x, y))[0] != 255:
                                xmin = (x if xmin == -1 else xmin)
                                ymin = (y if ymin == -1 else ymin)
                                xmin = (x if x < xmin else xmin)
                                ymin = (y if y < ymin else ymin)
                                xmax = (x if x > xmax else xmax)
                                ymax = (y if y > ymax else ymax)

                    if xmin!=-1 and xmax!=-1:
                        ic.image = ic.image.crop((xmin,ymin,xmax+1,ymax+1)).resize((64,64), Image.ANTIALIAS)
                        charlabel = asciiTolabel(char).zfill(4)
                        if not os.path.exists('/data/train_test_data/test/' + charlabel + '/'):
                            os.makedirs('/data/train_test_data/test/' + charlabel + '/')
                        path = '/data/train_test_data/test/' + charlabel + '/' + charlabel + '_' + file.replace(".", "_") + ".png"
                        ic.save(path)
                    # print "save path:", path
                    # break
                except Exception, e:
                    err_num += 1
                    traceback.print_exc()
                    print Exception, ':', e


if __name__ == "__main__":
    tstart = time.time()
    chars = getchars()

    procs = []
    for i in range(40):
        p = multiprocessing.Process(target=printchars, args=(chars, int(i*3500/20), int((i+1)*3500/20)))
        procs.append(p)
    # p1 = multiprocessing.Process(target=printchars, args=(chars, 0, 1))
    # p2 = multiprocessing.Process(target=printchars, args=(chars, 500, 1100))
    # p3 = multiprocessing.Process(target=printchars, args=(chars, 1000, 1500))
    # p4 = multiprocessing.Process(target=printchars, args=(chars, 1500, 2000))
    # p5 = multiprocessing.Process(target=printchars, args=(chars, 2000, 2500))
    # p6 = multiprocessing.Process(target=printchars, args=(chars, 2500, 3000))
    # p7 = multiprocessing.Process(target=printchars, args=(chars, 3000, 3500))

        

    print("The number of CPU is:" + str(multiprocessing.cpu_count()))
    for p in multiprocessing.active_children():
        print("child   p.name:" + p.name + "\tp.id" + str(p.pid))

    for p in procs:
        p.start();
    for p in procs:
        p.join();

    tend = time.time()
    print "Finished! Time used:", tend - tstart
