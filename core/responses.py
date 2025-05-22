# core/responses.py
# Helper functions to standardize JSON API responses

from flask import jsonify


def error(msg, code):
    """
    Return a standardized error response.

    Args:
        msg (str): Error message.
        code (int): HTTP status code.

    Returns:
        Response: Flask JSON response with {'error': msg} and given status code.
    """
    return jsonify({"error": msg}), code


def success(data=None, code=200):
    """
    Return a standardized success response.

    Args:
        data (dict, optional): Payload to include under 'data' key. Defaults to None.
        code (int, optional): HTTP status code. Defaults to 200.

    Returns:
        Response: Flask JSON response with {'data': data} and status code.
    """
    payload = {"data": data or {}}
    return jsonify(data or {}), code    
