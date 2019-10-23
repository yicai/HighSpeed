import cv2 as cv


def GetImageFileName(Path):

    return


filename = '/Users/mac/data/199.jpg'
TipsName = '/Users/mac/data/result/1.jpg'


img = cv.imread(filename)

print(img.shape)

cropped = img[100:200, 100:200]

cv.namedWindow('Test', cv.WINDOW_NORMAL)

cv.imshow("Test", img)

cv.waitKey(0)

cv.imshow("Crop", cropped)

key = cv.waitKey(0) & 0xFF

cv.destroyAllWindows()

if key == ord('s'):
    cv.imwrite(TipsName, cropped)

