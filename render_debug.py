# render_debug.py
import cv2
import numpy as np

class RendererDebug:
    def __init__(self, config=None):
        self.config = config or {}
        self.window_name = self.config.get("window_name", "DEBUG")
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 640, 480)
        cv2.moveWindow(self.window_name, 50, 50)

    def render(self, *, frame=None, game_state=None, blink_event=False, face_ok=False, ear=None):
        if frame is None:
            img = np.full((480, 640, 3), 40, dtype=np.uint8)
        else:
            img = frame.copy()

        cv2.putText(img, f"STATE: {game_state.state}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(img, f"face_ok: {face_ok}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(img, f"ear: {ear}", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(img, f"blink_event: {blink_event}", (10, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow(self.window_name, img)
