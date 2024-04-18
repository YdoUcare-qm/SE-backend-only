from application import app, api, celery

from application.apiuser import *
from application.apistaff import *
from application.apiadmin import * 
from application.apigeneral import *
from application.ticketapi import *


# api.add_resource(TicketAPI, '/api/ticket')
# api.add_resource(UserAPI,'/api/user')
# #api.add_resource(FAQApi, '/api/faq', '/api/faq/<int:ticket_id>')
# api.add_resource(ResponseAPI_by_ticket, '/api/respTicket') #For getting responses with ticket_id
# api.add_resource(ResponseAPI_by_response_id, '/api/respResp') #For getting responses with response_id
# api.add_resource(ResponseAPI_by_user, '/api/respUser') #For getting responses with user id.
# api.add_resource(TicketAll, '/api/ticketAll') #For getting all tickets
# api.add_resource(getResolutionTimes, '/api/getResolutionTimes') # For getting resolution times of support agents, only accessible to managers.
# api.add_resource(flaggedPostAPI, '/api/flaggedPosts') #For getting the flagged posts.
# api.add_resource(getResponseAPI_by_ticket,'/api/getResponseAPI_by_ticket') #Only for getting the responses by ticket ID
# api.add_resource(ImportResourceUser,'/api/importUsers')
# api.add_resource(TicketDelete,'/api/ticket/<int:ticket_id>')
# api.add_resource(UserDelete,'/api/user/<int:user_id>') 
# api.add_resource(ResponseAPI_by_responseID_delete, '/api/respRespDel/<int:responder_id>/<int:response_id>')

########################GENERAL APIS###################################

api.add_resource(Notifications, '/api/notifications')
api.add_resource(CategoryTopics, '/api/topics')
api.add_resource(TopicPosts, '/api/posts')
api.add_resource(Categories, '/api/categories')
#discourse apis from ajeet
api.add_resource(Verification, '/api/discourse/self_account/activate')
api.add_resource(Registration, '/api/discourse/register')
# api.add_resource(Sitaram, '/api/discourse/sitaram_user')
# api.add_resource(Discourse_post, '/api/discourse/sitaram_post1')
api.add_resource(Login,'/login')

########################USER APIS######################################

api.add_resource(UserProfile, '/api/user/profile')
api.add_resource(YourTickets, '/api/user/tickets')
api.add_resource(NewTicket, '/api/user/newticket')
api.add_resource(Recommendations, '/api/user/recommendations')
api.add_resource(MatchTopic, '/api/user/match')
api.add_resource(FAQs, '/api/user/faqs')
api.add_resource(Subscriptions, '/api/user/subscriptions')
api.add_resource(ToggleSubscription, '/api/user/togglesub')
api.add_resource(FullTicket, '/api/user/fullticket')
########################STAFF APIS#####################################
api.add_resource(CreateTopic, '/api/staff/createtopic')
api.add_resource(EditTopic, '/api/staff/edittopic')
api.add_resource(Merge, '/api/staff/merge')
api.add_resource(ResolveTopic, '/api/staff/resolvetopic')
api.add_resource(ResolveTicket, '/api/staff/resolveticket')
#apis by ajeet
api.add_resource(StaffProfile, '/api/staff/profile')
api.add_resource(AllottedCategory, '/api/staff/category')
api.add_resource(Respond, '/api/staff/respond')
api.add_resource(RequestFAQ, '/api/staff/requestfaq')
api.add_resource(RequestCategory, '/api/staff/requestcategory')
api.add_resource(UpdateSetting, '/api/staff/updatesetting')
########################ADMIN APIS#####################################

api.add_resource(CreateCategory, '/api/admin/createcategory')
api.add_resource(EditCategory, '/api/admin/editcategory')
api.add_resource(AdminHome, '/api/admin/home')
#for getting staff and user details , use "/users" api and use jinja2 on frontend 
# put condition for staff management role==2
#for user management role==1
api.add_resource(AdminGetRequest,'/api/admin/admingetrequest')
api.add_resource(AdminPostRequest,'/api/admin/adminpostrequest')
api.add_resource(RevokeStaff,'/api/admin/revokestaff')
api.add_resource(RevokeCategory,'/api/admin/revokecategory')
api.add_resource(AddStaff,'/api/admin/addstaff')
api.add_resource(BlockUser,'/api/admin/blockuser')

from application.routes import *
if __name__ == '__main__':
  # Run the Flask app
  app.run(debug=True,port=5000)