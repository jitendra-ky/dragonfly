from django.http import HttpResponse
from django.urls import get_resolver
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


def api_index_view(request):
    """Auto-generate API endpoint index page."""
    resolver = get_resolver()
    endpoints = []
    
    # Get filter parameter from request
    starts_with = request.GET.get('starts_with', '')

    def extract_urls(patterns, prefix='', starts_with=''):
        """Recursively extract all URL patterns including included ones."""
        for pattern in patterns:
            try:
                # Handle included URL patterns
                if hasattr(pattern, 'url_patterns'):
                    # This is an included URLconf
                    new_prefix = prefix + str(pattern.pattern).replace('^', '').replace('$', '')
                    extract_urls(pattern.url_patterns, new_prefix, starts_with)
                else:
                    # This is a regular URL pattern
                    url_path = prefix + str(pattern.pattern).replace('^', '').replace('$', '')
                    url_name = pattern.name
                    
                    if url_name:
                        clean_path = '/' + url_path.replace('\\', '').strip('/')
                        if clean_path == '/':
                            clean_path = '/'
                        else:
                            clean_path = clean_path + ('/' if not clean_path.endswith('/') else '')
                        
                        # Filter URLs based on starts_with parameter
                        if not starts_with or clean_path.startswith(starts_with):
                            view_class = getattr(pattern.callback, 'view_class', None)
                            view_name = view_class.__name__ if view_class else str(pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else pattern.callback)
                            
                            endpoints.append({
                                'path': clean_path,
                                'name': url_name,
                                'view': view_name
                            })
            except Exception as e:
                continue
    
    # Extract all URLs recursively
    extract_urls(resolver.url_patterns, starts_with=starts_with)
    
    # Sort endpoints by path for better organization
    endpoints.sort(key=lambda x: x['path'])
    
    # Generate minimal HTML
    filter_info = f" (filtered by: {starts_with})" if starts_with else ""
    html = f"""<html><head><title>API Endpoints</title></head><body>
    <h1>Available API Endpoints{filter_info}</h1>
    <form method="get">
        <label>Filter by URL starting with: </label>
        <input type="text" name="starts_with" value="{starts_with}" placeholder="/api/">
        <button type="submit">Filter</button>
        <a href="/api/">Clear</a>
    </form>
    <table border="1" cellpadding="5">
    <tr><th>Path</th><th>Name</th><th>View</th><th>Link</th></tr>"""
    
    for endpoint in endpoints:
        html += f"""<tr>
        <td>{endpoint['path']}</td>
        <td>{endpoint['name']}</td>
        <td>{endpoint['view']}</td>
        <td><a href="{endpoint['path']}" target="_blank">Test</a></td>
        </tr>"""
    
    html += "</table></body></html>"
    return HttpResponse(html)


class HealthCheckView(APIView):
    """Health check endpoint to verify server status."""

    def get(self, _request: Request) -> Response:
        """Return a simple health check response."""
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
