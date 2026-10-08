# this file runs the menu and connects user choices to the other modules.
import database
# these functions handle learning, suggestions, and text generation.
from ngram import train, suggest, generate
# catch database errors so the menu can keep running after a failed action.
from sqlalchemy.exc import SQLAlchemyError


# display the phrases saved for the selected n-gram size.
def show_ngrams(session, n):
    # fetch the context, final word, and count for each saved phrase.
    rows = database.get_ngrams(session, n)
    # let the user know when this size has no training data yet.
    if not rows:
        print("No saved n-grams yet.")
    # unpack each row into its three values.
    for context, word, count in rows:
        # rebuild the phrase; strip removes the extra space for unigrams.
        print((context + " " + word).strip(), "->", count)


# start the database session and keep the menu running until the user exits.
def main():
    # open the default ngrams.db file, creating it if needed.
    session = database.connect()
    # start with bigrams, which use one word to predict the next.
    n = 2
    # the outer try lets us handle an interrupted menu and always close the session.
    try:
        # repeat the menu after each action until we hit a break.
        while True:
            # show the current size and the available menu options.
            print("\nN-gram project (n = " + str(n) + ")")
            print("1. Change n")
            print("2. Train with text")
            print("3. Train with a text file")
            print("4. Show saved n-grams")
            print("5. Suggest next words")
            print("6. Generate text")
            print("7. Clear data for current n")
            print("0. Exit")
            # read the menu choice as text and remove surrounding whitespace.
            choice = input("Choose: ").strip()

            # handle errors from one action without ending the whole program.
            try:
                # change the size used by future training and lookups.
                if choice == "1":
                    # convert the input to an integer; invalid text raises a value error.
                    new_n = int(input("Enter n (1 or more): "))
                    # only positive n-gram sizes make sense.
                    if new_n < 1:
                        print("N must be at least 1.")
                    else:
                        # changing n selects a different set of rows; it does not train new data.
                        n = new_n
                # learn from text typed directly into the terminal.
                elif choice == "2":
                    text = input("Training text: ")
                    # train saves the counts and returns how many phrase windows it processed.
                    print("Trained on", train(session, text, n), "n-grams.")
                # learn from the contents of a text file.
                elif choice == "3":
                    path = input("Text file path: ")
                    # read the file as utf-8; with closes it automatically when we are done.
                    with open(path, "r", encoding="utf-8") as file:
                        # load the full file contents as our training text.
                        text = file.read()
                    # train saves the counts and returns how many phrase windows it processed.
                    print("Trained on", train(session, text, n), "n-grams.")
                # show saved phrases and counts for the current size.
                elif choice == "4":
                    show_ngrams(session, n)
                # suggest up to three next words for the starting text.
                elif choice == "5":
                    text = input("Starting text: ")
                    # the suggestions come back in order of frequency.
                    words = suggest(session, text, n, 3)
                    # print matching suggestions if we have any.
                    if words:
                        # join the suggestions with commas so they are easy to read.
                        print("Suggestions:", ", ".join(words))
                    else:
                        # the context might be unknown or too short for the selected size.
                        print("No matching next words.")
                # generate text by repeatedly choosing a weighted random next word.
                elif choice == "6":
                    text = input("Starting text: ")
                    # length is how many new words to add, excluding the starting text.
                    length = int(input("How many new words? "))
                    # zero is fine, but a negative number of new words is invalid.
                    if length < 0:
                        print("Length must be zero or more.")
                    else:
                        # show the result; generation can stop early if it runs out of matches.
                        print(generate(session, text, n, length))
                # clear only the training rows for the currently selected size.
                elif choice == "7":
                    database.clear_data(session, n)
                    print("Data cleared for n =", n)
                # leave the menu loop when the user chooses exit.
                elif choice == "0":
                    # breaking the loop still runs the cleanup in finally below.
                    break
                else:
                    # unrecognized menu choices just get a reminder.
                    print("Please choose an option from the menu.")
            # catch bad numbers, file problems, and database failures from this action.
            except (ValueError, OSError, SQLAlchemyError) as error:
                # discard uncommitted database changes so the session is ready to use again.
                session.rollback()
                # show what went wrong, then return to the menu.
                print("Error:", error)
    # exit gracefully on end of input or ctrl+c.
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    # this cleanup runs whether we exit normally or hit an error.
    finally:
        # release the session and its database resources.
        session.close()


# run the menu when this file is launched directly, rather than imported.
if __name__ == "__main__":
    main()
