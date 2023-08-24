import os
import glob
import shutil
import subprocess
import asyncio

import numpy as np
import cv2
from tempfile import NamedTemporaryFile, TemporaryDirectory
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.middleware.cors import CORSMiddleware

import backend.config as pathconfig
from video_inpainting.inference import main as remove_background


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def remove_background_task(video_path, output_dir):
    class Config:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    dict_config = {
        "video_path": video_path,
        "frames_path": os.path.join(output_dir, "bg_frames") + "/",
        "masks_path": os.path.join(output_dir, "bg_masks") + "/",
        "saved_model": "video_inpainting/release_model/E2FGVI-CVPR22.pth",
        "frame_rate": 25,
        "savefps": 1,
        "neighbor_stride": 5,
    }
    args = Config(**dict_config)
    remove_background(args)


def read_video_into_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        success, frame = cap.read()
        if success:
            frames.append(frame)
        else:
            break
    return frames


@app.post("/video", response_class=FileResponse)
async def motion_capture_in_video(video_file: UploadFile = File(...)):
    input_temp_dir = TemporaryDirectory()
    output_temp_dir = pathconfig.TEMP_PATH
    os.makedirs(output_temp_dir, exist_ok=True)
    # print(video_file)
    # print(input_temp_dir)
    try:
        contents = video_file.file.read()
        with open(os.path.join(input_temp_dir.name, "input.mp4"), "wb+") as f:
            f.write(contents)
    except Exception:
        return "There was an error uploading the file"
    finally:
        video_file.file.close()
        
    try:
        process = await asyncio.create_subprocess_exec(
            *[
                "xvfb-run",
                "-a",
                "python",
                "-m",
                "modeling.demo.demo_bodymocap",
                "--input_path",
                os.path.join(input_temp_dir.name, "input.mp4"),
                "--out_dir",
                output_temp_dir,
            ],
            cwd=pathconfig.AI_MODULE_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        ) 

        # Wait
        await remove_background_task(os.path.join(input_temp_dir.name, "input.mp4"), output_temp_dir)
        stdout, stderr = await process.communicate()
    except Exception as e:
        print(e)
        return "There was an error processing the file"

    # Merging two tasks
    modeling_frames = read_video_into_frames(os.path.join(input_temp_dir.name, "input.mp4"))
    bg_frames = read_video_into_frames(os.path.join(output_temp_dir, "bg_removal.mp4"))
    # There are less background frames than video frames
    stride = len(modeling_frames) // len(bg_frames)
    output_frames = []

    for frame_index, frame in enumerate(modeling_frames):
        bg_frame_index = min(frame_index // stride, len(bg_frames) - 1)
        bg_frame = bg_frames[bg_frame_index]
        bg_frame = cv2.resize(bg_frame, (frame.shape[1], frame.shape[0]))

        output_frame = np.where(
            frame == [0, 0, 0],
            bg_frame,
            frame,
        )
        output_frames.append(output_frame)

    # Write video
    out_video = cv2.VideoWriter(
        os.path.join(output_temp_dir, "output.mp4"),
        cv2.VideoWriter_fourcc(*"mp4v"),
        25,
        (modeling_frames[0].shape[1], modeling_frames[0].shape[0]),
    )
    for output_frame in output_frames:
        out_video.write(output_frame)
    out_video.release()

    # Return
    if os.path.exists(os.path.join(output_temp_dir, "output.mp4")):
        return FileResponse(
            path=os.path.join(output_temp_dir, "output.mp4"),
            filename="output.mp4",
            media_type="video/mp4",
        )
    os.system("rm -rf {}".format(output_temp_dir))
    return "There was an error writing the file"
