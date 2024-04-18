from application import app, api, celery

from application.apiuser import *
from application.apistaff import *
from application.apiadmin import * 
from application.apigeneral import *

########################GENERAL APIS###################################

api.add_resource(Notifications, '/api/notifications')
api.add_resource(CategoryTopics, '/api/topics')
api.add_resource(TopicPosts, '/api/posts')
api.add_resource(Categories, '/api/categories')
api.add_resource(Verification, '/api/discourse/self_account/activate')
api.add_resource(Registration, '/api/discourse/register')
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