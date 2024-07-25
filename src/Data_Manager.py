# Security packets
from secrets import choice
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

# Other packets
from base64 import urlsafe_b64encode
from uuid import uuid4
from datetime import datetime
from string import ascii_letters, digits, punctuation
from os.path import exists, join, splitext, split
from json import loads
from prettytable import PrettyTable
from assets import DEFAULT_SCHEMES
from logging import getLogger

logger = getLogger(__name__)


class Cryptographer:
    def __init__(self, key: str) -> None:
        try:
            self.fernet = Fernet(key)
        except Exception as e:
            logger.info(
                "Keyfile doesn't exist or someting else went wrong. For more detail see the error below."
            )
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

    def __init__(self, path_to_file: str, key: str) -> None:
        if not exists(path_to_file):
            logger.critical("File not found in given directory.")
            logger.info(f"Therefore a file was created at {path_to_file}")
            self.for_new_file(path_to_file, key)
            return
        self.crypt = Cryptographer(key)
        self.path_to_file: str = path_to_file
        self.backup_path: str = splitext(path_to_file)[0] + ".backup"
        self.data: dict = self.read_file_data()

    def for_new_file(self, path_with_filename_and_extension: str, key: str) -> None:
        """
        Alternative constructor for when the JSON file doesn't exist yet
        """
        crypt = Cryptographer(key)
        default_content = f'{{"settings":{{"dates_hidden":[true, true], "hidden_schemes": []}},"schemes": {DEFAULT_SCHEMES}, "entries": {{}}}}'
        with open(path_with_filename_and_extension, "wb") as f:
            f.write(crypt.encrypt(default_content))
        return

    def read_file_data(self) -> dict:
        """
        Read JSON file and move contents into dictionary
        """
        with open(self.path_to_file, "r") as f:
            data = self.crypt.decrypt(f.readline())
            if data != None:
                return loads(data.replace("'", '"'))

        logger.critical("Wrong password provided or something else went wrong.")
        raise Exception("Wrong Password")

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
    """
    Wrapperclass for a JSON structure like this:
    {
        "schemes": {
            "hash": list[str]
        },
        "entries": {
            "hash": {
                "scheme_hash": str,
                "values": list[str]
            }
        }
    }
    """

    def __init__(self, path_to_file: str, key: str) -> None:
        super().__init__(path_to_file, key)
        self.hidden_stats = [["Changedate", "Hidden"], ["Creationdate", "Hidden"]]
        self.current_data = None
        self.order = []

    def is_master_password(self, pw: str) -> bool:
        folder_path_cross_platform = split(self.path_to_file)[0]
        with open(join(folder_path_cross_platform, ".salt"), "rb") as f:
            kdf = get_hashing_obj(f.readline())
        try:
            key = convert_pw_to_key(kdf, pw)
            DataManager(self.path_to_file, key)
            return True
        except:
            return False

    @staticmethod
    def gen_hash() -> str:
        return uuid4().hex

    def group_data_by_schemes(self, data: dict) -> dict:
        """
        For display purposes
        """
        sorted_data = dict(
            sorted(data.items(), key=lambda item: item[1]["scheme_hash"])
        )
        first_time = True
        scheme_hashes, data = [], []
        for hash, values in sorted_data.items():
            if first_time or values["scheme_hash"] != scheme_hashes[-1]:
                first_time = False
                scheme_hashes.append(values["scheme_hash"])
                data.append([[hash, values["values"]]])
            else:
                data[-1].append([hash, values["values"]])
        # Order logic here
        for operation in self.order:
            idx = scheme_hashes.index(operation[0])
            data[idx].sort(key=lambda x: x[1][operation[1]], reverse=operation[2])
        return scheme_hashes, data

    # Getter methods
    def get_all_entries(self) -> dict:
        return self.data["entries"]

    def get_hidden_dates_settings(self) -> list:
        return self.data["settings"]["dates_hidden"]

    def get_entries_of_scheme(self, scheme_hash: str) -> dict:
        entries = {}
        for key, entry in self.data["entries"].items():
            if entry["scheme_hash"] == scheme_hash:
                entries.update({key: entry})
        return entries

    def get_entry_values(self, hash: str) -> list:
        if not hash in self.data["entries"].keys():
            return []
        return self.data["entries"][hash]["values"]

    def get_values_beautified(self, hash: str) -> list:
        if not hash in self.data["entries"].keys():
            return []
        scheme_hash = self.data["entries"][hash]["scheme_hash"]
        if not scheme_hash in self.data["schemes"].keys():
            return

        table = PrettyTable()
        table.field_names = (i[0] for i in self.data["schemes"][scheme_hash])
        table.add_row(self.data["entries"][hash]["values"])

        return table.__str__().splitlines()

    def get_scheme_hash_by_scheme(self, p_scheme: list) -> str:
        for hash, scheme in self.data["schemes"].items():
            if scheme[:-2] == p_scheme:
                return hash
        logger.critical("Couldn't find a the provided scheme")

    def get_scheme_hash_by_entry_hash(self, entry_hash: str) -> str:
        if not entry_hash in self.data["entries"].keys():
            return
        return self.data["entries"][entry_hash]["scheme_hash"]

    def get_schemes(self) -> list:
        return [i[:-2] for i in self.data["schemes"].values()]

    def get_schemes_with_hash(self) -> list:
        return [[i, j[:-2]] for i, j in self.data["schemes"].items()]

    def get_is_hidden_scheme_all_schemes(self) -> list[bool]:
        return [
            True if i in self.data["settings"]["hidden_schemes"] else False
            for i in self.data["schemes"].keys()
        ]

    def get_scheme(self, hash: str) -> list:
        if not hash in self.data["schemes"].keys():
            return
        return self.data["schemes"][hash][:-2]

    def get_scheme_head(self, scheme_hash: str) -> str:
        if not scheme_hash in self.data["schemes"].keys():
            return
        table = PrettyTable()
        table.field_names = [i[0] for i in self.data["schemes"][scheme_hash]]
        return table.__str__().splitlines()[1]

    def get_longest_entry_beautified(self) -> tuple:
        data = self.beautify_output(self.get_all_entries()).splitlines()
        y, x = len(data) - 1, max(len(i) for i in data) + 2
        return y, x

    def get_idx_of_entries(self) -> list[int]:
        if self.current_data == None:
            return []
        HEADER_SIZE, SPACE_BETWEEN_TABLES, SPACE_BETWEEN_ENTRIES = 4, 2, 1
        idx = []
        counter = -1
        for i in range(len(self.current_data)):
            if counter != -1:
                counter += SPACE_BETWEEN_TABLES
            counter += HEADER_SIZE
            idx.append(counter)
            for j in range(len(self.current_data[i]) - 1):
                counter += SPACE_BETWEEN_ENTRIES
                idx.append(counter)
        return idx

    def get_entry_hash_by_pointer_idx(self, pointer_idx: list) -> str | None:
        try:
            idx = pointer_idx[1].index(pointer_idx[0])
            joined_list = [i[0] for j in self.current_data for i in j]
            return joined_list[idx]
        except:
            return

    def get_pointer_idx_by_hash(self, entry_hash: str) -> int | None:
        joined_list = [i[0] for j in self.current_data for i in j]
        try:
            idx = joined_list.index(entry_hash)
            return self.get_idx_of_entries()[idx]
        except ValueError:
            return

    # Setter
    def set_hidden_dates_settings(self, new_settings: list[bool]) -> None:
        self.data["settings"]["dates_hidden"] = new_settings

    def set_hidden_schemes(self, hidden_schemes: list) -> None:
        self.data["settings"]["hidden_schemes"] = hidden_schemes

    # Add data
    def add_entry(self, scheme_hash: str, entry: list) -> None:
        data = {}
        now = str(datetime.now())
        entry.extend([now, now])
        data["scheme_hash"] = scheme_hash
        data["values"] = entry
        self.data["entries"].update({self.gen_hash(): data})

    def add_scheme(self, scheme: list) -> None:
        scheme.extend(self.hidden_stats)
        self.data["schemes"].update({self.gen_hash(): scheme})

    # Update methods
    def update_entry(self, entry_hash: str, new_data: list) -> None:
        if not entry_hash in self.data["entries"].keys():
            return
        new_data.extend(
            [str(datetime.now()), self.data["entries"][entry_hash]["values"][-1]]
        )
        self.data["entries"][entry_hash]["values"] = new_data

    def update_scheme(self, scheme_hash: str, new_data: list) -> None:
        if not scheme_hash in self.data["schemes"].keys():
            return
        new_data.extend(self.hidden_stats)
        self.data["schemes"][scheme_hash] = new_data

    # Delete methods
    def delete_entry(self, entry_hash: str) -> None:
        if not entry_hash in self.data["entries"].keys():
            return
        del self.data["entries"][entry_hash]

    def delete_scheme(self, scheme_hash: str) -> None:
        entries_with_scheme = self.get_entries_of_scheme(scheme_hash)
        for hash in entries_with_scheme.keys():
            self.delete_entry(hash)

        if not scheme_hash in self.data["schemes"].keys():
            return
        del self.data["schemes"][scheme_hash]

    # Output methods
    def apply_settings_to_hidden_dates(self, data: list, is_table_header=False) -> list:
        if is_table_header:
            idx = sorted(
                (num for num, i in enumerate(data[:-2]) if i[1] == "Hidden"),
                reverse=True,
            )
            for i in idx:
                data.pop(i)
        if all(self.data["settings"]["dates_hidden"]):
            data = data[:-2]
        elif not any(self.data["settings"]["dates_hidden"]):
            pass
        elif self.data["settings"]["dates_hidden"][0]:
            data = data[:-2] + data[-1:]
        else:
            data = data[:-1]
        return [i[0] for i in data]

    @staticmethod
    def apply_constraints_to_data(data: list) -> list:
        hidden_items = []
        for num, zip_item_constraint in enumerate(data[:-2]):
            match zip_item_constraint[1]:
                case "None":
                    continue
                case "Hidden":
                    hidden_items.append(num)
                case "Truncate":
                    length_item = len(zip_item_constraint[0])
                    idx = range(
                        int(length_item // 2 - 0.25 * length_item),
                        int(length_item // 2 + 0.3 * length_item),
                    )
                    data[num] = (
                        "".join(
                            value if not i in idx else "*"
                            for i, value in enumerate(zip_item_constraint[0])
                        ),
                        zip_item_constraint[1],
                    )
                case "Password":
                    data[num] = "*" * 8, zip_item_constraint[1]
        for i in sorted(hidden_items, reverse=True):
            data.pop(i)
        return data

    def beautify_output(self, data: dict) -> list[str]:
        """
        if multiple schemes display them below each other
        """
        output = ""
        scheme_hashes, entries = self.group_data_by_schemes(data)
        self.current_data = entries
        for i, scheme in enumerate(scheme_hashes):
            if scheme in self.data["settings"]["hidden_schemes"]:
                continue
            table = PrettyTable()
            # hide or unhide the date stuff
            table.field_names = self.apply_settings_to_hidden_dates(
                self.data["schemes"][scheme], True
            )

            for entry in entries[i]:
                # prepare data based on constraints
                modified_entry = self.apply_constraints_to_data(
                    list(zip(entry[1], (i[1] for i in self.data["schemes"][scheme])))
                )
                table.add_row(self.apply_settings_to_hidden_dates(modified_entry))
            output += f"{table.__str__()}\n\n"
        return (
            output
            if output != ""
            else "You have no entries to display yet. Add one with [A]."
        )


# SOME FUNCTIONS REGARDING PASSWORD STUFF
def generate_password(length: int) -> str:
    alphabet = ascii_letters + digits + punctuation
    password = "".join(choice(alphabet) for i in range(length))
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
    variaty = (
        element_is_in_password(ascii_letters[:26])
        + element_is_in_password(ascii_letters[26:])
        + element_is_in_password(digits)
        + element_is_in_password(punctuation)
    )

    if length < 8 or variaty <= 2:
        return "BAD"
    elif variaty == 3:
        return "OKAY"
    elif variaty == 4:
        return "EXCELLENT"


def get_hashing_obj(salt: str) -> object:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf


def convert_pw_to_key(kdf: object, pw: str) -> str:
    return urlsafe_b64encode(kdf.derive(pw.encode()))


if __name__ == "__main__":
    for _ in range(5):
        pw = generate_password(20)
        print(pw)
        print(evaluate_password(pw))
