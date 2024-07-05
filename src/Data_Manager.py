from secrets import choice
from cryptography.fernet import Fernet
from string import ascii_letters, digits, punctuation
from os.path import exists, dirname
from os import chdir
from json import load, dumps
from logging import getLogger

logger = getLogger(__name__)

class Cryptographer:
    def __init__(self, key: str, filepath: str) -> None:
        self.file = filepath
        self.fernet = Fernet(key)

    @classmethod
    def for_new_file(cls, filepath: str) -> None:
        return cls(self.gen_key(), filepath)

    @staticmethod
    def gen_key() -> str:
        return Fernet.generate_key()

    def encrypt(self, data: any) -> str:
        return self.fernet.encrypt(filedata.encode())

    def decrypt(self, data: any) -> str:
        return self.fernet.decrypt(filedata).decode()

class FileManager:
    """
    A class that manages a JSON file and the respective backup file
    """
    def __init__(self, path_to_file: str) -> None:
        if not exists(path_to_file): raise Exception("File not found in given directory.")
        crypt = Cryptographer()
        self.path_to_file: str = path_to_file
        self.backup_path: str = splitext(path_to_file)[0] + ".backup"
        self.data: dict = self.read_file_data()

    @classmethod
    def for_new_file(cls, path_with_filename_and_extension: str) -> None:
        """
        Alternative constructor for when the JSON file doesn't exist yet
        """
        with open(path_with_filename_and_extension, "w") as f:
            f.write(self.crypt.encrypt('{}'))
        return cls(path_with_filename_and_extension)

    def read_file_data(self) -> dict:
        """
        Read JSON file and move contents into dictionary
        """
        with open(self.crypt.decrypt(self.path_to_file), "r") as f:
            return load(f)

    def update_data(self, data: dict) -> None:
        """
        Overwrite old data with new data
        """
        self.data = data
        with open(self.path_to_file, "w") as f:
            f.write(self.crypt.encrypt(str(dumps(self.data))))

    def write_backup(self) -> None:
        with open(self.backup_path, "w") as f:
            f.write(self.crypt.encrypt(str(dumps(self.data))))

    def load_backup_data(self) -> None:
        """
        Load backup data as the dict
        """
        with open(self.crypt.decrypt(self.backup_path, "r")) as f:
            self.data = load(f)

    def overwrite_main_data_with_backup(self) -> None:
        with open(self.crypt.decrypt(self.backup_path, "r")) as f:
            update_data(load(f))

def generate_password(length: int) -> str:
    alphabet = ascii_letters + digits + punctuation
    password = ''.join(choice(alphabet) for i in range(length))
    return password

def evaluate_password(password: str) -> str:
    # make the search a bit more efficient
    def element_is_in_password(element: str) -> bool:
        for i in element:
            if i in password:
                return True
        return False
    # Evaluation
    length = len(password)
    variaty = element_is_in_password(ascii_letters[:26]) + element_is_in_password(ascii_letters[26:]) + element_is_in_password(digits) + element_is_in_password(punctuation)
    if length < 8 or variaty <= 2:
        return "bad"
    elif variaty == 3:
        return "medium"
    elif variaty == 4:
        return "good"

if __name__ == "__main__":
    for _ in range(5):
        pw = generate_password(20)
        print(pw)
        print(evaluate_password(pw))
