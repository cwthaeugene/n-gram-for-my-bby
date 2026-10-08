import database
from ngram import train, suggest, generate
from sqlalchemy.exc import SQLAlchemyError


def show_ngrams(session, n):
    rows = database.get_ngrams(session, n)
    if not rows:
        print("No saved n-grams yet.")
    for context, word, count in rows:
        print((context + " " + word).strip(), "->", count)


def main():
    session = database.connect()
    n = 2
    try:
        while True:
            print("\nN-gram project (n = " + str(n) + ")")
            print("1. Change n")
            print("2. Train with text")
            print("3. Train with a text file")
            print("4. Show saved n-grams")
            print("5. Suggest next words")
            print("6. Generate text")
            print("7. Clear data for current n")
            print("0. Exit")
            choice = input("Choose: ").strip()

            try:
                if choice == "1":
                    new_n = int(input("Enter n (1 or more): "))
                    if new_n < 1:
                        print("N must be at least 1.")
                    else:
                        n = new_n
                elif choice == "2":
                    text = input("Training text: ")
                    print("Trained on", train(session, text, n), "n-grams.")
                elif choice == "3":
                    path = input("Text file path: ")
                    with open(path, "r", encoding="utf-8") as file:
                        text = file.read()
                    print("Trained on", train(session, text, n), "n-grams.")
                elif choice == "4":
                    show_ngrams(session, n)
                elif choice == "5":
                    text = input("Starting text: ")
                    words = suggest(session, text, n, 3)
                    if words:
                        print("Suggestions:", ", ".join(words))
                    else:
                        print("No matching next words.")
                elif choice == "6":
                    text = input("Starting text: ")
                    length = int(input("How many new words? "))
                    if length < 0:
                        print("Length must be zero or more.")
                    else:
                        print(generate(session, text, n, length))
                elif choice == "7":
                    database.clear_data(session, n)
                    print("Data cleared for n =", n)
                elif choice == "0":
                    break
                else:
                    print("Please choose an option from the menu.")
            except (ValueError, OSError, SQLAlchemyError) as error:
                session.rollback()
                print("Error:", error)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    finally:
        session.close()


if __name__ == "__main__":
    main()
