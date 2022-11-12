import requests
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)


@api.route('/libraries', methods=['GET'])
def list_libraries():
    response = requests.get('http://library:8060/api/v1/libraries', params=dict(request.args))
    return jsonify(response.json()), response.status_code


@api.route('/libraries/<library_uid>/books', methods=['GET'])
def get_library_books(library_uid):
    response = requests.get(f'http://library:8060/api/v1/libraries/{library_uid}/books', params=dict(request.args))
    return jsonify(response.json()), response.status_code
