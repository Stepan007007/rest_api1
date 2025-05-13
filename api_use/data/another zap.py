from users import User
from jobs import Jobs
from departments import Department
from db_session import global_init, create_session

db = input()
global_init(db)
db_sess = create_session()
dep1 = db_sess.query(Department).filter(Department.id == 1)
data = []
for i in dep1:
    for k in list(map(int, i.members.split(','))):
        count = 0
        for j in db_sess.query(Jobs).filter(Jobs.is_finished == 1):
            if str(k) in j.collaborators.split(','):
                count += j.work_size
        if count > 25 and k not in data:
            pos = db_sess.query(User).filter(User.id == k)
            print(pos.surname, pos.name)
            data.append(k)