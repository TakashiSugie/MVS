import subprocess
import glob
import os
import sys
argv=sys.argv
DIR_NAME = "museum1"
# IMG_NAME = "IMG_1939.jpg"
# DIR_NAME = "RWC"
# IMG_NAME = "cam11_frame240.png"
# IMG_NAME = "%s.geometric.bin" % IMG_NAME
# IMG_NAME = "%s.photometric.bin" % IMG_NAME
imgPathList=glob.glob("../data/%s/wrk/dense/0/stereo/depth_maps/*.bin"%DIR_NAME)
# print(len(imgPathList))
# commandList=[]

def addAllDepthPath(commandList):
    commandList.append("mkdir -p ../data/%s/depth"%DIR_NAME)
    commandList.append("mkdir -p ../data/%s/normal"%DIR_NAME)
    for imgPath in imgPathList:
        IMG_NAME=os.path.basename(imgPath)
        baseName=IMG_NAME.split(".")[0]
        command="python ../data/mySaveDepth.py -d ../data/%s/wrk/dense/0/stereo/depth_maps/%s -n ../data/%s/wrk/dense/0/stereo/normal_maps/%s -dPath ../data/%s/depth/%s.png -nPath ../data/%s/normal/%s.png"%(DIR_NAME, IMG_NAME, DIR_NAME, IMG_NAME, DIR_NAME, baseName,DIR_NAME,baseName)
        commandList.append(command)
    return commandList

if len(argv)==1:
    commandList = [
        "cp ../data/autoInDocker.py ../data/%s/auto.py"
        % DIR_NAME,
        "./quick-start.sh /home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/%s"
        % DIR_NAME,
        # "python ../data/mySaveDepth.py -d ../data/%s/wrk/dense/0/stereo/depth_maps/%s -n ../data/%s/wrk/dense/0/stereo/normal_maps/%s -dPath ../data/%s/depth.png -nPath ../data/%s/normal.png"
        # % (DIR_NAME, IMG_NAME, DIR_NAME, IMG_NAME, DIR_NAME, DIR_NAME),
    ]
    commandList=addAllDepthPath(commandList)
elif len(argv)==2:
    commandList=[]
    commandList=addAllDepthPath(commandList)
    
# elif len(argv)==2:
#     commandList = [
#         "python ../data/mySaveDepth.py -d ../data/%s/wrk/dense/0/stereo/depth_maps/%s -n ../data/%s/wrk/dense/0/stereo/normal_maps/%s -dPath ../data/%s/depth.png -nPath ../data/%s/normal.png"
#         % (DIR_NAME, IMG_NAME, DIR_NAME, IMG_NAME, DIR_NAME, DIR_NAME),
#         "chmod "
#     ]




def main():
    global commandList
    for command in commandList:
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)

    if not len(imgPathList):
        imgPathList=glob.glob("../data/%s/wrk/dense/0/stereo/depth_maps/*.bin"%DIR_NAME)
        commandList=[]
        commandList=addAllDepthPath(commandList)
        for command in commandList:
            commandElement = command.split(" ")
            Flag = subprocess.call(commandElement)
            if Flag:
                print("this status", Flag)
                raise Exception(ValueError)

        

    return


main()