---
title:  数据集格式转换（一）
tags: [Code,Python]
categories: AI
mathjax: true
---



## 数据集VOC格式转YOLO格式

git：[kylinhx/DatasetTransform: This repository contains some python scripts that is used to change the format of a dataset. This repository will be updated continuously. (github.com)](https://github.com/kylinhx/DatasetTransform)

![](image-20230306201754229.png)

This Python program is used to convert object detection annotations in XML format to text files in YOLO format. It takes XML files containing object locations, class names, and image sizes and extracts the relevant information. The output is a set of text files that contain the same information in the YOLO format, which can be used for training object detection models.↳

The program first defines the paths to the input XML files and the output text files for training, validation, and testing. It also defines the classes for the objects being detected, and the percentages of the data to be used for training, validation, and testing.

The main functions of the program are:

- `readXML`: reads a single XML file and extracts the information about the object locations, class names, and image sizes. It saves this information in a dictionary called `box`, and appends this dictionary to a list called `boxes`.
- `getPath`: returns a list of all XML file names in the input path.
- `getBoxes`: calls `readXML` for all XML files in the input path, and returns a list of all `box` dictionaries.
- `gen_txt`: given a `box` dictionary, generates a text file in YOLO format with the same information.
- `gen_img`: given an image filename and the paths to the input and output image directories, copies the image file from the input directory to the output directory.
- `turn_to_Yolo`: converts the object location information from VOC format to YOLO format.
- `gen_index`: given an image filename and a number (0, 1, or 2), appends the filename to the corresponding text file for training, validation, or testing.

Finally, the program divides the dataset into training, validation, and testing sets according to the percentages defined earlier, and generates text files and copies image files for each set using the functions defined above.

使用说明：

1. 首先将需要转化为YOLO格式的标注文件以及对应的图片文件放在同一个文件夹中，例如“Annotations”和“JPEGImages”。
2. 修改代码中“Annotations_Path”和“Image_Path”为对应文件夹的路径。
3. 可以在“Classes”中定义物体的类别，根据实际情况修改。
4. 根据需要调整“train_percent”和“test_percent”来设置训练集和测试集的比例。
5. 运行代码，将会生成三个文件夹：train，test，val。其中train文件夹包含用于训练的图片，test文件夹包含用于测试的图片，val文件夹包含用于验证的图片。
6. 每张图片会对应一个txt标注文件，文件格式为每行为一个物体的标注，由五个数字组成：第一个数字是物体类别的序号，后四个数字是物体在图片中的位置信息，分别为中心坐标x、中心坐标y、宽度和高度。
7. 如果需要查看数据分割的结果，可以在“train.txt”，“test.txt”，“val.txt”中查看对应的图片文件名。

注意事项：

1. 请务必备份原始数据，以免误操作造成数据丢失。
2. 需要安装minidom模块，如果未安装请先安装该模块。
3. 需要确保所有的标注文件的格式符合VOC数据集格式，即文件格式为.xml，文件中包含了对应图片的标注信息。

```python
# This py program is used to get xml labels into boxes
# For each box in boxes
# boxes =[box]
# box = {
#   filename: str       the filename of picture
#   size:[width,height,depth]   the size of picture
#   bboxes: [[imgcls,xmin,ymin,xmax,ymax]]       the location of object
# }
# boxes=[
#   {
#       filename:str
#       bboxes:[[imgcls,xmin,ymin,xmax,ymax]]
# }
#   {
#       filename:str
#       bboxes:[[imgcls,xmin,ymin,xmax,ymax]]
# }
# ...
# ]
from xml.dom.minidom import parse
import os
import random
import shutil

# Define the path
Annotations_Path = 'Annotations'
Image_Path = 'JPEGImages'

Train_Path_img = 'images/train'
Val_Path_img = 'images/val'
Test_Path_img = 'images/test'

Train_Path_label = 'labels/train'
Val_Path_label = 'labels/val'
Test_Path_label = 'labels/test'

# Define classes
Classes = ['Platelets', 'RBC', 'WBC']

# Define percent
train_percent = 0.8
test_percent = 0.2
val_percent = train_percent * 0.2

# This function can read single xml label document and add a single box into boxes
def readXML(XMLPATH, boxes):
    box = {}
    bboxes = []
    bbox = []
    dom = parse(XMLPATH)
    rootNode = dom.documentElement

    # Get filename
    filename = rootNode.getElementsByTagName('filename')[0].firstChild.data
    print(filename)
    box['filename'] = filename

    # Get size of the picture
    sizes = rootNode.getElementsByTagName('size')
    for size in sizes:
        width = size.getElementsByTagName('width')[0].firstChild.data
        height = size.getElementsByTagName('height')[0].firstChild.data
        depth = size.getElementsByTagName('depth')[0].firstChild.data
    box['size'] = [width, height, depth]

    # Get imgcls and box
    locations = rootNode.getElementsByTagName('object')
    for location in locations:
        # Get imgcls
        imgcls = location.getElementsByTagName('name')[0].firstChild.data
        # Get box
        xmin = location.getElementsByTagName('xmin')[0].firstChild.data
        ymin = location.getElementsByTagName('ymin')[0].firstChild.data
        xmax = location.getElementsByTagName('xmax')[0].firstChild.data
        ymax = location.getElementsByTagName('ymax')[0].firstChild.data

        # Save bbox in bboxes
        bbox = [imgcls, int(xmin), int(ymin), int(xmax), int(ymax)]
        bboxes.append(bbox)
    # Save bboxes
    box['bboxes'] = bboxes

    # Get a box in boxes
    boxes.append(box)


# This function can get all filenames in the path
def getPath(Annotations_Path):
    XMLNAMES = os.listdir(Annotations_Path)
    return XMLNAMES


# This function can get all box contained in boxes
def getBoxes():
    boxes = []
    # Get all xml names
    Xml_Names = getPath(Annotations_Path)

    # Read all xml
    for xmlname in Xml_Names:
        xmlpath = Annotations_Path + '/' + xmlname
        readXML(xmlpath, boxes)

    return boxes


# This function is used to generate txt document
def gen_txt(box, path):
    save_path = path + '/' + box['filename'].split('.')[0] + '.txt'
    size = box['size']
    with open(save_path, 'w', encoding='utf-8') as f:
        for bbox in box['bboxes']:
            bbox = turn_to_Yolo(size, bbox)
            bbox[0] = Classes.index(bbox[0])
            f.write(
                str(bbox[0]) + ' ' + str(bbox[1]) + ' ' + str(bbox[2]) + ' ' + str(bbox[3]) + ' ' + str(bbox[4]) + '\n')
    f.close


# This function is used to generate img document
def gen_img(filename, path_old, path_new):
    oldpath = path_old + '/' + filename
    newpath = path_new + '/' + filename

    shutil.copy(oldpath, newpath)


# This function is used to turn VOC to Yolo
# Yolo_datasets is (x_center, y_center, w, h)
def turn_to_Yolo(size, bbox):
    cls = bbox[0]

    # Get number
    dw = 1./int(size[0])
    dh = 1./int(size[1])

    xmin = int(bbox[1])
    ymin = int(bbox[2])
    xmax = int(bbox[3])
    ymax = int(bbox[4])

    # Calculate
    dx_center = (xmin + xmax) / 2.0
    dy_center = (ymin + ymax) / 2.0
    x_center = dx_center * dw
    y_center = dy_center * dh

    w = xmax - xmin
    h = ymax - ymin
    w = w * dw
    h = h * dh

    return [cls, x_center, y_center, w, h]


def gen_index(filename, num):
    clas = ['train.txt', 'test.txt', 'val.txt']
    path = clas[num]
    with open(path, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')
    f.close


# This function is used to decide which part of your dataset is used in train or val or test
def div_dataset(boxes):
    for box in boxes:
        filename = box['filename']
        randNum = random.randint(1, 100)
        if randNum <= val_percent * 100:
            gen_txt(box, Val_Path_label)
            gen_img(filename, Image_Path, Val_Path_img)
            gen_index(filename, 2)
        elif randNum > train_percent * 100:
            gen_txt(box, Test_Path_label)
            gen_img(filename, Image_Path, Test_Path_img)
            gen_index(filename, 1)
        else:
            gen_txt(box, Train_Path_label)
            gen_img(filename, Image_Path, Train_Path_img)
            gen_index(filename, 0)

def detect_path():
    path_list = ['images/train', 'images/val', 'images/test',
                 'labels/train', 'labels/val', 'labels/test',
                 'test.txt', 'train.txt', 'val.txt']
    for path in path_list:
        if os.path.exists(path):
            # path exists
            # print(os.listdir(path))
            if path in ['test.txt', 'train.txt', 'val.txt']:
                os.remove(path)
                print(path + ' has been removed')
            else:
                items = os.listdir(path)
                for item in items:
                    os.remove(path+'/'+item)
                    print(path + '/' + item + ' has been removed')
        else:
            # path do not exist
            print("path not found, creating path: " + path)
            if path in ['test.txt', 'train.txt', 'val.txt']:
                file = open(path, 'w', encoding='utf-8')
                file.close()
            else:
                os.makedirs(path)
if __name__ == '__main__':
    detect_path()
    boxes = getBoxes()
    div_dataset(boxes)
```

