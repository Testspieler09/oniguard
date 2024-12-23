# Security packets
# Other packets
from base64 import urlsafe_b64encode, b64encode, b64decode
from datetime import datetime
from json import loads
from logging import getLogger
from os.path import exists, join, split, splitext
from secrets import choice
from string import ascii_letters, digits, punctuation
from uuid import uuid4

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from prettytable import PrettyTable

from assets import DEFAULT_SCHEMES

logger = getLogger(__name__)


class Cryptographer:
    def __init__(self, key: bytes) -> None:
        try:
            self.fernet = Fernet(key)
        except Exception as e:
            logger.info(
                "Keyfile doesn't exist or someting else went wrong. For more detail see the error below."
            )
            logger.critical(e)

    @staticmethod
    def gen_key() -> bytes:
        key = Fernet.generate_key()
        return key

    def encrypt(self, data: str) -> bytes | None:
        try:
            return self.fernet.encrypt(data.encode())
        except Exception as e:
            logger.critical(e)

    def decrypt(self, data: str) -> str | None:
        try:
            return self.fernet.decrypt(data).decode()
        except Exception as e:
            logger.critical(e)


class FileManager:
    """
    A class that manages a JSON file and the respective backup file
    """

    def __init__(self, path_to_file: str, key: bytes) -> None:
        if not exists(path_to_file):
            logger.critical("File not found in given directory.")
            logger.info(f"Therefore a file was created at {path_to_file}")
            self.for_new_file(path_to_file, key)
            return
        self.crypt = Cryptographer(key)
        self.path_to_file: str = path_to_file
        self.backup_path: str = splitext(path_to_file)[0] + ".backup"
        self.data: dict = self.read_file_data()

    def for_new_file(self, path_with_filename_and_extension: str, key: bytes) -> None:
        """
        Alternative constructor for when the JSON file doesn't exist yet
        """
        crypt = Cryptographer(key)
        default_content = f'{{"settings":{{"dates_hidden":[true, true], "hidden_schemes": []}},"schemes": {DEFAULT_SCHEMES}, "entries": {{}}}}'
        with open(path_with_filename_and_extension, "wb") as f:
            if (content := crypt.encrypt(default_content)) is None:
                return
            f.write(content)
        return

    def read_file_data(self) -> dict:
        """
        Read JSON file and move contents into dictionary
        """
        with open(self.path_to_file, "r") as f:
            data = self.crypt.decrypt(f.readline())
            if data is not None:
                return loads(data.replace("'", '"'))

        logger.critical("Wrong password provided or something else went wrong.")
        raise Exception("Wrong Password")

    def update_data(self) -> None:
        """
        Overwrite old data with new data
        """
        with open(self.path_to_file, "wb") as f:
            if (
                content := self.crypt.encrypt(str(self.data).replace("True", "true"))
            ) is None:
                return
            f.write(content)

    def write_backup(self) -> None:
        with open(self.backup_path, "wb") as f:
            if (
                content := self.crypt.encrypt(str(self.data).replace("True", "true"))
            ) is None:
                return
            f.write(content)

    def load_backup_data(self) -> None:
        """
        Load backup data as the dict
        """
        with open(self.backup_path, "r") as f:
            data = self.crypt.decrypt(f.readline())
            if data is not None:
                return loads(data.replace("'", '"'))

        logger.critical("Wrong password provided or something else went wrong.")
        raise Exception("Wrong Password")

    def overwrite_main_data_with_backup(self) -> None:
        self.load_backup_data()
        self.update_data()


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

    def __init__(self, path_to_file: str, key: bytes) -> None:
        super().__init__(path_to_file, key)
        self.hidden_stats = [["Changedate", "Hidden"], ["Creationdate", "Hidden"]]
        self.current_data: list = []
        self.order = []

    def is_master_password(self, pw: str) -> bool:
        folder_path_cross_platform = split(self.path_to_file)[0]
        with open(join(folder_path_cross_platform, ".salt"), "rb") as f:
            kdf = get_hashing_obj(f.readline())
        try:
            key = convert_pw_to_key(kdf, pw)
            DataManager(self.path_to_file, key)
            return True
        except Exception as e:
            logger.critical(e)
            return False

    @staticmethod
    def gen_hash() -> str:
        return uuid4().hex

    def group_data_by_schemes(self, data: dict) -> tuple[list, list]:
        """
        For display purposes
        """
        sorted_data = dict(
            sorted(data.items(), key=lambda item: item[1]["scheme_hash"])
        )
        first_time = True
        scheme_hashes, grouped_data = [], []
        for hash, values in sorted_data.items():
            if first_time or values["scheme_hash"] != scheme_hashes[-1]:
                first_time = False
                scheme_hashes.append(values["scheme_hash"])
                grouped_data.append([[hash, values["values"]]])
            else:
                grouped_data[-1].append([hash, values["values"]])
        # Order logic here
        for operation in self.order:
            idx = scheme_hashes.index(operation[0])
            grouped_data[idx].sort(
                key=lambda x: x[1][operation[1]], reverse=operation[2]
            )
        return scheme_hashes, grouped_data

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

    def get_entry_values(self, hash: str) -> list[str]:
        if hash not in self.data["entries"].keys():
            return []
        return [
            b64decode(i.encode()).decode() for i in self.data["entries"][hash]["values"]
        ]

    def get_values_beautified(self, hash: str) -> list[str] | None:
        if hash not in self.data["entries"].keys():
            return []
        scheme_hash = self.data["entries"][hash]["scheme_hash"]
        if scheme_hash not in self.data["schemes"].keys():
            return

        table = PrettyTable()
        table.field_names = (i[0] for i in self.data["schemes"][scheme_hash])
        table.add_row(
            [
                b64decode(i.encode()).decode()
                for i in self.data["entries"][hash]["values"]
            ]
        )

        return table.__str__().splitlines()

    def get_entries_beautified(self, hashes: list) -> list:
        data = {
            key: values for key, values in self.data["entries"].items() if key in hashes
        }
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
            output.splitlines()
            if output != ""
            else ["You have no entries to display yet. Add one with [A]."]
        )

    def get_entries_anonymised_with_hash(self, hashes: list) -> list[str]:
        entries = [i for i in self.data["entries"].items() if i[0] in hashes]
        options = []
        for entry in entries:
            options.append(
                [
                    entry[0],
                    " | ".join(
                        str(i[0])
                        for i in self.apply_constraints_to_data(
                            list(
                                zip(
                                    [
                                        b64decode(i.encode()).decode()
                                        for i in entry[1]["values"]
                                    ],
                                    (
                                        i[1]
                                        for i in self.data["schemes"][
                                            entry[1]["scheme_hash"]
                                        ]
                                    ),
                                )
                            )
                        )[:-2]
                    ),
                ]
            )
        return options

    def get_scheme_hash_by_scheme(self, p_scheme: list) -> str | None:
        for hash, scheme in self.data["schemes"].items():
            if scheme[:-2] == p_scheme:
                return hash
        logger.critical("Couldn't find a the provided scheme")

    def get_scheme_hash_by_entry_hash(self, entry_hash: str) -> str | None:
        if entry_hash not in self.data["entries"].keys():
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

    def get_scheme(self, hash: str) -> list | None:
        if hash not in self.data["schemes"].keys():
            return
        return self.data["schemes"][hash][:-2]

    def get_scheme_head(self, scheme_hash: str) -> str | None:
        if scheme_hash not in self.data["schemes"].keys():
            return
        table = PrettyTable()
        table.field_names = [i[0] for i in self.data["schemes"][scheme_hash]]
        return table.__str__().splitlines()[1]

    def get_longest_entry_beautified(self) -> tuple:
        data = self.beautify_output(self.get_all_entries()).splitlines()
        y, x = len(data) - 1, max(len(i) for i in data) + 2
        return y, x

    def get_idx_of_entries(self) -> list[int]:
        if self.current_data is None:
            return []
        entries = [
            scheme
            for scheme in self.current_data
            if self.data["entries"][scheme[0][0]]["scheme_hash"]
            not in self.data["settings"]["hidden_schemes"]
        ]
        HEADER_SIZE, SPACE_BETWEEN_TABLES, SPACE_BETWEEN_ENTRIES = 4, 2, 1
        idx = []
        counter = -1
        for i in range(len(entries)):
            if counter != -1:
                counter += SPACE_BETWEEN_TABLES
            counter += HEADER_SIZE
            idx.append(counter)
            for _ in range(len(entries[i]) - 1):
                counter += SPACE_BETWEEN_ENTRIES
                idx.append(counter)
        return idx

    def get_entry_hash_by_pointer_idx(self, pointer_idx: list) -> str:
        try:
            idx = pointer_idx[1].index(pointer_idx[0])
            joined_list = [
                entry[0]
                for scheme in self.current_data
                for entry in scheme
                if self.data["entries"][entry[0]]["scheme_hash"]
                not in self.data["settings"]["hidden_schemes"]
            ]
            return joined_list[idx]
        except ValueError:
            return self.current_data[0][0][0]

    def get_pointer_idx_by_hash(self, entry_hash: str) -> int | None:
        joined_list = [
            entry[0]
            for scheme in self.current_data
            for entry in scheme
            if self.data["entries"][entry[0]]["scheme_hash"]
            not in self.data["settings"]["hidden_schemes"]
        ]
        try:
            idx = joined_list.index(entry_hash)
            return self.get_idx_of_entries()[idx]
        except ValueError as e:
            logger.critical(e)
            return

    # Setter
    def set_hidden_dates_settings(self, new_settings: list[bool]) -> None:
        self.data["settings"]["dates_hidden"] = new_settings

    def set_hidden_schemes(self, hidden_schemes: list) -> None:
        self.data["settings"]["hidden_schemes"] = hidden_schemes

    # Add data
    def add_entry(self, scheme_hash: str, entry: list[str]) -> None:
        data = {}
        now = str(datetime.now())
        entry.extend([now, now])
        data["scheme_hash"] = scheme_hash
        data["values"] = [b64encode(i.encode()).decode() for i in entry]
        self.data["entries"].update({self.gen_hash(): data})

    def add_scheme(self, scheme: list) -> None:
        scheme.extend(self.hidden_stats)
        self.data["schemes"].update({self.gen_hash(): scheme})

    # Update methods
    def update_entry(self, entry_hash: str, new_data: list[str]) -> None:
        if entry_hash not in self.data["entries"].keys():
            return
        new_data.extend(
            [str(datetime.now()), self.data["entries"][entry_hash]["values"][-1]]
        )
        self.data["entries"][entry_hash]["values"] = [
            b64encode(i.encode()) for i in new_data
        ]

    def update_scheme(self, scheme_hash: str, new_data: list) -> None:
        if scheme_hash not in self.data["schemes"].keys():
            return
        new_data.extend(self.hidden_stats)
        self.data["schemes"][scheme_hash] = new_data

    # Delete methods
    def delete_entry(self, entry_hash: str) -> None:
        if entry_hash not in self.data["entries"].keys():
            return
        del self.data["entries"][entry_hash]

    def delete_scheme(self, scheme_hash: str) -> None:
        entries_with_scheme = self.get_entries_of_scheme(scheme_hash)
        for hash in entries_with_scheme.keys():
            self.delete_entry(hash)

        if scheme_hash not in self.data["schemes"].keys():
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
                            value if i not in idx else "*"
                            for i, value in enumerate(zip_item_constraint[0])
                        ),
                        zip_item_constraint[1],
                    )
                case "Password":
                    data[num] = "*" * 8, zip_item_constraint[1]
        for i in sorted(hidden_items, reverse=True):
            data.pop(i)
        return data

    def beautify_output(self, data: dict) -> str:
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
    password = "".join(choice(alphabet) for _ in range(length))
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
    else:
        return "HACKED"


def get_hashing_obj(salt: bytes) -> PBKDF2HMAC:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf


def convert_pw_to_key(kdf: PBKDF2HMAC, pw: str) -> bytes:
    return urlsafe_b64encode(kdf.derive(pw.encode()))
