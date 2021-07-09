import subprocess
import glob


def sizeChecker(fname):
    with open(fname, "rb") as img_file:
        img_file.seek(163)
        a = img_file.read(2)
        height = (a[0] << 8) + a[1]
        a = img_file.read(2)
        width = (a[0] << 8) + a[1]
    print("The resolution of the image is", width, "x", height)
    return max(width, height)


filename = "/working/images/*.jpg"
imgPathList = glob.glob(filename)

longerSize = sizeChecker(imgPathList[0])


commandList = [
    "mkdir /working/wrk -p",
    "colmap automatic_reconstructor --image_path /working/images --workspace_path /working/wrk --dense 1 --quality extreme",
    # "colmap image_undistorter --image_path /working/images/ --input_path /working/wrk/sparse/0 --output_path /working/image_undistort",
    # "colmap patch_match_stereo --workspace_path /working/image_undistort/"
    # "colmap patch_match_stereo --workspace_path /working/image_undistort/ --PatchMatchStereo.max_image_size %d"
    # % longerSize,
    "chmod 777 wrk --recursive",
]


def main():
    for command in commandList:
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


main()
