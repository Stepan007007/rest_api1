import flask
from flask import jsonify
from . import db_session
from .marsone import Jobs

blueprints = flask.Blueprint('jobs_api', __name__, template_folder='templates')


@blueprints.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    news = db_sess.query(Jobs).all()
    return jsonify(
        {
            'news':
            [item.to_dict(only=('id', 'job', 'work_size', 'team_leader', 'collaborators', 'is_finished'))
                 for item in news]
        }
    )