import requests
import os


class StravaClient:
    def __init__(self):
        self.client_id = os.environ.get('STRAVA_CLIENT_ID')
        self.client_secret = os.environ.get('STRAVA_CLIENT_SECRET')
        self.auth_url = "https://www.strava.com/oauth/token"
        self.base_url = "https://www.strava.com/api/v3"

    def refresh_access_token(self, refresh_token):
        """Exchanges a refresh token for a new access token."""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        response = requests.post(self.auth_url, data=payload)
        return response.json()

    def get_headers(self, access_token):
        return {'Authorization': f'Bearer {access_token}'}

    def get_activities(self, access_token, page=1):
        """Fetches a page of activities"""
        url = f"{self.base_url}/athlete/activities"
        params = {'page': page, 'per_page': 50}
        response = requests.get(url, headers=self.get_headers(access_token), params=params)
        return response.json()
