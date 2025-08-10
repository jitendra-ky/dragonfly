from django.http import HttpRequest, HttpResponse
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


def _extract_urls(
    patterns: list[URLPattern | URLResolver],
    endpoints: list[dict],
    prefix: str = "",
    starts_with: str = "",
) -> None:
    """Recursively extract all URL patterns including included ones."""
    for pattern in patterns:
        try:
            # Handle included URL patterns
            if hasattr(pattern, "url_patterns"):
                # This is an included URLconf
                new_prefix = prefix + str(pattern.pattern).replace("^", "").replace("$", "")
                _extract_urls(pattern.url_patterns, endpoints, new_prefix, starts_with)
            else:
                # This is a regular URL pattern
                url_path = prefix + str(pattern.pattern).replace("^", "").replace("$", "")
                url_name = pattern.name

                if url_name:
                    clean_path = "/" + url_path.replace("\\", "").strip("/")
                    if clean_path == "/":
                        clean_path = "/"
                    else:
                        clean_path = clean_path + ("/" if not clean_path.endswith("/") else "")

                    # Filter URLs based on starts_with parameter
                    if not starts_with or clean_path.startswith(starts_with):
                        view_class = getattr(pattern.callback, "view_class", None)
                        # Split long line for readability
                        if view_class:
                            view_name = view_class.__name__
                        elif hasattr(pattern.callback, "__name__"):
                            view_name = pattern.callback.__name__
                        else:
                            view_name = str(pattern.callback)

                        endpoints.append({
                            "path": clean_path,
                            "name": url_name,
                            "view": view_name,
                        })
        except Exception:  # noqa: S112, PERF203
            # Continue processing other patterns if one fails
            continue


def _generate_html(endpoints: list[dict], starts_with: str) -> str:
    """Generate HTML for the API endpoint list."""
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
    return html


def api_index_view(request: HttpRequest) -> HttpResponse:
    """Auto-generate API endpoint index page."""
    resolver = get_resolver()
    endpoints: list[dict] = []

    # Get filter parameter from request
    starts_with = request.GET.get("starts_with", "")

    # Extract all URLs recursively
    _extract_urls(resolver.url_patterns, endpoints, starts_with=starts_with)

    # Sort endpoints by path for better organization
    endpoints.sort(key=lambda x: x["path"])

    # Generate and return HTML
    html = _generate_html(endpoints, starts_with)
    return HttpResponse(html)


class HealthCheckView(APIView):
    """Health check endpoint to verify server status."""

    def get(self, _request: Request) -> Response:
        """Return a simple health check response."""
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
