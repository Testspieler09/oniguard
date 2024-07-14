# Security packets
from getpass import getpass
# Other packets
from os import get_terminal_size, mkdir, urandom
from os.path import exists, join
from time import sleep
from shutil import rmtree
from sys import exit
from assets import PROGRAM_NAME, DESCR
from Data_Manager import DataManager, generate_password, evaluate_password, get_hashing_obj, convert_pw_to_key
from Renderer import Renderer
from logging import shutdown
from LOGGER import setup_logger

class OniManager:
    def __init__(self, data: dict) -> None:
        self.rank = data["rank"]
        self.score = data["score"]

def ask_yes_no(message: str) -> bool:
    choice = ""
    while choice.lower() != "y" and choice.lower() != "n":
        choice = input(f"{message} [Y/n] ")
    if choice.lower()=="y":
        return True
    elif choice.lower()=="n":
        return False
    else:
        logger.critical("The ask yes no function is broken.")

def login_procedure(folder_path_cross_platform: str) -> object | None:
    if not exists(folder_path_cross_platform):
        choice = ask_yes_no(f"Do you want to create a new user {args.username}?")
        if choice:
            mkdir(folder_path_cross_platform)
            logger = setup_logger(join(folder_path_cross_platform, "oniguard.log"))
            salt = urandom(16)
            with open(join(folder_path_cross_platform, ".salt"), "wb") as f:
                f.write(salt)
            kdf = get_hashing_obj(salt)
            pw = getpass(f"Please provide a master password for {args.username}: ")
            check_pw = getpass(f"Please repeat the password for {args.username}: ")
            if pw != check_pw:
                print("The passwords are not identical.")
                shutdown() # disconnect logger so we can delete folder with items
                rmtree(folder_path_cross_platform)
                exit()
            else:
                DataManager(
                        join(folder_path_cross_platform, f"{args.username}.data"),
                        convert_pw_to_key(kdf, pw)
                )
        else:
            exit()
    logger = setup_logger(join(folder_path_cross_platform, "oniguard.log"))
    with open(join(folder_path_cross_platform, ".salt"), "rb") as f:
        kdf = get_hashing_obj(f.readline())
    password = getpass(f"Please provide the master password for {args.username}: ")
    try:
        key = convert_pw_to_key(kdf, password)
        return DataManager(join(folder_path_cross_platform, f"{args.username}.data"), key)
    except:
        print("Password not correct")
    #     sleep(5)
        exit()

def main(args: object) -> None:
    folder_path_cross_platform = join("..", "userdata", args.username)

    # Delete userdata
    if args.delete and exists(folder_path_cross_platform):
        choice = ask_yes_no(f"Do you realy whish to delete {args.username}?")
        if choice:
            rmtree(folder_path_cross_platform)
            print(f"User {args.username} got removed")
        exit()

    data_manager = login_procedure(folder_path_cross_platform)
    Renderer(data_manager)

if __name__ == "__main__":
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    max_width_ascii_art = max(len(line) for line in PROGRAM_NAME.strip().split('\n'))
    if get_terminal_size().columns < max_width_ascii_art: PROGRAM_NAME = "OniGuard"

    parser = ArgumentParser(prog=PROGRAM_NAME,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=DESCR,
                            epilog="Have fun with it = )")

    parser.add_argument("username", help="Specify which user you want to login as.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete the specified user.")

    args = parser.parse_args()

    main(args)
