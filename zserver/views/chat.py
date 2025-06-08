from urllib.request import Request

from django.shortcuts import render
from django.views import View

from zserver.utils import get_env_var


class Chat(View):

    def get(self, request: Request, contact_id: int):
        """Render the home page."""
        context = {
            "name" : "John Doe",
            "env_var" : get_env_var(),
            contact_id: contact_id,
        }
        return render(request, "home.html", context)
