from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Returns a consistent JSON error envelope:
    {
        "error": true,
        "message": "...",
        "details": { ... }   // optional field-level errors
    }
    """
    response = exception_handler(exc, context)

    if response is None:
        return response

    error_data = {
        'error': True,
        'message': _get_message(response),
        'details': {},
    }

    if isinstance(response.data, dict):
        detail = response.data.pop('detail', None)
        if detail:
            error_data['message'] = str(detail)
        if response.data:
            error_data['details'] = response.data
    elif isinstance(response.data, list):
        error_data['message'] = ' '.join(str(e) for e in response.data)

    response.data = error_data
    return response


def _get_message(response):
    messages = {
        status.HTTP_400_BAD_REQUEST: 'Validation failed.',
        status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided or are invalid.',
        status.HTTP_403_FORBIDDEN: 'You do not have permission to perform this action.',
        status.HTTP_404_NOT_FOUND: 'The requested resource was not found.',
        status.HTTP_405_METHOD_NOT_ALLOWED: 'This HTTP method is not allowed.',
    }
    return messages.get(response.status_code, 'An error occurred.')
