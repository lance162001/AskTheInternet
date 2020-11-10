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
        q.author=session['user']
        db.session.add(q)
        db.session.commit()

        return redirect('/')
    return render_template('ask.html',form=form)


@app.route('/answer', methods=['GET','POST'])
def answer():
    getUser()

    if session['initial']:
        session['initial']=False
        session['question']=chooseQuestion()
    if session['question'] == None:
        flash("no available questions to answer!")
        session['initial']=True
        return redirect('/')
    if request.method == 'POST':
        session['question'].viewed.append(user)
        if request.form['output'] == "1":
            session['question'].answeredOne=Question.answeredOne+1
            print("answeredOne+1")
        elif request.form['output'] == "2":
            session['question'].answeredTwo=Question.answeredTwo+1
            print("answeredTwo+1")
        elif request.form['output'] == "3":
            session['question'].dislikes=Question.dislikes+1
            print("dislikes+1")
            
        db.session.merge(session['question'])
        db.session.commit()
        session['question']=chooseQuestion()
        if session['question'] == None:
            flash("no available questions to answer!")
            session['initial']=True
            return redirect('/')
    return render_template('answer.html',question=session['question'])

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
    try:
        print(session['user'])
    except:
        session['initial']=True
        userIP = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
       # for testing
       # userIP = "googoogagaaaa"
        session['user'] = db.session.query(User).filter_by(ip=userIP).first()
        if session['user'] is None:
            session['user'] = User(ip=userIP)
            db.session.add(session['user'])
            db.session.commit()
    qCount=0
    for q in user.asked:
        qCount+=1
    session['qCount']=qCount
