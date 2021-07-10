# ./dataName/直下にデータを揃える
# left.png, dispMVS.png, dispMono.png, dispMono.pfm
import os

# import sys
import cv2
import numpy as np
import subprocess
import glob

# import myMiDaS.myRun as myRun

srcDirPath = "../data"
DIR_NAME = "bridge"
setDataPath = "%s/%s/4poisson" % (srcDirPath, DIR_NAME)


def doCommand(commandList=[]):
    for command in commandList:
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


def makeDataDir():
    print(setDataPath)
    os.makedirs(setDataPath, exist_ok=True)


def setDispMVS(imgName):
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


def setDispMono(imgName):
    commandList = [
        "cp %s/%s/dispMono/%s.pfm %s/dispMono.pfm"
        % (srcDirPath, DIR_NAME, imgName, setDataPath),
        "cp %s/%s/dispMono/%s.png %s/dispMono.png"
        % (srcDirPath, DIR_NAME, imgName, setDataPath),
    ]
    doCommand(commandList=commandList)


def setColorImg(imgName):
    imgPath = glob.glob(
        "%s/%s/wrk/dense/0/images/%s.*" % (srcDirPath, DIR_NAME, imgName)
    )
    colorImg = cv2.imread(imgPath[0])
    print("%s/left.png" % (setDataPath))
    cv2.imwrite("%s/left.png" % (setDataPath), colorImg)


def set4Poisson():
    global setDataPath
    imgPathList = glob.glob("%s/%s/depth/*_geometric.png" % (srcDirPath, DIR_NAME))
    for imgPath in imgPathList:
        imgName = os.path.basename(imgPath).strip("_geometric.png")
        setDataPath = "%s/%s/4poisson/%s" % (srcDirPath, DIR_NAME, imgName)
        makeDataDir()
        setColorImg(imgName)
        setDispMono(imgName)
        setDispMVS(imgName)


set4Poisson()
