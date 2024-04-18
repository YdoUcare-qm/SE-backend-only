from application import app
from flask import request, jsonify, render_template, redirect
from .models import *
from flask_restful import Resource, request, abort
from datetime import datetime, timedelta
from flask_restful import Resource, request, abort
from flask import jsonify
from datetime import datetime
from dateutil import tz, parser
from application.models import *
from application.models import  db
from application.workers import celery
from celery import chain
from application.tasks import send_email, response_notification
from datetime import datetime, timedelta
import jwt
from .config import Config
from werkzeug.exceptions import HTTPException 
from application import index
 

local_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZXhwIjoxNzEyOTEyNzA4fQ.ozVWm0cYyoCHFiYa0AdweaYOXEHqSDAfNqK3tpgob54"

#jwt tockenisation de-dockenization
#ajeet
def token_required(function):
	@functools.wraps(function)
	def loggedin(*args,**kwargs):
		auth_token=None
		try:
			auth_token = request.headers['secret_authtoken']
		
		except:
			return jsonify({"status":'unsuccessful, missing the authtoken'})
		
		try: 
			output = jwt.decode(auth_token,Config.SECRET_KEY,algorithms=["HS256"])
			#print(output)
			user = User.query.filter_by(id = output["id"]).first()
		except:
			return jsonify({"status":"failure, your token details do not match"})
		
		return function(user,*args,**kwargs)
	return loggedin

@app.route("/")
def home():
    print(local_token)
    return 'hi'

@app.route("/sitaram", methods=["GET", "POST"])
def home_ram():      
    return render_template("login.html")

# @app.route("/signin", methods=["GET", "POST"])
# def post1():
#     email = request.form["email"]
#     password = request.form["password"]
#     test = User.query.filter_by(email_id=email).first()
#     # print(test)
#     if (test is None):
#         abort(409,message="User does not exist")
#     elif (test.password == password):
#         token = jwt.encode({
#             'user_id': test.user_id,
#             'exp': datetime.utcnow() + timedelta(minutes=300)
#         }, Config.SECRET_KEY, algorithm="HS256")
#         # access_token = create_access_token(identity=email)
#         # print(token)
#         global local_token
#         local_token=token
#         print(local_token)
#         return jsonify({"message":"Login Succeeded!", "token":token,"user_id":test.user_id,"role":test.role_id})
#     else:
#         abort(401, message="Bad Email or Password")


@app.route("/users", methods=["GET"])
#@token_required
def get_users():
	
#def get_users(current_user):
    #print(current_user,current_user.id,current_user.email)
	
    users = User.query.filter_by(status=1).all()
    results = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
			
        } for user in users]

    return jsonify(results)

@app.route("/user/<id>", methods=["GET"])
#@token_required
def get_user1(id):
	
#def get_users(current_user):
    #print(current_user,current_user.id,current_user.email)
	
    user = User.query.filter_by(id=id).first()
    result =[
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
			
        }]

    return jsonify(result)

@app.route("/cat/<id>", methods=["GET"])
def getcat(id):
    try:
        
        #id=user.id
        cat=CategoryAllotted.query.filter_by(staff_id=id , is_approved=1).all()
        cat_list=[]
        for c in cat:
            d = {
                'staff_id':c.staff_id,
                'category':c.category
                }   
            cat_list.append(d)
        return jsonify(cat_list)
    except:
        abort(401,message="Failed to fetch alloted category")

#send eamail
from mail import send_email
@app.route("/sendmail")
def sendmail():
    sender = "005ajeet@gmail.com"
    receiver = "21f1000907@ds.study.iitm.ac.in"
    sub="jai ho siatam ji from direct mail"
    msg="sitaram"
    file="ram.pdf"
    return send_email(sender,receiver,sub,msg,file)


# from application.workers import celery
# from application.tasks import send_email
# @app.route("/email", methods=["POST"])
# def post_email():
#     html = request.get_json()['html']
#     email = request.get_json()['email']
#     subject = request.get_json()['subject']
#     send_email.s(eid=email, html=html, subject=subject).apply_async()
#     return jsonify({'message': 'success'})

# from application.workers import celery
# from application.tasks import unanswered_ticket_notification
# @app.route("/notification")
# def get_notif():
#     unanswered_ticket_notification.s().apply_async()
#     return "OK"