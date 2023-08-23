import os
import glob
import shutil
import subprocess
import asyncio

from tempfile import NamedTemporaryFile, TemporaryDirectory
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.middleware.cors import CORSMiddleware
import backend.config as pathconfig

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/video", response_class=FileResponse)
async def motion_capture_in_video(video_file: UploadFile = File(...)):
    input_temp_dir = TemporaryDirectory()
    output_temp_dir = pathconfig.TEMP_PATH
    # print(video_file)

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
        stdout, stderr = await process.communicate()
    except Exception as e:
        print(e)
        return "There was an error processing the file"

    video_files = glob.glob(os.path.join(output_temp_dir, "*.mp4"))
    if len(video_files) > 0:
        return FileResponse(path=video_files[0], filename="output.mp4", media_type="video/mp4")
    return "There was an error writing the file"
