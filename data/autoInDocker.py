import subprocess


commandList = [
    "mkdir /working/wrk -p",
    # "colmap automatic_reconstructor --image_path /working/images --workspace_path /working/wrk --dense 1 --quality low",
    "colmap automatic_reconstructor --image_path /working/images --workspace_path /working/wrk --dense 1 --quality extreme",
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
