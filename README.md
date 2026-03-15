# Intimidation Game

A machine–human staring contest.

The *Intimidation Game* is an interactive installation in which a human participant competes against a machine in a blink-based duel. The participant is recorded via camera, and a MediaPipe FaceMesh model is used to detect eye blinks through Eye Aspect Ratio (EAR). The machine presents either a *cute friendly* or a *cold hostile* robotic gaze. The time until the human blinks is measured and logged.

The project explores how minimal visual variations in a machine’s expression influence human behavior.

---

## Concept

The installation presents two possible robotic eye configurations:

* **Cute Friendly** – round eyes, soft brows, subtle social cues
* **Cold Hostile** – narrow eyes, rigid symmetry, non-blinking stare

Each trial randomly selects one of these configurations.

The visual condition is determined before the participant starts the game. The visitor therefore encounters a machine that already appears to have a specific “attitude”.

After a short priming phase and countdown, the staring contest begins.

The first blink ends the duel.

The blink time is recorded for later analysis.

The system investigates:

* priming effects
* perceived social presence
* human reaction to machine gaze
* minimal aesthetic differences and behavioral impact

---

## System Architecture

The project is structured into independent modules:

```
CameraCapture      → OpenCV camera input
BlinkDetector      → MediaPipe FaceMesh + EAR-based blink detection
GameStateMachine   → Trial logic and state transitions
RendererGame       → Fullscreen gaze rendering
RendererDebug      → Debug overlay window
TrialLogger        → CSV-based result logging
main.py            → Orchestration
```

Data flow:

```
Camera → BlinkDetector → GameStateMachine → Renderer → Logger
```

---

## Requirements

* Python 3.10 or 3.11 (recommended)
* Webcam

### Python dependencies

```
opencv-python
mediapipe
numpy
```

Install via:

```bash
pip install opencv-python mediapipe numpy
```

---

## Running the Application

From the project root:

```bash
python main.py
```

Controls:

* `SPACE` – Start / Next
* `ESC` – Exit

A fullscreen window displays the robotic gaze.
A debug window shows EAR values, blink detection, and state information.

---

## Blink Detection

Blink detection is based on the **Eye Aspect Ratio (EAR)** computed from MediaPipe FaceMesh landmarks.

Parameters:

* `EAR_THRESH` – threshold below which the eye is considered closed
* `MIN_CLOSED_S` – minimal duration for a valid blink
* `REFRACTORY_S` – minimal interval between blinks

These parameters can be tuned in `main.py`.

---

## Trial Logging

Each completed duel is appended to:

```
trials.csv
```

Logged fields:

* timestamp
* trial_id
* group
* condition (friendly / hostile)
* blink_time_s
* validity flag

The system is designed for later statistical evaluation.

---

## Current Status

* Real-time FaceMesh detection ✔
* EAR-based blink detection ✔
* State machine driven duel logic ✔
* Randomized condition assignment ✔
* CSV logging ✔
* Fullscreen rendering ✔

---

## Artistic Context

The project references Alan Turing’s *Imitation Game* but reverses the premise:

Instead of testing whether a machine can imitate a human,
the Intimidation Game tests whether a machine can intimidate a human.

No actual AI opponent is present — the “machine” is a deterministic visual system.
The experiment investigates how minimal aesthetic cues shape human response.

---

## License

BSD License

---

