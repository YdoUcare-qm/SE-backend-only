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
    def post(self):
        try:
            r=request.json
            id=r.get('user_id')
            user=User.query.filter_by(id=id).first()
            d = {
                'name': user.name,
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
    def post(self):
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

    def post(self):
        try:
            r=request.json
            catslug=r.get('cat-slug')  #cat slug
            params = {
                "q": '#'+catslug,
                "order":"latest"
            }
            response=requests.get(f'http://localhost:4200/search.json',params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)
            abort(401,message="Failed to get recommendations")
        

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

class Subscriptions(Resource):
    # @token_required
    def post(self):
        try:
            r=request.json
            subscriber=r.get('user_id')
            categories=Subscription.query.filter_by(user_id=subscriber).all()
            result=[]
            for c in categories:
                d={}
                d['cid']=c.category
                result.append(d)
            return jsonify({"categories": result})
        except:
            abort(401,message="Couldn't fetch User Subscriptions")

class ToggleSubscription(Resource):
    # @token_required
    def post(self):
        try:
            r=request.json
            user_id=r.get('user_id')
            print(user_id)
            category=r.get('category')
            sub=Subscription.query.filter_by(user_id=user_id,category=category).first()
            if not sub:
                print("no subscription present")
                sub=Subscription(
                    user_id=user_id,
                    category=category
                )
                db.session.add(sub)
                db.session.commit()
                print("subbed")
                return jsonify({"message": "Subscribed"})
            else:
                print("subscription present")
                db.session.delete(sub)
                db.session.commit()
                print("unsubbed")
                return jsonify({"message": "Unsubscribed"})
        except:
            print("error in toggling")
            abort(401,message="Error in Toggling")

class FullTicket(Resource):
    # @token_required
    def post(self):
        
        r=request.json
        ticket_id=r.get('ticket_id')
        user_id=r.get('user_id')
        print(ticket_id,user_id)
        t=Ticket.query.filter_by(id=ticket_id).first()
        print("t",t)
        if not t:
            abort(401,message="No such ticket")
        if int(t.creator) != int(user_id):
            print(user_id,t.creator)
            abort(401,message="This ticket is private to its author")
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
        print("ticket fetch done",d)
        r=Response.query.filter_by(ticket_id=ticket_id).first()
        e={}
        if r:
            e['responder']=r.responder
            e['response']=r.response
            e['date']=r.date 
        return jsonify({"ticket": d,
                        "response":e})
        
