"""Whoop OAuth 2.0 authentication handler."""
import os
import json
import secrets
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
import config


class WhoopAuth:
    """Handles Whoop OAuth 2.0 authentication and token management."""
    
    def __init__(self):
        self.client_id = config.WHOOP_CLIENT_ID
        self.client_secret = config.WHOOP_CLIENT_SECRET
        self.redirect_uri = config.WHOOP_REDIRECT_URI
        self.token_file = os.path.join(config.TOKENS_DIR, 'whoop_tokens.json')
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict:
        """Load tokens from file if they exist."""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_tokens(self):
        """Save tokens to file."""
        with open(self.token_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def generate_auth_url(self) -> tuple[str, str]:
        """
        Generate the authorization URL for OAuth flow.
        
        Returns:
            Tuple of (auth_url, state) where state is used for CSRF protection
        """
        state = secrets.token_urlsafe(8)
        scope = ' '.join(config.WHOOP_SCOPES)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state
        }
        
        auth_url = f"{config.WHOOP_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return auth_url, state
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Dictionary containing token information
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(config.WHOOP_TOKEN_URL, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Calculate expiration time
        expires_in = token_data.get('expires_in', 3600)
        expiry_time = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        
        self.tokens = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'expires_at': expiry_time,
            'token_type': token_data.get('token_type', 'Bearer')
        }
        
        self._save_tokens()
        return self.tokens
    
    def refresh_access_token(self) -> Dict:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            Dictionary containing new token information
        """
        if not self.tokens.get('refresh_token'):
            raise ValueError("No refresh token available. Please re-authenticate.")
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(config.WHOOP_TOKEN_URL, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Calculate expiration time
        expires_in = token_data.get('expires_in', 3600)
        expiry_time = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        
        self.tokens = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', self.tokens['refresh_token']),
            'expires_at': expiry_time,
            'token_type': token_data.get('token_type', 'Bearer')
        }
        
        self._save_tokens()
        return self.tokens
    
    def get_valid_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token string
        """
        if not self.tokens.get('access_token'):
            raise ValueError("No access token available. Please authenticate first.")
        
        # Check if token is expired or will expire in the next 5 minutes
        expiry = datetime.fromisoformat(self.tokens['expires_at'])
        if datetime.now() >= expiry - timedelta(minutes=5):
            print("Access token expired or expiring soon. Refreshing...")
            self.refresh_access_token()
        
        return self.tokens['access_token']
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with valid tokens."""
        return bool(self.tokens.get('access_token') and self.tokens.get('refresh_token'))
    
    def revoke_access(self):
        """Revoke access token and clear stored tokens."""
        if self.tokens.get('access_token'):
            try:
                headers = {
                    'Authorization': f"Bearer {self.tokens['access_token']}"
                }
                requests.delete(
                    f"{config.WHOOP_API_BASE_URL}/v2/user/access",
                    headers=headers
                )
            except Exception as e:
                print(f"Error revoking token: {e}")
        
        # Clear local tokens
        self.tokens = {}
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
