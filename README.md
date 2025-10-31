# Russian Phone Number OKVED Matcher

This utility takes a Russian phone number in any common format, normalizes it to the international E.164 format (`+7XXXXXXXXXX`), and uses the digit sequence to search for matching entries in the official Russian **OKVED** (All-Russian Classifier of Types of Economic Activities) database.

The search logic attempts to find OKVED codes that **suffix-match** the phone number digits. If no exact match is found, a fallback search using the **Knuth-Morris-Pratt (KMP)** substring algorithm is performed.

> **Note**: This is an experimental or demonstrative tool. The semantic connection between phone numbers and OKVED codes is not standard—it's a creative matching approach based on digit patterns.

---

## ✨ Features

- Accepts Russian phone numbers in flexible formats (e.g., `8 (999) 123-45-67`, `+79991234567`, `9991234567`).
- Normalizes input to `+7XXXXXXXXXX` format.
- Validates phone numbers using the robust [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers) library.
- Downloads the full OKVED classification from a remote JSON source.
- Performs two-stage search:
  1. **Exact suffix match**: OKVED code (with dots removed) must match the *end* of the phone number.
  2. **Fallback substring match**: Uses KMP algorithm to find partial matches if no exact match exists.
- Outputs all matching OKVED codes and their descriptions.

---

## 🚀 Usage

1. Clone or download the repository.
2. Ensure you have Python 3.10+ installed.
3. Install dependencies:

   ```bash
   pip install phonenumbers requests****