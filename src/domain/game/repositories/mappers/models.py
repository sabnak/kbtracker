from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class ItemModel(Base):
	__tablename__ = "items"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, unique=True, nullable=False, index=True)
	name = Column(String, nullable=False)
	price = Column(Integer, nullable=False, default=0)
	hint = Column(Text, nullable=True)
	propbits = Column(ARRAY(String), nullable=True)

	object_items = relationship("ObjectHasItemModel", back_populates="item")


class LocationModel(Base):
	__tablename__ = "locations"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, nullable=False, index=True)
	name = Column(String, nullable=False)

	objects = relationship("ObjectModel", back_populates="location")


class ObjectModel(Base):
	__tablename__ = "objects"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(Integer, unique=True, nullable=False, index=True)
	location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
	name = Column(String, nullable=False)
	hint = Column(Text, nullable=True)
	msg = Column(Text, nullable=True)

	location = relationship("LocationModel", back_populates="objects")
	object_items = relationship("ObjectHasItemModel", back_populates="object")


class ObjectHasItemModel(Base):
	__tablename__ = "objects_has_items"

	item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
	object_id = Column(Integer, ForeignKey("objects.id"), primary_key=True)
	profile_id = Column(Integer, ForeignKey("profiles.id"), primary_key=True)
	count = Column(Integer, nullable=False, default=1)

	item = relationship("ItemModel", back_populates="object_items")
	object = relationship("ObjectModel", back_populates="object_items")
	profile = relationship("ProfileMapper", back_populates="object_items")

