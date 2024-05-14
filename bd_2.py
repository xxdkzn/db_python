from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Подключение к базе данных PostgreSQL
engine = create_engine('postgresql://username:password@localhost:5432/bd_name')
Session = sessionmaker(bind=engine)

# Определение моделей данных
Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    publisher = relationship('Publisher', back_populates='books')
    purchases = relationship('Purchase', back_populates='book')

class Publisher(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship('Book', back_populates='publisher')

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='purchases')
    store_id = Column(Integer, ForeignKey('stores.id'))
    store = relationship('Store', back_populates='purchases')
    price = Column(Integer)
    purchase_date = Column(DateTime)

class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    purchases = relationship('Purchase', back_populates='store')

class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True)
    id_book = Column(Integer, ForeignKey('books.id'))
    id_shop = Column(Integer, ForeignKey('shops.id'))
    count = Column(Integer)

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    data_sale = Column(DateTime)
    id_stock = Column(Integer, ForeignKey('stock.id'))
    count = Column(Integer)

class Shop(Base):
    __tablename__ = 'shops'
    id = Column(Integer, primary_key=True)
    name = Column(String)

def create_tables(session):
    Base.metadata.create_all(engine)

# Запрос на выборку магазинов, продающих целевого издателя
def get_stores_by_publisher(session, publisher_name):
    publisher = session.query(Publisher).filter(Publisher.name == publisher_name).first()
    if publisher:
        purchases = session.query(Purchase).\
                     join(Purchase.book).\
                     filter(Book.publisher_id == publisher.id).\
                     join(Purchase.store).\
                     all()
        for purchase in purchases:
            print(f"{purchase.book.title} | {purchase.store.name} | {purchase.price} | {purchase.purchase_date.strftime('%d-%m-%Y')}")
    else:
        print(f"Издатель с именем '{publisher_name}' не найден.")


def get_shops(session, publisher_data):
    query = session.query(
        Book.title, Store.name, Purchase.price, Purchase.purchase_date
    ).select_from(Purchase).\
           join(Purchase.book).\
           join(Book.publisher).\
           join(Purchase.store)

    if publisher_data.isdigit():
        results = query.filter(Publisher.id == int(publisher_data)).all()
    else:
        results = query.filter(Publisher.name == publisher_data).all()

    for book_title, store_name, price, purchase_date in results:
        print(f"{book_title: <40} | {store_name: <10} | {price: <8} | {purchase_date.strftime('%d-%m-%Y')}")

if __name__ == '__main__':
    with Session() as session:
        create_tables(session)
        publisher_data = input("Введите имя или ID издателя: ")
        get_shops(session, publisher_data)