from application import app
from application.models import *

db.drop_all()
db.create_all()


# Create 10 users
users_data = [
    {'name': 'Admin', 'username': 'admin', 'password': 'admin', 'email': '21f1007034@ds.study.iitm.ac.in', 'role': 3, 'discourse_id': 1,'status':True},
    {'name': 'User 1', 'username': 'user1', 'password': 'user123456', 'email': 'user1@email.com', 'role': 2, 'discourse_id': 2,'status':True},
    {'name': 'User 2', 'username': 'user2', 'password': 'user123456', 'email': 'user2@email.com', 'role': 2, 'discourse_id': 3,'status':True},
    {'name': 'User 3', 'username': 'user3', 'password': 'user123456', 'email': 'user3@email.com', 'role': 1, 'discourse_id': 4,'status':True},
    {'name': 'User 4', 'username': 'user4', 'password': 'user123456', 'email': 'user4@email.com', 'role': 1, 'discourse_id': 5,'status':True},
    {'name': 'User 5', 'username': 'user5', 'password': 'user123456', 'email': 'user5@email.com', 'role': 2, 'discourse_id': 6,'status':True},

]


# Add users to the database
for user_data in users_data:
    user = User(**user_data)
    db.session.add(user)

# Commit the changes to the database
db.session.commit()
