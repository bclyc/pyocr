# -*-coding:utf-8-*-
from PIL import Image,ImageDraw,ImageFont
import random
import os
import math, string
import logging
# logger = logging.Logger(name='gen verification')
import traceback
import sys

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



char = int(sys.argv[1])
print "saving char:", char
rootPath = "/usr/workspace/LiuYongChao/fonts/"
if len(sys.argv)<3:
	for file in os.listdir(rootPath):
	    if file is file:         
		try:       
			ic = ImageChar(fontPath =rootPath+file, fontColor=(100,211, 90), size=(64,64), fontSize = 54)
			ic.drawText((0,0), unichr(char), ic.randRGB())
			if not os.path.exists('/data/train_test_data/'+str(char)+'/'):
			    os.makedirs('/data/train_test_data/'+str(char)+'/')
			path = '/data/train_test_data/'+str(char)+'/'+str(char)+'_'+file.replace(".","_")+".png"
			ic.save(path)
	
			#break
		except Exception,e:
			print "saving font error:", file
			traceback.print_exc()
			print Exception,':',e
elif len(sys.argv)==3:
	try:    
		file=sys.argv[2]   
		ic = ImageChar(fontPath =rootPath+file, fontColor=(100,211, 90), size=(64,64), fontSize = 64)
		ic.drawText((0,0), unichr(char), ic.randRGB())
		if not os.path.exists('/data/train_test_data/'+str(char)+'/'):
		    os.makedirs('/data/train_test_data/'+str(char)+'/')
		path = '/data/train_test_data/'+str(char)+'/'+str(char)+'_'+file.replace(".","_")+".png"
		ic.save(path)

		#break
	except Exception,e:
		print "saving font error:", file
		traceback.print_exc()
