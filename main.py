# main.py
import time
import cv2

from camera import CameraCapture
from blink_detector import BlinkDetector
from game import GameStateMachine
from render_game import RendererGame
from render_debug import RendererDebug
from logger import TrialLogger


DEBUG = True

def dbg(*args):
    if DEBUG:
        print(*args)


WINDOW_NAME = "Intimidation Game"


def setup_fullscreen_window():
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


def main():
    camera = CameraCapture({"device": 0})
    blink_detector = BlinkDetector({
        "EAR_THRESH": 0.18,
        "min_closed_s": 0.03,
        "refractory_s": 0.20,
    })
    game = GameStateMachine({"prime_s": 1.0, "countdown_s": 3.0})
    renderer = RendererGame({"width": 1280, "height": 720})
    debug_renderer = RendererDebug()
    logger = TrialLogger("trials.csv")

    setup_fullscreen_window()
    dbg("Controls: SPACE=start/next, ESC=quit")

    # --- Debug counters / throttling ---
    frame_count = 0
    last_state = None
    last_print_t = time.perf_counter()
    face_ok_false_count = 0
    none_frame_count = 0

    try:
        while True:
            now = time.perf_counter()
            frame_count += 1

            # 1) Read Camera
            frame = camera.read()
            if frame is not None:
                cv2.imshow("RAW_CAM", frame)
            dbg("frame type:", type(frame), "shape:", getattr(frame, "shape", None), "is None:", frame is None)

            if frame is None:
                none_frame_count += 1
                # Alle 2 Sekunden mal melden, wenn Kamera nix liefert
                if now - last_print_t > 2.0:
                    dbg(f"[WARN] camera.read() returned None (count={none_frame_count})")
                    last_print_t = now
                # trotzdem UI pumpen, sonst "hängt" das Fenster
                cv2.imshow(WINDOW_NAME, renderer.render(game, now))
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    break
                continue

            # 2) Blink detection
            blink_event, face_ok, ear = blink_detector.update(frame)

            if not face_ok:
                face_ok_false_count += 1

            # 3) Game update
            # input comes later after waitKey; start_pressed will then take effect from the next frame
            # that's why we call game.update() with start_pressed=False
            # so we do not have two frames in a row with start_pressed=True (was causing issues with the state machine)
            game.update(start_pressed=False, blink_event=blink_event, now=now)

            # 4) Logging when trial just finished:
            if getattr(game, "just_finished", False):
                logger.append({
                    "trial_id": getattr(game, "trial_id", ""),
                    "group": getattr(game, "group", ""),
                    "condition": getattr(game, "condition", ""),
                    "blink_time_s": round(getattr(game, "blink_time", 0.0), 3) if getattr(game, "blink_time", None) is not None else "",
                    "valid": 1,
                    "note": "",
                })
                dbg(f"[LOG] trial_id={game.trial_id} group={game.group} cond={game.condition} blink_time={game.blink_time:.3f}s")

            # 5) Debug window rendern
            debug_renderer.render(
                game_state=game,
                blink_event=blink_event,
                face_ok=face_ok,
                ear=ear,
            )

            # 6) Game screen rendern
            game_frame = renderer.render(game, now)
            cv2.imshow(WINDOW_NAME, game_frame)

            # 7) JETZT erst waitKey() -> wichtig für Windows/Fullscreen
            key = cv2.waitKey(1) & 0xFF

            # Exit
            if key == 27:  # ESC
                dbg("[KEY] ESC -> exit")
                break

            # Start / next
            start_pressed = (key == 32)  # SPACE
            if start_pressed:
                dbg("[KEY] SPACE")
                # Start-Input als separates Update (damit es sofort wirkt)
                game.update(start_pressed=True, blink_event=False, now=now)

            # 8) Debug prints: (a) bei State-Wechsel, (b) alle ~2 Sekunden
            if last_state != game.state:
                dbg(f"[STATE] {last_state} -> {game.state}")
                last_state = game.state

            if now - last_print_t > 2.0:
                dbg(
                    f"[DBG] frames={frame_count} state={game.state} "
                    f"face_ok={face_ok} ear={None if ear is None else round(ear, 3)} "
                    f"blink_event={blink_event} face_ok_false_total={face_ok_false_count}"
                )
                last_print_t = now

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
