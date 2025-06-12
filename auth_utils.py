# auth_utils.py

import json
import os

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(first_name, last_name, email, password):
    users = load_users()

    if email in users:
        return False, "Email already exists!"

    users[email] = {
        "first_name": first_name,
        "last_name": last_name,
        "password": password
    }

    save_users(users)
    return True, "Registration successful!"

def login_user(email, password):
    users = load_users()

    if email in users and users[email]["password"] == password:
        first_name = users[email].get("first_name", "User")
        return True, f"Welcome back, {first_name}!", first_name
    return False, "Invalid email or password.", None
