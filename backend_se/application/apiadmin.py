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
from sqlalchemy import func
from application.tasks import *
from application.quickstart import *

API_TOKEN="77a052969dae8a3d77c97021a8b53ef18d191761a4079c0487f255eadfcfcaff"
USER="21f1007034"                ##Just configured only for Unit Testing

headers = {
            "Api-key": API_TOKEN,
            "Api-Username": USER
        }


class CreateCategory(Resource):
    #CREATE A CATEGORY
    #can be restricted to admin later
    def post(self):

        r=request.json

        data = {
            "name": r.get('name'),
            "color": r.get('color'),
            "text_color": "f0fcfd",
            "allow_badges": "true",
            "topic_featured_links_allowed": "true",
            "permissions": {
                "everyone": 1,
                "staff": 0
            },
            "search_priority": 0,
            "form_template_ids": []
            }
        
        x = requests.post("http://localhost:4200/categories.json", json=data,headers=headers)
        if x.status_code==200:
            return jsonify({"message":"Category created successfully"})
        else:
            abort(404,message="Failed to create Category")

class EditCategory(Resource):
    #UPDATE A CATEGORY
    #can be restricted to admin later
    def patch(self):

        r=request.json
        id=r.get('id')
        del r['id']
    
        x = requests.put(f'http://localhost:4200/categories/{id}.json', json=r,headers=headers)
        if x.status_code==200:
            return jsonify({"message":"Category updated successfully"})
        else:
            abort(404,message="Failed to update Category")

#apis by ajeet
class AdminHome(Resource):
    # @token_required
    def get(self):
        try:
            user_count=db.session.query(func.count()).filter(User.role == 1, User.status == 1).scalar()
            staff_count=db.session.query(func.count()).filter(User.role == 2, User.status == 1).scalar()
            ticket_count=db.session.query(func.count()).select_from(Ticket).scalar()
            topic_count=db.session.query(func.count()).select_from(Topic).scalar()
            category_count=db.session.query(func.count()).filter(CategoryAllotted.is_approved == 1).scalar()
            faq_count=db.session.query(func.count()).filter(FAQ.is_approved == 1).scalar()
            response_count=db.session.query(func.count()).select_from(Response).scalar()
            #user=User.query.all()
            #row_count = db.session.query(func.count()).select_from(User).scalar()
            print(user_count)
            return jsonify({'user_count':user_count,'staff_count':staff_count,'ticket_count':ticket_count,'topic_count':topic_count,'category_count':category_count,'faq_count':faq_count,'response_count':response_count})
        except:
            abort(401)
class AdminGetRequest(Resource):
    #@token_required
    def get(self):
        try:
            category_request=CategoryAllotted.query.filter_by(is_approved=0).all()
            faq_request=FAQ.query.filter_by(is_approved=0).all()
            cr=[{
                'user_id':cat.staff_id,
                'category':cat.category
            }for cat in category_request]
            faq=[{
                'topic_id':f.topic_id,
                'solution_post_it':f.solution_post_id
            }for f in faq_request]
            return jsonify({'category_request':cr,'faq_request':faq})
        except:
            abort(401,message='failed to get request')
    
class AdminPostRequest(Resource):
    #@token_required
    def patch(self): 
        try:
            '''
            input
            {
            "section":"",       //category OR faq
            "sid": ,
            "ctid":"" ,
            "response":  ,       //1 for accepted -1 for rejected
            }
            '''
            r=request.json
            if(r['section'] == 'category'):
                cat=CategoryAllotted.query.filter_by(staff_id=r['sid'], category=r['ctid']).first()  
                if(r['response']==-1):
                    db.session.delete(cat)
                    db.session.commit()
                elif(r['response']==1):
                    cat.is_approved=1
                    db.session.add(cat)
                    db.session.commit()
            elif(r['section'] =='faq' ):
                faq=FAQ.query.filter_by(topic_id=r['ctid'], solution_post_id=r['sid']).first()
                if(r['response']==-1):
                    db.session.delete(faq)
                    db.session.commit()
                    
                elif(r['response']==1):
                    faq.is_approved=1
                    db.session.add(faq)
                    db.session.commit()
            return jsonify({'message':"updated successfully"})
        except:
            abort(401,message='failed to get request')

class RevokeStaff(Resource):
    #@token_required
    def patch(self):
        """
        {
        "staff_id":,
        "revoked":    //"yes" or 1 
        }
        """
        try:
            r=request.json
            id=r['staff_id']
            k=r['revoked']
            user=User.query.filter_by(id=id).first()
            if(user is not None):
                if(k==1 or k=="yes"):
                    user.role=1
                    db.session.add(user)
                    db.session.commit()
                receiver = "21f1000907@ds.study.iitm.ac.in"
                sub="{} is simple user".format(user.username)
                msg="Dear {},".format(user.email)+ "\n\nYour support staff membership has been revoked."+"\n\nRegards"
                send_email_ER.delay(receiver,sub,msg) if user.email_notif==1 else None
                webhook_task.delay(msg)  if user.webhook_notif==1 else None
            return jsonify({'message':'staff status revoked'})
        except:
            abort(401,message="failed")

class RevokeCategory(Resource):
    #@token_required
    def delete(self):
        """
        {
        "staff_id":,
        "category":""    
        }
        """
        try:
            r=request.json
            staff_id=r['staff_id']
            cat=r['category']
            category=CategoryAllotted.query.filter_by(staff_id=staff_id, category=cat).first()
            user=User.query.filter_by(id=staff_id).first()
            if(category is not None):
                db.session.delete(category)
                db.session.commit()
            receiver = "21f1000907@ds.study.iitm.ac.in"
            sub="{} -category revoked".format(user.username)
            msg="Dear {},".format(user.email)+ "\n\nYour {} category has been revoked".format(cat)+"\n\nRegards"
            send_email_ER.delay(receiver,sub,msg) if user.email_notif==1 else None
            webhook_task.delay(msg)  if user.webhook_notif==1 else None
            return jsonify({'message':'category for given staff revoked'})
        except:
            abort(401,message="failed")

class AddStaff(Resource):
    #@token_required
    def patch(self):
        """
        {
        "user_id":,
        "add_staff":    //"yes" or 1 
        }
        """
        try:
            r=request.json
            id=r['user_id']
            k=r['add_staff']
            user=User.query.filter_by(id=id).first()
            if(user is not None):
                if(k==1 or k=="yes"):
                    user.role=2
                    db.session.add(user)
                    db.session.commit()
            receiver = "21f1000907@ds.study.iitm.ac.in"
            sub="{} is staff member".format(user.username)
            msg="Dear {},".format(user.email)+ "\n\nYou are a support staff now. welcome!"+"\n\nRegards"
            send_email_ER.delay(receiver,sub,msg) if user.email_notif==1 else None
            webhook_task.delay(msg)  if user.webhook_notif==1 else None
            return jsonify({'message':'user is staff now'})
        except:
            abort(401,message="failed")

class BlockUser(Resource):
    #@token_required
    def patch(self):
        """
        {
        "user_id":,
        "blocked":   //"yes" or 1 
        }
        """
        try:
            r=request.json
            id=r['user_id']
            k=r['blocked']
            user=User.query.filter_by(id=id).first()
            if(user is not None):
                if(k==1 or k=="yes"):
                    user.status=0
                    db.session.add(user)
                    db.session.commit()
            
            receiver = "21f1000907@ds.study.iitm.ac.in"
            sub="{} is blocked".format(user.username)
            msg="Dear {},".format(user.email)+ "\n\nYou are blocked due to violation of term and conditions."+"\n\nRegards"
            send_email_ER.delay(receiver,sub,msg) if user.email_notif==1 else None
            webhook_task.delay(msg)  if user.webhook_notif==1 else None
            return jsonify({'message':'user is blocked'})
        except:
            abort(401,message="failed")