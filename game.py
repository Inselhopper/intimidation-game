# game.py
import time
import random

class GameStateMachine:
    def __init__(self, config=None):
        self.trial_id = 0
        self.just_finished = False
        self.group = None
        self.condition = None
        self.config = config or {}
        self.state = "ATTRACT"
        self.t_state = time.perf_counter()
        self.t_duel_start = None
        self.blink_time = None
        print("GameStateMachine initialized")

    def update(self, *, start_pressed: bool, blink_event: bool, now: float):
        self.just_finished = False

        # Minimal-Config mit Defaults
        prime_s = self.config.get("prime_s", 2.0)
        countdown_s = self.config.get("countdown_s", 3.0)

        if self.state == "ATTRACT":
            if start_pressed:
                self.group = random.choice(["A", "B"])
                self.condition = random.choice(["friendly", "unfriendly"])

                self.state = "PRIME"
                self.t_state = now

                print(f"NEW TRIAL: group={self.group}, condition={self.condition}")

        elif self.state == "PRIME":
            if now - self.t_state > prime_s:
                self.state = "COUNTDOWN"
                self.t_state = now
                print("STATE -> COUNTDOWN")

        elif self.state == "COUNTDOWN":
            if now - self.t_state > countdown_s:
                self.state = "DUEL"
                self.t_duel_start = now
                print("STATE -> DUEL")

        elif self.state == "DUEL":
            if blink_event:
                self.blink_time = now - self.t_duel_start
                self.state = "RESULT"
                self.t_state = now
                self.just_finished = True
                self.trial_id += 1
                print(f"STATE -> RESULT (blink_time={self.blink_time:.2f}s)")

        elif self.state == "RESULT":
            if start_pressed:
                self.state = "ATTRACT"
                self.t_state = now
                self.blink_time = None
                self.t_duel_start = None
                print("STATE -> ATTRACT")
