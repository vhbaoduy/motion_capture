import os
import cv2
import sys
import time
import argparse
import numpy as np
import subprocess

import torch
import albumentations as albu

from iglovikov_helper_functions.utils.image_utils import load_rgb, pad, unpad
from iglovikov_helper_functions.dl.pytorch.utils import tensor_from_rgb_image

from people_segmentation.pre_trained_models import create_model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def process_video(args, video_path, frames_path):
    cap = cv2.VideoCapture(video_path)

    frame_rate = args.frame_rate  # Desired frame rate in frames per second
    frame_interval = 1.0 / frame_rate

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        elapsed_time = current_time - start_time

        # Check if it's time to capture the next frame
        if elapsed_time >= frame_interval:
            frame_count += 1
            frame_filename = os.path.join(frames_path, f'frame_{str(frame_count).zfill(4)}.jpg')
            cv2.imwrite(frame_filename, frame)
            start_time = current_time


def create_mask(frames_path, masks_path):
    # setup model
    transform = albu.Compose([albu.Normalize(p=1)], p=1)

    model = create_model("Unet_2020-07-20")
    model.to(device)

    model.eval()
    with torch.no_grad():
        for dirpath, dirnames, filenames in os.walk(frames_path):
            if not dirnames:
                for file in filenames:
                    image = load_rgb(dirpath + file)

                    padded_image, pads = pad(image, factor=32, border=cv2.BORDER_CONSTANT)
                    x = transform(image=padded_image)["image"]
                    x = torch.unsqueeze(tensor_from_rgb_image(x), 0)
                    x = x.to(device)

                    prediction = model(x)[0][0]
                    mask = (prediction > 0).cpu().numpy().astype(np.uint8) * 255
                    mask = unpad(mask, pads)

                    cv2.imwrite(masks_path + file, mask)

    # free cache
    torch.cuda.empty_cache()


def human_segmentation(args):
    video_path = args.video_path
    frames_path = args.frames_path
    masks_path = args.masks_path

    os.makedirs(frames_path, exist_ok=True)
    os.makedirs(masks_path, exist_ok=True)

    process_video(args, video_path, frames_path)

    create_mask(frames_path, masks_path)


def video_inpainting(args):
    subprocess.call(['python', 'test.py', '--model', 'e2fgvi', '--video', \
                    f'{args.frames_path}', '--mask', f'{args.masks_path}', \
                    '--ckpt', f'{args.saved_model}', '--savefps', f'{args.savefps}', \
                    '--neighbor_stride', f'{args.neighbor_stride}'])

def main(args):
    human_segmentation(args)
    video_inpainting(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    """ Data processing """
    parser.add_argument(
        "--video_path", 
        default="video.mp4",
        help="path to video",
    )
    parser.add_argument(
        "--frames_path", 
        default="frames_origin",
        help="path to frames of video",
    )
    parser.add_argument(
        "--saved_model", 
        default="release_model/E2FGVI-CVPR22.pth",
        help="path to trained model",
    )
    parser.add_argument(
        "--masks_path", 
        default="frames_mask",
        help="path to mask of frames",
    )
    parser.add_argument(
        "--frame_rate", type=int, default=38, help="frame rate in frames per second"
    )
    parser.add_argument(
        "--savefps", type=int, default=10
    )
    parser.add_argument(
        "--neighbor_stride", type=int, default=5
    )

    args = parser.parse_args()
    
    if sys.platform == "win32":
        args.workers = 0

    args.gpu_name = "_".join(torch.cuda.get_device_name().split())
    if sys.platform == "linux":
        args.CUDA_VISIBLE_DEVICES = os.environ["CUDA_VISIBLE_DEVICES"]
    else:
        args.CUDA_VISIBLE_DEVICES = 0  # for convenience

    command_line_input = " ".join(sys.argv)
    print(
        f"Command line input: CUDA_VISIBLE_DEVICES={args.CUDA_VISIBLE_DEVICES} python {command_line_input}"
    )

    main(args)