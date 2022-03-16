import cv2


def remove_table(path_img, color_grey):
    # Load image, grayscale, and Otsu's threshold
    image = path_img# cv2.imread(path_img)
    if color_grey == 'color':
        gray = image[:, :, 0]#cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    image = gray
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (0, 0, 0), 2)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,15))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (0, 0, 0), 3)

    # Dilate to connect text and remove dots
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))
    dilate = cv2.dilate(thresh, kernel, iterations=2)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 500:
            cv2.drawContours(dilate, [c], -1, (0, 0, 0), -1)

    # Bitwise-and to reconstruct image
    result = cv2.bitwise_and(image, image, mask=dilate)
    result[dilate == 0] = 255#, 255, 255)
    return result
