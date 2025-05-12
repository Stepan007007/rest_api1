from flask import jsonify, make_response, request
from . import db_session
from .marsone import Jobs
import flask
from datetime import datetime

blueprint = flask.Blueprint('jobs_api', __name__, template_folder='templates')


@blueprint.route('/api/jobs/<jobs_id>')
def get_one_jobs(jobs_id):
    try:
        jobs_id = int(jobs_id)
    except Exception as e:
        return make_response(jsonify({'error': 'index_error'}), 404)
    ses = db_session.create_session()
    job = ses.query(Jobs).get(jobs_id)
    if not job:
        return make_response(jsonify({'error': 'not_found'}), 404)
    return jsonify(
        {
            'job': job.to_dict(only=(
            'id', 'job', 'work_size', 'team_leader', 'collaborators', 'start_date', 'end_date', 'is_finished'))
        }
    )


@blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    ses = db_session.create_session()
    jobs = ses.query(Jobs).all()
    if not jobs:
        return make_response(jsonify({'error': 'not_found'}), 404)
    return jsonify(
        {
            'job': [job.to_dict(only=(
            'id', 'job', 'work_size', 'team_leader', 'collaborators', 'start_date', 'end_date', 'is_finished')) for job
                    in jobs]
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    sp = ['job', 'work_size', 'team_leader', 'collaborators', 'start_date', 'end_date', 'is_finished']
    if not request.json:
        return make_response(jsonify({'error': 'need data'}), 400)

    elif not all(key in request.json for key in sp):
        return make_response(jsonify({'errors': 'neeed_moredata'}), 400)

    try:

        ses = db_session.create_session()
        new_job = Jobs(
            team_leader=request.json['team_leader'],
            job=request.json['job'],
            work_size=request.json['work_size'],
            collaborators=request.json['collaborators'],
            start_date=datetime.fromisoformat(request.json['start_date']),  # Конвертация строки в datetime
            end_date=datetime.fromisoformat(request.json['end_date']),
            is_finished=request.json['is_finished']
        )
        ses.add(new_job)
        ses.commit()
        return jsonify({'id': new_job.id})
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_jobs(job_id):
    ses = db_session.create_session()
    try:
        job = ses.query(Jobs).get(job_id)
        if not job:
            return make_response(jsonify({'error': 'pls send corret id'}), 400)
        ses.delete(job)
        ses.commit()
        return jsonify({'success': 'ok'})
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def put_jobs(job_id):
    try:
        if not request.json:
            return make_response(jsonify({'error': 'need data'}), 400)
        sp = ['job', 'work_size', 'team_leader', 'collaborators', 'start_date', 'end_date', 'is_finished']
        ses = db_session.create_session()
        job = ses.query(Jobs).get(job_id)
        if job is None:
            return make_response(jsonify({'error': 'pls send corret id'}), 400)
        elif not all(key in request.json for key in sp):
            return make_response(jsonify({'errors': 'neeed_moredata'}), 400)

        job.team_leader = request.json['team_leader']
        job.job = request.json['job']
        job.work_size = request.json['work_size']
        job.collaborators = request.json['collaborators']
        job.start_date = datetime.fromisoformat(request.json['start_date'])  # Конвертация строки в datetime
        job.end_date = datetime.fromisoformat(request.json['end_date'])
        job.is_finished = request.json['is_finished']
        ses.commit()

        return jsonify({"sec": f'{job.id}'})

    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)