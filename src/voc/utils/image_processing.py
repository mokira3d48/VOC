def crop(bbox, img):
    """Function of image extraction using bounding box"""
    x, y, w, h = bbox
    x = max(x, 0)
    y = max(y, 0)
    x1, y1 = round(x), round(y)
    x2, y2 = round(x+w), round(y+h)
    img_crop = img[y1:y2, x1:x2, :]
    return img_crop
