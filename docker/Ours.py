import subprocess
import glob
import os
import torch
import utils
import cv2
import numpy as np
import copy as cp

# import argparse

from torchvision.transforms import Compose
from midas.dpt_depth import DPTDepthModel
from midas.transforms import Resize, NormalizeImage, PrepareForNet

DIR_NAME = "bridge"
srcDirPath = "../data"
# DIR_NAME = "bridge"
setDataPath = "%s/%s/4poisson" % (srcDirPath, DIR_NAME)


def doCommand(commandList):
    for command in commandList:
        print("command", command)
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


def makeDataDir():
    print(setDataPath)
    os.makedirs(setDataPath, exist_ok=True)


"""save MVS Depth"""


def saveMVSDepth():
    commandList = [
        "cp ../data/autoInDocker.py ../data/%s/auto.py" % DIR_NAME,
        "./quick-start.sh /home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/%s"
        % DIR_NAME,
    ]
    imgPathList = glob.glob("../data/%s/wrk/dense/0/stereo/depth_maps/*.bin" % DIR_NAME)
    commandList = addAllDepthPath(commandList, imgPathList)
    doCommand(commandList=commandList)


def addAllDepthPath(commandList, imgPathList):
    commandList.append("mkdir -p ../data/%s/depth" % DIR_NAME)
    commandList.append("mkdir -p ../data/%s/normal" % DIR_NAME)
    for imgPath in imgPathList:
        IMG_NAME = os.path.basename(imgPath)
        baseName = IMG_NAME.split(".")[0]
        mode = IMG_NAME.split(".")[2]
        command = (
            "python ../data/mySaveDepth.py -d ../data/%s/wrk/dense/0/stereo/depth_maps/%s -n ../data/%s/wrk/dense/0/stereo/normal_maps/%s -dPath ../data/%s/depth/%s_%s.png -nPath ../data/%s/normal/%s_%s.png"
            % (
                DIR_NAME,
                IMG_NAME,
                DIR_NAME,
                IMG_NAME,
                DIR_NAME,
                baseName,
                mode,
                DIR_NAME,
                baseName,
                mode,
            )
        )
        commandList.append(command)
    return commandList


"""saveMonoDepth"""


def run(input_path, output_path, model_path, model_type="large", optimize=True):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # print("device: %s" % device)
    if model_type == "dpt_large":
        model = DPTDepthModel(
            path=model_path, backbone="vitl16_384", non_negative=True,
        )
        net_w, net_h = 384, 384
        resize_mode = "minimal"
        normalization = NormalizeImage(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    transform = Compose(
        [
            Resize(
                net_w,
                net_h,
                resize_target=None,
                keep_aspect_ratio=True,
                ensure_multiple_of=32,
                resize_method=resize_mode,
                image_interpolation_method=cv2.INTER_CUBIC,
            ),
            normalization,
            PrepareForNet(),
        ]
    )

    model.eval()

    if optimize == True:
        if device == torch.device("cuda"):
            model = model.to(memory_format=torch.channels_last)
            model = model.half()

    model.to(device)
    img_names = glob.glob(os.path.join(input_path, "*"))
    os.makedirs(output_path, exist_ok=True)

    for ind, img_name in enumerate(img_names):
        img = utils.read_image(img_name)
        img_input = transform({"image": img})["image"]
        with torch.no_grad():
            sample = torch.from_numpy(img_input).to(device).unsqueeze(0)
            if optimize == True and device == torch.device("cuda"):
                sample = sample.to(memory_format=torch.channels_last)
                sample = sample.half()
            prediction = model.forward(sample)
            prediction = (
                torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                )
                .squeeze()
                .cpu()
                .numpy()
            )

        filename = os.path.join(
            output_path, os.path.splitext(os.path.basename(img_name))[0]
        )
        utils.write_depth(filename, prediction, bits=2)


def saveMonoDepth():
    model_weights = "/home/takashi/Desktop/study/M2/poisson/MiDaS-master/weights/dpt_large-midas-2f21e586.pt"
    input_path = (
        "/home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/%s/wrk/dense/0/images"
        % DIR_NAME
    )
    output_path = (
        "/home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/%s/dispMono"
        % DIR_NAME
    )
    run(
        input_path=input_path,
        output_path=output_path,
        model_path=model_weights,
        model_type="dpt_large",
    )


"""set Data for Poisson"""


def setDispMVS(imgName, setDataPath):
    depthPath = "%s/%s/depth/" % (srcDirPath, DIR_NAME)
    depthPath = os.path.join(depthPath, imgName + "_geometric.png")
    depthMVS = cv2.imread(depthPath, 0)
    disp = np.zeros(depthMVS.shape)
    for x in range(depthMVS.shape[1]):
        for y in range(depthMVS.shape[0]):
            if depthMVS[y][x] == 0:
                continue
            else:
                disp[y][x] = 1.0 / depthMVS[y][x]
    Max = np.max(disp)
    Min = np.min(disp)
    disp = (disp - Min) / (Max - Min)
    saveDispMVSPath = os.path.join(setDataPath, "dispMVS.png")
    cv2.imwrite(saveDispMVSPath, disp * 255)


def setDispMono(imgName, setDataPath):
    commandList = [
        "cp %s/%s/dispMono/%s.pfm %s/dispMono.pfm"
        % (srcDirPath, DIR_NAME, imgName, setDataPath),
        "cp %s/%s/dispMono/%s.png %s/dispMono.png"
        % (srcDirPath, DIR_NAME, imgName, setDataPath),
    ]
    doCommand(commandList=commandList)


def setColorImg(imgName, setDataPath):
    imgPath = glob.glob(
        "%s/%s/wrk/dense/0/images/%s.*" % (srcDirPath, DIR_NAME, imgName)
    )
    colorImg = cv2.imread(imgPath[0])
    print("%s/left.png" % (setDataPath))
    cv2.imwrite("%s/left.png" % (setDataPath), colorImg)


def set4Poisson():
    imgPathList = glob.glob("%s/%s/depth/*_geometric.png" % (srcDirPath, DIR_NAME))
    for imgPath in imgPathList:
        imgName = os.path.basename(imgPath).strip("_geometric.png")
        setDataPath = "%s/4poisson/%s/%s" % (srcDirPath, DIR_NAME, imgName)
        # setDataPath = "%s/%s/4poisson/%s" % (srcDirPath, DIR_NAME, imgName)
        # makeDataDir()
        os.makedirs(setDataPath, exist_ok=True)
        setColorImg(imgName, setDataPath)
        setDispMono(imgName, setDataPath)
        setDispMVS(imgName, setDataPath)


"""Doing Ours Depth Fusion"""


def OursMethod():
    import depthFusionOurs

    dataPath = "%s/4poisson/%s/*" % (srcDirPath, DIR_NAME)
    imgPathList = glob.glob(dataPath)
    for imgPath in imgPathList:
        imgName = os.path.basename(imgPath)
        depthFusionOurs.mainProcess(DIR_NAME, imgName)


def main():
    print(DIR_NAME)
    print("saveMVSDisp")
    saveMVSDepth()
    print("saveMonoDisp")
    saveMonoDepth()
    print("set Data for Poisson Disparity fusion")
    set4Poisson()
    print("Doing Ours Depth Fusion")
    OursMethod()


main()
