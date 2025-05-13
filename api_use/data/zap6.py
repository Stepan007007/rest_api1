from data.users import User
from data.jobs import Jobs
from data.db_session import global_init, create_session

db = input()
global_init(db)
db_sess = create_session()
m = 0
data = []
for job in db_sess.query(Jobs):
    if len(job.collaborators.split(',')) > m:
        data = [job.team_leader]
        m = len(job.collaborators)
    elif len(job.collaborators.split(',')) == m:
        data.append(job.team_leader)
for user in db_sess.query(User).filter(User.id.in_(data)):
    print(user.name, user.surname)