import sys
import time
import cv2

VIDEO_FILE_CLIP = None
CONFIG_FILE = "config.txt"

    # noinspection PyPep8
def play_video(config, video_file_or_camera):
    print("play_video")

    if video_file_or_camera is None:
        video_file_or_camera = 0  # First camera

    cap = cv2.VideoCapture(video_file_or_camera)
    if not cap.isOpened():
        print("Error opening video stream or file, '" + video_file_or_camera + "'")
    else:
        if video_file_or_camera == 0:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["resolution"]["width"])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["resolution"]["height"])
            cap.set(cv2.CAP_PROP_FPS, config["video_fps"])

        # Note that setting camera properties may not always work...
        config["resolution"]["width"] = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        config["resolution"]["height"] = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        config["video_fps"] = cap.get(cv2.CAP_PROP_FPS)

        print("Video: Resolution = " + str(config["resolution"]["width"]) + " X "
              + str(config["resolution"]["height"]) + ". Frame rate = " + str(round(config["video_fps"])))

    frame_count = 0
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
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
    cap.release()



def read_config():
    with open(CONFIG_FILE, 'r') as config:
        dict_from_file = eval(config.read())
    return dict_from_file


def main(args):
    global VIDEO_FILE_CLIP
    config = read_config()
    if len(args) > 1:
        VIDEO_FILE_CLIP = args[1]
    play_video(config, VIDEO_FILE_CLIP)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
