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


def configure_quality(camera, cv2):
    """Select the largest verified frame size among common camera modes."""
    ok, frame = camera.read()
    if not ok or frame is None:
        raise RuntimeError("Cannot read the initial camera frame.")
    initial = (frame.shape[1], frame.shape[0])
    modes = {initial, (640, 480), (1280, 720), (1280, 960),
             (1600, 1200), (1920, 1080), (1920, 1200), (2048, 1536),
             (2560, 1440), (2560, 1920), (2592, 1944), (3264, 2448),
             (3840, 2160), (3840, 2880), (4096, 2160), (4096, 3072),
             (4608, 3456), (5120, 2880), (5120, 3840), (7680, 4320)}
    verified = []
    print("Selecting camera resolution; this may take a few seconds...", flush=True)

    def try_mode(width, height):
        try:
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            # Discard transitional frames after changing the capture mode.
            for _ in range(3):
                ok, candidate = camera.read()
            if ok and candidate is not None:
                return candidate.shape[1], candidate.shape[0]
        except cv2.error:
            pass
        return None

    for width, height in sorted(modes, key=lambda size: size[0] * size[1], reverse=True):
        actual = try_mode(width, height)
        if actual:
            # Preserve the request: drivers can round it to a different size.
            verified.append((actual[0] * actual[1], width, height))

    for _, width, height in sorted(verified, reverse=True):
        actual = try_mode(width, height)
        if actual and actual[0] * actual[1] == _:
            print(f"Selected resolution: {actual[0]} x {actual[1]}. Format: lossless PNG.", flush=True)
            return
    if try_mode(*initial):
        print("Using initial camera resolution. Format: lossless PNG.", flush=True)
        return
    raise RuntimeError("Cannot restore a working camera mode.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=positive_interval, default=5.0,
                        help="Seconds between snapshots (default: 5).")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "snapshots",
                        help="Directory for PNG images (default: snapshots beside this script).")
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

        configure_quality(camera, cv2)

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
                destination = args.output / f"snapshot_{stamp}.png"
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

