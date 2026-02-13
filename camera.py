# camera.py
import cv2

class CameraCapture:
    def __init__(self, config=None):
        cfg = config or {}
        self.device = cfg.get("device", 0)
        self.w = cfg.get("width", 640)
        self.h = cfg.get("height", 480)

        self.cap = cv2.VideoCapture(self.device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")

        print(f"CameraCapture opened device={self.device} {self.w}x{self.h}")

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame  # BGR

    def release(self):
        self.cap.release()
