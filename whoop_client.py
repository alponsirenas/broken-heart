"""Whoop API client for fetching health data."""
import requests
from datetime import datetime
from typing import Dict, List, Optional
from whoop_auth import WhoopAuth
import config


class WhoopClient:
    """Client for interacting with Whoop API endpoints."""
    
    def __init__(self, auth: WhoopAuth):
        self.auth = auth
        self.base_url = config.WHOOP_API_BASE_URL
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to Whoop API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        access_token = self.auth.get_valid_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        
        # Track rate limits
        self.rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
        self.rate_limit_reset = response.headers.get('X-RateLimit-Reset')
        
        response.raise_for_status()
        return response.json()
    
    def _paginate_request(self, endpoint: str, params: Optional[Dict] = None, limit: int = 25) -> List[Dict]:
        """
        Handle paginated requests to fetch all records.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            limit: Records per page (max 25)
            
        Returns:
            List of all records
        """
        if params is None:
            params = {}
        
        params['limit'] = min(limit, 25)
        all_records = []
        next_token = None
        
        while True:
            if next_token:
                params['nextToken'] = next_token
            
            response = self._make_request(endpoint, params)
            
            # Handle different response structures
            records = response.get('records', [])
            if not records:
                # Some endpoints return data directly
                if isinstance(response, list):
                    all_records.extend(response)
                    break
                elif isinstance(response, dict) and len(response) > 0:
                    all_records.append(response)
                    break
            else:
                all_records.extend(records)
            
            # Check for next page
            next_token = response.get('next_token')
            if not next_token:
                break
            
            print(f"Fetched {len(all_records)} records, continuing pagination...")
        
        return all_records
    
    def get_user_profile(self) -> Dict:
        """Get user profile information."""
        return self._make_request('/v2/user/profile/basic')
    
    def get_body_measurements(self) -> Dict:
        """Get user body measurements (height, weight, max HR)."""
        return self._make_request('/v2/user/measurement/body')
    
    def get_recovery_data(self, start: str, end: str) -> List[Dict]:
        """
        Get recovery data for date range.
        
        Args:
            start: Start date in ISO 8601 format (YYYY-MM-DD or full datetime)
            end: End date in ISO 8601 format
            
        Returns:
            List of recovery records
        """
        params = {
            'start': start,
            'end': end
        }
        return self._paginate_request('/v2/recovery', params)
    
    def get_sleep_data(self, start: str, end: str) -> List[Dict]:
        """
        Get sleep data for date range.
        
        Args:
            start: Start date in ISO 8601 format
            end: End date in ISO 8601 format
            
        Returns:
            List of sleep records
        """
        params = {
            'start': start,
            'end': end
        }
        return self._paginate_request('/v2/activity/sleep', params)
    
    def get_cycle_data(self, start: str, end: str) -> List[Dict]:
        """
        Get physiological cycle (day) data for date range.
        
        Args:
            start: Start date in ISO 8601 format
            end: End date in ISO 8601 format
            
        Returns:
            List of cycle records
        """
        params = {
            'start': start,
            'end': end
        }
        return self._paginate_request('/v2/cycle', params)
    
    def get_workout_data(self, start: str, end: str) -> List[Dict]:
        """
        Get workout data for date range.
        
        Args:
            start: Start date in ISO 8601 format
            end: End date in ISO 8601 format
            
        Returns:
            List of workout records
        """
        params = {
            'start': start,
            'end': end
        }
        return self._paginate_request('/v2/activity/workout', params)
    
    def get_all_health_data(self, start: str, end: str) -> Dict[str, List[Dict]]:
        """
        Fetch all health data types for the specified date range.
        
        Args:
            start: Start date in ISO 8601 format (YYYY-MM-DD)
            end: End date in ISO 8601 format (YYYY-MM-DD)
            
        Returns:
            Dictionary with keys: recovery, sleep, cycles, workouts
        """
        print(f"Fetching Whoop data from {start} to {end}...")
        
        # Add time component to dates
        start_dt = f"{start}T00:00:00.000Z"
        end_dt = f"{end}T23:59:59.999Z"
        
        data = {
            'recovery': [],
            'sleep': [],
            'cycles': [],
            'workouts': []
        }
        
        try:
            print("Fetching recovery data...")
            data['recovery'] = self.get_recovery_data(start_dt, end_dt)
            print(f"✓ Retrieved {len(data['recovery'])} recovery records")
        except Exception as e:
            print(f"✗ Error fetching recovery data: {e}")
        
        try:
            print("Fetching sleep data...")
            data['sleep'] = self.get_sleep_data(start_dt, end_dt)
            print(f"✓ Retrieved {len(data['sleep'])} sleep records")
        except Exception as e:
            print(f"✗ Error fetching sleep data: {e}")
        
        try:
            print("Fetching cycle data...")
            data['cycles'] = self.get_cycle_data(start_dt, end_dt)
            print(f"✓ Retrieved {len(data['cycles'])} cycle records")
        except Exception as e:
            print(f"✗ Error fetching cycle data: {e}")
        
        try:
            print("Fetching workout data...")
            data['workouts'] = self.get_workout_data(start_dt, end_dt)
            print(f"✓ Retrieved {len(data['workouts'])} workout records")
        except Exception as e:
            print(f"✗ Error fetching workout data: {e}")
        
        return data
