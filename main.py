import sys

from motion_capture import MotionCapture

#VIDEO_FILE_CLIP = "Fred_again.mov"
#VIDEO_FILE_CLIP = "Fred-110-heart-rate.mov"
# #VIDEO_FILE_CLIP = "Fred-57-heart-rate.mov"
#VIDEO_FILE_CLIP = "Fred-57-heart-rate-2.mov"
VIDEO_FILE_CLIP = "fred_77bpm_30fps.mov"
def main(args):
    mc = MotionCapture()
#    mc.test_filters()
    mc.capture(VIDEO_FILE_CLIP)
    return 0


if __name__ == '__main__':

    sys.exit(main(sys.argv))

