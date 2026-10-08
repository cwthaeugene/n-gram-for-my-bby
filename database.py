# sqlalchemy gives us python tools for talking to the sqlite database.
from sqlalchemy import Integer, String, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# our table models inherit from this so sqlalchemy can keep track of them.
class Base(DeclarativeBase):
    # nothing extra needed here, the parent class handles the setup.
    pass


# one object represents one saved n-gram row in our single table.
class NGram(Base):
    # this is the actual table name inside the database.
    __tablename__ = "ngrams"

    # n is the full phrase size: 1 for a unigram, 2 for a bigram, and so on.
    n: Mapped[int] = mapped_column(Integer, primary_key=True)
    # context is the first n - 1 words, or an empty string when n is 1.
    context: Mapped[str] = mapped_column(String, primary_key=True)
    # word is the last word; n, context, and word together uniquely identify a row.
    word: Mapped[str] = mapped_column(String, primary_key=True)
    # count tracks how often we saw this exact combination, starting at 1.
    count: Mapped[int] = mapped_column(Integer, default=1)


# open the database file and give the rest of the program a session to use.
def connect(path="ngrams.db"):
    # the engine handles database connections; sqlite stores the data in this file.
    engine = create_engine("sqlite:///" + path)
    # create any missing tables; existing tables and their data stay as they are.
    Base.metadata.create_all(engine)

    # this makes a session factory tied to our database engine.
    Session = sessionmaker(bind=engine)
    # a session lets us read rows and collect changes before saving them.
    return Session()


# save one phrase, or bump its count if we already know it.
def save_ngram(session, n, context, word):
    # look up the row using all three parts of its primary key.
    ngram = session.get(NGram, (n, context, word))

    # no match means this is a new phrase for us.
    if ngram is None:
        ngram = NGram(n=n, context=context, word=word, count=1)
        # queue the new row; the training function commits everything later.
        session.add(ngram)
    else:
        # seeing the same phrase again increases its frequency instead of adding a duplicate.
        ngram.count += 1


# find the words that have followed this context during training.
def get_next_words(session, n, context):
    statement = (
        # we only need each possible next word and its frequency.
        select(NGram.word, NGram.count)
        # match both the phrase size and the exact context.
        .where(NGram.n == n, NGram.context == context)
        # most common words come first; alphabetical order breaks ties.
        .order_by(NGram.count.desc(), NGram.word)
    )
    # run the query and return all matching rows as tuples.
    return session.execute(statement).all()


# get saved phrases for the currently selected size so we can display them.
def get_ngrams(session, n):
    statement = (
        # fetch the parts we need to rebuild each phrase and show its count.
        select(NGram.context, NGram.word, NGram.count)
        # keep the results limited to this n-gram size.
        .where(NGram.n == n)
        # show frequent phrases first, then sort tied rows by their text.
        .order_by(NGram.count.desc(), NGram.context, NGram.word)
    )
    # run the query and return all matching rows as tuples.
    return session.execute(statement).all()


# delete training data for just this size; other sizes keep their rows.
def clear_data(session, n):
    # queue a delete for all rows whose n matches the selected size.
    session.execute(delete(NGram).where(NGram.n == n))
    # commit makes these changes permanent in the database file.
    session.commit()
