# blink_detector.py
import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import (
    _normalized_to_pixel_coordinates as denormalize_coordinates
)

DEBUG = False
def dbg(*args):
    if DEBUG:
        print(*args)

def get_mediapipe_app(
    max_num_faces=1,
    refine_landmarks=True,                 # wie bei dir "lief gut"
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
):
    return mp.solutions.face_mesh.FaceMesh(
        max_num_faces=max_num_faces,
        refine_landmarks=refine_landmarks,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

def distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** 0.5

def get_ear(landmarks, refer_idxs, frame_width, frame_height):
    coords_points = []
    try:
        for i in refer_idxs:
            lm = landmarks[i]
            coord = denormalize_coordinates(lm.x, lm.y, frame_width, frame_height)
            if coord is None:
                return None  # important: if any coordinate is None, EAR is invalid (e.g. due to denormalize failure)
            coords_points.append(coord)

        P2_P6 = distance(coords_points[1], coords_points[5])
        P3_P5 = distance(coords_points[2], coords_points[4])
        P1_P4 = distance(coords_points[0], coords_points[3])
        if P1_P4 == 0:
            return None
        ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)
        return ear

    except Exception as e:
        dbg("[get_ear] Exception:", repr(e))
        return None

def calculate_avg_ear(landmarks, left_eye_idxs, right_eye_idxs, w, h):
    left = get_ear(landmarks, left_eye_idxs, w, h)
    right = get_ear(landmarks, right_eye_idxs, w, h)
    if left is None or right is None:
        return None
    return (left + right) / 2.0


class BlinkDetector:
    """
    update(frame) -> (blink_event, face_ok, ear)
    blink_event: True genau einmal pro Blink
    face_ok: True sobald Mediapipe ein Gesicht liefert
    ear: float oder None
    """

    def __init__(self, config=None):
        cfg = config or {}
        self.EAR_THRESH = cfg.get("EAR_THRESH", 0.18)
        self.MIN_CLOSED_S = cfg.get("min_closed_s", 0.04)
        self.REFRACTORY_S = cfg.get("refractory_s", 0.20)

        self.eye_idxs = {
            "left":  [362, 385, 387, 263, 373, 380],
            "right": [33, 160, 158, 133, 153, 144],
        }

        self.facemesh = get_mediapipe_app(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.state = "OPEN"
        self.t_closed = None
        self.t_last_blink = -1e9

        self._cnt = 0

    def update(self, frame):
        now = time.perf_counter()
        self._cnt += 1

        if frame is None:
            self._reset()
            return False, False, None

        h, w, _ = frame.shape

        # Make not writeable for mediapipe, but switch back before drawing
        frame.flags.writeable = False
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # mediapipe expects a contiguous array; if it's not, denormalize_coordinates can fail with "Expected Ptr<cv::UMat> for argument 'image'"
        rgb = np.ascontiguousarray(rgb)

        results = self.facemesh.process(rgb)
        frame.flags.writeable = True

        if not results.multi_face_landmarks:
            self._reset()
            return False, False, None

        # Ab hier: face_ok = True, weil FaceMesh wirklich was gefunden hat
        face_ok = True

        landmarks = results.multi_face_landmarks[0].landmark
        ear = calculate_avg_ear(landmarks, self.eye_idxs["left"], self.eye_idxs["right"], w, h)

        # Debug: alle 60 Frames mal zeigen, ob ear da ist
        if DEBUG and self._cnt % 60 == 0:
            dbg("face=1 ear=", ear)

        # Blink-StateMachine nur, wenn wir einen sinnvollen EAR haben
        if ear is None:
            # Gesicht da, aber EAR ungültig (z.B. denormalize None)
            return False, face_ok, None

        blink_event = False
        can_blink = (now - self.t_last_blink) > self.REFRACTORY_S

        if ear < self.EAR_THRESH:
            if self.state == "OPEN":
                self.state = "CLOSED"
                self.t_closed = now
        else:
            if self.state == "CLOSED":
                closed_time = now - (self.t_closed or now)
                self.state = "OPEN"
                self.t_closed = None

                if can_blink and closed_time >= self.MIN_CLOSED_S:
                    blink_event = True
                    self.t_last_blink = now

        return blink_event, face_ok, ear

    def _reset(self):
        self.state = "OPEN"
        self.t_closed = None
