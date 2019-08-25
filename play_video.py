import sys
import time
import os
import cv2

from camera_opencv import CameraOpenCv
from camera_raspbian import CameraRaspbian

VIDEO_FILE_CLIP = None
CONFIG_FILE = "config.txt"

    # noinspection PyPep8
def play_video(config, video_file_or_camera):
    print("play_video")

    if video_file_or_camera is None:
        video_file_or_camera = 0  # First camera

    video = create_camera(video_file_or_camera)

    is_opened = video.open_video(video_file_or_camera)
    if not is_opened:
        print("Error opening video stream or file, '" + video_file_or_camera + "'")
    else:
        if video_file_or_camera == 0:
            video.set_frame_rate(config["video_fps"])
            video.set_resolution(config["resolution"]["width"], config["resolution"]["height"])

        width, height = video.get_resolution()
        # Note that setting camera properties may not always work...
        config["resolution"]["width"] = width
        config["resolution"]["height"] = height
        config["video_fps"] = video.get_frame_rate()

        print("Video: Resolution = " + str(config["resolution"]["width"]) + " X "
              + str(config["resolution"]["height"]) + ". Frame rate = " + str(round(config["video_fps"])))

    frame_count = 0
    start_time = time.time()

    while video.is_opened():
        ret, frame = video.read_frame()
        if ret:
            frame_count = frame_count+1
            cv2.imshow('Frame', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        else:
            break

    end_time = time.time()
    print("Elapsed time: " + str(round(end_time-start_time)) + " seconds. fps:" + str( round(frame_count/(end_time-start_time), 2)))
    cv2.destroyWindow('Frame')
    # When everything done, release the video capture object
	video.close_video()



def read_config():
    with open(CONFIG_FILE, 'r') as config:
        dict_from_file = eval(config.read())
    return dict_from_file

def create_camera( video_file_or_camera):
     ### For files nor non raspberrypi devices, use open cv
	if os.path_exists("/etc/rpi-issue"):
		return CameraRaspbian()
	else:
		return None

def main(args):
    global VIDEO_FILE_CLIP
    config = read_config()
    if len(args) > 1:
        VIDEO_FILE_CLIP = args[1]
    play_video(config, VIDEO_FILE_CLIP)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
