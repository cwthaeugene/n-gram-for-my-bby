from sqlalchemy import Integer, String, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class NGram(Base):
    __tablename__ = "ngrams"

    n: Mapped[int] = mapped_column(Integer, primary_key=True)
    context: Mapped[str] = mapped_column(String, primary_key=True)
    word: Mapped[str] = mapped_column(String, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=1)


def connect(path="ngrams.db"):
    engine = create_engine("sqlite:///" + path)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()


def save_ngram(session, n, context, word):
    ngram = session.get(NGram, (n, context, word))

    if ngram is None:
        ngram = NGram(n=n, context=context, word=word, count=1)
        session.add(ngram)
    else:
        ngram.count += 1


def get_next_words(session, n, context):
    statement = (
        select(NGram.word, NGram.count)
        .where(NGram.n == n, NGram.context == context)
        .order_by(NGram.count.desc(), NGram.word)
    )
    return session.execute(statement).all()


def get_ngrams(session, n):
    statement = (
        select(NGram.context, NGram.word, NGram.count)
        .where(NGram.n == n)
        .order_by(NGram.count.desc(), NGram.context, NGram.word)
    )
    return session.execute(statement).all()


def clear_data(session, n):
    session.execute(delete(NGram).where(NGram.n == n))
    session.commit()
