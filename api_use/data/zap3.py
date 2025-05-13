from users import User
from jobs import Jobs
from db_session import global_init, create_session

db = input()
global_init(db)
db_sess = create_session()
for user in db_sess.query(User).filter(User.age < 18):
    print(f'<Colonist> {user.id} {user.name} {user.surname} {user.age} years')