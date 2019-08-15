import sys

from motion_capture import MotionCapture

#VIDEO_FILE_CLIP = "Fred_again.mov"
#VIDEO_FILE_CLIP = "Fred-110-heart-rate.mov"
#VIDEO_FILE_CLIP = "Fred-57-heart-rate.mov"
VIDEO_FILE_CLIP = "Fred-57-heart-rate-2.mov"
def main(args):
    mc = MotionCapture()
    mc.capture(VIDEO_FILE_CLIP)
    return 0


if __name__ == '__main__':

    sys.exit(main(sys.argv))

