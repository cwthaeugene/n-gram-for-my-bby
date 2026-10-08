# Simple n-gram project

A beginner-friendly Python project. It uses SQLAlchemy with SQLite to save word
n-grams and their counts.

Run it with Python 3:

```sh
python3 -m pip install -r requirements.txt
python3 main.py
```

Choose an option from the menu. The program creates `ngrams.db` in your current
folder, and saved training data is available the next time you run it.

## What is an n-gram?

An n-gram is a group of n words. For example, with n = 2, the text
`i like cats i like dogs` gives these pairs:

```text
i like -> 2
like cats -> 1
cats i -> 1
like dogs -> 1
```

Suggesting after `i` returns up to three of the most frequent next words.
Generating text randomly chooses a next word using the saved counts as weights.
It stops when there is no matching next word or it reaches the requested number
of new words.

## Project files

- `main.py`: menu, user input, and printing results.
- `ngram.py`: splitting text into words, training, prediction, and generation.
- `database.py`: SQLAlchemy model, SQLite connection, saving, reading, and deleting.
- `requirements.txt`: contains the SQLAlchemy dependency.
- `sample.txt`: small training example. Choose option 3 and enter `sample.txt`.
- `.gitignore`: keeps generated database and Python cache files out of Git.

The default n is 2. Each n has its own saved counts. For n greater than 1,
prediction and generation need at least n - 1 starting words. For n = 1, you can
leave the starting text empty. Training again adds to the existing counts.
This simple program treats the input as one word sequence, including across
sentence boundaries.

## Database schema

SQLAlchemy creates one table named `ngrams`:

| Column | Type | Meaning |
| --- | --- | --- |
| `n` | integer | Size of the complete n-gram |
| `context` | text | The first `n - 1` words |
| `word` | text | The final word, which the program predicts |
| `count` | integer | Number of times this n-gram was found |

The combined primary key is (`n`, `context`, `word`). This means one n-gram has
one row, and training it again increases its `count` instead of creating a copy.

Here is how different n-gram sizes fit into the same table:

| Kind | n | Full n-gram | context | word |
| --- | ---: | --- | --- | --- |
| unigram | 1 | `cats` | empty string | `cats` |
| bigram | 2 | `i like` | `i` | `like` |
| trigram | 3 | `i like cats` | `i like` | `cats` |
| 4-gram | 4 | `i really like cats` | `i really like` | `cats` |

For a bigram prediction, the program looks up one context word. For a trigram it
looks up two context words, and for a 4-gram it looks up three. For example, if
`n = 3` and the starting text is `i like`, the program finds all rows whose
context is `i like`, then chooses a value from the `word` column. The row with
the three rows with the highest `count` are shown as suggestions. Generation
uses the counts as random weights, adds the chosen word, and repeats with the new
context.
