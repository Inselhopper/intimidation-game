# render_game.py
import cv2
import numpy as np


def overlay_rgba(frame_bgr, png, x, y):
    h, w = png.shape[:2]
    H, W = frame_bgr.shape[:2]

    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(W, x + w), min(H, y + h)

    if x1 >= x2 or y1 >= y2:
        return

    src = png[(y1 - y):(y2 - y), (x1 - x):(x2 - x)]
    dst = frame_bgr[y1:y2, x1:x2]

    alpha = src[:, :, 3] / 255.0
    for c in range(3):
        dst[:, :, c] = alpha * src[:, :, c] + (1 - alpha) * dst[:, :, c]


class RendererGame:

    def __init__(self, config=None):
        self.config = config or {}
        self.w = self.config.get("width", 1280)
        self.h = self.config.get("height", 720)

        # PNGs laden (mit Alpha!)
        self.assets = {
            ("friendly", "open"):   cv2.imread("friendly_open.png", cv2.IMREAD_UNCHANGED),
            ("friendly", "closed"): cv2.imread("friendly_closed.png", cv2.IMREAD_UNCHANGED),
            ("mean", "open"):       cv2.imread("mean_open.png", cv2.IMREAD_UNCHANGED),
            ("mean", "closed"):     cv2.imread("mean_closed.png", cv2.IMREAD_UNCHANGED),
        }

        print("RendererGame initialized (PNG mode)")

    def render(self, game, now: float):
        frame = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        robot_closed = (
            game.state in {"ATTRACT", "PRIME", "COUNTDOWN"}
            and now < getattr(game, "robot_blink_until", 0.0)
        )

        eye_state = "closed" if robot_closed else "open"
        cond = getattr(game, "condition", "mean")

        if cond not in {"friendly", "mean"}:
            cond = "mean"

        eyes = self.assets[(cond, eye_state)]

        if eyes is not None:
            x = self.w // 2 - eyes.shape[1] // 2
            y = int(self.h * 0.15)
            overlay_rgba(frame, eyes, x, y)

        # Text
        if game.state == "ATTRACT":
            txt = "Press SPACE to start"
        elif game.state == "PRIME":
            txt = "Priming..."
        elif game.state == "COUNTDOWN":
            elapsed = now - game.t_state
            remaining = 3 - int(elapsed)
            remaining = max(1, min(3, remaining))
            txt = str(remaining)
        elif game.state == "DUEL":
            txt = "DON'T BLINK!"
        elif game.state == "RESULT":
            txt = f"You blinked after {game.blink_time:.2f}s"
        else:
            txt = game.state

        cv2.putText(frame, txt, (280, 620),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0,
                    (255, 255, 255), 4)

        return frame
