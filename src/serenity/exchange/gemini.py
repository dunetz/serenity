import requests


class GeminiCredentials:
    """
    Base class for public or private credentials.
    """


class PublicCredentials(GeminiCredentials):
    """
    Public credentials are a no-op for request signing.
    """


class GeminiConnection:
    """
    Primary client entry point for Gemini API connection
    """

    def __init__(self, credentials: GeminiCredentials = PublicCredentials(), api_url='https://api.gemini.com/v1'):
        self.credentials = credentials
        self.api_url = api_url.rstrip('/')

    def get_products(self):
        r = requests.get(self.api_url + '/symbols')
        return r.json()
