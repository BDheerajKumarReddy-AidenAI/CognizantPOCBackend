import msal
import httpx
from typing import Optional
from functools import lru_cache


class DynamicsAuthenticator:
    """Handle authentication with Microsoft Dynamics 365"""
    
    def __init__(self, settings):
        self.settings = settings
        self.authority = f"https://login.microsoftonline.com/{self.settings.dynamics_tenant_id}"
        self.scope = [f"{self.settings.dynamics_resource_url}/.default"]
        self.app = msal.ConfidentialClientApplication(
            self.settings.dynamics_client_id,
            authority=self.authority,
            client_credential=self.settings.dynamics_client_secret
        )
        self._access_token: Optional[str] = None
    
    def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self._access_token:
            return self._access_token
        
        result = self.app.acquire_token_for_client(scopes=self.scope)
        
        if "access_token" in result:
            self._access_token = result["access_token"]
            return self._access_token
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            raise Exception(f"Authentication failed: {error} - {error_description}")
    
    def get_headers(self) -> dict:
        """Get authentication headers for API requests"""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "return=representation"
        }
    
    def get_base_url(self) -> str:
        """Get the base API URL"""
        return f"{self.settings.dynamics_resource_url}/api/data/{self.settings.dynamics_api_version}"


# Singleton instance
_auth_instance: Optional[DynamicsAuthenticator] = None


def get_authenticator() -> DynamicsAuthenticator:
    """Get the singleton authenticator instance"""
    global _auth_instance
    if _auth_instance is None:
        # Import settings from your main config
        from src.app.config import settings
        _auth_instance = DynamicsAuthenticator(settings)
    return _auth_instance
