from secrets import choice
from cryptography.fernet import Fernet
from string import ascii_letters, digits, punctuation
from os.path import exists, join, splitext, split
from json import loads
from logging import getLogger

logger = getLogger(__name__)

class Cryptographer:
    def __init__(self, key: str) -> None:
        logger.info("Cryptographer initialized.")
        try:
            self.fernet = Fernet(key)
        except Exception as e:
            logger.info("Keyfile doesn't exist or someting else went wrong. For more detail see the error below.")
            logger.critical(e)

    @staticmethod
    def get_key(filepath) -> str:
        try:
            with open(join(split(filepath)[0], ".key"), "rb") as f:
                return f.readline()
        except Exception as e:
            logger.critical(e)

    @staticmethod
    def gen_key() -> str:
        key = Fernet.generate_key()
        return key

    def encrypt(self, data: any) -> str:
        try:
            return self.fernet.encrypt(data.encode())
        except Exception as e:
            logger.critical(e)

    def decrypt(self, data: any) -> str:
        try:
            return self.fernet.decrypt(data).decode()
        except Exception as e:
            logger.critical(e)

class FileManager:
    """
    A class that manages a JSON file and the respective backup file
    """
    def __init__(self, path_to_file: str) -> None:
        if not exists(path_to_file):
            self.for_new_file(path_to_file)
            logger.critical("File not found in given directory.")
            logger.info(f"Therefore a file was created at {path_to_file}")
            return
        self.crypt = Cryptographer(Cryptographer.get_key(path_to_file))
        self.path_to_file: str = path_to_file
        self.backup_path: str = splitext(path_to_file)[0] + ".backup"
        self.data: dict = self.read_file_data()

    @classmethod
    def for_new_file(cls, path_with_filename_and_extension: str) -> None:
        """
        Alternative constructor for when the JSON file doesn't exist yet
        """
        logger.info(path_with_filename_and_extension)
        crypt = Cryptographer(Cryptographer.get_key(path_with_filename_and_extension))
        with open(path_with_filename_and_extension, "wb") as f:
            f.write(crypt.encrypt('{}'))
        return cls(path_with_filename_and_extension)

    def read_file_data(self) -> dict:
        """
        Read JSON file and move contents into dictionary
        """
        with open(self.path_to_file, "r") as f:
            data = self.crypt.decrypt(f.readline())
            return loads(data)

    def update_data(self, data: dict) -> None:
        """
        Overwrite old data with new data
        """
        self.data = data
        with open(self.path_to_file, "wb") as f:
            f.write(self.crypt.encrypt(str(self.data)))

    def write_backup(self) -> None:
        with open(self.backup_path, "wb") as f:
            f.write(self.crypt.encrypt(str(self.data)))

    def load_backup_data(self) -> None:
        """
        Load backup data as the dict
        """
        with open(self.crypt.decrypt(self.backup_path), "rb") as f:
            self.data = load(f)

    def overwrite_main_data_with_backup(self) -> None:
        with open(self.crypt.decrypt(self.backup_path), "rb") as f:
            update_data(load(f))

class DataManager(FileManager):
    def __init__(self, path_to_file) -> None:
        super().__init__(path_to_file)

# SOME FUNCTIONS REGARDING PASSWORD STUFF
def generate_password(length: int) -> str:
    alphabet = ascii_letters + digits + punctuation
    password = ''.join(choice(alphabet) for i in range(length))
    return password

def evaluate_password(password: str) -> str:
    # make the search a bit more efficient
    def element_is_in_password(element: str) -> bool:
        for i in element:
            if i in password: return True
        return False

    # Evaluation
    length = len(password)
    variaty = element_is_in_password(ascii_letters[:26]) \
              + element_is_in_password(ascii_letters[26:]) \
              + element_is_in_password(digits) \
              + element_is_in_password(punctuation)

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
