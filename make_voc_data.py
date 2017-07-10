# -*-coding:utf-8-*-

from xml.dom.minidom import Document
import os
import traceback


def save_to_xml(save_path, im_width, im_height, im_depth, objects_axis, label_name):
    object_num = len(objects_axis)
    doc = Document()

    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)

    folder = doc.createElement('folder')
    folder_name = doc.createTextNode('Char2007')
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
        object_name.appendChild(doc.createTextNode(label_name))
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


if __name__=='__main__':

    if not os.path.exists("/data/MyVOC2017/ImageSets/Main/"):
        os.makedirs("/data/MyVOC2017/ImageSets/Main/")
    f = open("/data/MyVOC2017/ImageSets/Main/trainval.txt", 'w')

    if not os.path.exists("/data/MyVOC2017/Annotations/"):
        os.makedirs("/data/MyVOC2017/Annotations/")
    lines = []
    file_count = 0

    for root, dirs, files in os.walk("/data/MyVOC2017/JPEGImages/"):
        files = files.sort()
        for file in files:
            try:
                new_file_name = str(file_count).zfill(8)
                label = file.split('_')[1]
                save_to_xml("/data/MyVOC2017/Annotations/" + new_file_name + ".xml", 32, 32, 3, [[0, 0, 31, 31]], label)

                os.renames(os.path.join(root, file), os.path.join(root, new_file_name+".jpg"))
                lines.append(new_file_name+"\n")
            except:
                traceback.print_exc()
            finally:
                file_count += 1

    f.writelines(lines)
    f.close()
