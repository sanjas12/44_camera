"""Save periodic snapshots from the local webcam. Stop with Ctrl+C."""

import argparse
import math
import time
from datetime import datetime
from pathlib import Path


def positive_interval(value: str) -> float:
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("Interval must be a finite number greater than zero.")
    return seconds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=positive_interval, default=5.0,
                        help="Seconds between snapshots (default: 5).")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "snapshots",
                        help="Directory for JPEG images (default: snapshots beside this script).")
    parser.add_argument("--camera", type=int, default=0,
                        help="Camera index (default: 0, the first camera).")
    args = parser.parse_args()

    try:
        import cv2
    except ImportError:
        print("Install dependencies first: uv sync")
        return 1

    camera = None
    try:
        args.output.mkdir(parents=True, exist_ok=True)
        camera = cv2.VideoCapture(args.camera)
        if not camera.isOpened():
            raise RuntimeError("Cannot open camera. Check permissions, camera index, and other apps using it.")

        print(f"Camera: {args.camera}. Interval: {args.interval:g} seconds.", flush=True)
        print(f"Saving to: {args.output.resolve()}\nPress Ctrl+C to stop.", flush=True)
        next_capture = time.monotonic()
        while True:
            # Continuously read frames so snapshots do not come from an old buffer.
            success, frame = camera.read()
            if not success or frame is None:
                raise RuntimeError("Cannot read a frame from the camera.")
            now = time.monotonic()
            if now >= next_capture:
                stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
                destination = args.output / f"snapshot_{stamp}.jpg"
                if not cv2.imwrite(str(destination), frame):
                    raise RuntimeError(f"Cannot save image: {destination}")
                print(f"Saved: {destination}", flush=True)
                next_capture = now + args.interval
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except (OSError, RuntimeError, cv2.error) as error:
        print(f"Error: {error}")
        return 1
    finally:
        if camera is not None:
            camera.release()


if __name__ == "__main__":
    raise SystemExit(main())

