# Burn Captions

================

Burn a given SRT file into a video, with optional preservation of the original audio track.

This tool burns captions **frame-by-frame** and, when requested, safely **remuxes the original audio** back into the final output video.

---

## Requirements

* Python **3.7+**
* FFmpeg (must be available in `PATH`)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
usage: burn.py [-h]
               --video VIDEO
               --srt SRT
               --out OUT
               [--font FONT]
               [--font-size FONT_SIZE]
               [--secondary-font-size SECONDARY_FONT_SIZE]
               [--secondary-font-start SECONDARY_FONT_START]
               [--secondary-font-end SECONDARY_FONT_END]
               [--bottom-space BOTTOM_SPACE]
               [--pixelformat PIXELFORMAT]
               [--quality QUALITY]
               [--bitrate BITRATE]
               [--skip-first]
               [--blueback]
               [--break-after BREAK_AFTER]
               [--keep-audio]
               [--output-params OUTPUT_PARAMS]
```

---

## Arguments

### Required

* `--video VIDEO`
  Input video file

* `--srt SRT`
  Subtitle file in SRT format

* `--out OUT`
  Output video path (final file)

---

### Optional

* `--font FONT`
  Path to TTF/TTC font
  *(default: DejaVuSans)*

* `--font-size FONT_SIZE`
  Caption font size
  *(default: 36)*

* `--secondary-font-size SECONDARY_FONT_SIZE`
  Alternate font size for a caption range
  *(default: 52)*

* `--secondary-font-start SECONDARY_FONT_START`
  Caption index to start secondary font
  *(default: 432)*

* `--secondary-font-end SECONDARY_FONT_END`
  Caption index to end secondary font
  *(default: 448)*

* `--bottom-space BOTTOM_SPACE`
  Margin from bottom of the frame
  *(default: 36)*

* `--pixelformat PIXELFORMAT`
  Output pixel format
  *(default: yuv420p)*

* `--quality QUALITY`
  Video quality (0–10)
  *(default: 10)*

* `--bitrate BITRATE`
  Target bitrate in bits/sec
  *(default: unset)*

* `--skip-first`
  Skip the first caption

* `--blueback`
  Render captions on a solid blue background (debug)

* `--break-after BREAK_AFTER`
  Stop processing after N seconds (debug/testing)

* `--keep-audio`
  Preserve audio from the original video
  *(audio is remuxed without re-encoding)*

* `--output-params OUTPUT_PARAMS`
  Extra FFmpeg output parameters (advanced use)

---

## Examples

### Burn captions (video only)

```bash
python burn.py \
  --video sample.mp4 \
  --srt sample.srt \
  --out output.mp4
```

---

### Burn captions and keep original audio

```bash
python burn.py \
  --video sample.mp4 \
  --srt sample.srt \
  --out output.mp4 \
  --keep-audio
```

### Example

```bash
python burn.py \
  --video test/input.mp4\
  --srt test/input.srt\
  --out test/output.mp4\
  --keep-audio
```

---

## Notes

* When `--keep-audio` is enabled:

  * Audio is copied from the original video
  * No re-encoding is performed
  * Temporary files are handled internally and cleaned up automatically

* FFmpeg must be installed and accessible from the command line.
