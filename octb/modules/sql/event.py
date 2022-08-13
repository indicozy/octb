
import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, DateTime
from octb.modules.sql import BASE, SESSION

class Event(BASE):
      __tablename__ = "event"

      id = Column(Integer, primary_key=True, autoincrement=True)
      name = Column(String(64), unique=True)
      has_image = Column(Boolean, default=False)
      description = Column(String(10000), nullable=False)
      link = Column(String(2048), nullable=False)

      creator_id = Column(Integer, nullable=False)

      organizer = Column(String(64), nullable=False)
      location = Column(String(64), nullable=False)

      price = Column(Integer, nullable=False)

      date_starting = Column(DateTime, nullable=False)
      date_ending = Column(DateTime, nullable=True)
      date_all_day= Column(Boolean, nullable=False, default=False)

      mailing_done= Column(Boolean, nullable=False, default=False)

      def __init__(self, name, has_image, description, link, creator_id,
                   organizer, location, price, date_starting, date_ending, date_all_day):
          self.name = name 
          self.has_image = has_image
          self.description = description
          self.link = link
          self.creator_id = creator_id
          self.organizer = organizer
          self.location = location
          self.price = price
          self.date_starting = date_starting
          self.date_ending = date_ending
          self.date_all_day = date_all_day

      def __repr__(self):
          return "<Event {} ({})>".format(self.id, self.name)

Event.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

# def get_all_events():
#     try:
#         return SESSION.query(Category).all()
#     finally:
#         SESSION.close()

# def get_category_by_name(name):
#     try:
#         return SESSION.query(Category).where(Category.name == name).first()
#     finally:
#         SESSION.close()

# def get_category_by_id(category_id):
#     try:
#         return SESSION.query(Category).where(Category.id == category_id).first()
#     finally:
#         SESSION.close()

# def add_category(category_name):
#     with INSERTION_LOCK:
#         category = SESSION.query(Category).where(Category.name==category_name)
#         if not category:
#             category = Category(category_name)
#             SESSION.add(category)
#             SESSION.flush()
#         SESSION.commit()