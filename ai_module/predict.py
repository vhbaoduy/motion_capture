# Copyright (c) Facebook, Inc. and its affiliates.

import os
import sys
import os.path as osp
import torch
from torchvision.transforms import Normalize
import numpy as np
import cv2
import argparse
import json
import pickle
from datetime import datetime

from modeling.demo.demo_options import DemoOptions
from modeling.bodymocap.body_mocap_api import BodyMocap
from modeling.bodymocap.body_bbox_detector import BodyPoseEstimator
import modeling.mocap_utils.demo_utils as demo_utils
import modeling.mocap_utils.general_utils as gnu
from modeling.mocap_utils.timer import Timer

import modeling.renderer.image_utils as imu
from modeling.renderer.viewer2D import ImShow
import modeling.configs.path as pathconfigs
from modeling.renderer.visualizer import Visualizer

def run_body_mocap(args, body_bbox_detector, body_mocap, visualizer):
    #Setup input data to handle different types of inputs
    input_type, input_data = demo_utils.setup_input(args)

    cur_frame = args.start_frame
    video_frame = 0
    timer = Timer()
    while True:
        timer.tic()
        # load data
        load_bbox = False

        if input_type =='image_dir':
            if cur_frame < len(input_data):
                image_path = input_data[cur_frame]
                img_original_bgr  = cv2.imread(image_path)
            else:
                img_original_bgr = None

        elif input_type == 'bbox_dir':
            if cur_frame < len(input_data):
                print("Use pre-computed bounding boxes")
                image_path = input_data[cur_frame]['image_path']
                hand_bbox_list = input_data[cur_frame]['hand_bbox_list']
                body_bbox_list = input_data[cur_frame]['body_bbox_list']
                img_original_bgr  = cv2.imread(image_path)
                load_bbox = True
            else:
                img_original_bgr = None

        elif input_type == 'video':      
            _, img_original_bgr = input_data.read()
            if video_frame < cur_frame:
                video_frame += 1
                continue
            # save the obtained video frames
            image_path = osp.join(args.out_dir, "frames", f"{cur_frame:05d}.jpg")
            if img_original_bgr is not None:
                video_frame += 1
                if args.save_frame:
                    gnu.make_subdir(image_path)
                    cv2.imwrite(image_path, img_original_bgr)

        elif input_type == 'webcam':    
            _, img_original_bgr = input_data.read()

            if video_frame < cur_frame:
                video_frame += 1
                continue
            # save the obtained video frames
            image_path = osp.join(args.out_dir, "frames", f"scene_{cur_frame:05d}.jpg")
            if img_original_bgr is not None:
                video_frame += 1
                if args.save_frame:
                    gnu.make_subdir(image_path)
                    cv2.imwrite(image_path, img_original_bgr)
        else:
            assert False, "Unknown input_type"

        cur_frame +=1
        if img_original_bgr is None or cur_frame > args.end_frame:
            break   
        print("--------------------------------------")

        if load_bbox:
            body_pose_list = None
        else:
            body_pose_list, body_bbox_list = body_bbox_detector.detect_body_pose(
                img_original_bgr)
        hand_bbox_list = [None, ] * len(body_bbox_list)

        # save the obtained body & hand bbox to json file
        if args.save_bbox_output: 
            demo_utils.save_info_to_json(args, image_path, body_bbox_list, hand_bbox_list)

        if len(body_bbox_list) < 1: 
            print(f"No body deteced: {image_path}")
            continue

        #Sort the bbox using bbox size 
        # (to make the order as consistent as possible without tracking)
        bbox_size =  [ (x[2] * x[3]) for x in body_bbox_list]
        idx_big2small = np.argsort(bbox_size)[::-1]
        body_bbox_list = [ body_bbox_list[i] for i in idx_big2small ]
        if args.single_person and len(body_bbox_list)>0:
            body_bbox_list = [body_bbox_list[0], ]       

        # Body Pose Regression
        pred_output_list = body_mocap.regress(img_original_bgr, body_bbox_list)
        assert len(body_bbox_list) == len(pred_output_list)

        # extract mesh for rendering (vertices in image space and faces) from pred_output_list
        pred_mesh_list = demo_utils.extract_mesh_from_output(pred_output_list)

        # visualization
        res_img = visualizer.visualize(
            img_original_bgr,
            pred_mesh_list = pred_mesh_list, 
            body_bbox_list = body_bbox_list)
        
        # show result in the screen
        if not args.no_display:
            res_img = res_img.astype(np.uint8)
            ImShow(res_img)

        # save result image
        if args.out_dir is not None:
            demo_utils.save_res_img(args.out_dir, image_path, res_img)

        # save predictions to pkl
        if args.save_pred_pkl:
            demo_type = 'body'
            demo_utils.save_pred_to_pkl(
                args, demo_type, image_path, body_bbox_list, hand_bbox_list, pred_output_list)

        timer.toc(bPrint=True,title="Time")
        print(f"Processed : {image_path}")

    #save images as a video
    if not args.no_video_out and input_type in ['video', 'webcam']:
        demo_utils.gen_video_out(args.out_dir, args.seq_name)

    if input_type =='webcam' and input_data is not None:
        input_data.release()
    cv2.destroyAllWindows()
    
    
class Inference:
    def __init__(self,
                 use_smplx: bool=False,
                 renderer_type: str="opengl"):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        assert torch.cuda.is_available(), "Current version only supports GPU"

        # Set bbox detector
        self.body_bbox_detector = BodyPoseEstimator()

        # Set mocap regressor
        checkpoint_path = pathconfigs.DEFAULT_CHECKPOINT_PATH_SMPLX if use_smplx else pathconfigs.DEFAULT_CHECKPOINT_PATH_SMPL
        print("use_smplx", use_smplx)
        self.body_mocap = BodyMocap(checkpoint_path, self.device, use_smplx)

        # Set Visualizer
        # if args.renderer_type in ['pytorch3d', 'opendr']:
        #     from modeling.renderer.screen_free_visualizer import Visualizer
        # else:
        #     from modeling.renderer.visualizer import Visualizer
        self.renderer_type = renderer_type
        self.visualizer = Visualizer(rendererType=renderer_type)
        
    
    
def run_image(self, img_original_bgr, single_person):
    #Setup input data to handle different types of inputs
    timer = Timer()
    

    body_pose_list, body_bbox_list = self.body_bbox_detector.detect_body_pose(
        img_original_bgr)
    hand_bbox_list = [None, ] * len(body_bbox_list)

    # save the obtained body & hand bbox to json file
    # if args.save_bbox_output: 
    #     demo_utils.save_info_to_json(args, image_path, body_bbox_list, hand_bbox_list)

    # if len(body_bbox_list) < 1: 
    #     print(f"No body deteced: {image_path}")
    #     continue

    #Sort the bbox using bbox size 
    # (to make the order as consistent as possible without tracking)
    bbox_size =  [ (x[2] * x[3]) for x in body_bbox_list]
    idx_big2small = np.argsort(bbox_size)[::-1]
    body_bbox_list = [ body_bbox_list[i] for i in idx_big2small ]
    if single_person and len(body_bbox_list)>0:
        body_bbox_list = [body_bbox_list[0], ]       

    # Body Pose Regression
    pred_output_list = self.body_mocap.regress(img_original_bgr, body_bbox_list)
    assert len(body_bbox_list) == len(pred_output_list)

    # extract mesh for rendering (vertices in image space and faces) from pred_output_list
    pred_mesh_list = demo_utils.extract_mesh_from_output(pred_output_list)

    # visualization
    res_img = self.visualizer.visualize(
        img_original_bgr,
        pred_mesh_list = pred_mesh_list, 
        body_bbox_list = body_bbox_list)
    
    # show result in the screen

    # save result image
    # if args.out_dir is not None:
    #     demo_utils.save_res_img(args.out_dir, image_path, res_img)

    # # save predictions to pkl
    # if args.save_pred_pkl:
    #     demo_type = 'body'
    #     demo_utils.save_pred_to_pkl(
    #         args, demo_type, image_path, body_bbox_list, hand_bbox_list, pred_output_list)

    # timer.toc(bPrint=True,title="Time")
    # print(f"Processed : {image_path}")

    # #save images as a video
    # if not args.no_video_out and input_type in ['video', 'webcam']:
    #     demo_utils.gen_video_out(args.out_dir, args.seq_name)

    # if input_type =='webcam' and input_data is not None:
    #     input_data.release()
    # cv2.destroyAllWindows()
    
  
