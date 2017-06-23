import os

#build ASCII to Label relation
charlist = sorted(os.listdir('/data/elsedata/train'))
f = open('/data/elsedata/charToLabel.txt','w+')
label=3500
for char in charlist:
	f.write(str(label)+" ")
	f.write(char+" ")
	f.write(unichr(int(char)).encode('utf-8'))
	f.write("\n")
	label=label+1
f.close()

#change folder name from ASCII to Label
label=3500
for char in charlist:
	str1=str(label)	
	os.rename('/data/elsedata/train/'+char,'/data/elsedata/train/'+str1.zfill(4))
	label=label+1
	

