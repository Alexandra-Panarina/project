import os
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import numpy as np
import cv2

def get_class_names(path):
    classes_path = os.path.expanduser(path)
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names

def visualize_boxes_and_lables_on_image(image, boxes, classes, scores,threshold,class_names):
    objects_box = list()
    for i in range(boxes.shape[0]):
        if (scores[i]>threshold) and(classes[i]==1):
            box = boxes[i].tolist()
            display_str =''
            class_name = class_names[classes[i]-1]
            display_str = str(class_name)
            display_str = '{}:{}%'.format(display_str,int(scores[i]*100))
            ymin,xmin,ymax,xmax=box
            image,min_point, bottom = draw_bounding_box_on_image(image,ymin,xmin,ymax,xmax)
            person_point = tuple([min_point,bottom])
            person_score = scores[i]
            person = {'point':person_point,'probability':person_score}
            objects_box.append(person)
    return image, objects_box



def draw_bounding_box_on_image(image,ymin,xmin,ymax,xmax, color = 'red',thickness = 4,use_normalized_coordinates = True):
    image = Image.fromarray(np.uint8(image)).convert('RGB')
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    if use_normalized_coordinates:
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                      ymin * im_height, ymax * im_height)
    else:
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)

    draw.line([(left, top), (left, bottom), (right, bottom),
               (right, top), (left, top)], width=thickness, fill=color)
    min_point = (right+left)/ 2
    draw.point([(min_point,bottom)], fill='blue')
    # print (min_point, bottom)
    return image, min_point, bottom


def convert_to_local_coords(pts, mtxL, distL, rvecL, tvecL):

    roi_left = -10
    roi_right = 10
    roi_near = 15.126
    length = 60

    objpoint = np.array([
        (roi_left, 0, roi_near),
        (roi_right, 0, roi_near),
        (roi_left, 0, roi_near + length),
        (roi_right, 0, roi_near + length)], dtype='double')

    imgpoint, _ = cv2.projectPoints(objpoint, rvecL, tvecL, mtxL, distL)

    pts1 = np.float32([
        [imgpoint[0][0][0], imgpoint[0][0][1]],
        [imgpoint[1][0][0], imgpoint[1][0][1]],
        [imgpoint[2][0][0], imgpoint[2][0][1]],
        [imgpoint[3][0][0], imgpoint[3][0][1]]])

    out_width = 200
    out_height = int(out_width * length / (roi_right - roi_left))

    pts2 = np.float32([
        [0, out_height],
        [out_width, out_height],
        [0, 0],
        [out_width, 0]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    list_pts = []

    x, y = pts[0],pts[1]
    list_pts.append([[x, y]])

    pts = np.float32(list_pts)
    converted_pts = cv2.perspectiveTransform(pts, M)


    for pt in converted_pts:
        x, y = pt[0][0], pt[0][1]
        x, y = int(x), int(y)
        x = (x / out_width * (roi_right-roi_left) + roi_left)*-1
        y = (out_height - y) / out_height * length + roi_near
        # if (abs(x)< 1.8):
        #     y = y + FIRST_ZONE_A1_COEFF*y + FIRST_ZONE_A0_COEFF
        # else:
        #     y = y+SECOND_ZONE_A1_COEFF*y + SECOND_ZONE_A0_COEFF


    return x,y
