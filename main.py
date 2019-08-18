import sys

from motion_capture import MotionCapture

# VIDEO_FILE_CLIP = "Fred_again.mov"
# VIDEO_FILE_CLIP = "Fred-110-heart-rate.mov"
# VIDEO_FILE_CLIP = "Fred-57-heart-rate.mov"
# VIDEO_FILE_CLIP = "Fred-57-heart-rate-2.mov"
# VIDEO_FILE_CLIP = "fred_77bpm_30fps.mov"
VIDEO_FILE_CLIP = None

CONFIG_FILE = "config.txt"

def read_config():
    with open(CONFIG_FILE, 'r') as config:
        dict_from_file = eval(config.read())
    return dict_from_file


def main(args):
    config = read_config()
    mc = MotionCapture(config)
#    mc.test_filters()
    mc.capture(VIDEO_FILE_CLIP)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
