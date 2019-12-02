import cv2
import os


def v2i_cv(input_video, output_img):
    if not os.path.exists(input_video):
        raise Exception('input error!', input_video)

    if not os.path.exists(output_img):
        os.makedirs(output_img)

    video_capture = cv2.VideoCapture(input_video)
    success, frame = video_capture.read()
    counter = 0
    while success:
        img_name = os.path.join(output_img, str(counter) + '.jpg')
        cv2.imwrite(img_name, frame)

        success, frame = video_capture.read()
        counter += 1
    video_capture.release()
    print("Extract frames from video success: {} frames".format(counter))


if __name__ == '__main__':
    input = '/Users/mac/data/3D_Cloud/10.211.197.165_01_20191107103125741.mp4'
    output = '/Users/mac/data/3D_Cloud/imgs'

    v2i_cv(input, output)

''''
mp4_frame_files =
video_capture = cv2.VideoCapture(temp_mp4_file)
success ,frame = video_capture.read()
i = 0
while success:
    frame_basename = os.path.basename(img_files[i]).split('.')
    frame_name = frame_basename[0] + "_mp4." + frame_basename[1]
    dest_frame_file = os.path.join(temp_frame_dir, frame_name)
    cv2.imwrite(dest_frame_file, frame)
    assert os.path.exists(dest_frame_file), "file does not exist: {}".format(dest_frame_file)
    # mp4_frame_files.append(dest_frame_file)
    mp4_frame_files[os.path.basename(os.path.splitext(dest_frame_file)[0])[:-4]] = dest_frame_file

    success ,frame = video_capture.read()
    i += 1
video_capture.release()
assert len(mp4_frame_files) == len(img_files), "len(mp4_frame_files)={}; len(img_files)={}".format(len(mp4_frame_files), len(img_files))
print("Extract frames from video success: {} frames".format(i))
'''
