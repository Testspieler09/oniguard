from curses import newwin, newpad, initscr, init_pair, color_pair, start_color, curs_set, cbreak, noecho, nocbreak, echo, endwin, COLOR_BLACK, COLOR_BLUE, COLOR_GREEN, COLOR_RED, A_UNDERLINE, A_NORMAL
from textwrap import wrap
from os import get_terminal_size
from assets import HELP_MESSAGE, FOOTER_TEXT
from time import sleep
from logging import getLogger

logger = getLogger(__name__)

class PopUp:
    def __init__(self, screen: object) -> None:
        y, x = screen.getmaxyx()
        self.dimensions = (y-3, x)
        self.win = newwin(y-3, x, 2, 0)
        self.screen = screen
        self.screen.refresh()

        # Settings
        curs_set(0)
        cbreak()
        noecho()
        self.screen.nodelay(False)

    def kill_pop_up(self) -> None:
        self.screen.nodelay(True)
        del self.win

    # Read input
    def get_input_checkboxes(self, options: list, message: str) -> list:
        message = self.make_message_fit_width(message, self.dimensions[1]-2)
        height_of_msg = len(message.splitlines())+1
        self.win.addstr(1, 1, message)
        self.win.box()
        self.win.refresh()

        scroll_y, scroll_x = 0, 0
        pad = newpad(len(options)+1, max(len(i) for i in options)+5)

        selected = [False] * len(options)
        current_option = 0

        def display_menu():
            for idx, option in enumerate(options):
                if idx == current_option: pad.attron(color_pair(2))
                checkbox = "[X]" if selected[idx] else "[ ]"
                pad.addstr(idx, 0, checkbox)
                pad.addstr(idx, 4, option)
                if idx == current_option: pad.attroff(color_pair(2))
            bottom_right_y, bottom_right_x = height_of_msg+pad.getmaxyx()[0]+1, pad.getmaxyx()[1]+1
            if height_of_msg+pad.getmaxyx()[0]+1 >= self.win.getmaxyx()[0]:
                bottom_right_y = self.win.getmaxyx()[0]
            if pad.getmaxyx()[1] >= self.win.getmaxyx()[1]-1:
                bottom_right_x = self.win.getmaxyx()[1]-2
            pad.refresh(scroll_y, scroll_x, height_of_msg+3, 1, bottom_right_y, bottom_right_x)

        while True:
            display_menu()
            key = self.screen.getkey()

            if key == "KEY_UP" and current_option > 0:
                current_option -= 1
                if current_option < scroll_y: scroll_y -= 1
            elif key == "KEY_DOWN" and current_option < len(options) - 1:
                current_option += 1
                if current_option >= scroll_y + (self.win.getmaxyx()[0] - height_of_msg - 2): scroll_y += 1
            elif key == "KEY_LEFT" and scroll_x > 0:
                scroll_x -= 1
            elif key == "KEY_RIGHT" and scroll_x < pad.getmaxyx()[1] - self.win.getmaxyx()[1] + 2:
                scroll_x += 1
            elif key == ' ':
                selected[current_option] = not selected[current_option]
            elif key == '\n':
                break

        self.kill_pop_up()
        return [opt for idx, opt in enumerate(options) if selected[idx]]

    def get_input_radio_btn(self, options: list, message: str) -> str:
        pass

    # Helper methods
    def make_message_fit_width(self, message: str, width: int) -> str:
        paras = ["dbc71b7fc9e348da85ae5e095bd80855" if i == "" else i for i in message.splitlines()] # using a uuid4 here to preserve the custom linespacing via `\n`
        lines = [" "+j for i in paras for j in wrap(i,width)]
        return "\n".join(["" if i==" dbc71b7fc9e348da85ae5e095bd80855" else i for i in lines])

class Renderer:
    def __init__(self):
        self.screen = initscr()
        self.running = True

        # DETERMINE THE SIZE OF THE MAIN PAD
        y, x = self.get_main_dimensions()

        help_lines = HELP_MESSAGE.split("\n")
        self.window_dimensions = [self.screen.getmaxyx(),
                                  (y, x),
                                  (len(help_lines)+1, max(len(line) for line in help_lines)+1)]
        self.windows = [self.screen, # footer
                        newpad(self.window_dimensions[1][0], self.window_dimensions[1][1]), # main
                        newpad(self.window_dimensions[2][0], self.window_dimensions[2][1])] # help message popup

        self.scroll_y, self.scroll_x = 0, 0
        self.last_scroll_pos_main_scr = (0, 0)
        self.main_start_x_y = (2, 0)
        self.main_end_x_y = (self.window_dimensions[0][0]-2, self.window_dimensions[0][1]-1)
        self.active_window = 1

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
        self.output_text_to_window(0, self.space_footer_text(FOOTER_TEXT), self.window_dimensions[0][0]-1, 0)
        y, _ = self.get_coordinates_for_centered_text(headline)
        self.output_text_to_window(0, headline, 1, y, A_UNDERLINE)
        # self.beautify_output()
        while self.running:
            sleep(0.01) # so program doesn't use 100% cpu
            key=self.get_input()
            self.event_handler(key)

    def scroll_pad(self, pad_id: int) -> None:
        start_x, start_y, end_x, end_y = self.get_coordinates_for_centered_pad(pad_id)
        self.windows[pad_id].refresh(self.scroll_x, self.scroll_y, start_x, start_y, end_x, end_y)

    def event_handler(self, event: str) -> None:
        match event:
            # Scroll operations
            case "KEY_DOWN":
                if abs(self.scroll_x - self.window_dimensions[self.active_window][0]-3) <= self.window_dimensions[0][0]:
                    return
                self.scroll_x += 1
                self.scroll_pad(self.active_window)
            case "KEY_UP":
                self.scroll_x -= 1
                if self.scroll_x <= 0:
                    self.scroll_x = 0
                self.scroll_pad(self.active_window)
            case "KEY_RIGHT":
                if abs(self.scroll_y - self.window_dimensions[self.active_window][1]) <= self.window_dimensions[0][1]:
                    return
                self.scroll_y += 1
                self.scroll_pad(self.active_window)
            case "KEY_LEFT":
                self.scroll_y -= 1
                if self.scroll_y <= 0:
                    self.scroll_y = 0
                self.scroll_pad(self.active_window)
            # Main operations
            case "S" | "s":
                self.search_procedure()
            case "A" | "a":
                self.add_procedure()
            case "C" | "c":
                self.change_procedure()
            case "F" | "f":
                self.filter_procedure()
            case "D" | "d":
                self.delete_procedure()
            # Default operations
            case "H" | "h":
                if self.active_window == 2:
                    self.active_window = 1
                    self.scroll_x, self.scroll_y = self.last_scroll_pos_main_scr
                    self.windows[1].refresh(self.scroll_x, self.scroll_y,
                                            self.main_start_x_y[0], self.main_start_x_y[1],
                                            self.main_end_x_y[0], self.main_end_x_y[1])
                else:
                    self.active_window = 2
                    self.last_scroll_pos_main_scr = (self.scroll_x, self.scroll_y)
                    self.scroll_x, self.scroll_y = 0, 0
                    self.output_text_to_window(2, HELP_MESSAGE, 0, 0)
            case "Q" | "q":
                self.kill_scr()
            case "KEY_RESIZE":
                self.kill_scr()
                ScreenManager()

    # Implementations of the main procedures
    def search_procedure(self) -> None:
        popup = PopUp(self.screen)
        input = popup.get_input_checkboxes(["Python", "Java", "Go", "C", "C++"], "What programming languages do you use?")
        print(input)

    def add_procedure(self) -> None:
        pass

    def change_procedure(self) -> None:
        pass

    def filter_procedure(self) -> None:
        pass

    def delete_procedure(self) -> None:
        pass

    # Some getter methods
    def get_main_dimensions(self) -> tuple:
        # try:
        #     max_dimensions = self.data.get_longest_entry_beautified()
        # except ValueError:
        y, x = self.screen.getmaxyx()
        return y-3, x
        if max_dimensions[0]+2 > self.screen.getmaxyx()[0]-3:
            y = max_dimensions[0]+2
        else:
            y = self.screen.getmaxyx()[0]-3
        if max_dimensions[1]+2 > self.screen.getmaxyx()[1]:
            x = max_dimensions[1]+2
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
        return start_x, start_y-1

    def get_coordinates_for_centered_pad(self, win: int) -> list[int]:
        """
        Function returns top-left and bottom-right corner of pad so that it is centered (if possible)
        Should only center pop-ups like the help one
        """
        start_coords = [2, 0]
        end_coords = list(self.main_end_x_y)
        if self.window_dimensions[0][0]-3 > self.window_dimensions[win][0]:
            start_coords[0] = (self.window_dimensions[0][0]-1)//2 - self.window_dimensions[win][0]//2 + start_coords[0]
            end_coords[0] = start_coords[0] + self.window_dimensions[win][0]
        if self.window_dimensions[0][1] > self.window_dimensions[win][1]:
            start_coords[1] = (self.window_dimensions[0][1]-1)//2-self.window_dimensions[win][1]//2
            end_coords[1] = start_coords[1] + self.window_dimensions[win][1] - 1
        start_coords.extend(end_coords)
        return start_coords

    # Text manipulation and output methods
    def space_footer_text(self, footer_text: list) -> str:
        char_amount = len("".join(footer_text))
        width = (self.window_dimensions[0][1]-1 - char_amount) // (len(footer_text) - 1)
        return "".join([arg + " "*width for arg in footer_text]).strip()

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
            self.windows[win].refresh(self.scroll_x, self.scroll_y, start_x, start_y, end_x, end_y)

if __name__ == "__main__":
    renderer = Renderer()
    print(renderer)
