import cv2
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

from motion_processor import MotionProcessor

class MotionCapture:
    def __init__(self):
        print("MotionCapture:__init__")

    def capture(self, video_file_or_camera):
        print("MotionCapture:capture")
        face_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')

        clip = VideoFileClip(video_file_or_camera)
        print(video_file_or_camera + " duration "+ str(clip.duration) + ", framesPerSecond " + str(clip.fps))

        mp = MotionProcessor()

        cap = cv2.VideoCapture(video_file_or_camera)

        # Check if camera opened successfully
        if (cap.isOpened() == False):
            print("Error opening video stream or file, '"+ video_file_or_camera +"'")

#        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        mp.initialize()
        while (cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) == 1 :
                    for (x, y, w, h) in faces:
                        mp.add_motion_rectangle(x, y, w, h)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
#                        print("width",w, "height", h)
                else:
                    print("----------------------------------------------No face in frame!")


                cv2.imshow('Frame', frame)

                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break

        cv2.destroyWindow('Frame')
        # When everything done, release the video capture object
        cap.release()

        mp.fft_filter_motion('X', clip.fps)
        mp.fft_filter_motion('Y', clip.fps)
        mp.fft_filter_motion('W', clip.fps)
        mp.fft_filter_motion('H', clip.fps)
        plt.show()
