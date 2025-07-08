import json
import os
import random
import smtplib

USERS_FILE = "users.json"
RESET_CODES_FILE = "reset_codes.json"

# === Load & Save Users ===
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

# === Register & Login ===
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

# === Forgot Password Utilities ===
def send_reset_code(email):
    users = load_users()
    if email not in users:
        return False, "Email not found."

    code = str(random.randint(100000, 999999))
    reset_codes = load_reset_codes()
    reset_codes[email] = code
    save_reset_codes(reset_codes)

    # Simulate sending email — you should replace this with real email logic
    print(f"[DEBUG] Sending code to {email}: {code}")

    return True, "Reset code sent successfully."

def verify_reset_code(email, code):
    reset_codes = load_reset_codes()
    if reset_codes.get(email) == code:
        return True
    return False

def update_user_password(email, new_password):
    users = load_users()
    if email not in users:
        return False, "User not found."
    users[email]["password"] = new_password
    save_users(users)

    # Remove reset code after successful reset
    reset_codes = load_reset_codes()
    if email in reset_codes:
        del reset_codes[email]
        save_reset_codes(reset_codes)

    return True, "Password updated successfully."

# === Reset Code File Helpers ===
def load_reset_codes():
    if not os.path.exists(RESET_CODES_FILE):
        with open(RESET_CODES_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(RESET_CODES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_reset_codes(codes):
    with open(RESET_CODES_FILE, "w") as f:
        json.dump(codes, f, indent=4)
