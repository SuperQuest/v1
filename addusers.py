from app.models import User, Role, Project, Post

Role.insert_roles()

from werkzeug.security import generate_password_hash
password_hash=generate_password_hash('g')

one = User(email="jamoen7@gmail.com",
			  username="jamoen7",
			  new_role="student",
			  school="new-country",
			  password_hash=password_hash,
			  confirmed=True)

two = User(email="moenx271@umn.com",
			  username="moenx271",
			  new_role="teacher",
			  school="blake",
			  password_hash=password_hash,
			  confirmed=True)	

three = User(email="justin@superquest.co",
			  username="justin",
			  new_role="mentor",
			  expertise="hardware hacking, painting, entrepreneurship",
			  linkedin_id="highstatus",
			  interests="Arduino, Flying Machines, Service projects",
			  password_hash=password_hash,
			  confirmed=True)

db.session.add(one)
db.session.add(two)
db.session.add(three)
db.session.commit()	  

User.generate_fake()
Post.generate_fake()
Project.generate_fake()

for post in Post.query.filter_by(author=None): db.session.delete(post)


subjects =['mathematics', 'science', 'engineering', 'literature', 'music', \
		   'service', 'entrepreneurship', 'art', 'public-service',
		   'creative-writing']

length = len(subjects)

projects = []
all_students = User.query.filter_by(new_role="student").all()

for i in range(20):
	name = 'Project' + str(i)
	description = "a total work of Genius"
	subject = subjects[i%length]
	students=[all_students[0]]
	schools = [students[0].school]
	project = Project(name=name, description=description, 
					  subject=subject, students=students)
	
	db.session.add(project)

db.session.commit()
