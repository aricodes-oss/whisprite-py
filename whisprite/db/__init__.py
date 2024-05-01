from peewee import SqliteDatabase

# TODO: load from config
connection: SqliteDatabase = SqliteDatabase("data.db", pragmas={"foreign_keys": 1})
