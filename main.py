import json
import logging
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")

# ── Paths & Setup ────────────────────────────────────────────────────────────

# Current script directory (base for relative paths)
CURR = Path(__file__).absolute().parent
logging.info(f"Current Directory: '{CURR}'.")

# Create base application directory if missing
BASE_DIR = CURR / "data"
BASE_DIR.mkdir(parents=True, exist_ok=True)
logging.info(f"Base Directory: '{BASE_DIR}'.")

# Path to users JSON file and users folder
USERS_FILE = BASE_DIR / "Users.json"
USERS_DIR = BASE_DIR / "Users"
USERS_DIR.mkdir(parents=True, exist_ok=True)

try:
    # Create empty users file if missing or empty
    if not USERS_FILE.exists() or USERS_FILE.stat().st_size == 0:
        USERS_FILE.write_text("[]", encoding="UTF-8")
        logging.info(f"Created a new File: '{USERS_FILE.name}'.")

    # Validate JSON format and load users into memory
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))
    logging.info(f"Loaded {len(users)} users from '{USERS_FILE.name}'.")

except json.JSONDecodeError:
    # Backup corrupted file with timestamp to avoid data loss
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = USERS_FILE.with_stem(f"Users_backup_{timestamp}")
    USERS_FILE.rename(backup)
    logging.info(f"Created Backup File: '{backup.name}'.")

    # Reset users file and initialize empty list
    USERS_FILE.write_text("[]", encoding="UTF-8")
    logging.info(f"Created a new File: '{USERS_FILE.name}'.")


# ── Models ───────────────────────────────────────────────────────────────────

@dataclass
class User:
    id: int
    user_name: str
    password: str
    logged_in: bool = False


class TaskStatus(Enum):
    New = 1
    Hold = 2
    Canceled = 3
    Done = 4


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str = TaskStatus.New.name


# ── Validator ────────────────────────────────────────────────────────────────

class Validator:
    @staticmethod
    def username(prompt: str) -> str:
        while True:
            data = input(prompt)
            if re.fullmatch(r'[A-Za-z0-9]{3,}', data):
                return data
            print("\n" + "=" * 40)
            print("        USERNAME REQUIREMENTS")
            print("=" * 40)
            print("• Minimum 3 characters")
            print("• English letters only (A-Z, a-z)")
            print("• Numbers allowed (0-9)")
            print("• No spaces or special characters")
            print("=" * 40 + "\n")

    @staticmethod
    def password(prompt: str) -> str:
        while True:
            data = input(prompt)
            if re.fullmatch(r'(?=.*[A-Za-z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{5,}', data):
                return data
            print("\n" + "=" * 40)
            print("        PASSWORD REQUIREMENTS")
            print("=" * 40)
            print("• Minimum 5 characters")
            print("• At least 1 letter (A-Z, a-z)")
            print("• At least 1 number (0-9)")
            print("• At least 1 special character (!@#$%^&*)")
            print("• No spaces allowed")
            print("=" * 40 + "\n")

    @staticmethod
    def get_next_id(items: list) -> int:
        # Works for both users and tasks
        if not items:
            return 1
        return max(i["id"] for i in items) + 1

    @staticmethod
    def is_logged_in(users: list) -> bool:
        if not users:
            return False
        return any(u["logged_in"] for u in users)


# ── Task Helpers ─────────────────────────────────────────────────────────────

def get_task_file(user_name: str) -> Path:
    # Returns the path to the user's Tasks.json file
    return USERS_DIR / user_name / "Tasks.json"


def load_tasks(user_name: str) -> list:
    task_file = get_task_file(user_name)
    # Create empty tasks file if missing or empty
    if not task_file.exists() or task_file.stat().st_size == 0:
        task_file.write_text("[]", encoding="UTF-8")
    return json.loads(task_file.read_text(encoding="UTF-8"))


def save_tasks(user_name: str, tasks: list):
    # Save tasks back to the user's Tasks.json file
    get_task_file(user_name).write_text(json.dumps(tasks, indent=2), encoding="UTF-8")


# ── Task Service ─────────────────────────────────────────────────────────────

def create_task(user_name: str):
    tasks = load_tasks(user_name)

    title = input("Enter Title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    description = input("Enter Description: ").strip()
    if not description:
        print("Description cannot be empty.")
        return

    print("\nSelect a status:")
    for s in TaskStatus:
        print(f"{s.value} - {s.name}")

    try:
        status_input = int(input("Enter status number: "))
        selected_status = TaskStatus(status_input).name
    except ValueError:
        print("Invalid status, defaulting to New.")
        selected_status = TaskStatus.New.name

    new_task = Task(
        id=Validator.get_next_id(tasks),
        title=title,
        description=description,
        status=selected_status
    )

    tasks.append(asdict(new_task))
    save_tasks(user_name, tasks)
    print(f"Task '{new_task.title}' created successfully.")


def list_tasks(user_name: str):
    tasks = load_tasks(user_name)
    if not tasks:
        print("No tasks found.")
        return

    print("\n" + "=" * 40)
    for t in tasks:
        print(f"[{t['id']}] {t['title']} - {t['status']}")
        print(f"     {t['description']}")
    print("=" * 40 + "\n")


def modify_task(user_name: str):
    tasks = load_tasks(user_name)

    try:
        task_id = int(input("Enter Task ID to modify: "))
    except ValueError:
        print("Invalid ID, please enter a number.")
        return

    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        print("Task not found.")
        return

    print("\nWhat would you like to modify?")
    print("1 - Title")
    print("2 - Description")
    print("3 - Status")
    choice = input("Enter choice: ")

    if choice == "1":
        title = input("Enter new Title: ").strip()
        if not title:
            print("Title cannot be empty.")
            return
        task["title"] = title
    elif choice == "2":
        description = input("Enter new Description: ").strip()
        if not description:
            print("Description cannot be empty.")
            return
        task["description"] = description
    elif choice == "3":
        for s in TaskStatus:
            print(f"{s.value} - {s.name}")
        try:
            task["status"] = TaskStatus(int(input("Enter status number: "))).name
        except ValueError:
            print("Invalid status.")
            return
    else:
        print("Invalid choice.")
        return

    save_tasks(user_name, tasks)
    print("Task updated successfully.")


def delete_task(user_name: str):
    tasks = load_tasks(user_name)

    try:
        task_id = int(input("Enter Task ID to delete: "))
    except ValueError:
        print("Invalid ID, please enter a number.")
        return

    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        print("Task not found.")
        return

    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(user_name, tasks)
    print(f"Task '{task['title']}' deleted successfully.")


# ── User Service ─────────────────────────────────────────────────────────────

def get_logged_in_user(users: list) -> dict | None:
    # Helper to get the current logged in user dict
    return next((u for u in users if u["logged_in"]), None)


def create_user():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))

    user_name = Validator.username("Enter a Username: ")

    # Check username already exists
    if any(u["user_name"] == user_name for u in users):
        print("Username already taken.")
        return

    data = User(
        id=Validator.get_next_id(users),
        user_name=user_name,
        password=Validator.password("Enter a Password: "),
    )

    users.append(asdict(data))
    USERS_FILE.write_text(json.dumps(users, indent=4), encoding="UTF-8")
    logging.info(f"User '{data.user_name}' created successfully.")

    # Create user folder and empty Tasks.json
    user_path = USERS_DIR / data.user_name
    user_path.mkdir(parents=True, exist_ok=True)
    task_file = user_path / "Tasks.json"
    task_file.write_text("[]", encoding="UTF-8")
    logging.info(f"Created folder and Tasks.json for '{data.user_name}'.")


def login_user():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))

    if Validator.is_logged_in(users):
        print("There is a user already logged in.")
        return False

    user_data = Validator.username("Enter your Username: ")
    pass_data = Validator.password("Enter your Password: ")

    user = next((u for u in users if u["user_name"] == user_data and u["password"] == pass_data), None)

    if not user:
        print("Invalid username or password.")
        return False

    user["logged_in"] = True
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="UTF-8")
    print(f"Welcome back, {user['user_name']}!")
    return True


def logout_user():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))

    if not Validator.is_logged_in(users):
        print("No user is logged in.")
        return False

    user = get_logged_in_user(users)
    user["logged_in"] = False
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="UTF-8")
    print(f"Goodbye, {user['user_name']}!")
    return True


def modify_user():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))

    if not Validator.is_logged_in(users):
        print("User must be logged in.")
        return

    user_password = Validator.password("Enter your current Password: ")
    user = next((u for u in users if u["logged_in"] and u["password"] == user_password), None)

    if not user:
        print("Incorrect password.")
        return

    user["password"] = Validator.password("Enter a new Password: ")
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="UTF-8")
    print("Password updated successfully.")


def delete_user():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))

    if not Validator.is_logged_in(users):
        print("User must be logged in.")
        return

    user_password = Validator.password("Enter your Password to confirm deletion: ")
    user = next((u for u in users if u["logged_in"] and u["password"] == user_password), None)

    if not user:
        print("Incorrect password.")
        return

    users = [u for u in users if u != user]
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="UTF-8")
    print(f"User '{user['user_name']}' deleted successfully.")


def list_users():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))
    if not users:
        print("No users found.")
        return
    print("\n" + "=" * 40)
    for u in users:
        status = "logged in" if u["logged_in"] else "offline"
        print(f"[{u['id']}] {u['user_name']} - {status}")
    print("=" * 40 + "\n")


# ── Task operations (requires logged in user) ────────────────────────────────

def user_create_task():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))
    if not Validator.is_logged_in(users):
        print("User must be logged in.")
        return
    user = get_logged_in_user(users)
    create_task(user["user_name"])


def user_list_tasks():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))
    if not Validator.is_logged_in(users):
        print("User must be logged in.")
        return
    user = get_logged_in_user(users)
    list_tasks(user["user_name"])


def user_modify_task():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))
    if not Validator.is_logged_in(users):
        print("User must be logged in.")
        return
    user = get_logged_in_user(users)
    modify_task(user["user_name"])


def user_delete_task():
    users = json.loads(USERS_FILE.read_text(encoding="UTF-8"))
    if not Validator.is_logged_in(users):
        print("User must be logged in.")
        return
    user = get_logged_in_user(users)
    delete_task(user["user_name"])


# ── Main Menu ────────────────────────────────────────────────────────────────

def print_menu():
    print("\n" + "=" * 40)
    print("           TODO APP")
    print("=" * 40)
    print("  --- User ---")
    print("  1  - Register")
    print("  2  - Login")
    print("  3  - Logout")
    print("  4  - Modify Password")
    print("  5  - Delete Account")
    print("  6  - List Users")
    print("  --- Tasks ---")
    print("  7  - Create Task")
    print("  8  - List Tasks")
    print("  9  - Modify Task")
    print("  10 - Delete Task")
    print("  --- ---")
    print("  0  - Exit")
    print("=" * 40)


def main():
    options = {
        "1": create_user,
        "2": login_user,
        "3": logout_user,
        "4": modify_user,
        "5": delete_user,
        "6": list_users,
        "7": user_create_task,
        "8": user_list_tasks,
        "9": user_modify_task,
        "10": user_delete_task,
    }

    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in options:
            options[choice]()
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()