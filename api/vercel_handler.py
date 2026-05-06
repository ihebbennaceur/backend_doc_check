"""
Vercel Serverless handler for Django.
Converts Vercel request/response to WSGI format.
"""

import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Import WSGI app
from myproject.vercel_wsgi import application


async def handler(request, response):
    """
    Main handler for Vercel.
    """
    # Convert Vercel request to WSGI environ
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query if request.query else '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', ''),
        'SERVER_NAME': request.headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': request.headers.get('host', 'localhost:80').split(':')[1] if ':' in request.headers.get('host', '') else '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body if hasattr(request, 'body') else None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add headers to environ
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value
    
    # Call WSGI app
    response_started = False
    status = None
    response_headers = []
    
    def start_response(status_str, headers, exc_info=None):
        nonlocal response_started, status, response_headers
        if exc_info:
            try:
                if response_started:
                    raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info = None
        elif response_started:
            raise RuntimeError("Response has already started")
        
        response_started = True
        status = int(status_str.split(' ', 1)[0])
        response_headers = headers
        return lambda x: None  # write() function
    
    # Get response body
    response_body = b''
    for data in application(environ, start_response):
        if data:
            response_body += data
    
    # Send response
    response.status(status or 200)
    
    for header_name, header_value in response_headers:
        response.set_header(header_name, header_value)
    
    response.send(response_body)
