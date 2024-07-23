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
from re import match
from textwrap import wrap
from os.path import split, join
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
    INSTRUCTIONS,
    CONSTRAINTS,
    NAME_REGEX,
    ASCII_ONI_LOGO,
)
from time import sleep
from logging import getLogger

logger = getLogger(__name__)


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
    def get_input_checkboxes(self, options: list, message: str) -> list:
        message = self.make_message_fit_width(message, self.dimensions[1] - 2)
        height_of_msg = len(message.splitlines()) + 1
        self.win.addstr(1, 0, message)
        self.win.box()
        self.win.refresh()

        scroll_y, scroll_x = 0, 0
        pad = newpad(len(options) + 1, max(len(i) for i in options) + 5)

        selected = [False] * len(options)
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

    def get_input_string(self, p_message: str, p_regex=None) -> str:
        WRONG_INPUT_MESSAGE = "The provided input doesn't match the wanted pattern.\n\n"
        regex = r"[\S\s]*" if p_regex == None else p_regex
        message = self.make_message_fit_width(p_message, self.dimensions[1] - 2)
        height_of_msg = len(message.splitlines()) + 1
        message_is_updated = False
        while True:
            # Init new window and change some settings
            self.win.erase()
            echo()
            curs_set(1)

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
        pass

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
                    [str(i) for i in schemes], INSTRUCTIONS["add"]
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
        self.update_scr()

    def change_procedure(self, hash: str, type_of_data_to_change: str) -> None:
        match type_of_data_to_change:
            case "entry":
                pass
            case "scheme":
                pass

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
                        "Please provide the masterpassword to delete the scheme and all its entries. [Wrong input -> Back to entries]"
                    )
                    folder_path_cross_platform = split(self.data.path_to_file)[0]
                    with open(join(folder_path_cross_platform, ".salt"), "rb") as f:
                        kdf = get_hashing_obj(f.readline())
                    try:
                        key = convert_pw_to_key(kdf, password)
                        DataManager(self.data.path_to_file, key)
                        self.data.delete_scheme(hash)
                    except:
                        return
        self.update_contents(self.data.get_all_entries())

    def filter_procedure(self) -> None:
        pass

    def order_procedure(self) -> None:
        pass

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
                    folder_path_cross_platform = split(self.data.path_to_file)[0]
                    with open(join(folder_path_cross_platform, ".salt"), "rb") as f:
                        kdf = get_hashing_obj(f.readline())
                    try:
                        key = convert_pw_to_key(kdf, password.decode())
                        DataManager(self.data.path_to_file, key)
                        curs_set(0)
                        break
                    except:
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
                "Change data of entry",
                "Delete entry",
                "Rename columns of scheme",
                "Delete scheme",
            ],
            "What do you want to do?",
        )
        match choice:
            case 1:
                self.change_procedure(entry_hash, "entry")
            case 2:
                self.delete_procedure(
                    entry_hash,
                    "entry",
                    self.beautified_content.splitlines()[self.pointer_idx[0]],
                )
            case 3:
                scheme_hash = self.data.get_scheme_hash_by_entry_hash(entry_hash)
                if scheme_hash != None:
                    self.change_procedure(scheme_hash, "scheme")
            case 4:
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
        self.pointer_idx[1] = self.data.get_idx_of_entries()
        pointer_entry_hash = self.data.get_entry_hash_by_pointer_idx(self.pointer_idx)
        self.pointer_idx[0] = (
            3
            if pointer_entry_hash == None
            else self.data.get_pointer_idx_by_hash(
                pointer_entry_hash, self.pointer_idx[1]
            )
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
