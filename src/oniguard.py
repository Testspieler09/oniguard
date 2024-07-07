from os import get_terminal_size, mkdir
from os.path import exists, join
from assets import PROGRAM_NAME, DESCR
from Data_Manager import DataManager, generate_password, evaluate_password
from LOGGER import setup_logger

class OniManager:
    def __init__(self, data: dict) -> None:
        self.rank = data["rank"]
        self.score = data["score"]

def main(args: object) -> None:
    # Start logger in users data folder
    folder_path_cross_platform = join("..", "userdata", args.username)
    if not exists(folder_path_cross_platform): mkdir(folder_path_cross_platform)
    logger = setup_logger(join(folder_path_cross_platform, "oniguard.log"))
    DataManager(join(folder_path_cross_platform, f"{args.username}.data"))

if __name__ == "__main__":
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    max_width_ascii_art = max(len(line) for line in PROGRAM_NAME.strip().split('\n'))
    if get_terminal_size().columns < max_width_ascii_art: PROGRAM_NAME = "OniGuard"

    parser = ArgumentParser(prog=PROGRAM_NAME,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=DESCR,
                            epilog="Have fun with it = )")

    parser.add_argument("username", help="Specify which user you want to login as.")
    parser.add_argument("-d", "--debug", action="store_true", help="NOT FOR CASUAL USE. Stores data in plain text.")

    args = parser.parse_args()
    # check login info
    main(args)
