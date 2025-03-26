import os
import logging
from dataclasses import dataclass

import numpy as np
import cv2 as cv
import torch
from ultralytics import YOLO

LOG = logging.getLogger(__name__)

DEVICE = os.getenv('DEVICE', 'cuda:0' if torch.cuda.is_available() else 'cpu')
print(f"DEVICE SELECTED: {DEVICE}")


@dataclass
class ObjDetected(object):
    """Result data class

    :type clid: `int`
    :type name: `str`
    :type confidence: `float`
    :type box: `numpy.ndarray`
    :type logit: `numpy.ndarray`
    """
    clid = -1
    name = ''
    confidence = -1.0
    box = None
    logit = None

    def __str__(self):
        return (f"class name: {self.name:>12s} \t"
                f" confidence: {self.confidence:5.4f} \t"
                f" logit: {' '.join([f'{x:8.4f}' for x in list(self.logit)])}"
                f"\t box: {' '.join([f'{x:8.1f}' for x in list(self.box)])}")


class ObjectDetection(object):
    """Ultralytics YOLO object detection

    :param net:
    :param class_names:
    :param threshold:

    :type class_names: `tuple`
    :type threshold: `float`
    """
    def __init__(self, net, class_names=None, threshold=None, gap=10):
        self._net = net
        self._allow_cls_names = class_names
        self._gap = gap
        self.threshold = threshold
        self._class_names = [name for _, name in net.names.items()]
        self._memory = []

    @property
    def classes(self):
        """:list: returns number of classes"""
        return self._class_names

    @property
    def allow_num_classes(self):
        """:int: returns number of classes"""
        return len(self._allow_cls_names)

    @classmethod
    def get_instance(
        cls, model, class_names=None, threshold=None, gap=10, device=DEVICE
    ):
        """
        Class method that allows to build and return
        an instance of the object detection algorithm.

        :param model: The file path of pretrained model.
        :param class_names: The list of allowed class ids.
        :param threshold: The threshold value of detection precision.
        :param gap: This is the minimal gap between two bounding box.
        :param device: The selected device on which the calculations
            will be performed.

        :type model: `str`
        :type class_names: `tuple` of `str`
        :type threshold: `float`
        :type gap: `int`
        :type device: `torch.device`|`str`
        :rtype: `ObjectDetection`
        """
        if not os.path.isfile(model):
            raise FileNotFoundError(f"No such model file at {model}")
        net = YOLO(model, verbose=True)
        net = net.to(device)
        instance = cls(net, class_names, threshold, gap)
        return instance

    # def _rm_double(self, objs):
    #     if not objs:
    #         return
    #     new_objs = []
    #     while objs:
    #         obj = objs.pop()
    #         tmpo = objs[:]
    #         objs.clear()
    #         for oth in tmpo:
    #             x = np.abs(obj.box[0] - oth.box[0]) <= self._gap
    #             y = np.abs(obj.box[1] - oth.box[1]) <= self._gap
    #             w = np.abs(obj.box[2] - oth.box[2]) <= self._gap
    #             h = np.abs(obj.box[3] - oth.box[3]) <= self._gap
    #             LOG.debug("-------------------")
    #             LOG.debug(str(x))
    #             LOG.debug(str(y))
    #             LOG.debug(str(w))
    #             LOG.debug(str(h))
    #             LOG.debug(str(obj))
    #             LOG.debug(str(oth))
    #             if x and y and w and h:
    #                 if obj.confidence < oth.confidence:
    #                     obj = oth
    #                     continue
    #             objs.append(oth)
    #
    #         new_objs.append(obj)
    #     return new_objs

    def detect(self, image):
        """Method of object detection"""
        if not hasattr(image, 'shape'):
            raise TypeError(
                "The image must be a type of cv2.Mat or numpy.ndarray.")

        img_w = image.shape[1]
        img_h = image.shape[0]
        self._memory.clear()

        results = self._net(image, stream=True)
        objs_detected = []
        for result in results:
            # print(result.boxes)
            data = result.boxes
            iterator = zip(data.cls, data.conf, data.xywhn, data.xywh)
            for class_id, conf, logit, box in iterator:
                class_id = int(class_id.cpu().item())
                class_name = self._class_names[class_id]
                confidence = conf.cpu().item()
                # LOG.info(f"class id: {class_id:4d}"
                #          f" class name: {class_name:1s}"
                #          f" precision: {confidence:5.2f}"
                #          f" boxes: " + str(logit))

                # is_left_than = (
                #     self.threshold and confidence < self.threshold)
                # cls_not_allowed = (
                #     self._allow_cls_names
                #     and (class_name not in self._allow_cls_names))
                # if cls_not_allowed or is_left_than:
                #     continue

                # center_x = int(logit[0] * img_w)
                # center_y = int(logit[1] * img_h)
                # w = int(logit[2] * img_w)
                # h = int(logit[3] * img_h)
                # x = center_x - w / 2
                # y = center_y - h / 2

                center_x = logit[0] * img_w
                center_y = logit[1] * img_h
                w = logit[2] * img_w
                h = logit[3] * img_h
                x = center_x - w / 2
                y = center_y - h / 2

                logit = logit.cpu().numpy()
                box = [x.cpu().item(), y.cpu().item(),
                       w.cpu().item(), h.cpu().item()]
                box = np.asarray(box)

                obj_dec = ObjDetected()
                obj_dec.clid = class_id
                obj_dec.name = class_name
                obj_dec.confidence = confidence
                obj_dec.logit = logit
                obj_dec.box = box

                # LOG.debug(obj_dec)
                objs_detected.append(obj_dec)

        # objs_detected = self._rm_double(objs_detected)
        # print("-------------------------------------")
        # for x in objs_detected:
        #     print(x)
        boxes = [o.box for o in objs_detected]
        confs = [o.confidence for o in objs_detected]
        indexes = cv.dnn.NMSBoxes(
            bboxes=boxes,
            scores=confs,
            score_threshold=0.5,
            nms_threshold=0.4)
        indexes = list(indexes)
        objs_detected = [
            o for i, o in enumerate(objs_detected) if i in indexes]
        for o in objs_detected: LOG.debug(o)
        return objs_detected

    def __call__(self, img):
        res = self.detect(img)
        return res


# def wtf():
#     """Main function"""
#     import sys
#     import cv2 as cv
#
#     path = sys.argv[1]
#     image = cv.imread(path)
#     image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
#     model = 'resources/yolov8s.pt'
#     object_dec = ObjectDetection.get_instance(model, class_ids=(1, 2, 3, 5, 7))
#     detections = object_dec(image)
#     for detection in detections:
#         print(str(detection))
#
#
# if __name__ == '__main__':
#     wtf()
