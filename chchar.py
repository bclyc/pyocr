# -*- coding: utf-8 -*- #文件也为UTF-8
#!/usr/bin/env python
from PIL import Image,ImageDraw,ImageFont
import sys
print sys.getdefaultencoding()
fontpath = '/media/root/F8144D05144CC7F8/Sohu Work/Fonts/fonts/f005.ttf'
font = ImageFont.truetype(fontpath,24,index=0)
#font2 = ImageFont.truetype(fontpath,24,index=1)
img = Image.new('RGB',(300,200),(255,255,255))
draw = ImageDraw.Draw(img)
draw.text((0,60),unicode('你好','utf-8'),(0,0,0),font=font)
#draw.text((60,60),unicode('你好','utf-8'),(0,0,0),font=font2)
img.save(''.join(fontpath.split('/')[-1].split('.')[0])+'.jpg')