import sys
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
        fps = cap.get(cv2.CAP_PROP_FPS)

        if video_file_or_camera == 0:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["resolution"]["width"])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["resolution"]["height"])
            cap.set(cv2.CAP_PROP_FPS, config["video_fps"])
            fps = cap.get(cv2.CAP_PROP_FPS)
        else:
            config["resolution"]["width"] = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            config["resolution"]["height"] = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            config["video_fps"] = cap.get(cv2.CAP_PROP_FPS)

        print( "Video: Resolution = " + str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) + " X "
           + str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) + ". Frames rate = " + str(round(fps)))

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Frame', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        else:
            break

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
