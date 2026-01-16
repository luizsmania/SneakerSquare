"""
Vercel serverless function for Django
"""
import os
import sys
from pathlib import Path
from io import BytesIO

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneaker_square.settings')

# Import Django and setup
import django
django.setup()

from django.core.wsgi import get_wsgi_application

# Get Django WSGI application
application = get_wsgi_application()


def handler(request):
    """
    Vercel serverless function handler for Django
    """
    from django.core.handlers.wsgi import WSGIRequest
    
    # Extract request data - Vercel passes request as a dict
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    headers = request.get('headers', {}) or {}
    query_params = request.get('queryStringParameters', {}) or {}
    body = request.get('body', '') or ''
    
    # Build query string
    query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()]) if query_params else ''
    
    # Parse host
    host = headers.get('host', 'localhost')
    if ':' in host:
        server_name, server_port = host.split(':', 1)
    else:
        server_name = host
        server_port = '443' if headers.get('x-forwarded-proto') == 'https' else '80'
    
    # Determine URL scheme
    url_scheme = 'https' if headers.get('x-forwarded-proto') == 'https' else 'http'
    
    # Prepare body
    if body:
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        else:
            body_bytes = body
    else:
        body_bytes = b''
    
    # Convert Vercel request to Django WSGIRequest environment
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body_bytes)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': server_port,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': url_scheme,
        'wsgi.input': BytesIO(body_bytes),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers (convert to HTTP_* format)
    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value
    
    # Create Django request
    django_request = WSGIRequest(environ)
    
    # Get response from Django
    response = application(django_request)
    
    # Convert Django response to Vercel format
    response_body = b''.join(response)
    
    # Build response headers dict
    response_headers = {}
    for key, value in response.items():
        response_headers[key] = value
    
    # Ensure Content-Type is set
    if 'Content-Type' not in response_headers:
        response_headers['Content-Type'] = 'text/html; charset=utf-8'
    
    # Return Vercel-compatible response
    return {
        'statusCode': response.status_code,
        'headers': response_headers,
        'body': response_body.decode('utf-8', errors='replace')
    }
