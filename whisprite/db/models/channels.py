from peewee import CharField
from .base import BaseModel


class Channel(BaseModel):
    username = CharField(unique=True)
