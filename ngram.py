# random picks generated words, and re helps split text into words.
import random
import re

# our database module handles storing and looking up the counts.
import database


# clean the text the same way for both training and prediction.
def get_words(text):
    # lowercase everything, skip punctuation, and keep apostrophes inside words like don't.
    return re.findall(r"\b\w+(?:'\w+)*\b", text.lower())


# learn phrases from this text using only the selected n-gram size.
def train(session, text, n):
    # a phrase needs at least one word, so reject invalid sizes.
    if n < 1:
        raise ValueError("N must be at least 1.")

    # turn the input into a list of lowercase words.
    words = get_words(text)
    # there is nothing to learn if the text is shorter than one full phrase.
    if len(words) < n:
        # report that we processed zero phrases.
        return 0

    # slide a window of n words through the text, moving one word at a time.
    for i in range(len(words) - n + 1):
        # the first n - 1 words are the context; joining makes one searchable string.
        context = " ".join(words[i:i + n - 1])
        # the last word in this window is what we want to predict later.
        word = words[i + n - 1]
        # record this phrase or increase its existing count.
        database.save_ngram(session, n, context, word)

    # save all the training changes together.
    session.commit()
    # return the number of windows processed, including repeated phrases.
    return len(words) - n + 1


# look up possible next words using the end of the starting text.
def next_words(session, text, n):
    # a phrase needs at least one word, so reject invalid sizes.
    if n < 1:
        raise ValueError("N must be at least 1.")

    # turn the input into a list of lowercase words.
    words = get_words(text)
    # we need enough words to build the required context.
    if len(words) < n - 1:
        # an empty list means there are no suggestions available.
        return []

    # use the last n - 1 words; unigrams use an empty context and consider all saved words.
    context = " ".join(words[-(n - 1):]) if n > 1 else ""
    # the database returns (word, count) pairs with the highest counts first.
    return database.get_next_words(session, n, context)


# pick the single most common next word.
def predict(session, text, n):
    # get the matching words and their counts.
    choices = next_words(session, text, n)
    # only grab a result if the lookup found something.
    if choices:
        # the first row ranks highest, and its first item is the word.
        return choices[0][0]
    # none tells the caller that we have no matching prediction.
    return None


# return a few top suggestions; by default we show up to three.
def suggest(session, text, n, amount=3):
    # get the matching words and their counts.
    choices = next_words(session, text, n)
    # take the first amount of rows and keep just their words.
    return [row[0] for row in choices[:amount]]


# grow the starting text by choosing one next word at a time.
def generate(session, text, n, length):
    # turn the input into a list of lowercase words.
    words = get_words(text)
    # try to add as many new words as the caller requested.
    for i in range(length):
        # look up the next words again using the text we have built so far.
        choices = next_words(session, " ".join(words), n)
        # stop early when this context has never appeared in training.
        if not choices:
            break
        # extract the words we can choose from.
        possible_words = [row[0] for row in choices]
        # their counts become weights, so more common words are more likely.
        counts = [row[1] for row in choices]
        # pick one weighted random word; [0] unwraps the one-item result list.
        word = random.choices(possible_words, weights=counts)[0]
        # add the chosen word so it becomes part of the next lookup context.
        words.append(word)
    # join the starting words and generated words into one string.
    return " ".join(words)
