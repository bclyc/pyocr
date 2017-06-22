import os

#build ASCII to Label relation
charlist = sorted(os.listdir('/data/train_test_data/test'))
f = open('/data/train_test_data/charToLabel.txt','w+')
label=0
for char in charlist:
	f.write(str(label)+" ")
	f.write(char+" ")
	f.write(unichr(int(char)).encode('utf-8'))
	f.write("\n")
	label=label+1
f.close()

#change folder name from ASCII to Label
label=0
for char in charlist:
	str1=str(label)	
	os.rename('/data/train_test_data/test/'+char,'/data/train_test_data/test/'+str1.zfill(4))
	label=label+1
	

