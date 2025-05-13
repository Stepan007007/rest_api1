from data.users import User
from data.jobs import Jobs
from data.db_session import global_init, create_session

db = input()
global_init(db)
db_sess = create_session()
for job in db_sess.query(Jobs).filter(Jobs.work_size < 20, Jobs.is_finished == 0):
    print(job)