from os import get_terminal_size

class Renderer:
    def __init__(self):
        self.terminal_size = get_terminal_size()

    def __str__(self):
        return f"Terminal width: {self.terminal_size.columns}, heigth: {self.terminal_size.lines}"

if __name__ == "__main__":
    renderer = Renderer()
    print(renderer)
