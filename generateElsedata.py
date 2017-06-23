# -*-coding:utf-8-*-
from PIL import Image,ImageDraw,ImageFont
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
        val = ( head << 8 ) | (body << 4) | tail
        str = "%x" % val
        return str.decode('hex').decode('gb2312')

class ImageChar():
    def __init__(self, fontColor = (0, 0, 0),
    size = (100, 40),
    fontPath = '/usr/share/fonts/truetype/FreeSans',
    bgColor = (255, 255, 255),
    fontSize = 30):
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
        image=Image.new('RGB', (25,25), (255,255,255))
        draw = ImageDraw.Draw(image)
        draw.text( (0, -3), txt,  font=self.font, fill=fill)
        w=image.rotate(angle,  expand=1)
        self.image.paste(w, box=pos)
        del draw

    def randRGB(self):
        return (0,0,0)

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
    file = open('/usr/workspace/LiuYongChao/elsechars.txt')
    fonts=[]
    while True:
        line = file.readline()
        if not line:
            break
        line=line.split('\r\n')[0]

        if len(line) < 1:
            continue
        for word in line.split(' '):
            word = word.strip()
            if len(word) > 0:
		word = ord(unicode(word, 'utf-8'))
                fonts.append(word)

    return fonts

def printchars(chars,start,end):
	
	print 'fonts:',start,"-",end
	err_num = 0

	for char in chars[start:end]:
    
		#char = 105
		print "process:", multiprocessing.current_process().name, " saving char:", char
	
		rootPath = "/usr/workspace/LiuYongChao/fonts/"
		for file in os.listdir(rootPath):
		    if file is file:
			try:
				ic = ImageChar(fontPath =rootPath+file, fontColor=(100,211, 90), size=(64,64), fontSize = 54)
				ic.drawText((20,0), unichr(char), ic.randRGB())
				if not os.path.exists('/data/elsedata/train/'+str(char)+'/'):
				    os.makedirs('/data/elsedata/train/'+str(char)+'/')
				path = '/data/elsedata/train/'+str(char)+'/'+str(char)+'_'+file.replace(".","_")+".png"
				ic.save(path)
				#print "save path:", path
				#break
		    	except Exception,e:
				err_num += 1
				traceback.print_exc()
				print Exception,':',e


if __name__ == "__main__":
	tstart=time.time()
	chars = getchars()
	p1 = multiprocessing.Process(target = printchars, args = (chars,0,45))
	p2 = multiprocessing.Process(target = printchars, args = (chars,45,90))
	#p3 = multiprocessing.Process(target = printchars, args = (chars,1000,1500))
	#p4 = multiprocessing.Process(target = printchars, args = (chars,1500,2000))
	#p5 = multiprocessing.Process(target = printchars, args = (chars,2000,2500))
	#p6 = multiprocessing.Process(target = printchars, args = (chars,2500,3000))
	#p7 = multiprocessing.Process(target = printchars, args = (chars,3000,3500))
	#procs=[p1,p2,p3,p4,p5,p6,p7]
	procs=[p1,p2]

	print("The number of CPU is:" + str(multiprocessing.cpu_count()))
	for p in multiprocessing.active_children():
		print("child   p.name:" + p.name + "\tp.id" + str(p.pid))

	for p in procs:
		p.start();
	for p in procs:
		p.join();	
	

	tend=time.time()
	print "Finished! Time used:",tend-tstart
