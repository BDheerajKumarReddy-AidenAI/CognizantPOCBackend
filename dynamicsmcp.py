from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
import httpx
import json
from msal import ConfidentialClientApplication
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

from typing import Optional
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
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "return=representation"

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

@mcp.tool()
async def create_opportunity(
    name: str,
    account_id: str,
    customer_need: str,
    total_amount: float,
    contact_id: Optional[str] = None,
    estimated_value: Optional[float] = None,
    estimated_close_date: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Create an Opportunity in Dynamics 365 Sales.
    """
    if not account_id:
        raise ValueError("account_id is required to create an opportunity.")

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/opportunities"

    body = {
        "name": name,
        "customerid_account@odata.bind": f"/accounts({account_id})",
        "customerneed": customer_need,
        "totalamount": float(total_amount)  # MUST be number
    }

    if contact_id:
        body["customerid_contact@odata.bind"] = f"/contacts({contact_id})"

    if estimated_value is not None:
        body["estimatedvalue"] = estimated_value

    if estimated_close_date:
        body["estimatedclosedate"] = estimated_close_date

    if description:
        body["description"] = description

    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()





@mcp.tool()
async def create_opportunity_product(
    opportunity_id: str,
    opportunity_product_name: str,
    quantity: int,
    uom_id: str,
    product_id: str ,
    price_per_unit: Optional[float] = None,
    is_price_overridden: Optional[bool] = None,
    manual_discount_amount: Optional[float] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Create an Opportunity Product (Opportunity Line Item) in Dynamics 365.

    """

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/opportunityproducts"
    )

    body = {
        "opportunityid@odata.bind": f"/opportunities({opportunity_id})",
        "opportunityproductname": opportunity_product_name,
        "quantity": int(quantity),
        "uomid@odata.bind":f"/uoms({uom_id})",
        "productid@odata.bind":f"/products({product_id})"
    }

    # Optional pricing
    if price_per_unit is not None:
        body["priceperunit"] = price_per_unit

    if is_price_overridden is not None:
        body["ispriceoverridden"] = is_price_overridden

    if manual_discount_amount is not None:
        body["manualdiscountamount"] = manual_discount_amount

    if description is not None:
        body["description"] = description

    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()




@mcp.tool()
async def create_quote(
    name: str,
    opportunity_id: str ,
) -> dict:
    """
    Create a Quote record in Dynamics 365 Sales.
    """
    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/quotes"
    body = {
        "name": name,
        "opportunityid@odata.bind": f"/opportunities({opportunity_id})"
    }

    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()



@mcp.tool()
async def create_quote_with_discount(
    name: str,
    opportunity_id: str,
    discount_percentage: float,
    discount_amount: Optional[float]=None ,
    freight_amount: Optional[float] = None,
) -> dict:
    """
    Create a Quote with discount fields in Dynamics 365 Sales.
    opportunity_id is mandatory.
    """

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/quotes"


    body = {
        "name": name,
        "opportunityid@odata.bind": f"/opportunities({opportunity_id})",
        "discount_amount":float(discount_amount),
        "discount_percentage":float(discount_percentage)
    }


    if freight_amount is not None:
        body["freightamount"] = freight_amount



    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()



@mcp.tool()
async def create_lead(
    subject: str,
    firstname: Optional[str] = None,
    lastname: Optional[str] = None,
    email: Optional[str] = None,
    mobilephone: Optional[str] = None,
    companyname: Optional[str] = None,
    jobtitle: Optional[str] = None,
    description: Optional[str] = None,
    parent_account_id: Optional[str] = None,
    parent_contact_id: Optional[str] = None,
) -> dict:
    """
    Create a Lead in Dynamics 365 Sales.
    - subject is mandatory
    - optional fields included ONLY when values are provided
      IMPORTANT RULE

        You should pass EITHER:
        parentaccountid
        OR
        parentcontactid
        Never both.
        CRM doesn't allow a Lead to be linked to two parents simultaneously.
    """

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/leads"

    # Mandatory field
    body = {
        "subject": subject
    }

    # Optional normal fields — add ONLY if provided
    if firstname is not None:
        body["firstname"] = firstname

    if lastname is not None:
        body["lastname"] = lastname

    if email is not None:
        body["emailaddress1"] = email

    if mobilephone is not None:
        body["mobilephone"] = mobilephone

    if companyname is not None:
        body["companyname"] = companyname

    if jobtitle is not None:
        body["jobtitle"] = jobtitle


    if description is not None:
        body["description"] = description

    # OData bindings — optional
    if parent_account_id is not None:
        body["parentaccountid@odata.bind"] = f"/accounts({parent_account_id})"

    if parent_contact_id is not None:
        body["parentcontactid@odata.bind"] = f"/contacts({parent_contact_id})"

    # Send request
    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()


@mcp.tool()
async def create_sales_order(
    name: str,
    price_list_id: str ,
    is_price_locked: bool ,
    customer_account_id: str,
    customer_contact_id: Optional[str] = None,
    description: Optional[str] = None,
    bill_to_name: Optional[str] = None,
    ship_to_name: Optional[str] = None
) -> dict:
    """
    Create a Sales Order (salesorder) in Dynamics 365 Sales.

    Required:
    - name
    - customer (account or contact)
    - price_list_id (pricelevelid)
    - is_price_locked

    Optional:
    - description
    - bill_to_name
    - ship_to_name
    """

    if not price_list_id:
        raise ValueError("price_list_id is required to create a Sales Order.")

    if not (customer_account_id or customer_contact_id):
        raise ValueError("Either customer_account_id or customer_contact_id is required.")

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/salesorders"

    body = {
        "name": name,
        "ispricelocked": is_price_locked
    }

    # Customer - Account OR Contact
    if customer_account_id:
        body["customerid_account@odata.bind"] = f"/accounts({customer_account_id})"

    if customer_contact_id:
        body["customerid_contact@odata.bind"] = f"/contacts({customer_contact_id})"

    # Price List
    body["pricelevelid@odata.bind"] = f"/pricelevels({price_list_id})"

    # Optional fields
    if description is not None:
        body["description"] = description

    if bill_to_name is not None:
        body["billto_name"] = bill_to_name

    if ship_to_name is not None:
        body["shipto_name"] = ship_to_name

    # Send request
    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=6000, path="/mcp")