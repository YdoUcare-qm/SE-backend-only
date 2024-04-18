from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
import functools
from flask import request, jsonify
import jwt
from .config import Config
engine = None
Base = declarative_base()
db = SQLAlchemy()
from datetime import datetime



class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    name=db.Column(db.String(100))
    password=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    role=db.Column(db.Integer,nullable=False) #Role ID for students is 1, for Support Agents is 2, Admins is 3, Manager is 4.
    discourse_id=db.Column(db.Integer, unique=True, nullable=False) 
    status=db.Column(db.Boolean, default=False) #confirmation status
    notification=db.Column(db.Boolean, default=True)
    email_notif=db.Column(db.Boolean, default=True)
    webhook_notif=db.Column(db.Boolean, default=True)

class Ticket(db.Model):         #Ticket is Private (Invisible to peers,visible to staff)
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime,nullable=False, default=datetime.now())
    creator=db.Column(db.Integer, nullable=False)
    category=db.Column(db.Integer,nullable=False)  #discourse category id
    tags=db.Column(db.String(100))
    offensive=db.Column(db.Boolean, default=False)

    escalated=db.Column(db.Boolean, default=False)
    resolved=db.Column(db.Boolean, default=False)
    merged=db.Column(db.Integer, default=-1) #-1 means unmerged, any other int means the id of topic

class Response(db.Model):         #Response to Tickets
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    ticket_id=db.Column(db.Integer, nullable=False)
    responder=db.Column(db.Integer, nullable=False)
    response=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime,nullable=False, default=datetime.now())
    
class CategoryAllotted(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.Boolean,default=False) #requested by staff,approved by admin

class Topic(db.Model):
    topic_id = db.Column(db.Integer, primary_key=True)
    solution_post_id = db.Column(db.Integer, default=-1)    #-1 means unresolved topics 

class Matches(db.Model):
    topic_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    resolved = db.Column(db.Boolean, default=False)

class FAQ(db.Model):
    topic_id = db.Column(db.Integer, primary_key=True)
    solution_post_id = db.Column(db.Integer,nullable=False) #talk to him
    is_approved = db.Column(db.Boolean,default=False) #requested by staff,approved by admin

class Subscription(db.Model):
    user_id = db.Column(db.Integer, primary_key=True,default=0)
    category = db.Column(db.Integer, primary_key=True,default=0) #category id

