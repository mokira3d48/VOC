from .utils.yod import ObjectDetection
from .utils.image_processing import crop


class Inference:

    def __init__(self, args):
        self.args = args
        self.pipeline = []

        args_pipeline = args['pipeline']
        for i in range(len(args_pipeline)):
            data = args_pipeline[i]
            weights_file = data['weights']
            threshold = data['threshold']
            model = ObjectDetection.get_instance(weights_file)
            self.pipeline.append((model, threshold))

    def __call__(self, image, detections=None):
        x = [image]
        y = None
        for model, threshold in self.pipeline:
            y = []
            for img in x:
                detections = model(img)
                boxes = [
                    d.box for d in detections if d.confidence >= threshold]
                for box in boxes:
                    sub_img = crop(box, img)
                    y.append(sub_img)
            x = y[:]
        return y
