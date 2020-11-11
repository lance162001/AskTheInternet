import time
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models import User, Question
timetoPrune=60 * 3 - 1
def prune():
    while True:
        print("Pruning Question Database...")
        pruned=False
        for i in db.session.query(Question).all():
            if i.prune():
                print("Pruning ",i)
                db.session.delete(i)
                pruned=True
        if pruned:
            db.session.commit()
        print("Pruning complete, waiting ",timetoPrune," seconds.")
        time.sleep(timetoPrune)
