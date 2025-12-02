from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
import httpx
import json
from msal import ConfidentialClientApplication
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import os
 

CLIENT_ID = os.getenv("DYNAMICS_CLIENT_ID")
CLIENT_SECRET = os.getenv("DYNAMICS_CLIENT_SECRET")
TENANT_ID = os.getenv("DYNAMICS_TENANT_ID")

DYNAMICS_ORG = os.getenv("DYNAMICS_ORG")
DYNAMICS_REGION = os.getenv("DYNAMICS_REGION")

API_VERSION = "v9.2"
SCOPE = [os.getenv("SCOPE")]
print(SCOPE)
 

class Dynamics365Auth(httpx.Auth):
    """Custom authentication handler with automatic token refresh for Dynamics 365"""
 
    def __init__(self, client_id: str, client_secret: str, tenant_id: str, scope: list):
        self.msal_app = ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret
        )
        self.scope = scope
        self.token = None
        self.token_expiry = None
 
    def get_token(self) -> str:
        """Get token with automatic refresh if expired"""
        # Check if we have a valid cached token
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token
 
        # Try to get token silently from cache first
        result = self.msal_app.acquire_token_silent(self.scope, account=None)
 
        # If no cached token, acquire new one
        if not result:
            result = self.msal_app.acquire_token_for_client(scopes=self.scope)
 
        if "access_token" in result:
            self.token = result["access_token"]
            # Set expiry with 5 min buffer
            expires_in = result.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)
            return self.token
        else:
            raise Exception(f"Failed to acquire token: {result.get('error_description')}")
 
    def auth_flow(self, request):
        """HTTPX auth flow - adds Bearer token to each request"""
        token = self.get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request
 

auth = Dynamics365Auth(CLIENT_ID, CLIENT_SECRET, TENANT_ID, SCOPE)
 
client = httpx.AsyncClient(
    base_url=f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/{API_VERSION}",
    auth=auth,
    # timeout=30.0,
    headers={
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"
    }
)
mcp = FastMCP("dynamics365-mcp")
@mcp.tool()
async def get_opportunities() -> dict:
    """
    Get all opportunities
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/opportunities"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_leads() -> dict:
    """
    Get all leads
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/leads"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_accounts() -> dict:
    """
    Get all accounts
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/accounts"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_products() -> dict:
    """
    Get all products
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/products"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_quotes() -> dict:
    """
    Get all quotes
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/quotes"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_salesorders() -> dict:
    """
    Get all salesorders
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/salesorders"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_units() -> dict:
    """
    Get all units
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/uoms"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
@mcp.tool()
async def get_oprtunity_products() -> dict:
    """
    Get all opportunityproducts
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/opportunityproducts"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=6000, path="/mcp")