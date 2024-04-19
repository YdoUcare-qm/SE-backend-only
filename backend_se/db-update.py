from application import app
from application.models import *

db.session.query(CategoryAllotted).delete()
db.session.commit()
# Create 10 users
category_allotted = [
    {'staff_id': 2, 'category':5,'is_approved':True},
    {'staff_id': 2, 'category':7,'is_approved':True},
    {'staff_id': 2, 'category':8,'is_approved':True},
    {'staff_id': 2, 'category':6,'is_approved':True},
    {'staff_id': 3, 'category':6,'is_approved':True},
    {'staff_id': 6, 'category':8,'is_approved':True},


]


# Add users to the database
for ca in category_allotted:
    allotted = CategoryAllotted(**ca)
    db.session.add(allotted)

# Commit the changes to the database
db.session.commit()
