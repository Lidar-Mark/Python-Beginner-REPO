

MY_LIST = []

def check_content(mylist) -> None:
    for i, item in enumerate(mylist, +1):
        print(i, item.capitalize())


def user_input(prompt: str) -> str:
    return input(prompt).lower()


def add_item(prompt: str) -> None:
    while True:
        print("Exit Add Item Type 'Back'")
        val = user_input(prompt)
        if val == "back":
            break
        else:
            MY_LIST.append(val)


def remove_item(prompt: str) -> None:
    val = user_input(prompt)
    try:
        MY_LIST.remove(val)
    except ValueError:
        print("No Item Found")

def pop_last_item() -> None:
    MY_LIST.pop()


actions = {
    "add":    lambda: add_item("Add: "),
    "remove": lambda: remove_item("Remove: "),
    "list":   lambda: check_content(MY_LIST),
    "pop":    lambda: pop_last_item(),
    "exit":   None,
}


def list_commands() -> None:
    while True:
        for i, value in enumerate(actions, 1):
            print(f"{i}. {value.capitalize()}")

        val = user_input("Choose: ")
        action = actions.get(val)

        if action is None:
            if val == "exit":
                break
            print("Invalid command.")
        else:
            action()

if __name__ == "__main__":
    list_commands()
