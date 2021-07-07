import subprocess


commandList = [
    "mkdir /working/wrk -p",
    # "colmap automatic_reconstructor --image_path /working/images --workspace_path /working/wrk --dense 1 --quality extreme",
    "colmap image_undistorter --image_path /working/images/ --input_path /working/wrk/sparse/0 --output_path /working/image_undistort",
    "colmap patch_match_stereo --workspace_path /working/image_undistort/",
    "chmod 777 wrk --recursive",
]


def main():
    for command in commandList:
        # print(command)
        commandElement = command.split(" ")
        # print(commandElement)
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


main()
