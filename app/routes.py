from flask import flash, redirect, render_template, request
from app import app, db
from app.models import User,Question
from app.forms import AskForm, AnswerForm
import random      
from sqlalchemy.sql.expression import and_, func
import uuid

        
@app.route('/index')
@app.route('/')
def home(): 

    getUser()
    return render_template('main.html',user=user, asked=qCount)
    
@app.route('/ask', methods=['GET','POST'])
def ask():
    try:
        user
    except NameError:
        getUser()
    form = AskForm()
    if form.validate_on_submit():
        if qCount >= 5:
            return redirect('/')
            flash("Cannot ask more questions until current questions expire")
        q = Question(id=str(uuid.uuid4().int),body=request.form['question'],optionOne=request.form['answerOne'],optionTwo=request.form['answerTwo'])
        q.author=user
        db.session.add(q)
        db.session.commit()

        return redirect('/')
    return render_template('ask.html',form=form)

initial=True
@app.route('/answer', methods=['GET','POST'])
def answer():
    global user
    global question
    global initial
    try:
        user
    except NameError:
        getUser()

    if initial:
        initial=False
        question=chooseQuestion()
        print(question)
    if question == None:
        flash("no available questions to answer!")
        initial=True
        return redirect('/')
    if request.method == 'POST':
        question.viewed.append(user)
        if request.form['output'] == "1":
            question.answeredOne=Question.answeredOne+1
            print("answeredOne+1")
        elif request.form['output'] == "2":
            question.answeredTwo=Question.answeredTwo+1
            print("answeredTwo+1")
        elif request.form['output'] == "3":
            question.dislikes=Question.dislikes+1
            print("dislikes+1")
            
        print(question.answeredOne,":",question.answeredTwo,":",question.dislikes)
        print (question.popularity)
        db.session.merge(question)
        db.session.commit()
        question=chooseQuestion()
        print(question)
        if question == None:
            flash("no available questions to answer!")
            initial=True
            return redirect('/')
    return render_template('answer.html',question=question)

@app.route('/review')
def review():
    try:
        user
    except NameError:
        getUser()
    asked=db.session.query(Question).filter(Question.author==user)
    return render_template('review.html',questions=asked)

@app.route('/faq')
def faq():
    top=db.session.query(Question).filter(Question.popularity!=0).order_by(Question.popularity.desc()).limit(10).all()
    for i in top:
        print(i.popularity)
    return render_template('faq.html',questions=top)

def chooseQuestion():
    #if you want a pure random question
    #return Question.query.order_by(func.random()).first()

    #filter out questions that user has made or has already seen, then take a random question. Ideally this will trend towards more popular stuff but for now this works
    q = db.session.query(Question).options(db.joinedload(Question.viewed))
    question = q.filter(and_(Question.author!=user, ~Question.viewed.contains(user) )).order_by(func.random()).first()
    if question == None:
        return None
    while question.prune() and question != None:
        db.session.remove(question)
        db.session.commit()
        q = db.session.query(Question).options(db.joinedload(Question.viewed))
        question=q.filter(and_(Question.author!=user, ~Question.viewed.contains(user) )).order_by(func.random()).first()
        if question == None:
            return None
    return question
    
def getUser():
    global user
    global qCount
    userIP = str(request.remote_addr)
    userIP = "googoogagaaaa"
    user = db.session.query(User).filter_by(ip=userIP).first()
    if user is None:
        user = User(ip=userIP)
        db.session.add(user)
        db.session.commit()
    qCount=0
    for q in user.asked:
        qCount+=1