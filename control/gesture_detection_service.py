import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python import solutions
from mediapipe.tasks import python
from mediapipe.tasks.python import vision, BaseOptions
from mediapipe.tasks.python.vision import HandLandmarkerOptions, RunningMode, HandLandmarker


class GestureDetectionService:
    __model_path = 'hand_landmarker.task'

    __margin = 10  # pixels
    __font_size = 1
    __font_thickness = 1
    __handedness_text_color = (88, 205, 54)  # vibrant green

    def __init__(self, video_filepath):
        self.__video_filepath = video_filepath
        self.__options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.__model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=10)

    def get_offensiveness(self):
        with HandLandmarker.create_from_options(self.__options) as landmarker:
            video = cv2.VideoCapture(self.__video_filepath)
            fps = video.get(cv2.CAP_PROP_FPS)

            frames_to_skip = int(fps // 10)

            frame_number = 0
            recorded_frame_number = 0

            while True:
                ret, frame = video.read()
                if not ret:
                    print("Finished processing video. Exiting ...")
                    break

                if frame_number % frames_to_skip == 0:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                    time1 = int(frame_number / fps * 1e6)
                    hand_landmarker_result = landmarker.detect_for_video(mp_image, time1)

                    if hand_landmarker_result.handedness:
                        print(hand_landmarker_result.handedness)
                        annotated_image = self.__draw_landmarks_on_image(mp_image.numpy_view(), hand_landmarker_result)
                        cv2.imwrite('frame' + str(recorded_frame_number) + str(hand_landmarker_result.handedness) + '.jpg', annotated_image)
                        recorded_frame_number += 1

                frame_number += 1

            video.release()
            cv2.destroyAllWindows()
            return 0.13

    def __draw_landmarks_on_image(self, rgb_image, detection_result):
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = np.copy(rgb_image)

        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx]

            # Draw the hand landmarks.
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                solutions.hands.HAND_CONNECTIONS,
                solutions.drawing_styles.get_default_hand_landmarks_style(),
                solutions.drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - self.__margin

            # Draw handedness (left or right hand) on the image.
            cv2.putText(annotated_image, f"{handedness[0].category_name}",
                        (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                        self.__font_size, self.__handedness_text_color, self.__font_thickness, cv2.LINE_AA)

        return annotated_image
