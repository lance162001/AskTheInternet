from flask import flash, redirect, render_template, request, session
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
    return render_template('main.html',user=session['user'], asked=session['qCount'])
    
@app.route('/ask', methods=['GET','POST'])
def ask():
    getUser()
    form = AskForm()
    if form.validate_on_submit():
        if session['qCount'] >= 5:
            return redirect('/')
            flash("Cannot ask more questions until current questions expire")
        q = Question(body=request.form['question'],optionOne=request.form['answerOne'],optionTwo=request.form['answerTwo'])
        q.author=db.session.query(User).filter_by(ip=session['user']).first()
        db.session.add(q)
        db.session.commit()

        return redirect('/')
    return render_template('ask.html',form=form)


@app.route('/answer', methods=['GET','POST'])
def answer():
    getUser()
    if session['initial']:
        session['initial']=False
        question=chooseQuestion()
        if question == None:
            flash("no available questions to answer!")
            session['initial']=True
            return redirect('/')
    
        session['question']=question.id
    
    if request.method == 'POST':
        question = db.session.query(Question).filter_by(id=session['question']).first()
        question.viewed.append(db.session.query(User).filter_by(ip=session['user']).first())
        if request.form['output'] == "1":
            question.answeredOne=Question.answeredOne+1
            print("answeredOne+1")
        elif request.form['output'] == "2":
            question.answeredTwo=Question.answeredTwo+1
            print("answeredTwo+1")
        elif request.form['output'] == "3":
            question.dislikes=Question.dislikes+1
            print("dislikes+1")
            
        db.session.merge(question)
        db.session.commit()
        
        question=chooseQuestion()
        if question == None:
            flash("no available questions to answer!")
            session['initial']=True
            return redirect('/')
        session['question']=question.id
        
    return render_template('answer.html',question=question)

@app.route('/review')
def review():
    getUser()
    a=db.session.query(Question).options(db.joinedload(Question.author))
    asked=a.filter(Question.author==session['user'])
    return render_template('review.html',questions=asked)

@app.route('/faq')
def faq():
    top=db.session.query(Question).filter(Question.popularity!=0).order_by(Question.popularity.desc()).limit(10).all()
    return render_template('faq.html',questions=top)

def chooseQuestion():
    #if you want a pure random question
    #return Question.query.order_by(func.random()).first()

    #filter out questions that user has made or has already seen, then take a random question. Ideally this will trend towards more popular stuff but for now this works
    q = db.session.query(Question).options(db.joinedload(Question.viewed))
    question = q.filter(and_(Question.author!=user, ~Question.viewed.contains(user) )).order_by(func.random()).first()

    return question
    
def getUser():
    if 'user' not in session:
        session['initial']=True
        userIP = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
       # for testing
       # userIP = "googoogagaaaa"
        session['user'] = userIP
        user = db.session.query(User).filter_by(ip=userIP).first()
        if user is None:
            user = User(ip=userIP)
            db.session.add(user)
            db.session.commit()
    qCount=0
    for q in user.asked:
        qCount+=1
    session['qCount']=qCount
