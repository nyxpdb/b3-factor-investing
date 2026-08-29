from sqlalchemy import Column, Float, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class Ranking(Base):
    __tablename__ = "rankings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    rank = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    price_earnings = Column(Float)
    return_on_equity = Column(Float)
    volume = Column(Float)
    combined_score = Column(Float)
    __table_args__ = (UniqueConstraint("date", "symbol", name="uq_date_symbol"),)

    def __repr__(self) -> str:
        return f"<Ranking(date={self.date}, rank={self.rank}, symbol={self.symbol}, score={self.combined_score})>"


def create_db_engine(db_path: str):
    url = f"sqlite:///{db_path}"
    return create_engine(url, echo=False)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def get_session(engine) -> Session:
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
