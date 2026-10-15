# PassGuard - Password Strength Checker, Breach Check and Generator

import getpass
import hashlib
import re
import secrets
import string

import requests


def check_strength(password):
    # Give the password a score and collect tips
    score = 0
    tips = []

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        tips.append("Use at least 8 characters (12 or more is better)")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        tips.append("Add a lowercase letter")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        tips.append("Add an uppercase letter")

    if re.search(r"\d", password):
        score += 1
    else:
        tips.append("Add a number")

    if re.search(r"[^\w\s]", password):
        score += 1
    else:
        tips.append("Add a special character like @ # $ !")

    if score <= 2:
        label = "Weak"
    elif score <= 4:
        label = "Moderate"
    else:
        label = "Strong"
    return label, tips


def breach_count(password):
    # Check how many times the password appeared in known data breaches.
    # Only the first 5 characters of the hash are sent online,
    # so the real password never leaves your computer.
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]
    response = requests.get(
        "https://api.pwnedpasswords.com/range/" + prefix, timeout=10
    )
    response.raise_for_status()
    for line in response.text.splitlines():
        hash_part, count = line.split(":")
        if hash_part == suffix:
            return int(count)
    return 0


def generate_password(length=16):
    # Make a random strong password
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(characters) for _ in range(length))


def main():
    print("=== PassGuard ===")
    print("1) Check a password")
    print("2) Generate a strong password")
    choice = input("Choose 1 or 2: ").strip()

    if choice == "2":
        print("Your new password:", generate_password())
        return

    password = getpass.getpass("Enter password (it will be hidden): ")
    label, tips = check_strength(password)
    print("\nStrength:", label)
    for tip in tips:
        print(" -", tip)

    try:
        count = breach_count(password)
        if count > 0:
            print(f"\nWARNING: This password was found in {count:,} data breaches. Do not use it!")
        else:
            print("\nGood news: this password was not found in known breaches.")
    except requests.RequestException:
        print("\nCould not check breaches (no internet connection?).")


if __name__ == "__main__":
    main()
