import os
import shutil
from heapq import heappush, heappop

import cv2
from skimage import exposure
from ultralytics import YOLO


class ObjectDetectionService:
    __model_path = os.path.join('ml_models', 'yolo_v8.pt')
    __results_path = os.path.join('temp', 'predictions')
    __max_num_images = 20

    def __init__(self, video_filepath):
        self.__video_filepath = video_filepath

    def predict(self):
        print("Predicting...")
        shutil.rmtree(self.__results_path, ignore_errors=True)
        model = YOLO(self.__model_path)
        video = cv2.VideoCapture(self.__video_filepath)
        fps = video.get(cv2.CAP_PROP_FPS)

        heap = []
        frames_to_skip = int(fps // 7)
        frame_number = 0
        while video.isOpened():
            ret, frame = video.read()
            if ret:
                if frame_number % frames_to_skip == 0:
                    timestamp = video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    preprocessed_frame = self.__preprocess_frame(frame.copy())
                    results = model(preprocessed_frame, device=0, conf=0.5, retina_masks=True, verbose=False)
                    if len(results[0].boxes) > 0:
                        frame_with_boxes = self.__draw_boxes_on_frame(frame, preprocessed_frame, results)
                        heappush(heap, (-max([box.conf for box in results[0].boxes]), timestamp, frame_with_boxes))
            else:
                break
            frame_number += 1

        saved_images = []
        saved_times = []
        while heap and len(saved_images) < self.__max_num_images:
            _, timestamp, frame_with_boxes = heappop(heap)
            if all(abs(timestamp - t) >= 1 for t in saved_times):
                saved_images.append((frame_with_boxes, timestamp))
                saved_times.append(timestamp)
                self.__save_frame(frame_with_boxes, len(saved_images) - 1)

        print("Prediction complete.")
        return [image for image, _ in saved_images]

    @staticmethod
    def __preprocess_frame(frame):
        frame = cv2.resize(frame, (640, 640))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(frame)
        y = exposure.equalize_adapthist(y, clip_limit=0.03)
        y = (y * 255).astype('uint8')
        frame = cv2.merge((y, cr, cb))
        frame = cv2.cvtColor(frame, cv2.COLOR_YCrCb2BGR)

        return frame

    @staticmethod
    def __draw_boxes_on_frame(original_frame, processed_frame, results):
        resized_frame = cv2.resize(original_frame, (processed_frame.shape[1], processed_frame.shape[0]))

        for res in results:
            boxes = res.boxes.xyxy.cpu().numpy()
            scores = res.boxes.conf.cpu().numpy()
            for box, score in zip(boxes, scores):
                x1, y1, x2, y2 = box[:4]
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                resized_frame = cv2.rectangle(resized_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                score = "{:.2f}".format(score)
                cv2.putText(resized_frame, score, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return resized_frame

    def __save_frame(self, frame_with_boxes, frame_id):
        if not os.path.exists(self.__results_path):
            os.makedirs(self.__results_path)

        cv2.imwrite(os.path.join(self.__results_path, f"prediction_{frame_id}.jpg"), frame_with_boxes)

    @property
    def max_num_images(self):
        return self.__max_num_images
