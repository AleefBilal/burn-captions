#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pprint
import shlex
import subprocess
import tempfile
import os

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pycaption import SRTReader
from tqdm import tqdm


# Utilities

def load_font(path, size, index=None):
    if path.lower().endswith(".ttc") and index is not None:
        return ImageFont.truetype(
            path,
            size,
            index=index,
            layout_engine=ImageFont.LAYOUT_BASIC,
        )
    return ImageFont.truetype(
        path,
        size,
        layout_engine=ImageFont.LAYOUT_BASIC,
    )


def merge_audio_inplace(video_no_audio: str, original_video: str, final_output: str):
    """
    Merge audio from original_video into video_no_audio.
    Video and audio are copied without re-encoding.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", video_no_audio,
        "-i", original_video,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "copy",
        "-shortest",
        final_output,
    ]
    subprocess.run(cmd, check=True)


# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--video", type=str, required=True)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--srt", type=str, required=True)

    parser.add_argument("--font", type=str, default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    parser.add_argument("--font-size", type=int, default=36)

    parser.add_argument("--secondary-font-size", type=int, default=52)
    parser.add_argument("--secondary-font-start", type=int, default=432)
    parser.add_argument("--secondary-font-end", type=int, default=448)

    parser.add_argument("--bottom-space", type=int, default=36)
    parser.add_argument("--blueback", action="store_true", default=False)
    parser.add_argument("--pixelformat", type=str, default="yuv420p")

    parser.add_argument("--quality", type=int, default=10)
    parser.add_argument("--bitrate", type=int, default=None)

    parser.add_argument("--skip-first", action="store_true", default=False)
    parser.add_argument("--break-after", type=float, default=0)

    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Preserve audio from original video",
    )

    parser.add_argument("--output-params", type=str)
    args = parser.parse_args()

    # Load captions

    srt_text = open(args.srt).read()
    srt = SRTReader().read(srt_text, lang="en")
    captions = srt.get_captions("en")

    # Video reader

    reader = imageio.get_reader(args.video)
    meta = reader.get_meta_data()
    pprint.pprint(meta)

    fps = meta["fps"]

    # Fonts

    font_normal = load_font(args.font, args.font_size)
    font_italic = load_font(args.font, args.font_size)

    secondary_font_normal = load_font(args.font, args.secondary_font_size)
    secondary_font_italic = load_font(args.font, args.secondary_font_size)

    # Output params

    output_params = shlex.split(args.output_params) if args.output_params else []

    # Decide write target

    if args.keep_audio:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        video_write_path = tmp_file.name
        tmp_file.close()
    else:
        video_write_path = args.out

    # Video writer

    writer = imageio.get_writer(
        video_write_path,
        codec=meta["codec"],
        fps=fps,
        pixelformat=args.pixelformat,
        macro_block_size=20,
        quality=args.quality,
        bitrate=args.bitrate,
        output_params=output_params,
    )

    # Prepare caption data

    caption_data = []
    for caption in captions:
        if not caption_data and args.skip_first:
            args.skip_first = False
            continue

        start_sec = caption.start / 1_000_000
        end_sec = caption.end / 1_000_000

        text = caption.get_text()
        italic = "<i>" in text

        text = text.replace("<i>", "").replace("</i>", "")

        caption_data.append({
            "text": text,
            "italic": italic,
            "start": int(start_sec * fps),
            "end": int(end_sec * fps),
        })

    # Burn captions

    caption_i = 0
    total_frames = reader.count_frames()
    pbar = tqdm(total=total_frames)

    for frame_i, frame in enumerate(reader):
        if args.blueback:
            frame = np.full((1080, 1920, 3), [0, 0, 255], dtype=np.uint8)

        caption = caption_data[caption_i] if caption_i < len(caption_data) else None

        if caption and caption["start"] <= frame_i <= caption["end"]:
            img = Image.fromarray(frame)
            draw = ImageDraw.Draw(img)

            font = (
                secondary_font_italic if caption["italic"] else secondary_font_normal
                if args.secondary_font_start <= caption_i <= args.secondary_font_end
                else font_italic if caption["italic"] else font_normal
            )

            h, w, _ = frame.shape
            wt, ht = font.getsize_multiline(caption["text"])

            pos = (w // 2 - wt // 2, h - ht - args.bottom_space)

            draw.text(
                pos,
                caption["text"],
                font=font,
                fill=(255, 255, 255),
                stroke_width=2,
                stroke_fill=(0, 0, 0),
                align="center",
            )

            writer.append_data(np.array(img))

        else:
            writer.append_data(frame)

        if caption and frame_i > caption["end"]:
            caption_i += 1

        pbar.update(1)

        if args.break_after > 0 and frame_i / fps > args.break_after:
            break

    # Cleanup

    reader.close()
    writer.close()

    # Audio merge (if enabled)

    if args.keep_audio:
        print("Merging original audio...")
        merge_audio_inplace(
            video_no_audio=video_write_path,
            original_video=args.video,
            final_output=args.out,
        )
        os.remove(video_write_path)
