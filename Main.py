import cv2
import os
import cvzone
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)


class DragImg():
    def __init__(self, path, pos):
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise ValueError(f"Cannot load image {path}")

        self.h, self.w = self.img.shape[:2]
        self.pos = pos
        self.locked = False

    def grab(self, cursor):
        cx, cy = cursor
        self.pos[0] = cx - self.w // 2
        self.pos[1] = cy - self.h // 2


# LOAD IMAGES
folder = "ImagesPNG"
files = os.listdir(folder)

imgList = []
for i, f in enumerate(files):
    if f.lower().endswith((".png", ".jpg", ".jpeg")):
        imgList.append(
            DragImg(os.path.join(folder, f), [100 + i * 300, 200])
        )

print("Images loaded:", len(imgList))


while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    if hands:
        lm = hands[0]['lmList']
        ix, iy = lm[8][0], lm[8][1]
        tx, ty = lm[4][0], lm[4][1]

        dist, _, img = detector.findDistance((ix, iy), (tx, ty), img)
        print("Distance:", int(dist))

        for obj in imgList:
            x, y = obj.pos

            # GRAB
            if dist < 55:
                if x < ix < x + obj.w and y < iy < y + obj.h:
                    obj.locked = True

            # RELEASE
            if dist > 80:
                obj.locked = False

            # MOVE
            if obj.locked:
                obj.grab((ix, iy))

    # DRAW
    for obj in imgList:
        img = cvzone.overlayPNG(img, obj.img, obj.pos)

    cv2.imshow("Virtual Drag & Drop", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()





