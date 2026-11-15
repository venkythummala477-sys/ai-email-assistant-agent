
SUPPORTED_CATEGORIES = [
    "Work",
    "Personal",
    "Urgent"
]


def validate_email_draft(subject, body):
    if not isinstance(subject, str):
        return False

    if not isinstance(body, str):
        return False

    return bool(subject.strip() and body.strip())


def validate_category(category):
    return category in SUPPORTED_CATEGORIES


def validate_input(user_text):
    return isinstance(user_text, str) and bool(user_text.strip())
