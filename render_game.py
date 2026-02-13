# render_game.py
import cv2
import numpy as np
import time

class RendererGame:
    def __init__(self, config=None):
        self.config = config or {}
        self.w = self.config.get("width", 1280)
        self.h = self.config.get("height", 720)
        print("RendererGame initialized (OpenCV)")

    def render(self, game, now: float):
        # Schwarzer Canvas
        frame = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        # Platzhalter-"Robot-Augen"
        cx1, cx2 = int(self.w * 0.35), int(self.w * 0.65)
        cy = int(self.h * 0.45)
        eye_r = int(min(self.w, self.h) * 0.08)

        
        if game.condition == "friendly":
            # --- eyes ---
            cv2.circle(frame, (cx1, cy), eye_r, (255, 255, 255), 3)
            cv2.circle(frame, (cx2, cy), eye_r, (255, 255, 255), 3)

            # pupils (leicht nach innen)
            pupil_r = int(eye_r * 0.35)
            cv2.circle(frame, (cx1 + 5, cy), pupil_r, (255, 255, 255), -1)
            cv2.circle(frame, (cx2 - 5, cy), pupil_r, (255, 255, 255), -1)

            # eyebrows (leicht hoch, weich)
            cv2.line(frame, (cx1 - eye_r, cy - eye_r - 10),
                            (cx1 + eye_r, cy - eye_r - 15), (255,255,255), 2)
            cv2.line(frame, (cx2 - eye_r, cy - eye_r - 15),
                            (cx2 + eye_r, cy - eye_r - 10), (255,255,255), 2)

            
        else:
            # --- eyes (schmal) ---
            cv2.ellipse(frame, (cx1, cy), (eye_r, int(eye_r * 0.4)),
                        0, 0, 360, (255,255,255), 3)
            cv2.ellipse(frame, (cx2, cy), (eye_r, int(eye_r * 0.4)),
                        0, 0, 360, (255,255,255), 3)

            # pupils (starr zentriert, kleiner)
            pupil_r = int(eye_r * 0.25)
            cv2.circle(frame, (cx1, cy), pupil_r, (255,255,255), -1)
            cv2.circle(frame, (cx2, cy), pupil_r, (255,255,255), -1)

            # eyebrows (hart, nach innen fallend)
            cv2.line(frame, (cx1 - eye_r, cy - eye_r - 5),
                            (cx1 + eye_r, cy - eye_r - 20), (255,255,255), 2)
            cv2.line(frame, (cx2 - eye_r, cy - eye_r - 20),
                            (cx2 + eye_r, cy - eye_r - 5), (255,255,255), 2)


        

        # Text je Zustand
        if game.state == "ATTRACT":
            txt = "Press SPACE to start"
        elif game.state == "PRIME":
            txt = "Priming..."
        elif game.state == "COUNTDOWN":
            # Countdown: zeige 3..2..1 basierend auf Zeit im State
            elapsed = now - game.t_state
            remaining = 3 - int(elapsed)  # 3,2,1
            remaining = max(1, min(3, remaining))
            txt = str(remaining)
        elif game.state == "DUEL":
            txt = "DON'T BLINK!"
        elif game.state == "RESULT":
            txt = f"You blinked after {game.blink_time:.2f}s"
        else:
            txt = game.state

        # Text zeichnen
        cv2.putText(frame, txt, (60, 120), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 4)

        return frame
