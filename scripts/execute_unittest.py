import sys
import os

def main():

    file = sys.argv[1].split("src")[1]
    file = file.replace("\\", ".").replace(".py", "")[1:]

    print(f"Executing file \"{file}\"")

    os.system("docker-compose build")
    os.system(f"docker-compose run --rm showdown {file}")

if __name__ == "__main__":
    main()