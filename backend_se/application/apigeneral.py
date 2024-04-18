from flask_restful import Resource, request, abort
import requests
from flask import jsonify
from datetime import datetime
from dateutil import tz, parser
from application.models import *
from application.models import db
from application.routes import token_required
from application.workers import celery
from celery import chain
from application.tasks import send_email, response_notification
from datetime import datetime, timedelta
import jwt
from .config import Config
from werkzeug.exceptions import HTTPException 
from application import index

API_TOKEN="77a052969dae8a3d77c97021a8b53ef18d191761a4079c0487f255eadfcfcaff"
USER="21f1007034"                ##Just configured only for Unit Testing

headers = {
            "Api-key": API_TOKEN,
            "Api-Username": USER
        }

class Categories(Resource): 
    # LIST ALL CATEGORIES
    def get(self):
       x=requests.get("http://localhost:4200/categories.json")
       return x.json()
    
class CategoryTopics(Resource):

    #GET ALL TOPICS BY EITHER CATEGORY ID OR CATEGORY SLUG
    def post(self):
        try:
            r=request.json
            slug='j'
            id=r.get('id')
            
            response = requests.get(f'http://localhost:4200/c/{slug}/{id}.json', headers=headers)
            return response.json()
        except:
            abort(401,message="error getting topics")

class TopicPosts(Resource):
    #POSTS UNDER A TOPIC
    def post(self):
        try:
            r=request.json
            id=r.get('id')
            
            response = requests.get(f'http://localhost:4200/t/{id}.json', headers=headers)
            return response.json()
        except:
            abort(401,message="error getting posts")

class Notifications(Resource):
    #GET ALL NOTIFICATIONS BY USER ID
    def get(self):
        
        response = requests.get(f'http://localhost:4200/notifications.json',headers=headers)
        return response.json()
    

 
#for registering new user using discourse data  
#ajeet
class Registration(Resource):
    def post(self):
        if request.is_json:
            email = request.json["email"]
            password = request.json["password"]
        else:
            email = request.form["email"]
            password = request.form["password"]
        email=email
        check1=User.query.filter_by(email=email).first()
        if(check1 and check1.status==0):
            # verification_token = secrets.token_urlsafe(16)
            # print(verification_token)
            # send_verification_email(email, verification_token)
            #abort(400, message = "alreary registerd, verify your email")
            return jsonify({"Message":"alreary registerd, verify your email"})
        elif(check1 and check1.status==1):
            #abort(404, message = "already an active user, login")
            return jsonify({"message":"already an active user, login"})
        flag=["active","seen","last_emailed"]
        data={
            "show_emails": "true",
            "email":email
        }
        x=requests.get(f"http://localhost:4200/admin/users/list/{flag}.json",params=data,headers=headers)
        if x.json():
            out1=x.json()
            did=out1[0]['id']
            duser=out1[0]['username']
            dname=out1[0]['name']
            user1=User(username=duser,
                       name=dname,
                       password=password,
                       email=email,
                       role=1,
                       discourse_id=did
            )
            db.session.add(user1) 
            db.session.commit()
            # verification_token = secrets.token_urlsafe(16)
            # send_verification_email(email, verification_token)
            return jsonify({"id":did,"name":dname,"user":duser,"email":email,"role":1,"message": "do email verification to login","code":200})
        else:
            return jsonify({"Message":"You are not authorized to access this feature."})
            #abort(400, message = "You are not authorized to access this feature.")

#email verification to activate and deactivate
#ajeet      
class Verification(Resource):
    def get(self):
        email="21f1007034@ds.study.iitm.ac.in"
        user1=User.query.filter_by(email=email).first()
        print(user1)
        if(user1.status==0):
            user1.status=1
            db.session.add(user1)
            db.session.commit()  
            return jsonify({"message":"activated"})
        elif(user1.status==1):
            user1.status=0
            db.session.add(user1)
            db.session.commit() 
            return jsonify({"message":"already activate"})
         

#login user using mail, user name, user id
#ajeet
class Login(Resource):
    def post(self):
        #create_default_admin()
        print("test login1")
        flag=False
        if request.is_json:
            email = request.json["email"]
            password = request.json["password"]
        else:
            email = request.form["email"]
            password = request.form["password"]
        test = User.query.filter_by(email=email).first()
        if(test is None):
            test=User.query.filter_by(username=email).first()
        if(test is None):
            test=User.query.filter_by(discourse_id=email).first()
        # print(test)
        if (test is None):
            abort(409,message="User does not exist")
        elif (test.password == password):
            if(test.status==1):
                id=str(test.discourse_id)
                print(id)
                x=requests.get(f"http://localhost:4200/admin/users/{id}.json",headers=headers)
                print("check1",x.json())
                if x.json():
                    out1=x.json()
                    did=out1['id']
                    duser=out1['username']
                    dname=out1['name']
                    print("update3")
                    y=requests.get(f"http://localhost:4200/u/{duser}/emails.json",headers=headers)
                    demail=y.json()["email"]
                    print(demail)
                    if (demail!=test.email or duser!=test.username):
                        test.email=demail
                        test.username=duser
                        test.name=dname
                        db.session.add(test)
                        db.session.commit()
                        flag=True
                        print("update4")

                token = jwt.encode({
                    'id': test.id,
                    'exp': datetime.now() + timedelta(minutes=80)
                }, Config.SECRET_KEY, algorithm="HS256")
                # access_token = create_access_token(identity=email)
                print(token)
            else:
                abort(403, message="Account is not activated, verify email")
            if(flag):
                return jsonify({"message":"User email and user_id has been updated, kindly use new discorse email or user_id from next time", "token":token,"user_id":test.id,"role":test.role})
            else:
                return jsonify({"message":"Loggedin successfully !", "token":token,"id":test.id,"role":test.role})
        else:
            abort(401, message="Bad Email or Password")