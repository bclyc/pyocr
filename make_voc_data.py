# -*-coding:utf-8-*-

from xml.dom.minidom import Document
import os
import traceback
import time
import multiprocessing
from PIL import Image


def save_to_xml(save_path, im_width, im_height, im_depth, objects_axis, label_name):
    object_num = len(objects_axis)
    doc = Document()

    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)

    folder = doc.createElement('folder')
    folder_name = doc.createTextNode('MyVOC2017')
    folder.appendChild(folder_name)
    annotation.appendChild(folder)

    filename = doc.createElement('filename')
    filename_name = doc.createTextNode(save_path.split('/')[-1].replace('.xml', '.jpg'))
    filename.appendChild(filename_name)
    annotation.appendChild(filename)

    source = doc.createElement('source')
    annotation.appendChild(source)

    database = doc.createElement('database')
    database.appendChild(doc.createTextNode('LYC Char Database'))
    source.appendChild(database)

    annotation_s = doc.createElement('annotation')
    annotation_s.appendChild(doc.createTextNode('LYC'))
    source.appendChild(annotation_s)

    image = doc.createElement('image')
    image.appendChild(doc.createTextNode('flickr'))
    source.appendChild(image)

    flickrid = doc.createElement('flickrid')
    flickrid.appendChild(doc.createTextNode('None'))
    source.appendChild(flickrid)

    owner = doc.createElement('owner')
    annotation.appendChild(owner)

    flickrid_o = doc.createElement('flickrid')
    flickrid_o.appendChild(doc.createTextNode('None'))
    owner.appendChild(flickrid_o)

    name_o = doc.createElement('name')
    name_o.appendChild(doc.createTextNode('Liuyongchao'))
    owner.appendChild(name_o)


    size = doc.createElement('size')
    annotation.appendChild(size)

    width = doc.createElement('width')
    width.appendChild(doc.createTextNode(str(im_width)))
    height = doc.createElement('height')
    height.appendChild(doc.createTextNode(str(im_height)))
    depth = doc.createElement('depth')
    depth.appendChild(doc.createTextNode(str(im_depth)))
    size.appendChild(width)
    size.appendChild(height)
    size.appendChild(depth)
    segmented = doc.createElement('segmented')
    segmented.appendChild(doc.createTextNode('0'))
    annotation.appendChild(segmented)

    for i in range(object_num):
        objects = doc.createElement('object')
        annotation.appendChild(objects)
        object_name = doc.createElement('name')
        object_name.appendChild(doc.createTextNode(label_name[i]))
        objects.appendChild(object_name)
        pose = doc.createElement('pose')
        pose.appendChild(doc.createTextNode('Unspecified'))
        objects.appendChild(pose)
        truncated = doc.createElement('truncated')
        truncated.appendChild(doc.createTextNode('0'))
        objects.appendChild(truncated)
        difficult = doc.createElement('difficult')
        difficult.appendChild(doc.createTextNode('0'))
        objects.appendChild(difficult)
        bndbox = doc.createElement('bndbox')
        objects.appendChild(bndbox)
        xmin = doc.createElement('xmin')
        xmin.appendChild(doc.createTextNode(str(objects_axis[i][0])))
        bndbox.appendChild(xmin)
        ymin = doc.createElement('ymin')
        ymin.appendChild(doc.createTextNode(str(objects_axis[i][1])))
        bndbox.appendChild(ymin)
        xmax = doc.createElement('xmax')
        xmax.appendChild(doc.createTextNode(str(objects_axis[i][2])))
        bndbox.appendChild(xmax)
        ymax = doc.createElement('ymax')
        ymax.appendChild(doc.createTextNode(str(objects_axis[i][3])))
        bndbox.appendChild(ymax)

    f = open(save_path,'w')
    to_write = doc.toprettyxml(indent = '\t')
    ind = to_write.index('\n')
    f.write(to_write[ind+1:])
    f.close()



def gen_pic(pic_files, start, end):
    print "process:", multiprocessing.current_process().name, " saving :", start, "-", end
    filename_start_num = 149
    for pic_ind in range(start, end):
        t1 = time.time()
        print "process%", "/", float(pic_ind-start)/float(end-start)
        new_file_name = str(filename_start_num+pic_ind).zfill(6)

        big_img = Image.new('RGB',(320,320),(255,255,255))
        objects_axis = []
        labels = []
        for i in range(100):
            char_img = Image.open(pic_files[pic_ind*100+i])
            y = (i % 10)*32
            x = (i / 10)*32
            big_img.paste(char_img, (x, y))

            objects_axis.append([x, y, x+31, y+31])
            labels.append(pic_files[pic_ind*100+i].split('/')[-1].split('_')[0])

        big_img.save("/data/MyVOC2017/JPEGImages/"+new_file_name+".jpg")
        save_to_xml("/data/MyVOC2017/Annotations/" + new_file_name + ".xml", 320, 320, 3, objects_axis, labels)

        #lines.append(new_file_name + "\n")
        #print "one pic time", time.time() - t1


if __name__=='__main__':


    if not os.path.exists("/data/MyVOC2017/ImageSets/Main/"):
        os.makedirs("/data/MyVOC2017/ImageSets/Main/")

    if not os.path.exists("/data/MyVOC2017/Annotations/"):
        os.makedirs("/data/MyVOC2017/Annotations/")

    if not os.path.exists("/data/MyVOC2017/JPEGImages/"):
        os.makedirs("/data/MyVOC2017/JPEGImages/")

    char20test = [1510,2047,104,1001,436,2228,1175,1502,1011,1007,3262,2502,2371,3570,2113,2110,2137,2133,179,2868]
    char20test = [str(char) for char in char20test]

    file_count = 0

    t0 = time.time()
    pic_files = []
    for root, dirs, files in os.walk("/data/train_test_data/32test"):
        if len(files)>0 and root.split('/')[-1] in char20test:
            pic_files += [os.path.join(root, file) for file in files]
    pic_files.sort()
    print "read files time:", time.time() - t0, "filenum:", len(pic_files)

    out_pic_num = len(pic_files)/100
    filename_start_num = 149
    procs = []
    p_num = 48
    for i in range(p_num):
        try:
            p = multiprocessing.Process(target=gen_pic,
                                        args=(pic_files, int(i * out_pic_num / p_num), int((i + 1) * out_pic_num / p_num)))

            procs.append(p)
        except:
            traceback.print_exc()

    for p in procs:
        p.start();
    for p in procs:
        p.join();

    f = open("/data/MyVOC2017/ImageSets/Main/test.txt", 'w')
    lines = [str(i).zfill(6)+"\n" for i in range(filename_start_num, filename_start_num+out_pic_num)]
    f.writelines(lines)
    f.close()

    print "total time:", time.time() - t0

