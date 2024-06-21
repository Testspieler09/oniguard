from secrets import choice
from string import ascii_letters, digits, punctuation
from os.path import exists, dirname
from os import chdir
from json import load, dumps

class Cryptographer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def gen_salt(size: int) -> None:
        pass

    @staticmethod
    def encrypt(file: str) -> None:
        pass

    @staticmethod
    def decrypt(file: str) -> None:
        pass

class File_Manager:
    def __init__(self, path_to_file: str) -> None:
        if not exists(path_to_file): raise Exception("File not found in given directory.")
        self.path_to_file: str = path_to_file
        self.data: dict = {}

    @classmethod
    def for_new_file(cls, path_with_filename_and_extension: str) -> None:
        with open(path_with_filename_and_extension, "w") as f:
            f.write("{}")
        return cls(path_with_filename_and_extension)

    def read_file_to_dict(self) -> None:
        with open(self.path_to_file, "r") as f:
            self.data = load(f)

    def add_data_to_file(self, data: dict) -> None:
        self.data.update(data)
        with open(self.path_to_file, "w") as f:
            f.write(str(dumps(self.data)))

    def update_data(self, data: dict) -> None:
        self.data = data
        with open(self.path_to_file, "w") as f:
            f.write(str(dumps(self.data)))

    def load_backup(self) -> None:
        pass

    def write_backup(self) -> None:
        pass

def generate_password(length: int) -> str:
    alphabet = ascii_letters + digits + punctuation
    password = ''.join(choice(alphabet) for i in range(length))
    return password

if __name__ == "__main__":
    from os import getcwd
    cwd = getcwd()
    f = File_Manager(f"{cwd}\\test.txt")
    f.read_file_to_dict()
    f.add_data_to_file({"llo": "world mothertrucker"})
    print(f.path_to_file)
