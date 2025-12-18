from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
import httpx
import json
from msal import ConfidentialClientApplication
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.app.casbin.enforcer import authorize

load_dotenv()

from typing import Optional
import os
 
def enforce(role: str, resource: str, action: str):
    try:
        authorize(role.lower(), resource, action)
    except PermissionError as e:
        # IMPORTANT: return structured info, not exception
        return {
            "error": "PERMISSION_DENIED",
            "message": f"You are not allowed to {action} {resource}.",
            "role": role.lower(),
            "resource": resource,
            "action": action
        }


CLIENT_ID = os.getenv("DYNAMICS_CLIENT_ID")
CLIENT_SECRET = os.getenv("DYNAMICS_CLIENT_SECRET")
TENANT_ID = os.getenv("DYNAMICS_TENANT_ID")

DYNAMICS_ORG = os.getenv("DYNAMICS_ORG")
DYNAMICS_REGION = os.getenv("DYNAMICS_REGION")

API_VERSION = "v9.2"
SCOPE = [os.getenv("SCOPE")]
print(SCOPE)
 
# def filter_fields(data: dict, fields: list) -> dict:
#     return {field: data.get(field) for field in fields}

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

# @mcp.tool()
# async def get_opportunities() -> dict:
#     """
#     Get all opportunities
#     """
#     url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/opportunities"
#     response = await client.get(url)
#     response.raise_for_status()
#     full_data = response.json()
    
#     return response.json()

@mcp.tool()
async def get_opportunities(user_role: str) -> dict:
    """
    Get all opportunities but return only AI-relevant fields.
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "opportunity", "read")
    if denial:
        return denial

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/opportunities"
    response = await client.get(url)
    response.raise_for_status()

    raw_data = response.json().get("value", [])

    cleaned_list = []

    for opp in raw_data:
        cleaned = {
            "opportunityid": opp.get("opportunityid"),
            "name": opp.get("name"),
            "customer_need": opp.get("customerneed"),
            "description": opp.get("description"),
            "proposed_solution": opp.get("proposedsolution"),
            "email": opp.get("emailaddress"),
            "estimated_value": opp.get("estimatedvalue"),
            "estimated_close_date": opp.get("estimatedclosedate"),
            "close_probability": opp.get("closeprobability"),
            "purchase_timeframe": opp.get("purchasetimeframe"),
            "purchase_process": opp.get("purchaseprocess"),
            "decision_maker": opp.get("decisionmaker"),
            "identify_competitors": opp.get("identifycompetitors"),
            "identify_contacts": opp.get("identifycustomercontacts"),
            "customer_pain_points": opp.get("customerpainpoints"),
            "current_situation": opp.get("currentsituation"),
            "sales_stage": opp.get("salesstagecode"),
            "state": opp.get("statecode"),
            "status": opp.get("statuscode"),
            "created_on": opp.get("createdon"),
        }

        cleaned_list.append(cleaned)


    return {
        "count": len(cleaned_list),
        "opportunities": cleaned_list
    }


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
async def get_accounts(user_role: str) -> dict:
    denial = enforce(user_role, "account", "read")
    if denial:
        return denial
    """
    Get all accounts but return only AI-relevant fields.
    - user_role is required for authorization.
    """

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/accounts"
    response = await client.get(url)
    response.raise_for_status()

    raw_data = response.json().get("value", [])

    cleaned_list = []

    for acc in raw_data:
        cleaned = {
            "accountid": acc.get("accountid"),
            "name": acc.get("name"),
            "description": acc.get("description"),
            "website": acc.get("websiteurl"),
            "email": acc.get("emailaddress1"),
            "telephone": acc.get("telephone1"),
            "fax": acc.get("fax"),

            # Address fields (cleaned)
            "city": acc.get("address1_city"),
            "state": acc.get("address1_stateorprovince"),
            "country": acc.get("address1_country"),
            "postal_code": acc.get("address1_postalcode"),

            # Business metrics
            "revenue": acc.get("revenue"),
            "employees": acc.get("numberofemployees"),
            "industry": acc.get("industrycode"),
            "open_revenue": acc.get("openrevenue"),

            # Primary contact reference
            "primary_contact_id": acc.get("_primarycontactid_value"),

            # (Optional) created date for timeline sorting
            "created_on": acc.get("createdon"),
        }

        cleaned_list.append(cleaned)

    return {
        "count": len(cleaned_list),
        "accounts": cleaned_list
    }



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
async def get_quotes(user_role: str) -> dict:
    
    denial = enforce(user_role, "quote", "read")
    if denial:
        return denial
    """
    Get all quotes but return only AI-relevant fields.
    - user_role is required for authorization.
    """

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/quotes"
    )
    response = await client.get(url)
    response.raise_for_status()

    raw_data = response.json().get("value", [])

    cleaned_list = []

    for q in raw_data:
        cleaned = {
            "quoteid": q.get("quoteid"),
            "name": q.get("name"),
            "description": q.get("description"),
            "quotenumber": q.get("quotenumber"),

            # Financials
            "totalamount": q.get("totalamount"),
            "discountamount": q.get("discountamount"),
            "discountpercentage": q.get("discountpercentage"),
            "freightamount": q.get("freightamount"),
            "totallineitemamount": q.get("totallineitemamount"),

            # Status fields
            "statuscode": q.get("statuscode"),
            "statecode": q.get("statecode"),

            # Timestamps
            "createdon": q.get("createdon"),
            "modifiedon": q.get("modifiedon"),

            # Relationship fields
            "opportunity_id": q.get("_opportunityid_value"),
            "account_id": q.get("_accountid_value"),
            "customer_id": q.get("_customerid_value"),

            # Scheduling fields
            "request_delivery_by": q.get("requestdeliveryby"),
            "expires_on": q.get("expireson"),
        }

        cleaned_list.append(cleaned)

    return {
        "count": len(cleaned_list),
        "quotes": cleaned_list
    }


@mcp.tool()
async def get_salesorders(user_role: str) -> dict:
    """
    Get all sales orders but return only AI-relevant fields.
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "salesorder", "read")
    if denial:
        return denial

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/salesorders"
    )
    response = await client.get(url)
    response.raise_for_status()

    raw_data = response.json().get("value", [])

    cleaned_list = []

    for so in raw_data:
        cleaned = {
            # Core identifiers
            "salesorderid": so.get("salesorderid"),
            "ordernumber": so.get("ordernumber"),
            "name": so.get("name"),

            # Financials
            "totalamount": so.get("totalamount"),
            "totalamountlessfreight": so.get("totalamountlessfreight"),
            "totallineitemamount": so.get("totallineitemamount"),
            "discountamount": so.get("discountamount"),
            "discountpercentage": so.get("discountpercentage"),
            "freightamount": so.get("freightamount"),

            # Status
            "statecode": so.get("statecode"),
            "statuscode": so.get("statuscode"),
            "ispricelocked": so.get("ispricelocked"),
            "submitstatus": so.get("submitstatus"),
            "submitstatusdescription": so.get("submitstatusdescription"),

            # Related entities
            "quote_id": so.get("_quoteid_value"),
            "opportunity_id": so.get("_opportunityid_value"),
            "customer_id": so.get("_customerid_value"),
            "pricelevel_id": so.get("_pricelevelid_value"),

            # Dates
            "createdon": so.get("createdon"),
            "modifiedon": so.get("modifiedon"),
            "datefulfilled": so.get("datefulfilled"),
            "request_delivery_by": so.get("requestdeliveryby"),

            # Shipping details (clean)
            "shipto_city": so.get("shipto_city"),
            "shipto_state": so.get("shipto_stateorprovince"),
            "shipto_country": so.get("shipto_country"),
            "shipto_postalcode": so.get("shipto_postalcode"),

            # Billing details (clean)
            "billto_city": so.get("billto_city"),
            "billto_country": so.get("billto_country"),
        }

        cleaned_list.append(cleaned)

    return {
        "count": len(cleaned_list),
        "salesorders": cleaned_list
    }



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
async def create_account(
    user_role: str,
    name: str,
    primary_contact_id: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    website: Optional[str] = None,
    description: Optional[str] = None,
    annual_revenue: Optional[float] = None,
    number_of_employees: Optional[int] = None,
    address_street: Optional[str] = None,
    address_city: Optional[str] = None,
    address_state: Optional[str] = None,
    address_country: Optional[str] = None,
    address_postalcode: Optional[str] = None
) -> dict:
    """
    Create an Account in Dynamics 365 CRM.
    - name is required
    - user_role is required for authorization.
    - All other parameters are optional
    """
    denial = enforce(user_role, "account", "create")
    if denial:
        return denial
    if not name:
        raise ValueError("Account 'name' is required to create an account.")

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/accounts"

    body = {
        "name": name
    }

    # --- Optional Fields ---
    if primary_contact_id:
        body["primarycontactid@odata.bind"] = f"/contacts({primary_contact_id})"

    if email:
        body["emailaddress1"] = email

    if phone:
        body["telephone1"] = phone

    if website:
        body["websiteurl"] = website

    if description:
        body["description"] = description

    if annual_revenue is not None:
        body["revenue"] = float(annual_revenue)

    if number_of_employees is not None:
        body["numberofemployees"] = int(number_of_employees)

    # --- Address fields ---
    if address_street:
        body["address1_line1"] = address_street

    if address_city:
        body["address1_city"] = address_city

    if address_state:
        body["address1_stateorprovince"] = address_state

    if address_country:
        body["address1_country"] = address_country

    if address_postalcode:
        body["address1_postalcode"] = address_postalcode

    # --- Execute Request ---
    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()


@mcp.tool()
async def update_account(
    user_role: str,
    account_id: str,
    name: Optional[str] = None,
    primary_contact_id: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    website: Optional[str] = None,
    description: Optional[str] = None,
    annual_revenue: Optional[float] = None,
    number_of_employees: Optional[int] = None,
    address_street: Optional[str] = None,
    address_city: Optional[str] = None,
    address_state: Optional[str] = None,
    address_country: Optional[str] = None,
    address_postalcode: Optional[str] = None
) -> dict:
    """
    Update an existing Account in Dynamics 365 CRM.
    - account_id is required
    - user_role is required for authorization.
    - All other parameters are optional (only passed fields will be updated)
    """
    denial = enforce(user_role, "account", "update")
    if denial:
        return denial
    if not account_id:
        raise ValueError("account_id is required to update an account.")

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/accounts({account_id})"

    body = {}

    # --- Standard fields ---
    if name:
        body["name"] = name

    if email:
        body["emailaddress1"] = email

    if phone:
        body["telephone1"] = phone

    if website:
        body["websiteurl"] = website

    if description:
        body["description"] = description

    # --- Lookup field ---
    if primary_contact_id:
        body["primarycontactid@odata.bind"] = f"/contacts({primary_contact_id})"

    # --- Numeric fields ---
    if annual_revenue is not None:
        body["revenue"] = float(annual_revenue)

    if number_of_employees is not None:
        body["numberofemployees"] = int(number_of_employees)

    # --- Address fields ---
    if address_street:
        body["address1_line1"] = address_street

    if address_city:
        body["address1_city"] = address_city

    if address_state:
        body["address1_stateorprovince"] = address_state

    if address_country:
        body["address1_country"] = address_country

    if address_postalcode:
        body["address1_postalcode"] = address_postalcode

    # --- Execute PATCH request ---
    response = await client.patch(url, json=body)
    response.raise_for_status()

    # PATCH returns 204 No Content → return success object
    return {
        "status": "success",
        "accountid": account_id,       # <-- IMPORTANT
        "updated_fields": body
    }


@mcp.tool()
async def delete_account(user_role: str, account_id: str) -> dict:

    """
    Delete an Account from Dynamics 365 CRM.
    - account_id is required
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "account", "delete")
    if denial:
        return denial
    if not account_id:
        raise ValueError("account_id is required to delete an account.")

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}."
        f"dynamics.com/api/data/v9.2/accounts({account_id})"
    )

    response = await client.delete(url)
    response.raise_for_status()

    # DELETE returns 204 No Content → return custom success message
    return {
        "status": "success",
        "deleted_account_id": account_id
    }

@mcp.tool()
async def create_opportunity(
    user_role: str,
    name: str,
    account_id: str,
    customer_need: str,
    budget_amount: float,   # <-- FIX
    contact_id: Optional[str] = None,
    estimated_value: Optional[float] = None,
    estimated_close_date: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Create an Opportunity in Dynamics 365 Sales.
    - name is required
    - account_id is required
    - customer_need is required
    - budget_amount is required
    - user_role is required for authorization.
    - All other parameters are optional
    """
    denial = enforce(user_role, "opportunity", "create")
    print(user_role, name)

    if denial:
        return denial
    if not account_id:
        raise ValueError("account_id is required to create an opportunity.")

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/opportunities"

    body = {
        "name": name,
        "customerid_account@odata.bind": f"/accounts({account_id})",
        "customerneed": customer_need,
        "budgetamount": float(budget_amount)  # <-- FIXED
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
async def update_opportunity(
    user_role: str,
    opportunity_id: str,
    name: Optional[str] = None,
    customer_need: Optional[str] = None,
    budget_amount: Optional[float] = None,
    estimated_value: Optional[float] = None,
    estimated_close_date: Optional[str] = None,
    description: Optional[str] = None,
    account_id: Optional[str] = None,
    contact_id: Optional[str] = None
) -> dict:
    """
    Update fields on an existing Opportunity in Dynamics 365 Sales.

    - opportunity_id is required
    - user_role is required for authorization.
    - All other parameters are optional (only passed fields will be updated)
    """

    denial = enforce(user_role, "opportunity", "update")
    if denial:
        return denial

    if not opportunity_id:
        raise ValueError("opportunity_id is required to update an opportunity.")

    # PATCH URL for updating opportunity
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/opportunities({opportunity_id})"
    )

    body = {}

    # Optional updates
    if name is not None:
        body["name"] = name

    if customer_need is not None:
        body["customerneed"] = customer_need

    if budget_amount is not None:
        body["budgetamount"] = float(budget_amount)

    if estimated_value is not None:
        body["estimatedvalue"] = float(estimated_value)

    if estimated_close_date is not None:
        body["estimatedclosedate"] = estimated_close_date  # must be YYYY-MM-DD

    if description is not None:
        body["description"] = description

    if account_id is not None:
        body["customerid_account@odata.bind"] = f"/accounts({account_id})"

    if contact_id is not None:
        body["customerid_contact@odata.bind"] = f"/contacts({contact_id})"

    # Ensure at least one field is updated
    if not body:
        raise ValueError("At least one field must be provided to update the opportunity.")

    # Perform PATCH
    response = await client.patch(url, json=body)
    response.raise_for_status()

    # Success: Dynamics returns empty body for PATCH
    return {
        "message": "Opportunity updated successfully",
        "opportunityid": opportunity_id,
        "updated_fields": body
    }


@mcp.tool()
async def delete_opportunity(user_role: str, opportunity_id: str) -> dict:
    """
    Delete an Opportunity in Dynamics 365 Sales.
    - opportunity_id is required
    - user_role is required for authorization.
    """

    denial = enforce(user_role, "opportunity", "delete")
    if denial:
        return denial
    
    if not opportunity_id:
        raise ValueError("opportunity_id is required to delete an opportunity.")

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/opportunities({opportunity_id})"
    )

    response = await client.delete(url)
    response.raise_for_status()

    return {
        "message": "Opportunity deleted successfully",
        "opportunityid": opportunity_id
    }




@mcp.tool()
async def create_quote(
    user_role: str,
    name: str,
    opportunity_id: str,
    discount_percentage: Optional[float]=None,
    discount_amount: Optional[float]=None ,
    freight_amount: Optional[float] = None,
) -> dict:

    denial = enforce(user_role, "quote", "create")
    print(denial)
    print(user_role, name, opportunity_id, discount_percentage, discount_amount, freight_amount)
    if denial:
        return denial
    """
    Create a Quote with discount fields in Dynamics 365 Sales.
    - user_role is required for authorization.
    name is mandatory.
    opportunity_id is mandatory.
    discount_percentage is optional.
    freight_amount is optional.
    discount_amount is optional.
    """

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/quotes"


    body = {
        "name": name,
        "opportunityid@odata.bind": f"/opportunities({opportunity_id})",
    }

    if discount_percentage is not None:
        body["discountpercentage"] = discount_percentage
    if discount_amount is not None:
        body["discountamount"] = discount_amount
    if freight_amount is not None:
        body["freightamount"] = freight_amount



    response = await client.post(url, json=body)
    response.raise_for_status()

    return response.json()


@mcp.tool()
async def update_quote(
    user_role: str,
    quote_id: str,
    discount_percentage: Optional[float]=None,
    discount_amount: Optional[float] = None,
    freight_amount: Optional[float] = None,
    description: Optional[str] = None
) -> dict:
    denial = enforce(user_role, "quote", "update")
    if denial:
        return denial
    """
    Update discount-related fields on a Quote in Dynamics 365 Sales.
    - quote_id is mandatory
    - All other fields are optional; only provided fields will be updated.
    - user_role is required for authorization.
    """

    if not quote_id:
        raise ValueError("quote_id is required to update a quote.")

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/quotes({quote_id})"
    )

    body = {}

    # If any field is provided, add it to update body
    if discount_percentage is not None:
        body["discountpercentage"] = float(discount_percentage)

    if discount_amount is not None:
        body["discountamount"] = float(discount_amount)

    if freight_amount is not None:
        body["freightamount"] = float(freight_amount)

    if description is not None:
        body["description"] = description

    # No fields supplied → error
    if not body:
        raise ValueError(
            "At least one field must be provided to update the quote."
        )

    response = await client.patch(url, json=body)
    response.raise_for_status()

    # Dynamics returns empty body for PATCH success → return a message
    return {
        "message": "Quote updated successfully",
        "quoteid": quote_id,
        "updated_fields": body
    }

@mcp.tool()
async def delete_quote(user_role: str,quote_id: str) -> dict:

    """
    Delete a Quote in Dynamics 365 Sales.
    - quote_id is required
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "quote", "delete")
    if denial:
        return denial
    if not quote_id:
        raise ValueError("quote_id is required to delete a quote.")

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/"
        f"api/data/v9.2/quotes({quote_id})"
    )

    try:
        response = await client.delete(url)
        response.raise_for_status()

        return {
            "message": "Quote deleted successfully",
            "quoteid": quote_id
        }

    except httpx.HTTPStatusError as e:
        # If quote already deleted or never existed → Dynamics returns 404 Not Found
        if e.response.status_code == 404:
            return {
                "message": "Quote does not exist to delete",
                "quoteid": quote_id
            }

        # Any other HTTP error → rethrow
        raise e
    except Exception as e:
        # Non-HTTP errors
        raise e





# Create Sales Order
@mcp.tool()
async def create_sales_order(
    user_role: str,
    name: str,
    customer_account_id: Optional[str] = None,
    customer_contact_id: Optional[str] = None,
    description: Optional[str] = None,
    request_delivery_by: Optional[str] = None,
    payment_terms_code: Optional[int] = None,
    freight_terms_code: Optional[int] = None
) -> dict:
    """
    Create a Sales Order in Dynamics 365 CRM.
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "salesorder", "create")
    if denial:
        return denial
    
    if not name:
        raise ValueError("Sales Order 'name' is required.")

    # customer lookup requirement
    if not (customer_account_id or customer_contact_id):
        raise ValueError("Either account or contact customer must be provided.")

    url = f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}.dynamics.com/api/data/v9.2/salesorders"

    body = {"name": name}

    # bind to account or contact (customer)
    if customer_account_id:
        body["customerid_account@odata.bind"] = f"/accounts({customer_account_id})"
    if customer_contact_id:
        body["customerid_contact@odata.bind"] = f"/contacts({customer_contact_id})"

    if description:
        body["description"] = description
    if request_delivery_by:
        body["requestdeliveryby"] = request_delivery_by
    if payment_terms_code is not None:
        body["paymenttermscode"] = payment_terms_code
    if freight_terms_code is not None:
        body["freighttermscode"] = freight_terms_code

    response = await client.post(url, json=body)
    response.raise_for_status()
    return response.json()


#Update Sales Order
@mcp.tool()
async def update_sales_order(
    user_role: str,
    sales_order_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    request_delivery_by: Optional[str] = None,
    payment_terms_code: Optional[int] = None,
    freight_terms_code: Optional[int] = None
) -> dict:
    """
    Update an existing Sales Order.
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "salesorder", "update")
    if denial:
        return denial
    if not sales_order_id:
        raise ValueError("sales_order_id is required.")

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}."
        f"dynamics.com/api/data/v9.2/salesorders({sales_order_id})"
    )

    body = {}
    if name:
        body["name"] = name
    if description:
        body["description"] = description
    if request_delivery_by:
        body["requestdeliveryby"] = request_delivery_by
    if payment_terms_code is not None:
        body["paymenttermscode"] = payment_terms_code
    if freight_terms_code is not None:
        body["freighttermscode"] = freight_terms_code

    response = await client.patch(url, json=body)
    response.raise_for_status()

    return {"status": "success", "salesorderid": sales_order_id, "updated_fields": body}


# Delete Sales Order
@mcp.tool()
async def delete_sales_order(user_role: str, sales_order_id: str) -> dict:
    """
    Delete a Sales Order by ID.
    - user_role is required for authorization.
    """
    denial = enforce(user_role, "salesorder", "delete")
    if denial:
        return denial
    
    if not sales_order_id:
        raise ValueError("sales_order_id is required.")

    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}."
        f"dynamics.com/api/data/v9.2/salesorders({sales_order_id})"
    )

    response = await client.delete(url)
    response.raise_for_status()


    return {
        "status": "success",
        "salesorderid": sales_order_id
    }

# Create Lead
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
    - opportunity_id: ID of the parent Opportunity (mandatory)
    - opportunity_product_name: Name of the Opportunity Product (mandatory) 
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




if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=6000, path="/mcp")