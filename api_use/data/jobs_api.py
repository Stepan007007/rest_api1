import flask
from flask import jsonify, make_response, request

from data import db_session
from data.jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).all()
        return jsonify(
            {
                'jobs':
                    [item.to_dict(only=('team_leader', 'job', 'work_size', 'collaborators', 'is_finished'))
                     for item in jobs]
            }
        )
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators', 'is_finished']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    elif any(key not in ['team_leader', 'job', 'work_size', 'collaborators', 'is_finished'] for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    jobs = Jobs(
        team_leader=request.json['team_leader'],
        job=request.json['job'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        is_finished=request.json['is_finished']
    )
    db_sess.add(jobs)
    db_sess.commit()
    return jsonify({'id': jobs.id})


@blueprint.route('/api/jobs/<job_id>', methods=['GET'])
def jobs_id(job_id):
    db_sess = db_session.create_session()
    if not job_id.isdigit():
        return make_response(jsonify({'error': 'Not found'}), 404)
    jobs = db_sess.query(Jobs).get(int(job_id))
    if not jobs:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'job':
                [jobs.to_dict(only=('team_leader', 'job', 'work_size', 'collaborators',
                                    'start_date', 'end_date', 'is_finished', 'user.name'))]
        }
    )


@blueprint.route('/api/del_jobs/<int:jobs_id>', methods=['DELETE'])
def delete_jobs(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(jobs_id)
    if not jobs:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})

@blueprint.route('/api/edit_job/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    required_fields = ['team_leader', 'job', 'work_size', 'collaborators', 'is_finished']
    if not all(key in request.json for key in required_fields):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Job not found'}), 404)
    job.team_leader = request.json.get('team_leader')
    job.job = request.json.get('job')
    job.work_size = request.json.get('work_size')
    job.collaborators = request.json.get('collaborators')
    job.is_finished = request.json.get('is_finished')
    db_sess.commit()
    return jsonify({'success': 'OK'})
