import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, DateTime, BigInteger, Boolean, or_
from octb.modules.sql import BASE, SESSION

INSERTION_LOCK = threading.RLock()

class DatingUser(BASE):
      __tablename__ = "dating_user"

      user_id = Column(BigInteger, primary_key=True)
      name = Column(String(64))
      description = Column(String(2048), default="")
      gender = Column(Boolean, nullable=True) # True = Boy, False = Girl, None = Other
      interest_gender = Column(Boolean, nullable=True)
      is_on_campus = Column(Boolean, default=True)
      location = Column(String(64))
      age = Column(Integer)
      has_image = Column(Boolean) # TODO remove

      is_archived = Column(Boolean, default=False)
      # Interests
      # Study-buddy, romance, friend, sport, hobbies, roomate

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, user_id, name, gender, interest_gender, location, age, has_image, is_on_campus=True, description=""):
          self.user_id = user_id
          self.name = name
          self.description = description
          self.gender = gender
          self.interest_gender = interest_gender
          self.is_on_campus = is_on_campus
          self.location = location
          self.age = age
          self.has_image = has_image

      def __repr__(self):
          return "<DatingUser ({})>".format(self.user_id)
DatingUser.__table__.create(checkfirst=True)

def add_dating_user(user_id, name, gender, interest_gender, location, age, has_image, is_on_campus=True, description=""):
    dating_user_obj = SESSION.query(DatingUser)\
        .where(DatingUser.user_id == user_id)\
        .first() # TODO try except
    if dating_user_obj:
        dating_user_obj.name = name
        dating_user_obj.gender = gender
        dating_user_obj.interest_gender = interest_gender
        dating_user_obj.location = location
        dating_user_obj.age = age
        dating_user_obj.has_image = has_image
        dating_user_obj.is_on_campus = is_on_campus
        dating_user_obj.description = description
        dating_user_obj.is_archived = False
    else:
        with INSERTION_LOCK:
            dating_user_obj = DatingUser(user_id, name, gender, interest_gender, location, age, has_image, is_on_campus=True, description="")
    SESSION.add(dating_user_obj)
    SESSION.commit()
    return dating_user_obj

def get_dating_user_by_id(user_id):
    try:
        return SESSION.query(DatingUser).where(DatingUser.user_id == user_id).first()
    finally:
        SESSION.close()

def count_dating_users():
  try:
    return SESSION.query(DatingUser.user_id).count()
  finally:
      SESSION.close()

class DatingCategory(BASE):
      __tablename__ = "dating_category"

      id = Column(Integer, primary_key=True, autoincrement=True)
      user_id = Column(BigInteger)
      name = Column(String(64))

      def __init__(self, name, user_id):
          self.name = name
          self.user_id = user_id

      def __repr__(self):
          return "<DatingCategory {} ({})>".format(self.id, self.name)
DatingCategory.__table__.create(checkfirst=True)

class DatingMatch(BASE):
      __tablename__ = "dating_match"

      id = Column(Integer, primary_key=True, autoincrement=True)
      from_id = Column(BigInteger)
      to_id = Column(BigInteger)

      def __init__(self, from_id, to_id):
          self.from_id = from_id
          self.to_id = to_id

      def __repr__(self):
          return "<DatingMatch {}>".format(self.id)
DatingMatch.__table__.create(checkfirst=True)

class DatingReject(BASE):
      __tablename__ = "dating_reject"

      id = Column(Integer, primary_key=True, autoincrement=True)
      rejector_id = Column(BigInteger)
      rejectee_id = Column(BigInteger)

      def __init__(self, rejector_id, rejectee_id):
          self.rejector_id = rejector_id
          self.rejectee_id = rejectee_id

      def __repr__(self):
          return "<DatingMatch {}>".format(self.id)
DatingReject.__table__.create(checkfirst=True)

def get_dating_category_by_user_id(user_id):
    try:
        return SESSION.query(DatingCategory).where(DatingCategory.user_id == user_id).all()
    finally:
        SESSION.close()

def toggle_dating_category(user_id, name):
    dating_category_user = SESSION.query(DatingCategory)\
        .where(DatingCategory.user_id == user_id)\
        .where(DatingCategory.name == name)\
        .first() # TODO try except
    if not dating_category_user:
        with INSERTION_LOCK:
            dating_category_user = DatingCategory(name, user_id)
            SESSION.add(dating_category_user)
            SESSION.commit()
        return dating_category_user
    else:
        # print("helo")
        SESSION.delete(dating_category_user)
        SESSION.commit()
        return None

def get_user_categories(user_id):
    query = SESSION.query(DatingCategory.name)\
            .where(DatingCategory.user_id == user_id)\
            .all()
    SESSION.close()
    return [x[0] for x in query]
    

def get_potential_partner_by_interest(user_id, user_id_start, interests):
    print(user_id_start, "lol")
    user = get_dating_user_by_id(user_id)
    try:
        partner =  SESSION.query(DatingUser, DatingCategory)\
            .where(DatingUser.user_id > user_id_start)\
            .join(DatingReject, DatingReject.rejectee_id == DatingUser.user_id, isouter=True)\
            .where(DatingUser.user_id != user_id)\
            .where(
                DatingUser.user_id == DatingCategory.user_id
            )\
            .where(DatingCategory.name.in_(interests))\
            .where(
                or_(DatingReject.rejector_id != DatingUser.user_id, DatingReject.rejector_id == None)
            )\
            .where(
                or_(DatingReject.rejectee_id != user_id, DatingReject.rejectee_id == None)
            )\
            .where(
                DatingUser.is_archived != True
            )\
            .where(
                or_(DatingUser.interest_gender == user.gender, DatingUser.interest_gender == None) # TODO NOT TESTED
            )
        if user.interest_gender:
            partner = partner\
                .where(
                    DatingUser.gender == user.interest_gender # TODO NOT TESTED
                )
        partner = partner\
            .order_by(DatingUser.user_id.asc())\
            .first()
        if partner:
            print(partner[0].user_id, "lmao")
            return partner[0]
        else:
            print("not found")
            return None
    finally:
        SESSION.close()

def add_match(from_id, to_id):
    dating_user_obj = SESSION.query(DatingMatch)\
        .where(DatingMatch.from_id == from_id)\
        .where(DatingMatch.to_id == to_id)\
        .first() # TODO try except
    if not dating_user_obj:
        with INSERTION_LOCK:
            dating_user_obj = DatingMatch(from_id, to_id)
    SESSION.add(dating_user_obj)
    SESSION.commit()
    return dating_user_obj

def add_reject(rejector_id, rejectee_id):
    dating_user_obj = SESSION.query(DatingReject)\
        .where(DatingReject.rejector_id == rejector_id)\
        .where(DatingReject.rejectee_id == rejectee_id)\
        .first() # TODO try except
    if not dating_user_obj:
        with INSERTION_LOCK:
            dating_user_obj = DatingReject(rejector_id, rejectee_id)
    SESSION.add(dating_user_obj)
    SESSION.commit()
    return dating_user_obj

def get_reject(rejector_id, rejectee_id):
    try:
        return SESSION.query(DatingReject)\
        .where(DatingReject.rejector_id == rejector_id)\
        .where(DatingReject.rejectee_id == rejectee_id)\
        .first()
    finally:
        SESSION.close()

def remove_reject(rejector_id, rejectee_id):
    dating_reject = SESSION.query(DatingReject)\
        .where(DatingReject.rejector_id == rejector_id)\
        .where(DatingReject.rejectee_id == rejectee_id)\
        .first() # TODO try except
    if dating_reject:
        SESSION.delete(dating_reject)
        SESSION.commit()
        return None

def count_dating_matches():
  try:
    return SESSION.query(DatingMatch.id).count()
  finally:
      SESSION.close()

def count_dating_users_gender(is_male):
  try:
    return SESSION.query(DatingUser.user_id).where(DatingUser.gender==is_male).count()
  finally:
      SESSION.close()
      
def activate_user(user_id):
    dating_user_obj = SESSION.query(DatingUser)\
        .where(DatingUser.user_id == user_id)\
        .first() # TODO try except
    if dating_user_obj:
        dating_user_obj.is_archived = False
        SESSION.add(dating_user_obj)
        SESSION.commit()
    return dating_user_obj

def archive_user(user_id):
    dating_user_obj = SESSION.query(DatingUser)\
        .where(DatingUser.user_id == user_id)\
        .first() # TODO try except
    if dating_user_obj:
        dating_user_obj.is_archived = True
        SESSION.add(dating_user_obj)
        SESSION.commit()
    return dating_user_obj