import cv2
import json
import string

IMG_WIDTH = 267
IMG_HEIGHT = 400

def str2coord(st):
    strs = st.split(' ')
    res = dict()
    strs = [s.translate(str.maketrans("", "", string.punctuation)) for s in strs]
    for i in range(4):
        res[strs[i*2]] = int(strs[i*2+1][:-2])
    return res

def cal_bounding_box_are(coordinate):
    return coordinate['width'] * coordinate['height']

def img_resize(img, width, height):
    return cv2.resize(img, (width, height))

def main():
    query = 'dresses-cocktail'
    with open('data/' + query + 'boundingbox.json') as infile:
        for line in infile:
            data = json.loads(line)
            temp = list(data.keys())
            temp.remove('size')
            file_name = temp[0]
            img = img_resize(cv2.imread('data/'+query+'/'+file_name), data['size']['width'], data['size']['height'])

            data[file_name] = [str2coord(st) for st in data[file_name]]
            bounding_box_areas = [(cal_bounding_box_are(coord), i) for i, coord in enumerate(data[file_name])]
            bounding_box_areas.sort(reverse=True)
            main_bounding_box = data[file_name][bounding_box_areas[0][1]]
            print(main_bounding_box)

            cv2.rectangle(img, (main_bounding_box['left'], main_bounding_box['top']), (main_bounding_box['left']+
                        main_bounding_box['width'], main_bounding_box['top']+main_bounding_box['height']), (255, 0, 0), 2)

            cv2.imshow('Image with Bounding Box', img)
            cv2.waitKey(0)

if __name__ == '__main__':
    main()
