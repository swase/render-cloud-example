from flask import jsonify, Blueprint
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from auth.auth import AuthError, requires_auth


blueprint = Blueprint('error_handlers', __name__)

@blueprint.app_errorhandler(422)
def unprocessable(error):
    return (jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422)



@blueprint.app_errorhandler(404)
def unprocessable(error):
    return (jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404)

@blueprint.app_errorhandler(400)
def bad_request(error):
    return (
        jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"}),
        400
    )

@blueprint.app_errorhandler(AuthError)
def bad_request(error):
    return (
        jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error}),
        error.status_code
    )