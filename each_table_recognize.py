import numpy as np
import pytesseract
import cv2
from remove_table import *

def sort2(val):  # helper for sorting by y
    return val[1]

def rec_txt(crop_img,row,path_to_img, PATH_TO_SAVE, color_grey, filter_, rm):

    recognized_string = pytesseract.image_to_string(crop_img, lang="rus")
    row.append(recognized_string.replace("\n", " "))
    print(recognized_string)
    p = path_to_img[:-4].split("\\")

    with open(PATH_TO_SAVE + str(p[-1:][0]) + f'_table_{rm}_{color_grey}_{filter_}.txt', 'a+') as f:
        f.write(str(recognized_string))

def improve_image_quality(crop_img):
    max_v = 200
    min_v = 100
    mid_tone = 128
    other_max_v = 255
    other_min_v = 0
    gamma = 1
    # img = crop_img
    img = crop_img.astype(int)
    sub = (img - min_v)
    img = 255 * (sub / (max_v - min_v))
    if mid_tone != 128:
        img = 255 * ((img / 255) ** gamma)
        img[img > 255] = 255
    img = (img / 255) * (other_max_v - other_min_v) + other_min_v
    img = np.clip(img, 0, 255)
    crop_img = img.astype(np.uint8)
    return crop_img

def recogn_table(path_to_img: str, PATH_TO_SAVE:str, color_grey: str, filter_: str):
    image = cv2.imread(path_to_img)
    # remove color info
    gray_image = image[:, :, 0]

    # (1) thresholding image
    ret, thresh_value = cv2.threshold(gray_image, 180, 255, cv2.THRESH_BINARY_INV)

    # (2) dilating image to glue letter with e/a
    kernel = np.ones((2, 2), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

    # (3) looking for contours
    contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # (4) extracting coordinates and filtering them empirically
    coordinates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > 50 and w > 50 and h * w < 350000:
            coordinates.append((x, y, w, h))

    recognized_table = row = []
    prev_y = 0
    coordinates.sort()  # sort by x
    coordinates.sort(key=sort2)  # sort by y
    for coord in coordinates:
        x, y, w, h = coord
        if y > prev_y + 5:  # new row if y is changed
            recognized_table.append(row)
            row = []

        if color_grey == 'color':
            ## original image processing
            crop_img = image[y:y + h, x:x + w]
        else:
            ### grey_scale image processing
            crop_img = gray_image[y:y + h, x:x + w]

        if filter_ != '' and color_grey == 'grey':
            if filter_ == 'THRESH_OTSU':
                ret, crop_img = cv2.threshold(crop_img, 100, 255, cv2.THRESH_OTSU)
            elif filter_ == 'THRESH_BINARY+THRESH_OTSU':
                ret, crop_img = cv2.threshold(crop_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif filter_ == 'equalizeHist':
                crop_img = cv2.equalizeHist(crop_img)
            elif filter_ == 'createCLAHE':
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                crop_img = clahe.apply(crop_img)

        crop_img = improve_image_quality(crop_img)
        crop_img_rm_table = remove_table(crop_img, color_grey)
        # cv2.imshow('crop', crop_img_rm_table)
        # cv2.waitKey()
        rec_txt(crop_img, row, path_to_img, PATH_TO_SAVE, color_grey, filter_, rm='')
        rec_txt(crop_img_rm_table, row, path_to_img, PATH_TO_SAVE, color_grey, filter_, rm='rm')

        # recognized_string = pytesseract.image_to_string(crop_img_rm_table, lang="rus")
        # row.append(recognized_string.replace("\n", " "))
        # print(recognized_string)
        # p = path_to_img[:-4].split("\\")
        #
        # with open(PATH_TO_SAVE + str(p[-1:][0]) + f'_table_rm_{color_grey}_{filter_}.txt', 'a+') as f:
        #     f.write(str(recognized_string))
        #
        # recognized_string = pytesseract.image_to_string(crop_img, lang="rus")
        # row.append(recognized_string.replace("\n", " "))
        # print(recognized_string)
        #
        # with open(PATH_TO_SAVE+str(p[-1:][0]) + f'_table_{color_grey}_{filter_}.txt', 'a+') as f:
        #     f.write(str(recognized_string))

        prev_y = y
    recognized_table
