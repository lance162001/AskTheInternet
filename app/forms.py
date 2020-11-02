from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms import TextAreaField
from app.models import Question, User
from flask import flash

class AskForm(FlaskForm):
    submit = SubmitField('Submit Question')
    question = TextAreaField('Question To Ask', render_kw={"rows": 10, "cols": 50},validators=[validators.Length(min=2, max=100,message='Question must be between 2 & 100 characters')])
    answerOne = TextAreaField('Option One',render_kw={"rows":5,"cols":20}, validators=[validators.Length(min=1,max=30,message='Answer must be between 1 & 30 characters')])
    answerTwo = TextAreaField('Option Two',render_kw={"rows":5,"cols":20}, validators=[validators.Length(min=1,max=30,message='Answer must be between 1 & 30 characters')])
    
    def validate_question(self,question):
        question = Question.query.filter_by(body=question.data).first()
        if question is not None:
            raise validators.ValidationError('This *exact* question is already being answered...')
        
class AnswerForm(FlaskForm):
    optionOne = SubmitField('   ')
    optionTwo = SubmitField('   ')
    abstain = SubmitField('Bad Question')
