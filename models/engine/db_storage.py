#!/usr/bin/python3
"""New engine DBStorage: (models/engine/db_storage.py)"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.review import Review
from models.user import User
the_classes = {
    'Amenity': Amenity,
    'City': City,
    'Place': Place,
    'State': State,
    'Review': Review,
    'User': User
}


class DBStorage:
    """private class attributes"""
    __engine = None
    __session = None

    """the all important __init__ *bows head*"""
    def __init__(self):
        """link to the user, data retrieved from environment variables"""
        user = os.getenv('HBNB_MYSQL_USER')
        passwd = os.getenv('HBNB_MYSQL_PWD')
        host = os.getenv('HBNB_MYSQL_HOST')
        database = os.getenv('HBNB_MYSQL_DB')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'
                                      .format(user, passwd, host, database))
        if os.getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """return all objects in a dict"""
        if not self.__session:
            self.reload()
        objects = {}
        if type(cls) == str:
            cls = the_classes.get(cls, None)
        if cls:
            for obj in self.__session.query(cls):
                objects[obj.__class__.__name__ + '.' + obj.id] = obj
        else:
            for cls in the_classes.values():
                for obj in self.__session.query(cls):
                    objects[obj.__class__.__name__ + '.' + obj.id] = obj
        return objects

    """The easy stuff"""
    def new(self, obj):
        self.__session.add(obj)

    def close(self):
        """Close db storage"""
        self.__session.remove()

    def get(self, cls, id):
        """Retrieve an object"""
        if cls is not None and type(cls) is str and id is not None and\
           type(id) is str and cls in the_classes:
            cls = the_classes[cls]
            result = self.__session.query(cls).filter(cls.id == id).first()
            return result
        else:
            return None

    def save(self):
        """save the session"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete object"""
        if not self.__session:
            self.reload()
        if obj:
            self.__session.delete(obj)

    def reload(self):
        """reload the session"""
        session_factory = sessionmaker(bind=self.__engine,
                                       expire_on_commit=False)
        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(session_factory)
