# -*- coding: utf-8 -*- #文件也为UTF-8
#!/usr/bin/env python
from PIL import Image,ImageDraw,ImageFont
import sys
print sys.getdefaultencoding()
font = ImageFont.truetype('/usr/share/fonts/windows/msyh.ttf',24)
img = Image.new('RGB',(300,200),(255,255,255))
draw = ImageDraw.Draw(img)
draw.text( (0,50), u'你好,世界!',(0,0,0),font=font)
draw.text((0,60),unicode('你好','utf-8'),(0,0,0),font=font)
img.save('1.JPEG')