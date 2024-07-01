from os import get_terminal_size
from assets import PROGRAM_NAME, DESCR

class OniManager:
    def __init__(self, data: dict) -> None:
        self.rank = data["rank"]
        self.score = data["score"]

if __name__ == "__main__":
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    max_width_ascii_art = max(len(line) for line in program_name.strip().split('\n'))
    if get_terminal_size().columns < max_width_ascii_art: program_name = "OniGuard"

    parser = ArgumentParser(prog=PROGRAM_NAME,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=DESCR,
                            epilog="Have fun with it = )")

    parser.add_argument("username", help="Specify which user you want to login as.")
    parser.add_argument("-d", "--debug", action="store_true", help="NOT FOR CASUAL USE. Stores data in plain text.")

    args = parser.parse_args()
