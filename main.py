import json
import re
import datetime
from pathlib import Path
from pprint import pprint
from typing import Dict

import phonenumbers
import requests

json_url = (
    "https://gist.githubusercontent.com/dmitry-naumenko/"
    "5a8afef9d94e9bcf9d91052dd65089ab/raw/"
    "c19ebdf3594e60db183cc2a9be9a7996a63dbf66/"
    "%25D0%25BE%25D0%25BA%25D0%25B2%25D1%258D%25D0%25B4.json"
)
matches = {}
CACHE_FILE = Path("okved_cache.json")


def normalize_russian_phone(phone_number: str) -> str | None:
    """
    Get phone string at any format and trying to convert to valid
    Russian phone number
    :param phone_number:
    :return: Correctly formatted phone number or None if phone number is invalid
    """
    if not isinstance(phone_number, str):
        return None

    extension_patterns = [
        r"\s*доб[:.]?\s*\d.*$",
        r"\s*ext[:.]?\s*\d.*$",
        r"\s*[хxХX]\s*\d.*$",
        r"\s*#\s*\d.*$",
        r"\s*\*\s*\d.*$",
        r"\s*доп[:.]?\s*\d.*$",
    ]

    cleaned = phone_number
    for pattern in extension_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    replacements = {
        "O": "0", "o": "0", "О": "0", "о": '0',
        "З": "3", "з": "3",
        "Ч": "4", "ч": "4",
        "b": "6", "ь": "6",
        "B": "8", "В": "8", "в": "8",
    }

    for char, digit in replacements.items():
        cleaned = cleaned.replace(char, digit)

    # Getting any digits from a string, ignoring all any other symbols
    digits = re.sub(r"\D", "", cleaned)

    if digits.startswith("007"):
        digits = "7" + digits[3:]
    elif digits.startswith("00"):
        return None

    if digits.startswith("8"):
        if len(digits) != 11:
            return None
        digits = "7" + digits[1:]
    elif digits.startswith("7"):
        if len(digits) != 11:
            return None
    elif len(digits) == 10:
        digits = "7" + digits
    else:
        return None

    if len(digits) == 11 and digits[0] == "7":
        return "+" + digits

    return None


def get_phone_number() -> str | None:
    """
    Get phone number at any format and trying to convert to valid
    :return: Phone number in Russian format or None if no correct phone number
    """
    raw_number = input("Input phone number: ")

    normalized = normalize_russian_phone(raw_number)
    if not normalized:
        print("Please enter a valid phone number")

        return

    phone_number = phonenumbers.parse(normalized)

    if phonenumbers.is_valid_number(phone_number):
        print("Correct phone number")

        return normalized

    else:
        print("Incorrect phone number")

    return


def check_cache_expired() -> bool:
    """
    Check if cache expired
    :return:
    """
    if not CACHE_FILE.exists():
        return True

    mtime = CACHE_FILE.stat().st_mtime
    mod_date = datetime.date.fromtimestamp(mtime)
    today = datetime.date.today()

    return mod_date < today


def get_okved_base() -> list[Dict]:
    """
    Getting remote json based list of all OKVEDs
    :return:
    """
    if check_cache_expired():
        raw_json = requests.get(
            url=json_url,
        )
        try:
            okved_base: list[Dict] = raw_json.json()
            with open(CACHE_FILE, "w") as f:
                json.dump(okved_base, f)
        except json.decoder.JSONDecodeError:
            return []
    else:
        with open(CACHE_FILE, "r") as f:
            okved_base = json.load(f)

    return okved_base


def tree_search(tree: list[Dict], target: str, fallback: bool = False) -> Dict:
    """
    Searching our json tree recursively
    :param tree: Tree to search
    :param target: Target string to search for
    :param fallback: Fallback searching mode
    :return:
    """
    for each in tree:
        if each.get("items"):
            # Searching recursively for items
            matches.update(tree_search(each["items"], target, fallback))

        # Searching in a base element, cos it is having a code also
        result: Dict[str, str] = linear_search(each, target, fallback)

        if result:
            # As long as codes are unique, we could use them directly as keys
            matches[result["code"]] = result["name"]

    return matches


def linear_search(
        current_items: Dict[str, str],
        target: str,
        fallback
) -> Dict[str, str]:
    """
    Searching the exact category, ignoring 'items' element
    :param current_items: Dict with current items
    :param target: Target string to search for
    :param fallback: Fallback searching mode
    :return:
    """
    result = {}
    raw_code = current_items["code"]
    code = "".join(raw_code.split("."))

    if not fallback:
        if code == target[-len(code):]:
            result = {
                "code": current_items["code"],
                "name": current_items["name"],
            }
    else:
        # In case of fallback, using Knuth-Morris-Pratt algorithm
        if kmp(code, target) > 0:
            result = {
                "code": current_items["code"],
                "name": current_items["name"],
            }

    return result


def prefix(s: str) -> list[int]:
    """
    Prefix function for KMP algorithm
    :param s: String to prefix
    :return:
    """
    v = [0]*len(s)
    for i in range(1, len(s)):
        k = v[i-1]
        while k > 0 and s[k] != s[i]:
            k = v[k-1]
        if s[k] == s[i]:
            k = k + 1
        v[i] = k
    return v


def kmp(s: str, t: str) -> int:
    """
    Knuth-Morris-Pratt algorithm
    :param s: String to search for
    :param t: String to search in
    :return: Starting index of searched string or -1
    """
    index = -1
    f = prefix(s)
    k = 0
    for i in range(len(t)):
        while k > 0 and s[k] != t[i]:
            k = f[k-1]
        if s[k] == t[i]:
            k = k + 1
        if k == len(s):
            index = i - len(s) + 1
            break
    return index


if __name__ == '__main__':
    phone = get_phone_number()
    if not phone:
        exit(-1)
    base = get_okved_base()
    simple_search = tree_search(base, phone)
    if not simple_search:
        print("No exact suffix matches found, doing fallback search")
        tree_search(base, phone, fallback=True)
    pprint(matches)
