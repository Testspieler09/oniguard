from curses import (
    newwin,
    newpad,
    initscr,
    init_pair,
    color_pair,
    start_color,
    curs_set,
    cbreak,
    noecho,
    nocbreak,
    echo,
    endwin,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    A_UNDERLINE,
    A_NORMAL,
)
from pyperclip import copy
from re import match
from ast import literal_eval
from textwrap import wrap
from os.path import split, join
from Finder import Finder
from Data_Manager import (
    DataManager,
    generate_password,
    evaluate_password,
    get_hashing_obj,
    convert_pw_to_key,
)
from assets import (
    HELP_MESSAGE,
    FOOTER_TEXT,
    CONSTRAINTS,
    NAME_REGEX,
    ASCII_ONI_LOGO,
    ONI_ENEMIES,
)
from time import sleep
from logging import getLogger

logger = getLogger(__name__)


class OniManager:
    def __init__(self, data: dict) -> None:
        self.name = data["name"]
        self.max_hp = data["hp"]
        self.hp = data["hp"]
        self.damage = data["damage"]
        self.ko = False
        self.num_guesses = 0
        self.leaderboard = self.get_leaderboard()
        self.run_game()

    def __str__(self) -> str:
        healthbar = "=" * round(10 * self.hp / self.max_hp)
        return (
            f"{self.name} {healthbar if healthbar != '' and not self.is_ko() else ':'}"
        )

    @staticmethod
    def get_leaderboard() -> None:
        with open(join("..", "userdata", ".leaderboard"), "r") as f:
            return literal_eval(f.readline())

    def add_leaderboard(self) -> None:
        if (
            len(self.leaderboard) == 5
            and not self.leaderboard[-1][1] > self.num_guesses
        ):
            return

        self.leaderboard.append([self.name, self.num_guesses])
        self.leaderboard.sort(key=lambda x: x[1])
        print(self.leaderboard)

        if len(self.leaderboard) >= 5:
            self.leaderboard = self.leaderboard[:5]

        with open(join("..", "userdata", ".leaderboard"), "w") as f:
            f.write(str(self.leaderboard))

    @classmethod
    def init_player(cls, name: str) -> None:
        cls({"name": name, "hp": 500, "damage": 50})

    def run_game(self) -> None:
        pass

    def is_ko(self) -> bool:
        if self.ko:
            return True
        else:
            return False

    def attack(self, target: object) -> None:
        target._damage(self.damage)

    def _damage(self, damage_value: int) -> None:
        self.hp -= damage_value
        if self.hp <= 0:
            self.hp = 0
            self.ko = True


class PopUp:
    def __init__(self, screen: object) -> None:
        y, x = screen.getmaxyx()
        self.dimensions = (y - 3, x)
        self.win = newwin(y - 3, x, 2, 0)
        self.screen = screen
        self.screen.refresh()

        # Settings
        curs_set(0)
        cbreak()
        noecho()
        self.screen.nodelay(False)

    def kill_pop_up(self) -> None:
        curs_set(0)
        noecho()
        self.screen.nodelay(True)
        del self

    # Read input
    def get_input_checkboxes(self, options: list, message: str, cache=None) -> list:
        message = self.make_message_fit_width(message, self.dimensions[1] - 2)
        height_of_msg = len(message.splitlines()) + 1
        self.win.addstr(1, 0, message)
        self.win.box()
        self.win.refresh()

        scroll_y, scroll_x = 0, 0
        pad = newpad(len(options) + 1, max(len(i) for i in options) + 5)

        selected = (
            [False] * len(options)
            if cache == None and len(cache) != len(options)
            else cache
        )
        current_option = 0

        def display_menu():
            for idx, option in enumerate(options):
                if idx == current_option:
                    pad.attron(color_pair(2))
                checkbox = "[X]" if selected[idx] else "[ ]"
                pad.addstr(idx, 0, checkbox)
                pad.addstr(idx, 4, option)
                if idx == current_option:
                    pad.attroff(color_pair(2))
            bottom_right_y, bottom_right_x = (
                height_of_msg + pad.getmaxyx()[0] + 1,
                pad.getmaxyx()[1] + 1,
            )
            if height_of_msg + pad.getmaxyx()[0] + 1 >= self.win.getmaxyx()[0]:
                bottom_right_y = self.win.getmaxyx()[0]
            if pad.getmaxyx()[1] >= self.win.getmaxyx()[1] - 1:
                bottom_right_x = self.win.getmaxyx()[1] - 2
            pad.refresh(
                scroll_y, scroll_x, height_of_msg + 3, 1, bottom_right_y, bottom_right_x
            )

        while True:
            sleep(0.01)
            display_menu()
            key = self.screen.getkey()

            if key == "KEY_UP" and current_option > 0:
                current_option -= 1
                if current_option < scroll_y:
                    scroll_y -= 1
            elif key == "KEY_DOWN" and current_option < len(options) - 1:
                current_option += 1
                if current_option >= scroll_y + (
                    self.win.getmaxyx()[0] - height_of_msg - 2
                ):
                    scroll_y += 1
            elif key == "KEY_LEFT" and scroll_x > 0:
                scroll_x -= 1
            elif (
                key == "KEY_RIGHT"
                and scroll_x < pad.getmaxyx()[1] - self.win.getmaxyx()[1] + 2
            ):
                scroll_x += 1
            elif key == " ":
                selected[current_option] = not selected[current_option]
            elif key == "\n":
                break

        self.kill_pop_up()
        return [idx for idx, value in enumerate(selected) if value], [
            opt for idx, opt in enumerate(options) if selected[idx]
        ]

    def get_input_radio_btn(self, options: list, message: str) -> tuple:
        message = self.make_message_fit_width(message, self.dimensions[1] - 2)
        height_of_msg = len(message.splitlines()) + 1
        self.win.addstr(1, 0, message)
        self.win.box()
        self.win.refresh()

        scroll_y, scroll_x = 0, 0
        pad = newpad(len(options) + 1, max(len(i) for i in options) + 5)

        current_option = 0

        def display_menu():
            for idx, option in enumerate(options):
                if idx == current_option:
                    pad.attron(color_pair(2))
                    checkbox = "(X)"
                else:
                    checkbox = "( )"
                pad.addstr(idx, 0, checkbox)
                pad.addstr(idx, 4, option)
                if idx == current_option:
                    pad.attroff(color_pair(2))
            bottom_right_y, bottom_right_x = (
                height_of_msg + pad.getmaxyx()[0] + 1,
                pad.getmaxyx()[1] + 1,
            )
            if height_of_msg + pad.getmaxyx()[0] + 1 >= self.win.getmaxyx()[0]:
                bottom_right_y = self.win.getmaxyx()[0]
            if pad.getmaxyx()[1] >= self.win.getmaxyx()[1] - 1:
                bottom_right_x = self.win.getmaxyx()[1] - 2
            pad.refresh(
                scroll_y, scroll_x, height_of_msg + 3, 1, bottom_right_y, bottom_right_x
            )

        while True:
            sleep(0.01)
            display_menu()
            key = self.screen.getkey()

            if key == "KEY_UP" and current_option > 0:
                current_option -= 1
                if current_option < scroll_y:
                    scroll_y -= 1
            elif key == "KEY_DOWN" and current_option < len(options) - 1:
                current_option += 1
                if current_option >= scroll_y + (
                    self.win.getmaxyx()[0] - height_of_msg - 2
                ):
                    scroll_y += 1
            elif key == "KEY_LEFT" and scroll_x > 0:
                scroll_x -= 1
            elif (
                key == "KEY_RIGHT"
                and scroll_x < pad.getmaxyx()[1] - self.win.getmaxyx()[1] + 2
            ):
                scroll_x += 1
            elif key == "\n":
                break

        self.kill_pop_up()
        return current_option, options[current_option]

    def get_input_string(
        self, p_message: str, p_regex=None, anonymize_input=False
    ) -> str:
        WRONG_INPUT_MESSAGE = "The provided input doesn't match the wanted pattern.\n\n"
        regex = r"[\S\s]*" if p_regex == None else p_regex
        message = self.make_message_fit_width(p_message, self.dimensions[1] - 2)
        height_of_msg = len(message.splitlines()) + 1
        message_is_updated = False
        while True:
            # Init new window and change some settings
            self.win.erase()
            curs_set(1)
            if not anonymize_input:
                echo()

            # Output info and get input
            self.win.addstr(1, 0, message)
            self.win.box()
            self.win.refresh()
            input = self.win.getstr(height_of_msg, 1).decode(
                "utf-8", "backslashreplace"
            )

            if match(regex, input):
                break
            elif not message_is_updated:
                message_is_updated = True
                message = self.make_message_fit_width(
                    WRONG_INPUT_MESSAGE + p_message, self.dimensions[1] - 2
                )
                height_of_msg = len(message.splitlines()) + 1
        self.kill_pop_up()
        return input

    # Helper methods
    @staticmethod
    def make_message_fit_width(message: str, width: int) -> str:
        paras = [
            "dbc71b7fc9e348da85ae5e095bd80855" if i == "" else i
            for i in message.splitlines()
        ]  # using a uuid4 here to preserve the custom linespacing via `\n`
        lines = [" " + j for i in paras for j in wrap(i, width)]
        return "\n".join(
            ["" if i == " dbc71b7fc9e348da85ae5e095bd80855" else i for i in lines]
        )


class Renderer:
    def __init__(
        self, data_mng: object, content=None, beautified_content=None, pointer_idx=None
    ) -> None:
        self.screen = initscr()
        self.data = data_mng
        self.running = True

        # DETERMINE THE SIZE OF THE MAIN PAD
        y, x = self.get_main_dimensions()

        help_lines = HELP_MESSAGE.split("\n")
        self.window_dimensions = [
            self.screen.getmaxyx(),
            (y, x),
            (len(help_lines) + 1, max(len(line) for line in help_lines) + 1),
        ]
        self.windows = [
            self.screen,  # footer
            newpad(self.window_dimensions[1][0], self.window_dimensions[1][1]),  # main
            newpad(
                self.window_dimensions[2][0], self.window_dimensions[2][1]
            ),  # help message popup
        ]

        self.pointer_idx = (
            [3, self.data.get_idx_of_entries()] if pointer_idx == None else pointer_idx
        )
        self.scroll_y, self.scroll_x = (
            self.pointer_idx[0] - self.window_dimensions[0][0] + 6,
            0,
        )
        if self.scroll_y < 0:
            self.scroll_y = 0
        self.last_scroll_pos_main_scr = (0, 0)
        self.main_start_y_x = (2, 0)
        self.main_end_y_x = (
            self.window_dimensions[0][0] - 2,
            self.window_dimensions[0][1] - 1,
        )
        self.active_window = 1
        self.content = self.data.get_all_entries() if content == None else content
        self.beautified_content = (
            self.data.beautify_output(self.data.get_all_entries())
            if beautified_content == None
            else beautified_content
        )

        # COLOR STUFF FOR IMPORTANCE
        start_color()
        init_pair(1, COLOR_GREEN, COLOR_BLACK)
        init_pair(2, COLOR_BLUE, COLOR_BLACK)
        init_pair(3, COLOR_RED, COLOR_BLACK)
        self.low_importance = color_pair(1)
        self.medium_importance = color_pair(2)
        self.high_importance = color_pair(3)

        # ADJUST SETTINGS
        curs_set(0)
        cbreak()
        noecho()
        self.screen.nodelay(True)
        self.screen.keypad(True)

        # CLEAR SCREEN AND RUN IT
        self.screen.clear()
        self.screen.refresh()
        self.run_scr()

    def kill_scr(self) -> None:
        self.running = False
        nocbreak()
        self.screen.keypad(False)
        echo()
        endwin()

    def run_scr(self) -> None:
        headline = "OniGuard"
        self.output_text_to_window(
            0, self.space_footer_text(FOOTER_TEXT), self.window_dimensions[0][0] - 1, 0
        )
        y, _ = self.get_coordinates_for_centered_text(headline)
        self.output_text_to_window(0, headline, 1, y, A_UNDERLINE)
        self.update_scr()
        while self.running:
            sleep(0.01)  # so program doesn't use 100% cpu
            key = self.get_input()
            self.event_handler(key)

    def scroll_pad(self, pad_id: int) -> None:
        start_y, start_x, end_y, end_x = self.get_coordinates_for_centered_pad(pad_id)
        self.windows[pad_id].refresh(
            self.scroll_y, self.scroll_x, start_y, start_x, end_y, end_x
        )

    def event_handler(self, event: str) -> None:
        match event:
            # Scroll operations
            case "KEY_DOWN":
                try:
                    if self.active_window == 2:
                        raise ValueError
                    length_idx, current_idx = len(
                        self.pointer_idx[1]
                    ) - 1, self.pointer_idx[1].index(self.pointer_idx[0])
                    if current_idx + 1 > length_idx:
                        raise ValueError
                    self.pointer_idx[0] = self.pointer_idx[1][current_idx + 1]
                    self.update_scr()
                    if (
                        abs(
                            self.scroll_y
                            - self.window_dimensions[self.active_window][0]
                            - 3
                        )
                        <= self.window_dimensions[0][0]
                    ):
                        return
                    if (
                        self.pointer_idx[1][current_idx + 1] - 1
                        != self.pointer_idx[1][current_idx]
                        and self.window_dimensions[0][0] - 3
                        <= self.pointer_idx[0] - self.scroll_y
                    ):
                        self.scroll_y = (
                            self.pointer_idx[0] - self.window_dimensions[0][0] + 6
                        )
                    else:
                        self.scroll_y += 1
                except ValueError:
                    if (
                        abs(
                            self.scroll_y
                            - self.window_dimensions[self.active_window][0]
                            - 3
                        )
                        <= self.window_dimensions[0][0]
                    ):
                        return
                    self.scroll_y += 1
                self.scroll_pad(self.active_window)
            case "KEY_UP":
                try:
                    if self.active_window == 2:
                        raise ValueError
                    length_idx, current_idx = len(
                        self.pointer_idx[1]
                    ) - 1, self.pointer_idx[1].index(self.pointer_idx[0])
                    if current_idx - 1 < 0:
                        raise ValueError
                    self.pointer_idx[0] = self.pointer_idx[1][current_idx - 1]
                    self.update_scr()
                    if (
                        self.pointer_idx[1][current_idx]
                        == self.pointer_idx[1][current_idx - 1] + 1
                    ):
                        self.scroll_y -= 1
                    else:
                        self.scroll_y -= -(
                            self.pointer_idx[0] - self.window_dimensions[0][0] + 6
                        )
                except ValueError:
                    self.scroll_y -= 1
                if self.scroll_y <= 0:
                    self.scroll_y = 0
                self.scroll_pad(self.active_window)
            case "KEY_RIGHT":
                if (
                    abs(self.scroll_x - self.window_dimensions[self.active_window][1])
                    <= self.window_dimensions[0][1]
                ):
                    return
                self.scroll_x += 1
                self.scroll_pad(self.active_window)
            case "KEY_LEFT":
                self.scroll_x -= 1
                if self.scroll_x <= 0:
                    self.scroll_x = 0
                self.scroll_pad(self.active_window)
            # Main operations
            case "S" | "s":
                if self.active_window == 2:
                    return
                self.search_procedure()
            case "A" | "a":
                if self.active_window == 2:
                    return
                self.add_procedure()
            case "F" | "f":
                # filter schemes and date stats
                if self.active_window == 2:
                    return
                self.filter_procedure()
            case "O" | "o":
                # order by any column in table pointer is at (if multiple shown)
                if self.active_window == 2:
                    return
                self.order_procedure()
            case "C" | "c":
                if self.active_window == 2:
                    return
                self.copy_procedure()
            case "L" | "l":
                # enter lockscreen for -> masterpassword to reenter
                if self.active_window == 2:
                    return
                self.lock_procedure()
            case "\n":
                # do something to the item the pointer is on (change, delete)
                if self.active_window == 2:
                    return
                self.on_item_procedure()
            # Default operations
            case "H" | "h":
                if self.active_window == 2:
                    self.active_window = 1
                    self.scroll_y, self.scroll_x = self.last_scroll_pos_main_scr
                    self.windows[1].refresh(
                        self.scroll_y,
                        self.scroll_x,
                        self.main_start_y_x[0],
                        self.main_start_y_x[1],
                        self.main_end_y_x[0],
                        self.main_end_y_x[1],
                    )
                else:
                    self.active_window = 2
                    self.last_scroll_pos_main_scr = (self.scroll_y, self.scroll_x)
                    self.scroll_y, self.scroll_x = 0, 0
                    self.output_text_to_window(2, HELP_MESSAGE, 0, 0)
            case "Q" | "q":
                self.kill_scr()
            case "KEY_RESIZE":
                self.kill_scr()
                Renderer(
                    self.data, self.content, self.beautified_content, self.pointer_idx
                )

    # Implementations of the main procedures
    def search_procedure(self) -> None:
        if self.content == {}:
            return
        search_key = PopUp(self.screen).get_input_string(
            "What are you searching for?", NAME_REGEX
        )
        elements = Finder().fuzzy_search(search_key, self.content)
        self.update_scr()

    def add_procedure(self) -> None:
        popup = PopUp(self.screen)
        _, input = popup.get_input_radio_btn(
            ["Scheme", "Entry"], "What do you want to add?"
        )
        match input:
            case "Scheme":
                data = []
                while True:
                    _, action = PopUp(self.screen).get_input_radio_btn(
                        ["Add column", "Remove column", "Stop"],
                        f"What do you want to do?\nScheme: {data}",
                    )
                    match action:
                        case "Stop":
                            break
                        case "Add column":
                            name = PopUp(self.screen).get_input_string(
                                "Please provide a name for the column.", NAME_REGEX
                            )
                            _, constraint = PopUp(self.screen).get_input_radio_btn(
                                CONSTRAINTS, "What constraint would you like to add."
                            )
                            if not [name, constraint] in data:
                                data.append([name, constraint])
                        case "Remove column":
                            if data == []:
                                PopUp(self.screen).get_input_string(
                                    "There are no columns yet. Press `Enter` to continue."
                                )
                                continue
                            idx, _ = PopUp(self.screen).get_input_checkboxes(
                                [str(i) for i in data],
                                "Which columns do you want to remove?",
                            )
                            for i in sorted(idx, reverse=True):
                                data.remove(data[i])
                if data != []:
                    self.data.add_scheme(data)
            case "Entry":
                # get scheme_hash
                schemes = self.data.get_schemes()
                schemes.insert(0, "Cancel")
                popup = PopUp(self.screen)
                idx, _ = popup.get_input_radio_btn(
                    [str(i) for i in schemes],
                    "What scheme do you want to add the entry to?",
                )
                if idx == 0:
                    self.update_scr()
                    return
                scheme_hash = self.data.get_scheme_hash_by_scheme(schemes[idx])
                # iterate over scheme and ask for entries
                entry = []
                for item in schemes[idx]:
                    popup = PopUp(self.screen)
                    if item[1] != "Password":
                        input = popup.get_input_string(
                            f"Provide a entry for the '{item[0]}' column.\n", NAME_REGEX
                        )
                    else:
                        idx, _ = popup.get_input_radio_btn(
                            ["generate password", "input it manually"],
                            "What do you want to do?",
                        )
                        if idx == 0:
                            length = PopUp(self.screen).get_input_string(
                                "How long is the password supposed to be?", r"^\d+$"
                            )
                            input = generate_password(int(length))
                        else:
                            while True:
                                input = popup.get_input_string(
                                    f"Provide a entry for the '{item[0]}' column.\n",
                                    NAME_REGEX,
                                )
                                rating = evaluate_password(input)
                                idx, _ = PopUp(self.screen).get_input_radio_btn(
                                    ["Continue", "New password"],
                                    f"Your password has a security rating of {rating}.",
                                )
                                if idx == 0:
                                    break
                    entry.append(input)
                self.data.add_entry(scheme_hash, entry)
        self.update_contents(self.data.get_all_entries())
        self.update_main_dimensions()
        self.update_scr(hard_clear=True)

    def change_procedure(self, hash: str, type_of_data_to_change: str) -> None:
        match type_of_data_to_change:
            case "entry":
                scheme_values = self.data.get_scheme(
                    self.data.get_scheme_hash_by_entry_hash(hash)
                )
                choice = PopUp(self.screen).get_input_checkboxes(
                    [
                        i.strip()
                        for i in self.beautified_content.splitlines()[
                            self.pointer_idx[0]
                        ].split("|")
                        if i != ""
                    ],
                    "What entries do you want to update?",
                )
                if choice[0] == []:
                    return
                entry = self.data.get_entry_values(hash)
                for idx, column in zip(choice[0], choice[1]):
                    entry[idx] = PopUp(self.screen).get_input_string(
                        f"Please provide the new entry for `{scheme_values[idx][0]}` column.\nThe old one was {column}",
                        NAME_REGEX,
                    )
                self.data.update_entry(hash, entry[:-2])
            case "scheme":
                scheme_values = self.data.get_scheme(hash)
                choice = PopUp(self.screen).get_input_checkboxes(
                    [i[0] for i in scheme_values], "What columns do you want to rename?"
                )
                if choice[0] == []:
                    self.update_scr()
                    return
                for idx, column in zip(choice[0], choice[1]):
                    scheme_values[idx][0] = PopUp(self.screen).get_input_string(
                        f"Please provide the new name for the `{column}` column.",
                        NAME_REGEX,
                    )
                self.data.update_scheme(hash, scheme_values)
        self.update_contents(self.data.get_all_entries())
        self.update_scr(hard_clear=True)

    def delete_procedure(
        self, hash: str, type_of_data_to_delete: str, data: str
    ) -> None:
        match type_of_data_to_delete:
            case "entry":
                choice, _ = PopUp(self.screen).get_input_radio_btn(
                    ["No", "Yes"],
                    f"Do you want to delete this entry.\n\n{data}",
                )
                if choice:
                    self.data.delete_entry(hash)
                else:
                    return
            case "scheme":
                choice, _ = PopUp(self.screen).get_input_radio_btn(
                    ["No", "Yes"],
                    f"Do you want to delete this scheme AND ALL ENTRIES ASSOCIATED WITH IT?\n\n{data}",
                )
                if choice:
                    password = PopUp(self.screen).get_input_string(
                        "Please provide the masterpassword to delete the scheme and all its entries. [Wrong input -> Back to entries]",
                        anonymize_input=True,
                    )
                    if self.data.is_master_password(password):
                        self.data.delete_scheme(hash)
                    else:
                        return
        self.update_contents(self.data.get_all_entries())
        self.update_main_dimensions()

    def filter_procedure(self) -> None:
        choice, _ = PopUp(self.screen).get_input_radio_btn(
            ["Cancel", "Show hidden date statistics", "Filter schemes"],
            "What do you want to do?",
        )
        match choice:
            case 0:
                self.update_scr()
                return
            case 1:
                settings = self.data.get_hidden_dates_settings()
                choice, _ = PopUp(self.screen).get_input_checkboxes(
                    ["Changedate", "Creationdate"],
                    "Which hidden date statistics do you want to show?",
                    [1 - int(i) for i in settings],
                )
                self.data.set_hidden_dates_settings(
                    [True if i not in choice else False for i in range(len(settings))]
                )
            case 2:
                schemes = self.data.get_schemes_with_hash()
                idx, _ = PopUp(self.screen).get_input_checkboxes(
                    [str(i[1]) for i in schemes],
                    "Which schemes do you not want to display?",
                    self.data.get_is_hidden_scheme_all_schemes(),  # maybe save in settings?!
                )
                self.data.set_hidden_schemes(
                    [j[0] for i, j in enumerate(schemes) if i in idx]
                )
        self.update_contents(self.data.get_all_entries())
        self.update_scr(hard_clear=True)

    def show_procedure(self, hash: str) -> None:
        entry_hash = self.data.get_entry_hash_by_pointer_idx(self.pointer_idx)
        if entry_hash == None:
            return
        password = PopUp(self.screen).get_input_string(
            "Please provide the masterpassword as the data will be displayed without anonymization.",
            anonymize_input=True,
        )
        if not self.data.is_master_password(password):
            self.update_scr()
            return
        # end of password part
        content: list = self.data.get_values_beautified(entry_hash)
        dimensions = len(content), max(len(i) for i in content)
        win = newpad(
            (
                dimensions[0]
                if self.main_end_y_x[0] - 1 < dimensions[0]
                else self.main_end_y_x[0] - 1
            ),
            (
                dimensions[1]
                if self.main_end_y_x[1] - 1 < dimensions[1]
                else self.main_end_y_x[1] - 1
            ),
        )
        y, x = (
            1
            if dimensions[0] >= self.main_end_y_x[0] - 1
            else self.main_end_y_x[0] // 2 + dimensions[0] // 2 - 5
        ), (
            0
            if dimensions[1] >= self.main_end_y_x[1] - 1
            else self.main_end_y_x[1] // 2 - dimensions[1] // 2 - 1
        )
        win.addstr(y - 1, x, "Press `ENTER` when you are finished.")
        for i, line in enumerate(content):
            win.addstr(y + i, x, line)
        self.screen.nodelay(False)
        scroll_y, scroll_x = 0, 0
        win.refresh(
            scroll_y,
            scroll_x,
            self.main_start_y_x[0] + 1,
            self.main_start_y_x[1] + 1,
            self.main_end_y_x[0] - 1,
            self.main_end_y_x[1] - 1,
        )
        while True:
            key = self.screen.getkey()
            match key.lower():
                case "key_up":
                    scroll_y -= 1
                    if scroll_y <= 0:
                        scroll_y = 0
                    win.refresh(
                        scroll_y,
                        scroll_x,
                        self.main_start_y_x[0] + 1,
                        self.main_start_y_x[1] + 1,
                        self.main_end_y_x[0] - 1,
                        self.main_end_y_x[1] - 1,
                    )
                case "key_down":
                    if (
                        abs(scroll_y - dimensions[0])
                        <= self.window_dimensions[0][0] - 3
                    ):
                        continue
                    scroll_y += 1
                    win.refresh(
                        scroll_y,
                        scroll_x,
                        self.main_start_y_x[0] + 1,
                        self.main_start_y_x[1] + 1,
                        self.main_end_y_x[0] - 1,
                        self.main_end_y_x[1] - 1,
                    )
                case "key_left":
                    scroll_x -= 1
                    if scroll_x <= 0:
                        scroll_x = 0
                    win.refresh(
                        scroll_y,
                        scroll_x,
                        self.main_start_y_x[0] + 1,
                        self.main_start_y_x[1] + 1,
                        self.main_end_y_x[0] - 1,
                        self.main_end_y_x[1] - 1,
                    )
                case "key_right":
                    if (
                        abs(scroll_x - dimensions[1] - 2)
                        <= self.window_dimensions[0][1]
                    ):
                        continue
                    scroll_x += 1
                    win.refresh(
                        scroll_y,
                        scroll_x,
                        self.main_start_y_x[0] + 1,
                        self.main_start_y_x[1] + 1,
                        self.main_end_y_x[0] - 1,
                        self.main_end_y_x[1] - 1,
                    )
                case "key_resize":
                    self.kill_scr()
                    Renderer(
                        self.data,
                        self.content,
                        self.beautified_content,
                        self.pointer_idx,
                    )
                    return
                case "\n":
                    break
        self.screen.nodelay(True)
        self.update_scr()

    def order_procedure(self) -> None:
        entry_hash = self.data.get_entry_hash_by_pointer_idx(self.pointer_idx)
        if entry_hash == None:
            return
        scheme_hash = self.data.get_scheme_hash_by_entry_hash(entry_hash)
        scheme_values = self.data.get_scheme(scheme_hash)
        scheme_values.insert(0, ["Cancel", "None"])
        scheme_values.extend(self.data.hidden_stats)
        idx, _ = PopUp(self.screen).get_input_radio_btn(
            [i[0] for i in scheme_values], "What column do you want to order by?"
        )
        if idx == 0:
            self.update_scr()
            return
        choice, _ = PopUp(self.screen).get_input_radio_btn(
            ["Ascending [1, 2, 3, 4, ...]", "Descending [100, 99, 98, ...]"],
            "How should the data be displayed?",
        )
        if scheme_hash in (i[0] for i in self.data.order):
            idx = [i[0] for i in self.data.order].index(scheme_hash)
            self.data.order.pop(idx)
        self.data.order.append([scheme_hash, idx - 1, choice])
        self.update_contents(self.data.get_all_entries())
        self.update_scr()

    def copy_procedure(self) -> None:
        entry_hash = self.data.get_entry_hash_by_pointer_idx(self.pointer_idx)
        if entry_hash == None:
            return
        password = PopUp(self.screen).get_input_string(
            "Please provide the masterpassword as the data will be displayed without anonymization.",
            anonymize_input=True,
        )
        if not self.data.is_master_password(password):
            self.update_scr()
            return
        options = self.data.get_entry_values(entry_hash)
        if options == []:
            return
        options.insert(0, "Cancel")
        _, value = PopUp(self.screen).get_input_radio_btn(
            options, "Which value do you want to copy to your clipboard?"
        )
        if value != "Cancel":
            copy(value)
        self.update_scr()

    def lock_procedure(self) -> None:
        win = newwin(self.window_dimensions[0][0], self.window_dimensions[0][1], 0, 0)
        message = PopUp.make_message_fit_width(
            "Press [L] to login again or [Q] to quit.", self.window_dimensions[0][1]
        )
        exiting = False
        for logo in ASCII_ONI_LOGO:
            y, x = len(logo.splitlines()), max(len(i) for i in logo.splitlines())
            if y <= self.main_end_y_x[0] and x <= self.main_end_y_x[1]:
                break

        noecho()
        curs_set(0)
        self.screen.nodelay(False)

        for i, line in enumerate(logo.splitlines()):
            win.addstr(
                (self.window_dimensions[0][0] - y) // 2 - 1 + i,
                (self.window_dimensions[0][1] - x) // 2 - 2,
                line,
            )
        win.addstr(
            self.window_dimensions[0][0] - 2,
            0,
            message,
        )
        win.refresh()

        while True:
            key = self.screen.getkey()
            match key.lower():
                case "l":
                    self.screen.move(self.window_dimensions[0][0] - 1, 0)
                    curs_set(1)
                    password = win.getstr(self.window_dimensions[0][0] - 1, 0)
                    if self.data.is_master_password(password.decode()):
                        curs_set(0)
                        break
                    else:
                        error_msg = " Password not correct!"
                        win.addstr(
                            self.window_dimensions[0][0] - 2,
                            0,
                            error_msg + " " * (len(error_msg) - len(message[0])),
                        )
                        win.refresh()
                        curs_set(0)
                        sleep(2)
                        win.addstr(self.window_dimensions[0][0] - 2, 0, message)
                        win.refresh()
                case "q" | "key_resize":
                    exiting = True
                    break

        if exiting:
            self.kill_scr()
            return

        del win
        self.screen.clear()
        headline = "OniGuard"
        self.output_text_to_window(
            0, self.space_footer_text(FOOTER_TEXT), self.window_dimensions[0][0] - 1, 0
        )
        y, _ = self.get_coordinates_for_centered_text(headline)
        self.output_text_to_window(0, headline, 1, y, A_UNDERLINE)
        self.windows[1].refresh(
            self.scroll_y,
            self.scroll_x,
            self.main_start_y_x[0],
            self.main_start_y_x[1],
            self.main_end_y_x[0],
            self.main_end_y_x[1],
        )

    def on_item_procedure(self) -> None:
        entry_hash = self.data.get_entry_hash_by_pointer_idx(self.pointer_idx)
        if entry_hash == None:
            return
        choice, _ = PopUp(self.screen).get_input_radio_btn(
            [
                "Cancel",
                "Show content uncensored",
                "Change data of entry",
                "Delete entry",
                "Rename columns of scheme",
                "Delete scheme",
            ],
            "What do you want to do?",
        )
        match choice:
            case 1:
                self.show_procedure(entry_hash)
            case 2:
                self.change_procedure(entry_hash, "entry")
            case 3:
                self.delete_procedure(
                    entry_hash,
                    "entry",
                    self.beautified_content.splitlines()[self.pointer_idx[0]],
                )
            case 4:
                scheme_hash = self.data.get_scheme_hash_by_entry_hash(entry_hash)
                if scheme_hash != None:
                    self.change_procedure(scheme_hash, "scheme")
            case 5:
                scheme_hash = self.data.get_scheme_hash_by_entry_hash(entry_hash)
                if scheme_hash != None:
                    self.delete_procedure(
                        scheme_hash, "scheme", self.data.get_scheme_head(scheme_hash)
                    )
        self.update_scr(hard_clear=True)

    # update methods
    def update_main_dimensions(self) -> None:
        y, x = self.get_main_dimensions()
        del self.window_dimensions[1]
        self.window_dimensions.insert(1, (y, x))
        del self.windows[1]
        self.windows.insert(
            1, newpad(self.window_dimensions[1][0], self.window_dimensions[1][1])
        )

    def update_contents(self, new_content: dict) -> None:
        self.content = new_content
        self.beautified_content = self.data.beautify_output(self.content)
        pointer_entry_hash = self.data.get_entry_hash_by_pointer_idx(self.pointer_idx)
        self.pointer_idx[1] = self.data.get_idx_of_entries()
        new_pointer_idx = self.data.get_pointer_idx_by_hash(pointer_entry_hash)
        self.pointer_idx[0] = (
            3
            if pointer_entry_hash == None or new_pointer_idx == None
            else new_pointer_idx
        )
        self.scroll_y, self.scroll_x = (
            self.pointer_idx[0] - self.window_dimensions[0][0] + 6,
            0,
        )

    def update_scr(self, start_y=1, start_x=0, hard_clear=False) -> None:
        """
        Updates the main screen, which displays the tables
        """
        if hard_clear:
            self.windows[1].erase()
        else:
            self.windows[1].clrtobot()
        if len(self.beautified_content.splitlines()) == 1:
            self.output_text_to_window(
                1, " " + self.beautified_content, start_y, start_x
            )
            return
        for idx, line in enumerate(self.beautified_content.splitlines()):
            if idx == self.pointer_idx[0] and self.pointer_idx[0] != None:
                line = " > " + line
                self.output_text_to_window(1, line, start_y, start_x, color_pair(2))
            else:
                line = "   " + line
                self.output_text_to_window(1, line, start_y, start_x)
            start_y += 1

    # Some getter methods
    def get_main_dimensions(self) -> tuple:
        try:
            max_dimensions = self.data.get_longest_entry_beautified()
        except ValueError:
            y, x = self.screen.getmaxyx()
            return y - 3, x
        if max_dimensions[0] + 2 > self.screen.getmaxyx()[0] - 3:
            y = max_dimensions[0] + 2
        else:
            y = self.screen.getmaxyx()[0] - 3
        if max_dimensions[1] + 2 > self.screen.getmaxyx()[1]:
            x = max_dimensions[1] + 2
        else:
            x = self.screen.getmaxyx()[1]
        return y, x

    def get_input(self) -> str:
        try:
            return self.screen.getkey()
        except:
            return None

    def get_coordinates_for_centered_text(self, text: str) -> tuple[int]:
        height, width = self.window_dimensions[0]
        start_y = height // 2
        start_x = (width // 2) - (len(text) // 2)
        return start_x, start_y - 1

    def get_coordinates_for_centered_pad(self, win: int) -> list[int]:
        """
        Function returns top-left and bottom-right corner of pad so that it is centered (if possible)
        Should only center pop-ups like the help one
        """
        start_coords = [2, 0]
        end_coords = list(self.main_end_y_x)
        if self.window_dimensions[0][0] - 3 > self.window_dimensions[win][0]:
            start_coords[0] = (
                (self.window_dimensions[0][0] - 1) // 2
                - self.window_dimensions[win][0] // 2
                + start_coords[0]
            )
            end_coords[0] = start_coords[0] + self.window_dimensions[win][0]
        if self.window_dimensions[0][1] > self.window_dimensions[win][1]:
            start_coords[1] = (
                self.window_dimensions[0][1] - 1
            ) // 2 - self.window_dimensions[win][1] // 2
            end_coords[1] = start_coords[1] + self.window_dimensions[win][1] - 1
        start_coords.extend(end_coords)
        return start_coords

    # Text manipulation and output methods
    def space_footer_text(self, footer_text: list) -> str:
        char_amount = len("".join(footer_text))
        width = (self.window_dimensions[0][1] - 1 - char_amount) // (
            len(footer_text) - 1
        )
        return "".join([arg + " " * width for arg in footer_text]).strip()

    def output_text_to_window(self, win: int, text: str, y=0, x=0, *args) -> None:
        error_msg = "Couldn't print string to window."
        attributes = A_NORMAL
        for attr in args:
            attributes |= attr
        try:
            self.windows[win].addstr(y, x, text, attributes)
        except Exception:
            logger.critical(error_msg)
        try:
            self.windows[win].refresh()
        except Exception:
            self.windows[win].box()
            start_x, start_y, end_x, end_y = self.get_coordinates_for_centered_pad(win)
            self.windows[win].refresh(
                self.scroll_y, self.scroll_x, start_x, start_y, end_x, end_y
            )


if __name__ == "__main__":
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from base64 import urlsafe_b64encode
    from Data_Manager import DataManager

    with open("..\\userdata\\test\\.salt", "rb") as f:
        salt = f.readline()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = urlsafe_b64encode(kdf.derive(b"g"))
    dm = DataManager("..\\userdata\\test\\test.data", key)
    renderer = Renderer(dm)
    # game
    player = OniManager.init_player("test")
