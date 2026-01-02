from random import randint

BOX_WIDTH = 40

SETTINGS: dict[str, int] = {
    "WIN_COND": randint(1, 10),
    "MAX_NUMBER_OF_TRIES": 5,
    "GAMES_WON": 0,
    "GAMES_LOST": 0,
}

def print_box(lines: list[str], align: str = "center") -> None:
    """Prints a box. align='center' for centered text, 'left' for left-aligned."""
    print("╔" + "═" * BOX_WIDTH + "╗")
    for line in lines:
        line_len = len(line)
        if line_len > BOX_WIDTH:
            line = line[:BOX_WIDTH]  # חותך אם ארוך מדי
            line_len = BOX_WIDTH
        if align == "center":
            left_pad = (BOX_WIDTH - line_len) // 2
            right_pad = BOX_WIDTH - line_len - left_pad
        elif align == "left":
            left_pad = 0
            right_pad = BOX_WIDTH - line_len
        else:
            left_pad = 0
            right_pad = 0
        print(f"║{' ' * left_pad}{line}{' ' * right_pad}║")
    print("╚" + "═" * BOX_WIDTH + "╝")


def user_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print_box(["VALUE ERROR -> MUST BE AN INTEGER."])


def game_loop() -> bool:
    NUMBER_OF_TRIES = 0
    while NUMBER_OF_TRIES < SETTINGS["MAX_NUMBER_OF_TRIES"]:
        tries_left = SETTINGS["MAX_NUMBER_OF_TRIES"] - NUMBER_OF_TRIES
        print_box([
            "GAME STARTED",
            f"TRIES LEFT: {tries_left}"
        ])

        val = user_input("GUESS: ")

        if val == SETTINGS["WIN_COND"]:
            print_box(["CONGRATULATIONS!"])
            return True
        else:
            NUMBER_OF_TRIES += 1
            print_box(["WRONG. TRY AGAIN."])

    print_box(["GAME OVER"])
    return False


def score_board(result: bool) -> None:
    SETTINGS["GAMES_WON" if result else "GAMES_LOST"] += 1


def change_difficulty() -> None:
    while True:
        print_box([
            "CHANGE DIFFICULTY",
            "1. Easy",
            "2. Medium",
            "3. Hard"
        ])

        val = user_input("CHOOSE: ")

        if val == 1:
            SETTINGS["WIN_COND"] = randint(1, 10)
            SETTINGS["MAX_NUMBER_OF_TRIES"] = 5
            break
        elif val == 2:
            SETTINGS["WIN_COND"] = randint(1, 15)
            SETTINGS["MAX_NUMBER_OF_TRIES"] = 4
            break
        elif val == 3:
            SETTINGS["WIN_COND"] = randint(1, 20)
            SETTINGS["MAX_NUMBER_OF_TRIES"] = 3
            break
        else:
            print_box(["WRONG INPUT. TRY AGAIN."])


def start_game() -> None:
    print_box(["WELCOME TO GUESS GAME"])
    menu_items = ["START GAME", "CHANGE DIFFICULTY", "SCORE BOARD", "EXIT"]

    while True:
        lines = ["MENU:"]
        lines += [f"{i}. {item}" for i, item in enumerate(menu_items, 1)]
        print_box(lines)

        val = user_input("CHOOSE: ")
        if val == 1:
            result = game_loop()
            score_board(result)
        elif val == 2:
            change_difficulty()
        elif val == 3:
            print_box([
                f"TIMES WON : {SETTINGS['GAMES_WON']}",
                f"TIMES LOST: {SETTINGS['GAMES_LOST']}"
            ])
        elif val == 4:
            break
        else:
            print_box(["INVALID INPUT"])


if __name__ == "__main__":
    start_game()
