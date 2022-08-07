# SQL https://docs.sqlalchemy.org/en/14/orm/quickstart.html
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine

from decouple import config

from sqlalchemy import create_engine

# env
DB=config('DB')

Base = declarative_base()
metadata = Base.metadata
Session = sessionmaker(engine, future=True)

class User(Base):
      __tablename__ = "user"

      id = Column(Integer, primary_key=True)
      tg_id = Column(Integer, nullable=False, unique=True)
      tg_username = Column(String(255), unique=True)
      name = Column(String(255))

      products_sold = relationship("Product", back_populates="seller", primaryjoin="User.id == Product.seller_id")
      products_bought = relationship("Product", back_populates="buyer", primaryjoin="User.id == Product.buyer_id")

      def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, name={self.name!r}, tg_id={self.tg_id!r})"

class Product(Base):
      __tablename__ = "product"

      id = Column(Integer, primary_key=True)
      archived = Column(Boolean, default=False)
      is_selling = Column(Boolean, default=True)
      is_sold = Column(Boolean, default=False)

      message_id = Column(Integer, nullable=False, unique=True)

      name = Column(String(255), nullable=False)
      has_image = Column(Boolean, default=False)
      description = Column(String(10000), nullable=False)

      seller_id = Column(Integer, ForeignKey("user.id"), nullable=False)
      seller = relationship("User", back_populates="products_sold", foreign_keys=[seller_id], primaryjoin="User.id == Product.seller_id")
      buyer_id = Column(Integer, ForeignKey("user.id"), nullable=True)
      buyer = relationship("User", back_populates="products_bought", foreign_keys=[buyer_id], primaryjoin="User.id == Product.buyer_id")

      category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
      category = relationship("Category", back_populates="products", primaryjoin="Product.category_id == Category.id")

      def __repr__(self):
        return f"Product(id={self.id!r})..."

class Category(Base):
      __tablename__ = "category"

      id = Column(Integer, primary_key=True)
      user_id = Column(Integer, ForeignKey("user.id"))

      name = Column(String(64), unique=True)

      products = relationship("Product", back_populates="category", primaryjoin="Category.id == Product.category_id")

      def __repr__(self):
        return f"Seller(id={self.id!r})..."

engine = create_engine(DB, echo=True, future=True, client_encoding="utf8")

def create_user(user):
    with engine.connect() as conn:
      user_new = insert(User).values(tg_id = user.id, tg_username=user.username, name=user.first_name)\
                  .on_conflict_do_update(index_elements=['tg_id'], set_=dict(tg_id = user.id, name=user.first_name))
      user_id = conn.execute(user_new)
      conn.commit()
    return user_id

def get_all_categories():
    with Session().begin() as session:
        stmt = select(Category)
        categories = [category.name for category in session.scalars(stmt)]
        return categories

def add_category(category_name):
    with engine.connect() as conn:
        category_new = insert(Category).values(name=category_name)\
            .on_conflict_do_nothing(index_elements=['name'])
        conn.execute(category_new)
        conn.commit()

def add_product(message_id, is_selling, name, description, seller_tg_id, category_name, has_image):
    category = None
    seller = None

    results = None

    with Session() as session:
      category = Category(name=category_name)
      category_stmt = select(Category).where(Category.name == category_name)
      category = session.scalars(category_stmt).one()

      seller = User(tg_id=seller_tg_id)
      seller_stmt = select(User).where(User.tg_id == seller_tg_id)
      seller = session.scalars(seller_stmt).one()

    with engine.connect() as conn:
        product_new = insert(Product).values(message_id=message_id, is_selling=is_selling, name=name, description=description, seller_id=seller.id, category_id=category.id, has_image=has_image)\
          .returning(Product.id)
        results = conn.execute(product_new)
        conn.commit()
    return results.first()[0]# TODO refactor it's id of product

def get_products_from_tg_user(tg_id):
    with Session() as session:
        stmt = select(Product)\
          .join(Product.seller)\
          .where(User.tg_id == tg_id)
        results = session.scalars(stmt).all()
    return results

def get_product_by_id(product_id, tg_id, seller=True):
    results = None
    with Session().begin() as session:
      if seller==True:
        stmt = select(Product)\
          .join(Product.seller)\
          .where(User.tg_id == tg_id)
      else:
        stmt = select(Product)\
          .join(Product.buyer)\
          .where(User.tg_id == tg_id)\
          .where(Product.id == product_id)
      results = session.scalars(stmt).first()
      print(results)
    return results
  

def create_tables():
    metadata.create_all(engine)