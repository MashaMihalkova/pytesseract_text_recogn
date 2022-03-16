from pdf2image import convert_from_path
import os
import matplotlib.pyplot as plt
import cv2
from pytesseract import Output
from each_table_recognize import *
import optparse


# Simple image to string
def load_image(path):
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)


def process_image_tesseract(img_path: str, PATH_TO_SAVE, COLOR_GREY: str, FILTER: str):
    img = load_image(img_path)

    text = pytesseract.image_to_string(img, lang='rus')
    p = img_path[:-4].split("\\")

    with open(PATH_TO_SAVE+str(p[-1:][0]) + f'{COLOR_GREY}_{FILTER}.txt', 'a+') as f:
        f.write(str(text))
    return text


def convert_pdf_to_txt(PATH_TO_PDF, PATH_TO_POPPLER, PATH_TO_SAVE, target_word, target_word_end):
    pdfs = PATH_TO_PDF
    pages = convert_from_path(pdfs, 350, poppler_path=PATH_TO_POPPLER)
    i = 1
    for page in pages:
        image_name = PATH_TO_SAVE + "Page_" + str(i) + '.png'
        page.save(image_name, "png")
        process_img(PATH_TO_SAVE, "Page_" + str(i) + '.png', target_word, target_word_end)
        i = i + 1


def process_img(PATH_TO_FOLDER, file, PATH_TO_SAVE, target_word, target_word_end):
    img = cv2.imread(PATH_TO_FOLDER + '/' + file)
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='rus')
    print(d['text'])
    word_occurences = [i for i, word in enumerate(d["text"]) if word.lower() == target_word]
    word_occurences_end = [i for i, word in enumerate(d["text"]) if word.lower() == target_word_end]
    image_copy = img.copy()

    if not word_occurences:
        process_image_tesseract(PATH_TO_SAVE + f"{file}", PATH_TO_SAVE, COLOR_GREY, FILTER)
        recogn_table(PATH_TO_SAVE + f"{file}", PATH_TO_SAVE, color_grey=COLOR_GREY, filter_=FILTER)
    for occ in word_occurences:
        l = d["left"][occ]
        t = d["top"][occ]

        if not word_occurences_end:
            image_copy = image_copy[t - 25:image_copy.shape[0], 0:image_copy.shape[1]]
            plt.imsave(PATH_TO_SAVE + f"small_{file}", image_copy)
            process_image_tesseract(PATH_TO_SAVE + f"small_{file}", PATH_TO_SAVE, COLOR_GREY, FILTER)
            recogn_table(PATH_TO_SAVE + f"small_{file}", PATH_TO_SAVE, color_grey=COLOR_GREY, filter_=FILTER)
            break

        else:
            for end_ in word_occurences_end:
                t_end_ = d["top"][end_]

                image_copy = image_copy[t - 25:t_end_, 0:image_copy.shape[1]]
                plt.imsave(PATH_TO_SAVE + f"small_{file}", image_copy)
                process_image_tesseract(PATH_TO_SAVE + f"small_{file}", PATH_TO_SAVE, COLOR_GREY, FILTER)
                recogn_table(PATH_TO_SAVE + f"small_{file}", PATH_TO_SAVE, color_grey=COLOR_GREY, filter_=FILTER)

                break
            break


if __name__ == '__main__':

    parser = optparse.OptionParser()

    parser.add_option('-t', '--PYTESSERACT', type=str,
                      help="PATH TO PYTESSERACT", default="D:\\work2\\recognition_text\\Tesseract-OCR_rus\\tesseract")

    parser.add_option('-p', '--popler', type=str,
                      help="PATH TO POPPLER", default="D:\\work2\\recognition_text\\poppler-0.68.0_x86\\poppler-0.68.0\\bin")

    parser.add_option('-s', '--save', type=str,
                      help="PATH TO SAVE", default="D:\\work2\\recognition_text\\test_img1\\lkk\\")

    parser.add_option('-f', '--folder', type=str,
                      help="PATH TO FOLDER", default="D:\\work2\\recognition_text\\test_img1\\")

    parser.add_option('-c', '--color', type=str,
                      help="COLOR or GREY", default="grey")

    parser.add_option('-l', '--filter_table', type=str,
                      help="FILTER examples:'', THRESH_OTSU, THRESH_BINARY+THRESH_OTSU, equalizeHist, createCLAHE", default="")

    options, args = parser.parse_args()

    PATH_TO_PYTESSERACT = getattr(options, 'PYTESSERACT')  # -pyt
    PATH_TO_POPPLER = getattr(options, 'popler')  # -pop
    PATH_TO_SAVE = getattr(options, 'save')  # -s
    PATH_TO_FOLDER = getattr(options, 'folder')  # -fol
    COLOR_GREY = getattr(options, 'color')  # -c
    FILTER = getattr(options, 'filter_table')  # -f

    #
    # PATH_TO_PYTESSERACT = "D:\\work2\\recognition_text\\Tesseract-OCR_rus\\tesseract"
    # PATH_TO_POPPLER = "D:\\work2\\recognition_text\\poppler-0.68.0_x86\\poppler-0.68.0\\bin"
    # PATH_TO_SAVE = "D:\\work2\\recognition_text\\test_img1\\"
    # PATH_TO_FOLDER = "D:\\work2\\recognition_text\\test_img1\\"
    #
    # # processing mode of each table
    # COLOR_GREY = 'grey'  # examples: color, grey
    # FILTER = ''  # examples: THRESH_OTSU, THRESH_BINARY+THRESH_OTSU, equalizeHist, createCLAHE

    pytesseract.pytesseract.tesseract_cmd = PATH_TO_PYTESSERACT

    target_word = 'смены'  # "продолжительность"
    target_word_end = "бригадир"
    if not os.path.exists(PATH_TO_SAVE):
        os.makedirs(PATH_TO_SAVE)
    for p, dirs, files in os.walk(PATH_TO_FOLDER):
        for file in files:
                if file[-4:] == '.pdf':
                    # print('pdf')
                    convert_pdf_to_txt(PATH_TO_FOLDER + '/' + file, PATH_TO_POPPLER, PATH_TO_FOLDER,
                                       target_word, target_word_end)
                elif file[-4:] == '.png' or file[-4:] == '.jpg' or file[-5:] == '.jpeg':
                    process_img(PATH_TO_FOLDER, file, PATH_TO_SAVE, target_word, target_word_end)

        break
