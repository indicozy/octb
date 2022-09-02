import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, Boolean, Enum, DateTime, BigInteger
from octb.modules.sql import BASE, SESSION

from octb.modules.sql.user import User # needed for Foreignkey, do not delete
import enum

INSERTION_LOCK = threading.RLock()

class Category(BASE):
      __tablename__ = "category"

      id = Column(Integer, primary_key=True, autoincrement=True)

      name = Column(String(64), unique=True)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, name):
          self.name = name 

      def __repr__(self):
          return "<Category {} ({})>".format(self.id, self.name)
Category.__table__.create(checkfirst=True)

class Subcategory(BASE):
      __tablename__ = "subcategory"

      id = Column(Integer, primary_key=True, autoincrement=True)
      category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

      name = Column(String(256), nullable=False)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, category_id, name):
        self.name = name
        self.category_id = category_id

      def __repr__(self):
          return "<Subcategory {} ({})>".format(self.id, self.name)
Subcategory.__table__.create(checkfirst=True)

def get_subcategories_by_category_id(category_id):
    try:
        return SESSION.query(Subcategory).where(Subcategory.category_id == category_id).all()
    finally:
        SESSION.close()

def get_subcategory_by_name_and_category_id(name, category_id):
    try:
        return SESSION.query(Subcategory).where(Subcategory.name == name).where(Subcategory.category_id == category_id).first()
    finally:
        SESSION.close()

def get_subcategory_by_id(subcategory_id):
    try:
        return SESSION.query(Subcategory).where(Subcategory.id == subcategory_id).first()
    finally:
        SESSION.close()

def get_category_by_subcategory_id(subcategory_id):
    subcategory_obj = get_subcategory_by_id(subcategory_id)
    try:
        return SESSION.query(Category).where(Category.id == subcategory_obj.category_id).first()
    finally:
        SESSION.close()

def get_all_categories():
    try:
        return SESSION.query(Category).all()
    finally:
        SESSION.close()

def get_category_by_name(name):
    try:
        return SESSION.query(Category).where(Category.name == name).first()
    finally:
        SESSION.close()

def get_category_by_id(category_id):
    try:
        return SESSION.query(Category).where(Category.id == category_id).first()
    finally:
        SESSION.close()

def add_category(category_name):
    with INSERTION_LOCK:
        category = SESSION.query(Category).where(Category.name==category_name).all()
        if len(category) == 0:
            category = Category(category_name)
            SESSION.add(category)
            SESSION.commit()
            return category
        else:
            return category[0]

def add_subcategory(subcategory, category_id):
    with INSERTION_LOCK:
        subcategory_obj = SESSION.query(Category)\
            .where(Subcategory.name==subcategory)\
            .where(Subcategory.category_id==category_id)\
            .all()
        if len(subcategory_obj) == 0:
            subcategory_obj = Subcategory(category_id, subcategory)
            SESSION.add(subcategory_obj)
            SESSION.commit()
            return subcategory_obj
        else:
            return subcategory_obj[0]

class Seller(BASE):
      __tablename__ = "seller"

      user_id = Column(BigInteger, primary_key=True)
    
      name = Column(String(256), default="")
      has_delivery = Column(Boolean, default=False)
      working_time = Column(String(32), default="")
      phone_number = Column(String(32), default="")
      instant_message = Column(String(2096), nullable=True)
      link = Column(String(256), nullable=True)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, user_id, name="", has_delivery=False, working_time=None, phone_number="", instant_message=None, link=None):
          self.user_id = user_id
          self.name = name
          self.has_delivery = has_delivery
          self.working_time = working_time
          self.phone_number = phone_number
          self.instant_message = instant_message
          self.link = link 

      def __repr__(self):
          return "<Seller ({})>".format(self.user_id)
Seller.__table__.create(checkfirst=True)

def get_seller_by_user_id(user_id):
    try:
        return SESSION.query(Seller)\
          .where(Seller.user_id == user_id)\
          .first()
    finally:
        SESSION.close()

def get_sellers():
    try:
        return SESSION.query(Seller)\
          .all()
    finally:
        SESSION.close()

def update_seller_name(user_id, text):
  with INSERTION_LOCK:
    seller = SESSION.query(Seller).get(user_id)
    if seller:
        seller.name = text
        SESSION.commit()
    SESSION.close()
    return seller

def update_seller_delivery(user_id, has_delivery):
  with INSERTION_LOCK:
    seller = SESSION.query(Seller).get(user_id)
    if seller:
        seller.has_delivery = has_delivery
        SESSION.commit()
    SESSION.close()
    return seller

def update_seller_working_time(user_id, text):
  with INSERTION_LOCK:
    seller = SESSION.query(Seller).get(user_id)
    if seller:
        seller.working_time = text
        SESSION.commit()
    SESSION.close()
    return seller

def update_seller_phone_number(user_id, text):
  with INSERTION_LOCK:
    seller = SESSION.query(Seller).get(user_id)
    if seller:
        seller.phone_number = text
        SESSION.commit()
    SESSION.close()
    return seller

def update_seller_instant_message(user_id, text):
  with INSERTION_LOCK:
    seller = SESSION.query(Seller).get(user_id)
    if seller:
        seller.instant_message = text
        SESSION.commit()
    SESSION.close()
    return seller

def update_seller_link(user_id, text):
  with INSERTION_LOCK:
    seller = SESSION.query(Seller).get(user_id)
    if seller:
        seller.link = text
        SESSION.commit()
    SESSION.close()
    return seller

def get_seller_by_product_id(product_id):
    product = get_product_by_id_no_verify(product_id)
    try:
        return SESSION.query(Seller)\
          .where(Seller.user_id == product.seller_id)\
          .first()
    finally:
        SESSION.close()

def add_seller(user_id):
    with INSERTION_LOCK:
        seller_obj = SESSION.query(Seller).where(Seller.user_id == user_id).all()
        if len(seller_obj) == 0:
            seller_obj = Seller(user_id)
            SESSION.add(seller_obj)
            SESSION.commit()
            return seller_obj
        else:
            return seller_obj[0]

def remove_seller(user_id):
    with INSERTION_LOCK:
        seller_obj = SESSION.query(Seller).where(Seller.user_id == user_id).all()
        if len(seller_obj) != 0:
            SESSION.delete(seller_obj[0])
            SESSION.commit()
            return True

        SESSION.close()
        return False
        
class ProductTypeEnum(enum.Enum):
    sell = 'продаю'
    buy = 'куплю'
    lend = 'сдаю'
    borrow = 'одолжу'
    give = 'отдам'

# TODO two pooints of truths here in Column() and init
class Product(BASE):
      __tablename__ = "product"

      id = Column(Integer, primary_key=True, autoincrement=True)
      seller_id = Column(BigInteger, nullable=False)
      subcategory_id = Column(Integer, ForeignKey("subcategory.id"), nullable=False)
      message_id = Column(Integer, nullable=True, unique=True)

      name = Column(String(256), nullable=False)
      has_image = Column(Boolean, default=False)
      description = Column(String(10000), default="")
      product_type = Column(Enum(ProductTypeEnum))
      price = Column(String, nullable=False)

      is_archived = Column(Boolean, default=False)
      is_sold = Column(Boolean, default=False)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, name, has_image, description, product_type, price, seller_id, subcategory_id, message_id, is_archived=False, is_sold=False):
        self.name = name 
        self.is_archived = is_archived
        self.has_image = has_image
        self.description = description
        self.product_type = product_type
        self.price = price
        self.seller_id = seller_id
        self.subcategory_id = subcategory_id
        self.message_id = message_id
        self.is_archived = is_archived
        self.is_sold = is_sold

      def __repr__(self):
          return "<Product {} ({})>".format(self.id, self.name)
Product.__table__.create(checkfirst=True)

class Product_buyer(BASE):
      __tablename__ = "product_buyer"

      id = Column(Integer, primary_key=True, autoincrement=True)

      product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
      buyer_id = Column(BigInteger, nullable=False) # user.id
      message_id = Column(Integer, nullable=True)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, product_id, buyer_id, message_id=None):
        self.product_id = product_id 
        self.buyer_id = buyer_id 
        self.message_id = message_id

      def __repr__(self):
          return "<Product Buyer {} ({})>".format(self.id, self.buyer_id)
Product_buyer.__table__.create(checkfirst=True)

def add_buyer(product_id, buyer_id, message_id=None):
    with INSERTION_LOCK:
        product_buyer = Product_buyer(product_id, buyer_id, message_id=message_id)
        SESSION.add(product_buyer)
        SESSION.flush()
        SESSION.commit()

def get_buyer_count_by_product_id(product_id):
    query = SESSION.query(Product_buyer)\
            .where(Product_buyer.product_id==product_id).all()
    query_count = len(query)
    return query_count

def add_product(message_id, product_type, name, description, price, seller_id, subcategory, has_image):
    with INSERTION_LOCK:
        product = Product(name, has_image, description, product_type, price, seller_id, subcategory, message_id)
        SESSION.add(product)
        SESSION.flush()
        SESSION.commit()
    return product

def add_product_by_obj(product):
    with INSERTION_LOCK:
        SESSION.add(product)
        SESSION.commit()
    return product

def archive_product(product_id, user_id):
    with INSERTION_LOCK:
        product = SESSION.query(Product)\
          .where(Product.id == product_id)\
          .where(Product.seller_id == user_id)\
          .first() # TODO try except
        product.is_archived = True
        SESSION.add(product)
        SESSION.commit()
        return product

def count_products():
  try:
    return SESSION.query(Product.id).count()
  finally:
      SESSION.close()

def count_product_buyers():
  try:
    return SESSION.query(Product_buyer.id).count()
  finally:
      SESSION.close()

# def count_product_sold_by_seller_id(seller_id):
#   try:
#     return SESSION.query(Product_buyer.id).where(Product_buyer.seller_id == seller_id).count()
#   finally:
#       SESSION.close()

# def count_product_sold_by_seller_id_all():
#     sellers = get_sellers()
#     seller_products_sold = {}

#     print(sellers)
#     for seller in sellers:
#         print(seller)
#         print(seller.user_id)
#         # if seller.name:
#         #     print(seller)
#         #     print(seller.user_id)
#         #     seller_products_sold[seller.name] = count_product_sold_by_seller_id(seller.user_id)
#         # else:
#         seller_products_sold[str(seller.user_id)] = count_product_sold_by_seller_id(seller.user_id)
#     return seller_products_sold

def product_sold(product_id, user_id):
    with INSERTION_LOCK:
        product = SESSION.query(Product)\
          .where(Product.id == product_id)\
          .where(Product.seller_id == user_id)\
          .first() # TODO try except
        product.is_sold = True
        SESSION.add(product)
        SESSION.commit()
        return product

def product_restore(product_id, user_id):
    with INSERTION_LOCK:
        product = SESSION.query(Product)\
          .where(Product.id == product_id)\
          .where(Product.seller_id == user_id)\
          .first() # TODO try except
        product.is_sold = False
        SESSION.add(product)
        SESSION.commit()
        return product

def get_products_from_tg_user(tg_id):
    try:
        return SESSION.query(Product)\
          .where(Product.seller_id == tg_id)\
          .all()
    finally:
        SESSION.close()

def get_active_products_from_tg_user(tg_id):
    try:
        return SESSION.query(Product)\
          .where(Product.seller_id == tg_id)\
          .where(Product.is_archived == False)\
          .all()
    finally:
        SESSION.close()

def get_product_by_id(product_id, tg_id):
    query = SESSION.query(Product)\
            .where(Product.id == product_id)\
            .where(Product.seller_id == tg_id)
    try:
        return query.first()
    finally:
      SESSION.close()

def get_product_sellers_by_subcategory(subcategory_id):
    sellers = SESSION.query(Seller).subquery()
    query = SESSION.query(Product)\
            .where(Product.subcategory_id == subcategory_id)\
            .where(Product.is_sold == False)\
            .where(Product.is_archived == False)\
            .where(Product.product_type.in_((ProductTypeEnum.sell.name, ProductTypeEnum.lend.name)))\
            .join(
                sellers, Product.seller_id == sellers.c.user_id
            )
    return query.all()

def get_product_by_id_no_verify(product_id):
    query = SESSION.query(Product)\
            .where(Product.id == product_id)
    try:
        return query.first()
    finally:
      SESSION.close()

class Review(BASE):
      __tablename__ = "review"

      id = Column(Integer, primary_key=True, autoincrement=True)

      product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
      user_id = Column(BigInteger, nullable=False) 

      points = Column(Integer, nullable=False) 
      description = Column(String(4096), default="")

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, product_id, user_id, points, description=""):
        self.product_id = product_id 
        self.user_id = user_id 
        self.points = points 
        self.description = description

      def __repr__(self):
          return "<Review {}>".format(self.id)
Review.__table__.create(checkfirst=True)


def add_review(product_id, user_id, points, description=""):
    query = SESSION.query(Review)\
        .where(Review.product_id==product_id)\
        .where(Review.user_id==user_id).all()
    # print(query)
    with INSERTION_LOCK:
        if len(query) == 0:
            review = Review(product_id, user_id, points, description=description)
            SESSION.add(review)
        else:
            review = query[0]
            review.points = points
            review.description = description
        SESSION.commit()
    return review

def get_reviews_to_user(user_id): # review -> product -> user
    products = SESSION.query(Product).where(Product.seller_id == user).all()
    query = SESSION.query(Reviews)\
            .where(Review.product_id.in_([product.id for product in products]))
    return query.all()

def get_reviews_by_product_id(product_id):
    query = SESSION.query(Review)\
            .where(Review.product_id==product_id).all()
    query_count = len(query)
    query_sum = 0
    for product in query:
        query_sum += product.points
    if query_count == 0:
        return 0, 0
    query_sum /= query_count
    return query_sum, query_count

def get_products_by_seller():
    try:
        return SESSION.query(Seller, Product, Product_buyer)\
            .where(Seller.user_id == Product.seller_id)\
            .where(Product.id == Product_buyer.product_id)\
            .all()
    finally:
        SESSION.close()