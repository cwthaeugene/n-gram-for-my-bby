import random
import re

import database


def get_words(text):
    return re.findall(r"\b\w+(?:'\w+)*\b", text.lower())


def train(session, text, n):
    if n < 1:
        raise ValueError("N must be at least 1.")

    words = get_words(text)
    if len(words) < n:
        return 0

    for i in range(len(words) - n + 1):
        context = " ".join(words[i:i + n - 1])
        word = words[i + n - 1]
        database.save_ngram(session, n, context, word)

    session.commit()
    return len(words) - n + 1


def next_words(session, text, n):
    if n < 1:
        raise ValueError("N must be at least 1.")

    words = get_words(text)
    if len(words) < n - 1:
        return []

    context = " ".join(words[-(n - 1):]) if n > 1 else ""
    return database.get_next_words(session, n, context)


def predict(session, text, n):
    choices = next_words(session, text, n)
    if choices:
        return choices[0][0]
    return None


def suggest(session, text, n, amount=3):
    choices = next_words(session, text, n)
    return [row[0] for row in choices[:amount]]


def generate(session, text, n, length):
    words = get_words(text)
    for i in range(length):
        choices = next_words(session, " ".join(words), n)
        if not choices:
            break
        possible_words = [row[0] for row in choices]
        counts = [row[1] for row in choices]
        word = random.choices(possible_words, weights=counts)[0]
        words.append(word)
    return " ".join(words)
