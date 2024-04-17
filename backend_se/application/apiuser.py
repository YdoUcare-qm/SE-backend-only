from flask_restful import Resource, request, abort
from flask import jsonify
import requests
from datetime import datetime
from dateutil import tz, parser
from application.models import *
from application.models import  db
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
USER="21f1007034"              ##Just configured only for Unit Testing

headers = {
            "Api-key": API_TOKEN,
            "Api-Username": USER
        }



  
class UserProfile(Resource):
    # @token_required
    def get(self):
        try:
            r=request.json
            id=r.get('user_id')
            user=User.query.filter_by(id=id).first()
            d = {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'discourse_id': user.discourse_id,
                'status': user.status,
                'notification': user.notification,
                'email_notif': user.email_notif,
                'webhook_notif': user.webhook_notif
                }   
            return jsonify({"data": d})
        except:
            abort(401,message="Failed to fetch user details")


class YourTickets(Resource):
    # @token_required
    def get(self):
        r=request.json
        creator=r.get('user_id')
        ticket=Ticket.query.filter_by(creator=creator).all()
        result=[]
        for t in ticket:
            d={}
            d['id']=t.id
            d['title']=t.title
            d['description']=t.description
            d['date']=str(t.date)
            d['category']=t.category
            d['tags']=t.tags
            d['offensive']=t.offensive
            d['escalated']=t.escalated
            d['resolved']=t.resolved
            d['merged']=t.merged
            result.append(d)
        return jsonify({"data": result})
     
class NewTicket(Resource):       
    # @token_required
    def post(self):
        try:
            data=request.json
            ticket=Ticket(title=data['title'],
                        description=data['description'],
                        date=datetime.now(),
                        creator=data['creator'],
                        category=data['category'],
                        tags=data['tags'])
            db.session.add(ticket)
            db.session.commit()
            return jsonify({'message':'Ticket created successfully'})
        except:
            abort(401,message="Failed to create ticket")
        

class Recommendations(Resource):
    #GET RECOMMENDATIONS BEFORE CREATING TICKETS 
    #SO THAT USERS CAN VIEW/MATCH THEIR ISSUES

    def get(self):
        try:
            r=request.json
            category=r.get('category')  #cat id
            tags=r.get('tags') 
            response=requests.post()
            return response.json()
        except:
            abort(401,message="Failed to create ticket")
        

class MatchTopic(Resource):
    #Upon getting shown recommended topics,
    #if the user finds his issue listed there,
    #they can match it with that topic instead 
    #of creating a new ticket
    def post(self):
        try:
            r=request.json
            user_id=r.get('user_id')
            topic_id=r.get('topic_id')

            m=Matches(user_id=user_id,
                      topic_id=topic_id)
            db.session.add(m)
            db.session.commit()
            return jsonify({"message": "Ticket matched with Topic"})
        except:
            abort(401,message="Ticket didn't match")


class FAQs(Resource):
    def get(self):
        try:
            faqs=FAQ.query.all()
            data=[]
            for faq in faqs:
                id=faq.topic_id
                sol_id=faq.solution_post_id
                json={
                    "post_ids[]":sol_id
                }
                response = requests.put(f'http://localhost:4200/t/{id}/posts.json',json=json, headers=headers)
                data=data.append(response)
            return jsonify({"FAQS":data})
        except:
            abort(401,message="Error in fetching FAQ")