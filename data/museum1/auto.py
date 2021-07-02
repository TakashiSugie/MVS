import subprocess


commandList = [
    "mkdir /working/wrk -p",
    "colmap automatic_reconstructor --image_path /working/imgs --workspace_path /working/wrk --dense 1 --quality low",
    "chmod --recursive 777 wrk"
]


def main():
    for command in commandList:
        print(command)
        commandElement = command.split(" ")
        print(commandElement)
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


main()