from app import db
from datetime import datetime, timedelta

class User(db.Model):
    __tablename__= 'users'
    ip = db.Column(db.String(16), primary_key=True)
    asked = db.relationship('Question', backref='author', lazy='dynamic')
    qCount = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return '<User {}>'.format(self.ip)

class Question(db.Model):
    __tablename__= 'questions'

    id = db.Column(db.String(37), primary_key=True)
    body = db.Column(db.String(100), index=True, unique=True)
    optionOne = db.Column(db.String(30))
    optionTwo = db.Column(db.String(30))
    
    dislikes = db.Column(db.Integer, default=0)
    answeredOne = db.Column(db.Integer, default=0)
    answeredTwo = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(16), db.ForeignKey('users.ip'))
    
    totalViews = db.column_property(answeredOne+answeredTwo+dislikes)
    popularity = db.column_property(answeredOne+answeredTwo)
    
    viewed = db.relationship('User', secondary="middle")
    
    def __repr__(self):
        return '<Question {}>'.format(self.body)

    def prune(self):
        if self.answeredOne + self.answeredTwo < self.dislikes and self.totalViews > 10:
            return True
        if self.timestamp+timedelta(days = 2) < datetime.utcnow():
            return True
        return False
        
class Middle(db.Model):
    __tablename__= 'middle'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(16), db.ForeignKey('users.ip'))
    question_id = db.Column(db.String(37), db.ForeignKey('questions.id'))

    user = db.relationship(User, backref=db.backref("middle", cascade="all, delete-orphan"))
    question = db.relationship(Question, backref=db.backref("middle", cascade="all, delete-orphan"))
