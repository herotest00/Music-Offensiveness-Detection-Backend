import cv2
# import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision, BaseOptions
from mediapipe.tasks.python.vision import HandLandmarkerOptions, RunningMode, HandLandmarker


class GestureDetectionService:
    # __model_path = 'hand_landmarker.task'

    def __init__(self, video_filepath):
        self.__video_filepath = video_filepath
        # self.__options = HandLandmarkerOptions(
        #     base_options=BaseOptions(model_asset_path=self.__model_path),
        #     running_mode=RunningMode.VIDEO)

    def get_offensiveness(self):
        # with HandLandmarker.create_from_options(self.__options) as landmarker:
        #     video = cv2.VideoCapture(self.__video_filepath)
        #
        #     fps = video.get(cv2.CAP_PROP_FPS)
        #     time = 0
        #
        #     while True:
        #         # Citește următorul cadru
        #         ret, frame = video.read()
        #
        #         # Dacă cadru este citit corect ret este True
        #         if not ret:
        #             print("Can't receive frame (stream end?). Exiting ...")
        #             break
        #
        #         # Convert the frame received from OpenCV to a MediaPipe’s Image object.
        #         mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        #
        #         # Perform hand landmarks detection on the provided single image.
        #         # The hand landmarker must be created with the video mode.
        #         hand_landmarker_result = landmarker.detect_for_video(mp_image, time)
        #
        #         # Afișează cadru pe ecran
        #         cv2.imshow('frame', hand_landmarker_result)
        #
        #         # Afișează timpul curent (în secunde)
        #         print('Timestamp: ', time)
        #
        #         # Așteaptă 1 ms între cadre (pentru a afișa videoclipul)
        #         key = cv2.waitKey(1)
        #
        #         # Actualizează timpul
        #         time += 1 / fps
        #
        #     # Eliberează obiectul VideoCapture și închide ferestrele deschise
        #     video.release()
        #     cv2.destroyAllWindows()
        return 0.13
