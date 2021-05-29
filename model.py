from enum import unique
from peewee import *


db = SqliteDatabase('history.db')

class History(Model):

    command = CharField()
    session = CharField()
    date = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])

    class Meta:
        database = db




if __name__ == '__main__':
    db.connect()
    db.create_tables([History])
    print('TABLES CREATED')
    db.close()
