from users import User
from jobs import Jobs
from db_session import global_init, create_session

db = input()
global_init(db)
db_sess = create_session()
for user in db_sess.query(User).filter(User.age < 21, User.address == 'module_1'):
    user.address = 'module_3'
    db_sess.commit()
