from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
import httpx
from httpx import HTTPStatusError, TimeoutException
from typing import List, Optional, Dict, Any

from msal import ConfidentialClientApplication
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.app.casbin.enforcer import authorize
from src.app.config import settings

import logging

logger = logging.getLogger(__name__)


load_dotenv()


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


CLIENT_ID = settings.dynamics.auth.client_id
CLIENT_SECRET = settings.dynamics.auth.client_secret
TENANT_ID = settings.dynamics.auth.tenant_id

DYNAMICS_ORG = settings.dynamics.org
DYNAMICS_REGION = settings.dynamics.region

API_VERSION = settings.dynamics.api_version
SCOPE = [settings.dynamics.scope]
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
            "accountid": opp.get("_parentaccountid_value"),
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
    raw_data = response.json().get("value", [])

    cleaned_list = []

    

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
            "opportunityid": q.get("_opportunityid_value"),
            "accountid": q.get("_accountid_value"),
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
            "quoteid": so.get("_quoteid_value"),
            "opportunityid": so.get("_opportunityid_value"),
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
    address_postalcode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Securely create an Account in Dynamics 365 CRM.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "account", "create")
    if denial:
        logger.warning(
            "Account creation denied",
            extra={"user_role": user_role},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not name or not name.strip():
        return {"error": "Account name is required and cannot be empty."}

    if annual_revenue is not None and annual_revenue < 0:
        return {"error": "annual_revenue cannot be negative."}

    if number_of_employees is not None and number_of_employees < 0:
        return {"error": "number_of_employees cannot be negative."}

    if description is not None and not description.strip():
        return {"error": "Description cannot be empty if provided."}

    # =========================
    # 3️⃣ Build Request Payload
    # =========================
    body: Dict[str, Any] = {
        "name": name.strip(),
    }

    if primary_contact_id:
        body["primarycontactid@odata.bind"] = (
            f"/contacts({primary_contact_id})"
        )

    if email:
        body["emailaddress1"] = email

    if phone:
        body["telephone1"] = phone

    if website:
        body["websiteurl"] = website

    if description:
        body["description"] = description.strip()

    if annual_revenue is not None:
        body["revenue"] = float(annual_revenue)

    if number_of_employees is not None:
        body["numberofemployees"] = int(number_of_employees)

    # Address fields
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

    # =========================
    # 4️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/accounts"
    )

    try:
        response = await client.post(url, json=body)
        response.raise_for_status()

        logger.info(
            "Account created successfully",
            extra={
                "user_role": user_role,
                "account_name": name,
            },
        )

        return response.json()

    except HTTPStatusError as exc:
        logger.error(
            "Dynamics API error while creating account",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to create account in Dynamics.",
        }

    except TimeoutException:
        logger.error("Timeout while creating account")
        return {
            "error": "Request timed out while creating account. Please try again."
        }

    except Exception:
        logger.exception("Unexpected error during account creation")
        return {
            "error": "An unexpected error occurred while creating the account."
        }

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
    address_postalcode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Securely update an Account in Dynamics 365 CRM.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "account", "update")
    if denial:
        logger.warning(
            "Account update denied",
            extra={"user_role": user_role, "accountid": account_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not account_id or not account_id.strip():
        return {"error": "account_id is required to update an account."}

    if name is not None and not name.strip():
        return {"error": "Account name cannot be empty if provided."}

    if description is not None and not description.strip():
        return {"error": "Description cannot be empty if provided."}

    if annual_revenue is not None and annual_revenue < 0:
        return {"error": "annual_revenue cannot be negative."}

    if number_of_employees is not None and number_of_employees < 0:
        return {"error": "number_of_employees cannot be negative."}

    # =========================
    # 3️⃣ Build PATCH Payload
    # =========================
    body: Dict[str, Any] = {}

    if name is not None:
        body["name"] = name.strip()

    if email:
        body["emailaddress1"] = email

    if phone:
        body["telephone1"] = phone

    if website:
        body["websiteurl"] = website

    if description is not None:
        body["description"] = description.strip()

    if primary_contact_id:
        body["primarycontactid@odata.bind"] = (
            f"/contacts({primary_contact_id})"
        )

    if annual_revenue is not None:
        body["revenue"] = float(annual_revenue)

    if number_of_employees is not None:
        body["numberofemployees"] = int(number_of_employees)

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

    if not body:
        return {
            "error": "At least one field must be provided to update the account."
        }

    # =========================
    # 4️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/accounts({account_id})"
    )

    try:
        response = await client.patch(url, json=body, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Account updated successfully",
            extra={
                "user_role": user_role,
                "accountid": account_id,
                "updated_fields": list(body.keys()),
            },
        )

        return {
            "message": "Account updated successfully",
            "accountid": account_id,
            "updated_fields": list(body.keys()),
        }

    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Account not found.",
                "accountid": account_id,
            }

        logger.error(
            "Dynamics API error while updating account",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to update account in Dynamics.",
        }

    except TimeoutException:
        logger.error("Timeout while updating account")
        return {
            "error": "Request timed out while updating account. Please try again."
        }

    except Exception:
        logger.exception("Unexpected error during account update")
        return {
            "error": "An unexpected error occurred while updating the account."
        }

@mcp.tool()
async def delete_account(user_role: str, account_id: str) -> Dict[str, Any]:
    """
    Securely delete an Account from Dynamics 365 CRM.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "account", "delete")
    if denial:
        logger.warning(
            "Account deletion denied",
            extra={"user_role": user_role, "accountid": account_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not account_id or not account_id.strip():
        return {"error": "account_id is required to delete an account."}

    # =========================
    # 3️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/accounts({account_id})"
    )

    try:
        response = await client.delete(url, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Account deleted successfully",
            extra={
                "user_role": user_role,
                "accountid": account_id,
            },
        )

        return {
            "message": "Account deleted successfully",
            "accountid": account_id,
        }

    except HTTPStatusError as exc:
        # Account not found / already deleted
        if exc.response.status_code == 404:
            logger.info(
                "Account not found during deletion",
                extra={"accountid": account_id},
            )
            return {
                "message": "Account does not exist or was already deleted",
                "accountid": account_id,
            }

        logger.error(
            "Dynamics API error while deleting account",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to delete account in Dynamics.",
        }

    except TimeoutException:
        logger.error(
            "Timeout while deleting account",
            extra={"accountid": account_id},
        )
        return {
            "error": "Request timed out while deleting account. Please try again."
        }

    except Exception:
        logger.exception(
            "Unexpected error during account deletion",
            extra={"accountid": account_id},
        )
        return {
            "error": "An unexpected error occurred while deleting the account."
        }

@mcp.tool()
async def create_opportunity(
    user_role: str,
    name: str,
    account_id: str,
    customer_need: str,
    budget_amount: float,
    contact_id: Optional[str] = None,
    estimated_value: Optional[float] = None,
    estimated_close_date: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Securely create an Opportunity in Dynamics 365 Sales.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "opportunity", "create")
    if denial:
        logger.warning(
            "Opportunity creation denied",
            extra={"user_role": user_role},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not name or not name.strip():
        return {"error": "Opportunity name is required and cannot be empty."}

    if not account_id or not account_id.strip():
        return {"error": "account_id is required to create an opportunity."}

    if not customer_need or not customer_need.strip():
        return {"error": "customer_need is required and cannot be empty."}

    if budget_amount is None or budget_amount < 0:
        return {"error": "budget_amount must be a valid non-negative number."}

    if estimated_value is not None and estimated_value < 0:
        return {"error": "estimated_value cannot be negative."}

    if description is not None and not description.strip():
        return {"error": "Description cannot be empty if provided."}

    # =========================
    # 3️⃣ Build Request Payload
    # =========================
    body: Dict[str, Any] = {
        "name": name.strip(),
        "customerid_account@odata.bind": f"/accounts({account_id})",
        "customerneed": customer_need.strip(),
        "budgetamount": float(budget_amount),
    }

    if contact_id:
        body["customerid_contact@odata.bind"] = f"/contacts({contact_id})"

    if estimated_value is not None:
        body["estimatedvalue"] = float(estimated_value)

    if estimated_close_date:
        body["estimatedclosedate"] = estimated_close_date

    if description:
        body["description"] = description.strip()

    # =========================
    # 4️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/opportunities"
    )

    try:
        response = await client.post(url, json=body, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Opportunity created successfully",
            extra={
                "user_role": user_role,
                "accountid": account_id,
            },
        )

        return response.json()

    except HTTPStatusError as exc:
        logger.error(
            "Dynamics API error while creating opportunity",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to create opportunity in Dynamics.",
            "details": "Dynamics API returned an error.",
        }

    except TimeoutException:
        logger.error("Timeout while creating opportunity")
        return {
            "error": "Request timed out while creating opportunity. Please try again."
        }

    except Exception:
        logger.exception("Unexpected error during opportunity creation")
        return {
            "error": "An unexpected error occurred while creating the opportunity."
        }

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
    contact_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Securely update an Opportunity in Dynamics 365 Sales.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "opportunity", "update")
    if denial:
        logger.warning(
            "Opportunity update denied",
            extra={"user_role": user_role, "opportunityid": opportunity_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not opportunity_id or not opportunity_id.strip():
        return {"error": "opportunity_id is required to update an opportunity."}

    if name is not None and not name.strip():
        return {"error": "Name cannot be empty if provided."}

    if customer_need is not None and not customer_need.strip():
        return {"error": "customer_need cannot be empty if provided."}

    if budget_amount is not None and budget_amount < 0:
        return {"error": "budget_amount cannot be negative."}

    if estimated_value is not None and estimated_value < 0:
        return {"error": "estimated_value cannot be negative."}

    if description is not None and not description.strip():
        return {"error": "Description cannot be empty if provided."}

    # Prevent conflicting customer bindings
    if account_id and contact_id:
        return {
            "error": "Provide either account_id OR contact_id, not both."
        }

    # =========================
    # 3️⃣ Build PATCH Payload
    # =========================
    body: Dict[str, Any] = {}

    if name is not None:
        body["name"] = name.strip()

    if customer_need is not None:
        body["customerneed"] = customer_need.strip()

    if budget_amount is not None:
        body["budgetamount"] = float(budget_amount)

    if estimated_value is not None:
        body["estimatedvalue"] = float(estimated_value)

    if estimated_close_date is not None:
        body["estimatedclosedate"] = estimated_close_date

    if description is not None:
        body["description"] = description.strip()

    if account_id is not None:
        body["customerid_account@odata.bind"] = f"/accounts({account_id})"

    if contact_id is not None:
        body["customerid_contact@odata.bind"] = f"/contacts({contact_id})"

    if not body:
        return {
            "error": "At least one field must be provided to update the opportunity."
        }

    # =========================
    # 4️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/opportunities({opportunity_id})"
    )

    try:
        response = await client.patch(url, json=body, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Opportunity updated successfully",
            extra={
                "user_role": user_role,
                "opportunityid": opportunity_id,
                "updated_fields": list(body.keys()),
            },
        )

        return {
            "message": "Opportunity updated successfully",
            "opportunityid": opportunity_id,
            "updated_fields": list(body.keys()),
        }

    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Opportunity not found.",
                "opportunityid": opportunity_id,
            }

        logger.error(
            "Dynamics API error while updating opportunity",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to update opportunity in Dynamics.",
        }

    except TimeoutException:
        logger.error("Timeout while updating opportunity")
        return {
            "error": "Request timed out while updating opportunity. Please try again."
        }

    except Exception:
        logger.exception("Unexpected error during opportunity update")
        return {
            "error": "An unexpected error occurred while updating the opportunity."
        }

@mcp.tool()
async def delete_opportunity(user_role: str, opportunity_id: str) -> Dict[str, Any]:
    """
    Securely delete an Opportunity in Dynamics 365 Sales.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "opportunity", "delete")
    if denial:
        logger.warning(
            "Opportunity deletion denied",
            extra={"user_role": user_role, "opportunityid": opportunity_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not opportunity_id or not opportunity_id.strip():
        return {"error": "opportunity_id is required to delete an opportunity."}

    # =========================
    # 3️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/opportunities({opportunity_id})"
    )

    try:
        response = await client.delete(url, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Opportunity deleted successfully",
            extra={
                "user_role": user_role,
                "opportunityid": opportunity_id,
            },
        )

        return {
            "message": "Opportunity deleted successfully",
            "opportunityid": opportunity_id,
        }

    except HTTPStatusError as exc:
        # Already deleted / not found
        if exc.response.status_code == 404:
            logger.info(
                "Opportunity not found during deletion",
                extra={"opportunityid": opportunity_id},
            )
            return {
                "message": "Opportunity does not exist or was already deleted",
                "opportunityid": opportunity_id,
            }

        logger.error(
            "Dynamics API error while deleting opportunity",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to delete opportunity in Dynamics."
        }

    except TimeoutException:
        logger.error(
            "Timeout while deleting opportunity",
            extra={"opportunityid": opportunity_id},
        )
        return {
            "error": "Request timed out while deleting opportunity. Please try again."
        }

    except Exception:
        logger.exception(
            "Unexpected error during opportunity deletion",
            extra={"opportunityid": opportunity_id},
        )
        return {
            "error": "An unexpected error occurred while deleting the opportunity."
        }


@mcp.tool()
async def create_quote(
    user_role: str,
    name: str,
    opportunity_id: str,
    discount_percentage: Optional[float] = None,
    discount_amount: Optional[float] = None,
    freight_amount: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Create a Quote in Dynamics 365 Sales with optional discounts.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "quote", "create")
    if denial:
        logger.warning(
            "Quote creation denied",
            extra={"user_role": user_role, "action": "create_quote"},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not name or not name.strip():
        return {"error": "Quote name is required and cannot be empty."}

    if not opportunity_id or not opportunity_id.strip():
        return {"error": "Opportunity ID is required."}

    if discount_percentage is not None and not (0 <= discount_percentage <= 100):
        return {"error": "Discount percentage must be between 0 and 100."}

    if discount_amount is not None and discount_amount < 0:
        return {"error": "Discount amount cannot be negative."}

    if freight_amount is not None and freight_amount < 0:
        return {"error": "Freight amount cannot be negative."}

    # ❗ Prevent conflicting discount usage
    if discount_percentage is not None and discount_amount is not None:
        return {
            "error": "Provide either discount_percentage OR discount_amount, not both."
        }

    # =========================
    # 3️⃣ Request Construction
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes"
    )

    body: Dict[str, Any] = {
        "name": name.strip(),
        "opportunityid@odata.bind": f"/opportunities({opportunity_id})",
    }

    if discount_percentage is not None:
        body["discountpercentage"] = discount_percentage

    if discount_amount is not None:
        body["discountamount"] = discount_amount

    if freight_amount is not None:
        body["freightamount"] = freight_amount

    # =========================
    # 4️⃣ HTTP Call with Safe Handling
    # =========================
    try:
        response = await client.post(url, json=body, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Quote created successfully",
            extra={
                "user_role": user_role,
                "opportunityid": opportunity_id,
            },
        )

        return response.json()

    except HTTPStatusError as exc:
        logger.error(
            "Dynamics API error while creating quote",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to create quote in Dynamics.",
            "details": "Dynamics API returned an error.",
        }

    except TimeoutException:
        logger.error("Timeout while calling Dynamics create quote API")
        return {
            "error": "Request timed out while creating quote. Please try again.",
        }

    except Exception as exc:
        logger.exception("Unexpected error during quote creation")
        return {
            "error": "An unexpected error occurred while creating the quote.",
        }


@mcp.tool()
async def update_quote(
    user_role: str,
    quote_id: str,
    discount_percentage: Optional[float] = None,
    discount_amount: Optional[float] = None,
    freight_amount: Optional[float] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Securely update fields on a Quote in Dynamics 365 Sales.
    Enforces RBAC, validates inputs, and handles failures safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "quote", "update")
    if denial:
        logger.warning(
            "Quote update denied",
            extra={"user_role": user_role, "quoteid": quote_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not quote_id or not quote_id.strip():
        return {"error": "quote_id is required to update a quote."}

    if discount_percentage is not None and not (0 <= discount_percentage <= 100):
        return {"error": "Discount percentage must be between 0 and 100."}

    if discount_amount is not None and discount_amount < 0:
        return {"error": "Discount amount cannot be negative."}

    if freight_amount is not None and freight_amount < 0:
        return {"error": "Freight amount cannot be negative."}

    # ❗ Prevent conflicting discount updates
    if discount_percentage is not None and discount_amount is not None:
        return {
            "error": "Provide either discount_percentage OR discount_amount, not both."
        }

    # =========================
    # 3️⃣ Build PATCH Payload
    # =========================
    body: Dict[str, Any] = {}

    if discount_percentage is not None:
        body["discountpercentage"] = float(discount_percentage)

    if discount_amount is not None:
        body["discountamount"] = float(discount_amount)

    if freight_amount is not None:
        body["freightamount"] = float(freight_amount)

    if description is not None:
        if not description.strip():
            return {"error": "Description cannot be empty if provided."}
        body["description"] = description.strip()

    if not body:
        return {
            "error": "At least one field must be provided to update the quote."
        }

    # =========================
    # 4️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
    )

    try:
        response = await client.patch(url, json=body, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Quote updated successfully",
            extra={
                "user_role": user_role,
                "quoteid": quote_id,
                "updated_fields": list(body.keys()),
            },
        )

        # Dynamics PATCH returns empty body
        return {
            "message": "Quote updated successfully",
            "quoteid": quote_id,
            "updated_fields": list(body.keys()),
        }

    except HTTPStatusError as exc:
        logger.error(
            "Dynamics API error while updating quote",
            extra={
                "status_code": exc.response.status_code,
                "quoteid": quote_id,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to update quote in Dynamics.",
            "details": "Dynamics API returned an error.",
        }

    except TimeoutException:
        logger.error(
            "Timeout while updating quote",
            extra={"quoteid": quote_id},
        )
        return {
            "error": "Request timed out while updating quote. Please try again."
        }

    except Exception:
        logger.exception(
            "Unexpected error during quote update",
            extra={"quoteid": quote_id},
        )
        return {
            "error": "An unexpected error occurred while updating the quote."
        }

@mcp.tool()
async def delete_quote(user_role: str, quote_id: str) -> Dict[str, Any]:
    """
    Securely delete a Quote in Dynamics 365 Sales.
    Enforces RBAC, validates inputs, and handles errors safely.
    """

    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "quote", "delete")
    if denial:
        logger.warning(
            "Quote deletion denied",
            extra={"user_role": user_role, "quoteid": quote_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not quote_id or not quote_id.strip():
        return {"error": "quote_id is required to delete a quote."}

    # =========================
    # 3️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
    )

    try:
        response = await client.delete(url, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Quote deleted successfully",
            extra={
                "user_role": user_role,
                "quoteid": quote_id,
            },
        )

        return {
            "message": "Quote deleted successfully",
            "quoteid": quote_id,
        }

    except HTTPStatusError as exc:
        status_code = exc.response.status_code

        # Quote not found / already deleted
        if status_code == 404:
            logger.info(
                "Quote not found during deletion",
                extra={"quoteid": quote_id},
            )
            return {
                "message": "Quote does not exist or was already deleted",
                "quoteid": quote_id,
            }

        logger.error(
            "Dynamics API error while deleting quote",
            extra={
                "status_code": status_code,
                "quoteid": quote_id,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to delete quote in Dynamics.",
            "details": "Dynamics API returned an error.",
        }

    except TimeoutException:
        logger.error(
            "Timeout while deleting quote",
            extra={"quoteid": quote_id},
        )
        return {
            "error": "Request timed out while deleting quote. Please try again."
        }

    except Exception:
        logger.exception(
            "Unexpected error during quote deletion",
            extra={"quoteid": quote_id},
        )
        return {
            "error": "An unexpected error occurred while deleting the quote."
        }




# @mcp.tool()
# async def create_sales_order(
#     user_role: str,
#     name: str,
#     customer_account_id: Optional[str] = None,
#     customer_contact_id: Optional[str] = None,
#     description: Optional[str] = None,
#     request_delivery_by: Optional[str] = None,
#     payment_terms_code: Optional[int] = None,
#     freight_terms_code: Optional[int] = None,
# ) -> Dict[str, Any]:
#     """
#     Securely create a Sales Order in Dynamics 365 CRM.
#     Enforces RBAC, validates inputs, and handles failures safely.
#     """

#     # =========================
#     # 1️⃣ Authorization (Fail Fast)
#     # =========================
#     denial = enforce(user_role, "salesorder", "create")
#     if denial:
#         logger.warning(
#             "Sales order creation denied",
#             extra={"user_role": user_role},
#         )
#         return denial

#     # =========================
#     # 2️⃣ Input Validation
#     # =========================
#     if not name or not name.strip():
#         return {"error": "Sales Order name is required and cannot be empty."}

#     # Must bind to exactly ONE customer type
#     if not customer_account_id and not customer_contact_id:
#         return {
#             "error": "Either customer_account_id or customer_contact_id must be provided."
#         }

#     if customer_account_id and customer_contact_id:
#         return {
#             "error": "Provide only one customer: account OR contact, not both."
#         }

#     if description is not None and not description.strip():
#         return {"error": "Description cannot be empty if provided."}

#     if payment_terms_code is not None and payment_terms_code < 0:
#         return {"error": "payment_terms_code must be a valid positive integer."}

#     if freight_terms_code is not None and freight_terms_code < 0:
#         return {"error": "freight_terms_code must be a valid positive integer."}

#     # =========================
#     # 3️⃣ Build Request Payload
#     # =========================
#     body: Dict[str, Any] = {
#         "name": name.strip(),
#     }

#     # Bind customer
#     if customer_account_id:
#         body["customerid_account@odata.bind"] = (
#             f"/accounts({customer_account_id})"
#         )
#     else:
#         body["customerid_contact@odata.bind"] = (
#             f"/contacts({customer_contact_id})"
#         )

#     if description:
#         body["description"] = description.strip()

#     if request_delivery_by:
#         body["requestdeliveryby"] = request_delivery_by

#     if payment_terms_code is not None:
#         body["paymenttermscode"] = payment_terms_code

#     if freight_terms_code is not None:
#         body["freighttermscode"] = freight_terms_code

#     # =========================
#     # 4️⃣ Dynamics API Call
#     # =========================
#     url = (
#         f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
#         f".dynamics.com/api/data/v9.2/salesorders"
#     )

#     try:
#         response = await client.post(url, json=body, timeout=10.0)
#         response.raise_for_status()

#         logger.info(
#             "Sales order created successfully",
#             extra={
#                 "user_role": user_role,
#                 "customer_type": "account" if customer_account_id else "contact",
#             },
#         )

#         return response.json()

#     except HTTPStatusError as exc:
#         logger.error(
#             "Dynamics API error while creating sales order",
#             extra={
#                 "status_code": exc.response.status_code,
#                 "response": exc.response.text,
#             },
#         )
#         return {
#             "error": "Failed to create sales order in Dynamics.",
#             "details": "Dynamics API returned an error.",
#         }

#     except TimeoutException:
#         logger.error("Timeout while creating sales order")
#         return {
#             "error": "Request timed out while creating sales order. Please try again."
#         }

#     except Exception:
#         logger.exception("Unexpected error during sales order creation")
#         return {
#             "error": "An unexpected error occurred while creating the sales order."
#         }


@mcp.tool()
async def update_sales_order(
    user_role: str,
    sales_order_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    request_delivery_by: Optional[str] = None,
    payment_terms_code: Optional[int] = None,
    freight_terms_code: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Securely update a Sales Order in Dynamics 365.
    """

    # =========================
    # 1️⃣ Authorization
    # =========================
    denial = enforce(user_role, "salesorder", "update")
    if denial:
        logger.warning(
            "Sales order update denied",
            extra={"user_role": user_role, "salesorderid": sales_order_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not sales_order_id or not sales_order_id.strip():
        return {"error": "sales_order_id is required to update a sales order."}

    if name is not None and not name.strip():
        return {"error": "Name cannot be empty if provided."}

    if description is not None and not description.strip():
        return {"error": "Description cannot be empty if provided."}

    if payment_terms_code is not None and payment_terms_code < 0:
        return {"error": "payment_terms_code must be a positive integer."}

    if freight_terms_code is not None and freight_terms_code < 0:
        return {"error": "freight_terms_code must be a positive integer."}

    # =========================
    # 3️⃣ Build PATCH Payload
    # =========================
    body: Dict[str, Any] = {}

    if name:
        body["name"] = name.strip()

    if description:
        body["description"] = description.strip()

    if request_delivery_by:
        body["requestdeliveryby"] = request_delivery_by

    if payment_terms_code is not None:
        body["paymenttermscode"] = payment_terms_code

    if freight_terms_code is not None:
        body["freighttermscode"] = freight_terms_code

    if not body:
        return {
            "error": "At least one field must be provided to update the sales order."
        }

    # =========================
    # 4️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/salesorders({sales_order_id})"
    )

    try:
        response = await client.patch(url, json=body, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Sales order updated successfully",
            extra={
                "user_role": user_role,
                "salesorderid": sales_order_id,
                "updated_fields": list(body.keys()),
            },
        )

        return {
            "message": "Sales order updated successfully",
            "salesorderid": sales_order_id,
            "updated_fields": list(body.keys()),
        }

    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Sales order not found.",
                "salesorderid": sales_order_id,
            }

        logger.error(
            "Dynamics API error while updating sales order",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to update sales order in Dynamics.",
        }

    except TimeoutException:
        logger.error("Timeout while updating sales order")
        return {
            "error": "Request timed out while updating sales order. Please try again."
        }

    except Exception:
        logger.exception("Unexpected error during sales order update")
        return {
            "error": "An unexpected error occurred while updating the sales order."
        }
    

@mcp.tool()
async def delete_sales_order(user_role: str, sales_order_id: str) -> Dict[str, Any]:
    """
    Securely delete a Sales Order in Dynamics 365.
    """

    # =========================
    # 1️⃣ Authorization
    # =========================
    denial = enforce(user_role, "salesorder", "delete")
    if denial:
        logger.warning(
            "Sales order deletion denied",
            extra={"user_role": user_role, "salesorderid": sales_order_id},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not sales_order_id or not sales_order_id.strip():
        return {"error": "sales_order_id is required to delete a sales order."}

    # =========================
    # 3️⃣ Dynamics API Call
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/salesorders({sales_order_id})"
    )

    try:
        response = await client.delete(url, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "Sales order deleted successfully",
            extra={
                "user_role": user_role,
                "salesorderid": sales_order_id,
            },
        )

        return {
            "message": "Sales order deleted successfully",
            "salesorderid": sales_order_id,
        }

    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "message": "Sales order does not exist or was already deleted",
                "salesorderid": sales_order_id,
            }

        logger.error(
            "Dynamics API error while deleting sales order",
            extra={
                "status_code": exc.response.status_code,
                "response": exc.response.text,
            },
        )
        return {
            "error": "Failed to delete sales order in Dynamics."
        }

    except TimeoutException:
        logger.error("Timeout while deleting sales order")
        return {
            "error": "Request timed out while deleting sales order. Please try again."
        }

    except Exception:
        logger.exception("Unexpected error during sales order deletion")
        return {
            "error": "An unexpected error occurred while deleting the sales order."
        }



# Create Lead
@mcp.tool()
async def create_lead(
    user_role:str,
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
    - user role is mandatory
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


    # =========================
    # 1️⃣ Authorization
    # =========================
    denial = enforce(user_role, "lead", "create")

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


# Quotes Process MCP Tools
@mcp.tool()
async def activate_quote(
    user_role: str,
    quote_id: str,
) -> Dict[str, Any]:
    """
    Activate a Quote in Dynamics 365 Sales (Draft → Active).
    
    Activating a quote locks it in read-only mode and makes it ready for 
    customer review or approval. Once activated, the quote can be won, 
    lost, or revised, but cannot be directly edited.
    
    Prerequisites:
    - Quote must be in Draft state (statecode: 0)
    - Quote must have at least one quote product
    - Required fields must be populated
    
    Args:
        user_role: Role of the user performing the action
        quote_id: GUID of the quote to activate
    
    Returns:
        Success message or error details
    """
    
    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "quote", "activate_quote")
    if denial:
        logger.warning(
            "Quote activation denied",
            extra={"user_role": user_role, "action": "activate_quote"},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not quote_id or not quote_id.strip():
        return {"error": "Quote ID is required and cannot be empty."}
    
    # Validate GUID format
    quote_id = quote_id.strip()
    try:
        # Basic GUID format check
        if len(quote_id) != 36 or quote_id.count('-') != 4:
            raise ValueError("Invalid GUID format")
    except (ValueError, AttributeError):
        return {
            "error": "Invalid Quote ID format. Must be a valid GUID.",
            "example": "12345678-1234-1234-1234-123456789abc"
        }

    # =========================
    # 3️⃣ Pre-Activation Validation (Optional but Recommended)
    # =========================
    # Check current state before attempting activation
    validation_url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
        f"?$select=statecode,statuscode,name"
    )
    
    try:
        validation_response = await client.get(validation_url, timeout=10.0)
        validation_response.raise_for_status()
        quote_data = validation_response.json()
        
        current_state = quote_data.get("statecode")
        
        # Quote must be in Draft state (0) to be activated
        if current_state == 1:
            return {
                "error": "Quote is already in Active state.",
                "details": "The quote cannot be activated because it is already active.",
                "quote_name": quote_data.get("name"),
                "current_statecode": current_state
            }
        elif current_state == 2:
            return {
                "error": "Quote is already Won.",
                "details": "Won quotes cannot be activated. Consider revising the quote instead.",
                "quote_name": quote_data.get("name")
            }
        elif current_state == 3:
            return {
                "error": "Quote is Closed.",
                "details": "Closed quotes cannot be activated. Consider revising the quote instead.",
                "quote_name": quote_data.get("name")
            }
        
    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Quote not found.",
                "details": f"No quote exists with ID: {quote_id}"
            }
        logger.error(
            "Failed to validate quote state",
            extra={"quoteid": quote_id, "status_code": exc.response.status_code}
        )
        # Continue with activation attempt even if validation fails
    except Exception as exc:
        logger.warning(
            "Quote state validation failed, continuing with activation",
            extra={"quoteid": quote_id, "error": str(exc)}
        )
        # Continue with activation attempt

    # =========================
    # 4️⃣ Activation Request
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
    )

    # State transition: Draft (0) → Active (1)
    # StatusCode 2 = "In Progress" for Active state
    body = {
        "statecode": 1,      # Active
        "statuscode": 2      # In Progress (default for Active)
    }

    # =========================
    # 5️⃣ HTTP Call with Safe Handling
    # =========================
    try:
        response = await client.patch(url, json=body)
        response.raise_for_status()

        logger.info(
            "Quote activated successfully",
            extra={
                "user_role": user_role,
                "quoteid": quote_id,
            },
        )

        return {
            "success": True,
            "message": "Quote activated successfully",
            "quoteid": quote_id,
            "new_state": "Active (Read-Only)",
            "statecode": 1,
            "statuscode": 2,
            "next_actions": [
                "Create new Quote",
                "List Sales Orders", 
            ]
        }

    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        error_details = exc.response.text
        
        logger.error(
            "Dynamics API error while activating quote",
            extra={
                "quoteid": quote_id,
                "status_code": status_code,
                "response": error_details,
            },
        )
        
        # Common error scenarios
        if status_code == 400:
            # Parse common activation errors
            if "not in draft state" in error_details.lower():
                return {
                    "error": "Quote activation failed",
                    "details": "The quote cannot be activated because it is not in draft state.",
                    "suggestion": "Check the current state of the quote. Only Draft quotes can be activated."
                }
            elif "quote product" in error_details.lower():
                return {
                    "error": "Quote activation failed",
                    "details": "The quote must have at least one quote product before activation.",
                    "suggestion": "Add products to the quote before attempting to activate it."
                }
            else:
                return {
                    "error": "Quote activation failed due to validation error",
                    "details": error_details,
                }
        elif status_code == 404:
            return {
                "error": "Quote not found",
                "details": f"No quote exists with ID: {quote_id}"
            }
        else:
            return {
                "error": "Failed to activate quote in Dynamics",
                "details": "Dynamics API returned an error",
                "status_code": status_code
            }

    except TimeoutException:
        logger.error("Timeout while calling Dynamics activate quote API")
        return {
            "error": "Request timed out while activating quote",
            "details": "Please try again"
        }

    except Exception as exc:
        logger.exception("Unexpected error during quote activation")
        return {
            "error": "An unexpected error occurred while activating the quote",
            "details": str(exc)
        }


@mcp.tool()
async def win_quote(
    user_role: str,
    quote_id: str,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    actual_revenue: Optional[float] = None,
    close_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mark a Quote as Won in Dynamics 365 Sales (Active → Won).
    Approving this Quote signifies customer acceptance of the proposed terms.
    When a customer accepts a quote, this action closes it as won and 
    creates a QuoteClose activity record. The won quote can then be 
    converted to a Sales Order if needed.
    
    Prerequisites:
    - Quote must be in Active state (statecode: 1)
    - Quote must have been previously activated
    - User must have appropriate permissions
    
    Args:
        user_role: Role of the user performing the action
        quote_id: GUID of the quote to mark as won
        subject: Subject/reason for winning (defaults to "Quote Won")
        description: Additional details about the win
        actual_revenue: Actual revenue amount (optional)
        close_date: Close date in ISO format (defaults to today)
    
    Returns:
        Success message with won quote details or error information
    """
    
    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "quote", "win_quote")
    if denial:
        logger.warning(
            "Win quote denied",
            extra={"user_role": user_role, "action": "win_quote"},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not quote_id or not quote_id.strip():
        return {"error": "Quote ID is required and cannot be empty."}
    
    # Validate GUID format
    quote_id = quote_id.strip()
    try:
        if len(quote_id) != 36 or quote_id.count('-') != 4:
            raise ValueError("Invalid GUID format")
    except (ValueError, AttributeError):
        return {
            "error": "Invalid Quote ID format. Must be a valid GUID.",
            "example": "12345678-1234-1234-1234-123456789abc"
        }
    
    # Set default subject if not provided
    if not subject or not subject.strip():
        subject = "Quote Won"
    else:
        subject = subject.strip()[:200]  # Max length 200 per schema
    
    # Validate actual revenue if provided
    if actual_revenue is not None and actual_revenue < 0:
        return {"error": "Actual revenue cannot be negative."}
    
    # Validate close date format if provided
    if close_date:
        try:
            from datetime import datetime
            datetime.fromisoformat(close_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return {
                "error": "Invalid close_date format. Use ISO 8601 format.",
                "example": "2026-01-05T16:14:00Z or 2026-01-05"
            }

    # =========================
    # 3️⃣ Pre-Win Validation (Recommended)
    # =========================
    validation_url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
        f"?$select=statecode,statuscode,name,quotenumber"
    )
    
    try:
        validation_response = await client.get(validation_url)
        validation_response.raise_for_status()
        quote_data = validation_response.json()
        
        current_state = quote_data.get("statecode")
        quote_name = quote_data.get("name", "Unknown")
        quote_number = quote_data.get("quotenumber", "N/A")
        
        # Quote must be Active (1) to be won
        if current_state == 0:  # Draft
            return {
                "error": "Quote must be activated before it can be won.",
                "details": "The quote is currently in Draft state.",
                "quote_name": quote_name,
                "quote_number": quote_number,
                "suggestion": "Use activate_quote tool first, then mark as won."
            }
        elif current_state == 2:  # Won
            return {
                "error": "Quote is already Won.",
                "details": "This quote has already been marked as won (statecode: 2, statuscode: 4).",
                "quote_name": quote_name,
                "quote_number": quote_number
            }
        elif current_state == 3:  # Closed
            return {
                "error": "Quote is Closed.",
                "details": "Closed quotes cannot be won.",
                "quote_name": quote_name,
                "quote_number": quote_number
            }
        elif current_state != 1:  # Not Active
            return {
                "error": f"Invalid quote state: {current_state}",
                "details": "Quote must be in Active state (1) to be won.",
                "quote_name": quote_name,
                "quote_number": quote_number
            }

        
    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Quote not found.",
                "details": f"No quote exists with ID: {quote_id}"
            }
        logger.error(
            "Failed to validate quote state before winning",
            extra={"quoteid": quote_id, "status_code": exc.response.status_code}
        )
    except Exception as exc:
        logger.warning(
            "Quote state validation failed, continuing with win attempt",
            extra={"quoteid": quote_id, "error": str(exc)}
        )

    # =========================
    # 4️⃣ Build WinQuote Request
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/WinQuote"
    )

    # Build QuoteClose entity
    quote_close: Dict[str, Any] = {
        "subject": subject,
        "quoteid@odata.bind": f"/quotes({quote_id})"
    }
    
    # Add optional fields if provided
    if description:
        quote_close["description"] = description.strip()
    
    if actual_revenue is not None:
        quote_close["actualrevenue"] = actual_revenue
    
    if close_date:
        quote_close["actualend"] = close_date

    # Main request body
    # Status: -1 means use default statuscode (4 = Won)
    body = {
        "Status": -1,
        "QuoteClose": quote_close
    }

    # =========================
    # 5️⃣ HTTP Call with Safe Handling
    # =========================
    try:
        response = await client.post(url, json=body)
        response.raise_for_status()

        logger.info(
            "Quote marked as won successfully",
            extra={
                "user_role": user_role,
                "quoteid": quote_id,
                "subject": subject
            },
        )

        return {
            "success": True,
            "message": "Quote marked as Won successfully",
            "quoteid": quote_id,
            "new_state": "Won",
            "statecode": 2,
            "statuscode": 4,
            "quote_close_subject": subject,
            "next_actions": [
                "Convert to Sales Order - Create order from won quote",
                "View Opportunity - Check associated opportunity (auto-closed as won)",
                "Generate Invoice - If applicable to your process"
            ],
            "notes": [
                "The quote is now read-only and cannot be edited",
                "If an opportunity was linked, it will be automatically closed as won",
                "A QuoteClose activity has been created in the timeline"
            ]
        }

    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        error_details = exc.response.text
        
        logger.error(
            "Dynamics API error while winning quote",
            extra={
                "quoteid": quote_id,
                "status_code": status_code,
                "response": error_details,
            },
        )
        
        # Common error scenarios
        if status_code == 400:
            # Parse common win quote errors
            if "not in active state" in error_details.lower():
                return {
                    "error": "Quote cannot be won",
                    "details": "The quote must be in Active state to be marked as won.",
                    "suggestion": "Activate the quote first using activate_quote tool."
                }
            elif "already won" in error_details.lower():
                return {
                    "error": "Quote is already Won",
                    "details": "This quote has already been marked as won."
                }
            elif "subject" in error_details.lower() and "required" in error_details.lower():
                return {
                    "error": "Subject is required",
                    "details": "The QuoteClose subject field is mandatory."
                }
            else:
                return {
                    "error": "Quote win failed due to validation error",
                    "details": error_details,
                }
        elif status_code == 404:
            return {
                "error": "Quote not found",
                "details": f"No quote exists with ID: {quote_id}"
            }
        elif status_code == 403:
            return {
                "error": "Permission denied",
                "details": "You don't have sufficient permissions to win this quote.",
                "suggestion": "Contact your system administrator."
            }
        else:
            return {
                "error": "Failed to win quote in Dynamics",
                "details": "Dynamics API returned an error",
                "status_code": status_code
            }

    except TimeoutException:
        logger.error("Timeout while calling Dynamics WinQuote API")
        return {
            "error": "Request timed out while marking quote as won",
            "details": "The operation may still complete. Please verify the quote state.",
            "suggestion": "Check the quote record to confirm its current status."
        }

    except Exception as exc:
        logger.exception("Unexpected error during quote win operation")
        return {
            "error": "An unexpected error occurred while winning the quote",
            "details": str(exc)
        }

@mcp.tool()
async def close_quote(
    user_role: str,
    quote_id: str,
    status: int,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    competitor_id: Optional[str] = None,
    close_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Close a Quote as Lost, Canceled, or Revised in Dynamics 365 Sales (Active → Closed).
    
    This action closes an active quote with a specific reason. Closed quotes
    are read-only but can be revised to create a new draft version.
    
    Prerequisites:
    - Quote must be in Active state (statecode: 1)
    - Valid status code must be provided (5=Lost, 6=Canceled, 7=Revised)
    
    Args:
        user_role: Role of the user performing the action
        quote_id: GUID of the quote to close
        status: Status reason code (5=Lost, 6=Canceled, 7=Revised)
        subject: Subject/reason for closing (optional, auto-generated if not provided)
        description: Additional details about why the quote was closed
        competitor_id: GUID of competitor who won (if status=Lost)
        close_date: Close date in ISO format (defaults to today)
    
    Returns:
        Success message with closed quote details or error information
    """
    
    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    denial = enforce(user_role, "quote", "close_quote")
    if denial:
        logger.warning(
            "Close quote denied",
            extra={"user_role": user_role, "action": "close_quote"},
        )
        return denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not quote_id or not quote_id.strip():
        return {"error": "Quote ID is required and cannot be empty."}
    
    # Validate GUID format
    quote_id = quote_id.strip()
    try:
        if len(quote_id) != 36 or quote_id.count('-') != 4:
            raise ValueError("Invalid GUID format")
    except (ValueError, AttributeError):
        return {
            "error": "Invalid Quote ID format. Must be a valid GUID.",
            "example": "12345678-1234-1234-1234-123456789abc"
        }
    
    # Validate status code
    VALID_STATUSES = {
        5: "Lost",
        6: "Canceled", 
        7: "Revised"
    }
    
    if status not in VALID_STATUSES:
        return {
            "error": "Invalid status code.",
            "details": "Status must be one of the following:",
            "valid_statuses": {
                "5": "Lost - Customer chose competitor or declined",
                "6": "Canceled - Quote process abandoned",
                "7": "Revised - Quote will be revised (creates new version)"
            },
            "provided": status
        }
    
    # Auto-generate subject based on status if not provided
    if not subject or not subject.strip():
        subject = f"Quote {VALID_STATUSES[status]}"
    else:
        subject = subject.strip()[:200]  # Max length 200 per schema
    
    # Validate competitor GUID if provided
    if competitor_id:
        competitor_id = competitor_id.strip()
        try:
            if len(competitor_id) != 36 or competitor_id.count('-') != 4:
                raise ValueError("Invalid competitor GUID format")
        except (ValueError, AttributeError):
            return {
                "error": "Invalid Competitor ID format. Must be a valid GUID.",
                "example": "12345678-1234-1234-1234-123456789abc"
            }
    
    # Validate close date format if provided
    if close_date:
        try:
            from datetime import datetime
            datetime.fromisoformat(close_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return {
                "error": "Invalid close_date format. Use ISO 8601 format.",
                "example": "2026-01-05T16:16:00Z or 2026-01-05"
            }

    # =========================
    # 3️⃣ Pre-Close Validation
    # =========================
    validation_url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
        f"?$select=statecode,statuscode,name,quotenumber,totalamount"
    )
    
    quote_name = "Unknown"
    quote_number = "N/A"
    
    try:
        validation_response = await client.get(validation_url, timeout=10.0)
        validation_response.raise_for_status()
        quote_data = validation_response.json()
        
        current_state = quote_data.get("statecode")
        quote_name = quote_data.get("name", "Unknown")
        quote_number = quote_data.get("quotenumber", "N/A")
        total_amount = quote_data.get("totalamount", 0)
        
        # Quote must be Active (1) to be closed
        if current_state == 0:
            return {
                "error": "Quote must be activated before it can be closed.",
                "details": "The quote is currently in Draft state.",
                "quote_name": quote_name,
                "quote_number": quote_number,
                "suggestion": "Use activate_quote tool first, then close the quote."
            }
        elif current_state == 2:
            return {
                "error": "Quote is already Won.",
                "details": "Won quotes cannot be closed. They are already in a final state.",
                "quote_name": quote_name,
                "quote_number": quote_number
            }
        elif current_state == 3:
            return {
                "error": "Quote is already Closed.",
                "details": f"This quote was already closed with status: {quote_data.get('statuscode')}",
                "quote_name": quote_name,
                "quote_number": quote_number
            }
        
    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Quote not found.",
                "details": f"No quote exists with ID: {quote_id}"
            }
        logger.error(
            "Failed to validate quote state before closing",
            extra={"quoteid": quote_id, "status_code": exc.response.status_code}
        )
    except Exception as exc:
        logger.warning(
            "Quote state validation failed, continuing with close attempt",
            extra={"quoteid": quote_id, "error": str(exc)}
        )

    # =========================
    # 4️⃣ Build CloseQuote Request
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/CloseQuote"
    )

    # Build QuoteClose entity
    quote_close: Dict[str, Any] = {
        "subject": subject,
        "quoteid@odata.bind": f"/quotes({quote_id})"
    }
    
    # Add optional fields if provided
    if description:
        quote_close["description"] = description.strip()
    
    # Add competitor if quote was lost
    if competitor_id and status == 5:
        quote_close["competitorid@odata.bind"] = f"/competitors({competitor_id})"
    
    if close_date:
        quote_close["actualend"] = close_date

    # Main request body
    # Status: Use explicit statuscode (5=Lost, 6=Canceled, 7=Revised)
    body = {
        "Status": status,
        "QuoteClose": quote_close
    }

    # =========================
    # 5️⃣ HTTP Call with Safe Handling
    # =========================
    try:
        response = await client.post(url, json=body, timeout=15.0)
        response.raise_for_status()

        logger.info(
            "Quote closed successfully",
            extra={
                "user_role": user_role,
                "quoteid": quote_id,
                "status": status,
                "status_label": VALID_STATUSES[status],
                "subject": subject
            },
        )

        # Build response with status-specific guidance
        result = {
            "success": True,
            "message": f"Quote closed as {VALID_STATUSES[status]} successfully",
            "quoteid": quote_id,
            "quote_name": quote_name,
            "quote_number": quote_number,
            "new_state": "Closed",
            "statecode": 3,
            "statuscode": status,
            "status_reason": VALID_STATUSES[status],
            "quote_close_subject": subject,
        }
        
        # Status-specific next actions
        if status == 5:  # Lost
            result["next_actions"] = [
                "Analyze Loss - Review why the quote was lost",
                "Update Opportunity - Linked opportunity may auto-close as lost",
                "Contact Competitor Analysis - Track which competitor won"
            ]
            if competitor_id:
                result["competitor_tracked"] = competitor_id
        elif status == 6:  # Canceled
            result["next_actions"] = [
                "Document Reason - Record why the quote was canceled",
                "Update Opportunity - May need manual closure",
                "Follow Up - Consider future engagement with customer"
            ]
        elif status == 7:  # Revised
            result["next_actions"] = [
                "Revise Quote - Use ReviseQuote action to create new version",
                "Update Products - Modify pricing or products in new version",
                "Reactivate - New revised quote will be in Draft state"
            ]
            result["notes"] = [
                "Use ReviseQuote action to create a new draft version",
                "Original quote remains as historical record",
                "New quote will link to this closed version"
            ]
        
        # Common notes for all closed quotes
        result["general_notes"] = [
            "The quote is now read-only and cannot be edited",
            "A QuoteClose activity has been created in the timeline",
            "Quote can be revised to create a new version if needed"
        ]
        
        return result

    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        error_details = exc.response.text
        
        logger.error(
            "Dynamics API error while closing quote",
            extra={
                "quoteid": quote_id,
                "status_code": status_code,
                "response": error_details,
                "close_status": status
            },
        )
        
        # Common error scenarios
        if status_code == 400:
            # Parse common close quote errors
            if "not in active state" in error_details.lower():
                return {
                    "error": "Quote cannot be closed",
                    "details": "The quote must be in Active state to be closed.",
                    "suggestion": "Activate the quote first using activate_quote tool."
                }
            elif "already closed" in error_details.lower() or "already won" in error_details.lower():
                return {
                    "error": "Quote is already in a final state",
                    "details": "This quote has already been won or closed."
                }
            elif "subject" in error_details.lower() and "required" in error_details.lower():
                return {
                    "error": "Subject is required",
                    "details": "The QuoteClose subject field is mandatory."
                }
            elif "invalid status" in error_details.lower():
                return {
                    "error": "Invalid status code",
                    "details": f"Status {status} is not valid for CloseQuote action.",
                    "valid_statuses": "5 (Lost), 6 (Canceled), 7 (Revised)"
                }
            else:
                return {
                    "error": "Quote closure failed due to validation error",
                    "details": error_details,
                }
        elif status_code == 404:
            # Could be quote not found or competitor not found
            if competitor_id and "competitor" in error_details.lower():
                return {
                    "error": "Competitor not found",
                    "details": f"No competitor exists with ID: {competitor_id}",
                    "suggestion": "Verify the competitor ID or omit it from the request."
                }
            else:
                return {
                    "error": "Quote not found",
                    "details": f"No quote exists with ID: {quote_id}"
                }
        elif status_code == 403:
            return {
                "error": "Permission denied",
                "details": "You don't have sufficient permissions to close this quote.",
                "suggestion": "Contact your system administrator."
            }
        else:
            return {
                "error": "Failed to close quote in Dynamics",
                "details": "Dynamics API returned an error",
                "status_code": status_code
            }

    except TimeoutException:
        logger.error("Timeout while calling Dynamics CloseQuote API")
        return {
            "error": "Request timed out while closing quote",
            "details": "The operation may still complete. Please verify the quote state.",
            "suggestion": "Check the quote record to confirm its current status."
        }

    except Exception as exc:
        logger.exception("Unexpected error during quote close operation")
        return {
            "error": "An unexpected error occurred while closing the quote",
            "details": str(exc)
        }


@mcp.tool()
async def convert_quote_to_sales_order(
    user_role: str,
    quote_id: str,
    close_subject: Optional[str] = None,
    close_description: Optional[str] = None,
    close_date: Optional[str] = None,
    columns_to_retrieve: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Convert a Quote to a Sales Order in Dynamics 365 Sales.
    This action creates a Sales Order from a won quote, transferring all
    products, pricing, customer information, and terms. The quote must be
    in Won state before conversion. The action automatically closes the
    quote and creates the order with the same line items.
    
    Prerequisites:
    - Quote must be in Won state (statecode: 2, statuscode: 4)
    - Quote must have at least one quote product
    - User must have create privileges on Sales Order entity
    
    Args:
        user_role: Role of the user performing the action
        quote_id: GUID of the won quote to convert
        close_subject: Subject for the quote closure (defaults to "Quote Converted to Order")
        close_description: Additional closure details
        close_date: Date to close the quote (ISO format, defaults to today)
        columns_to_retrieve: List of Sales Order columns to return (e.g., ["name", "totalamount"])
    
    Returns:
        Created Sales Order entity with requested columns or error details
    """
    
    # =========================
    # 1️⃣ Authorization (Fail Fast)
    # =========================
    # Requires both quote update and sales order create permissions
    quote_denial = enforce(user_role, "quote", "quote_to_salesorder")
    if quote_denial:
        logger.warning(
            "Quote conversion denied - no quote update permission",
            extra={"user_role": user_role, "action": "quote_to_salesorder"},
        )
        return quote_denial
    
    # order_denial = enforce(user_role, "salesorder", "create")
    # if order_denial:
    #     logger.warning(
    #         "Quote conversion denied - no sales order create permission",
    #         extra={"user_role": user_role, "action": "convert_quote_to_sales_order"},
    #     )
    #     return order_denial

    # =========================
    # 2️⃣ Input Validation
    # =========================
    if not quote_id or not quote_id.strip():
        return {"error": "Quote ID is required and cannot be empty."}
    
    # Validate GUID format
    quote_id = quote_id.strip()
    try:
        if len(quote_id) != 36 or quote_id.count('-') != 4:
            raise ValueError("Invalid GUID format")
    except (ValueError, AttributeError):
        return {
            "error": "Invalid Quote ID format. Must be a valid GUID.",
            "example": "12345678-1234-1234-1234-123456789abc"
        }
    
    # Set default close subject if not provided
    if not close_subject or not close_subject.strip():
        close_subject = "Quote Converted to Sales Order"
    else:
        close_subject = close_subject.strip()[:200]
    
    # Validate close date format if provided
    if close_date:
        try:
            from datetime import datetime
            datetime.fromisoformat(close_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return {
                "error": "Invalid close_date format. Use ISO 8601 format.",
                "example": "2026-01-05T16:21:00Z or 2026-01-05"
            }
    
    # Validate columns to retrieve
    if columns_to_retrieve is not None:
        if not isinstance(columns_to_retrieve, list):
            return {
                "error": "columns_to_retrieve must be a list of strings.",
                "example": ["name", "totalamount", "ordernumber"]
            }
        # Filter out empty strings
        columns_to_retrieve = [col.strip() for col in columns_to_retrieve if col and col.strip()]

    # =========================
    # 3️⃣ Pre-Conversion Validation
    # =========================
    validation_url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/quotes({quote_id})"
        f"?$select=statecode,statuscode,name,quotenumber,totalamount"
    )
    
    quote_name = "Unknown"
    quote_number = "N/A"
    total_amount = 0
    
    try:
        validation_response = await client.get(validation_url, timeout=10.0)
        validation_response.raise_for_status()
        quote_data = validation_response.json()
        
        current_state = quote_data.get("statecode")
        current_status = quote_data.get("statuscode")
        quote_name = quote_data.get("name", "Unknown")
        quote_number = quote_data.get("quotenumber", "N/A")
        total_amount = quote_data.get("totalamount", 0)
        
        # Quote must be Won (state: 2, status: 4) to be converted
        if current_state == 0:
            return {
                "error": "Quote must be won before conversion to sales order.",
                "details": "The quote is currently in Draft state.",
                "quote_name": quote_name,
                "quote_number": quote_number,
                "required_steps": [
                    "1. Activate the quote using activate_quote",
                    "2. Win the quote using win_quote",
                    "3. Convert to sales order"
                ]
            }
        elif current_state == 1:
            return {
                "error": "Quote must be won before conversion to sales order.",
                "details": "The quote is currently Active but not won.",
                "quote_name": quote_name,
                "quote_number": quote_number,
                "suggestion": "Use win_quote tool to mark the quote as won first."
            }
        elif current_state == 3:
            return {
                "error": "Closed quotes cannot be converted to sales orders.",
                "details": f"This quote was closed with status: {current_status}",
                "quote_name": quote_name,
                "quote_number": quote_number,
                "suggestion": "Only Won quotes can be converted to orders."
            }
        elif current_state == 2 and current_status != 4:
            return {
                "error": "Quote state is inconsistent.",
                "details": f"Quote shows Won state but unexpected status: {current_status}",
                "quote_name": quote_name,
                "quote_number": quote_number
            }
        
    except HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "error": "Quote not found.",
                "details": f"No quote exists with ID: {quote_id}"
            }
        logger.error(
            "Failed to validate quote state before conversion",
            extra={"quoteid": quote_id, "status_code": exc.response.status_code}
        )
    except Exception as exc:
        logger.warning(
            "Quote state validation failed, continuing with conversion attempt",
            extra={"quoteid": quote_id, "error": str(exc)}
        )

    # =========================
    # 4️⃣ Build ConvertQuoteToSalesOrder Request
    # =========================
    url = (
        f"https://{DYNAMICS_ORG}.{DYNAMICS_REGION}"
        f".dynamics.com/api/data/v9.2/ConvertQuoteToSalesOrder"
    )

    # Build request body
    body: Dict[str, Any] = {
        "QuoteId": quote_id,
        "QuoteCloseStatus": 4,  # Won status
        "QuoteCloseSubject": close_subject,
        "ColumnSet": {
            "AllColumns": True,
        }
    }
    
    # Add optional close fields
    if close_description:
        body["QuoteCloseDescription"] = close_description.strip()
    
    if close_date:
        body["QuoteCloseDate"] = close_date
    
    # Build ColumnSet for returned Sales Order
    # if columns_to_retrieve:
    #     body["ColumnSet"] = {
    #         "AllColumns": False,
    #         "Columns": columns_to_retrieve
    #     }
    # else:
    #     # Default columns to retrieve
    #     body["ColumnSet"] = {
    #         "AllColumns": False,
    #         "Columns": [
    #             "salesorderid",
    #             "name", 
    #             "ordernumber",
    #             "totalamount",
    #             "quoteid"
    #         ]
    #     }

    # =========================
    # 5️⃣ HTTP Call with Safe Handling
    # =========================
    try:
        response = await client.post(url, json=body, timeout=20.0)
        response.raise_for_status()

        # Parse response - contains the created Sales Order entity
        sales_order = response.json()
        sales_order_id = sales_order.get("salesorderid")
        
        logger.info(
            "Quote converted to sales order successfully",
            extra={
                "user_role": user_role,
                "quoteid": quote_id,
                "salesorderid": sales_order_id,
                "quote_number": quote_number
            },
        )

        return {
            "success": True,
            "message": "Quote successfully converted to Sales Order",
            "quote_info": {
                "original_amount": total_amount
            },
            "salesorderid": sales_order_id,
            "sales_order": {
                "name": sales_order.get("name"),
                "ordernumber": sales_order.get("ordernumber"),
                "totalamount": sales_order.get("totalamount"),
                # "quoteid": sales_order.get("quoteid"),
                # **{k: v for k, v in sales_order.items() 
                #    if k not in ["salesorderid", "name", "ordernumber", "totalamount", "quoteid"]}
            },
            "next_actions": [
                "Fulfill Order - Process the order for delivery",
                "Generate Invoice - Create invoice from the order",
                "Track Shipment - Monitor order fulfillment status",
                "Update Inventory - Adjust stock levels"
            ],
            "notes": [
                "All **quote** products have been transferred to the order",
                "Quote is now closed with 'Converted to Order' status",
                "Any quote customizations or notes are preserved in the order"
            ]
        }

    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        error_details = exc.response.text
        
        logger.error(
            "Dynamics API error while converting quote to sales order",
            extra={
                "quoteid": quote_id,
                "status_code": status_code,
                "response": error_details,
            },
        )
        
        # Common error scenarios
        if status_code == 400:
            # Parse common conversion errors
            if "not won" in error_details.lower() or "not in won state" in error_details.lower():
                return {
                    "error": "Quote conversion failed",
                    "details": "The quote must be in Won state before conversion.",
                    "suggestion": "Use win_quote tool to mark the quote as won first."
                }
            elif "quote product" in error_details.lower() or "no products" in error_details.lower():
                return {
                    "error": "Quote conversion failed",
                    "details": "The quote must have at least one product line before conversion.",
                    "suggestion": "Add products to the quote before attempting conversion."
                }
            elif "price list" in error_details.lower():
                return {
                    "error": "Quote conversion failed",
                    "details": "The quote has an invalid or inactive price list.",
                    "suggestion": "Ensure the quote has a valid, active price list assigned."
                }
            elif "already converted" in error_details.lower():
                return {
                    "error": "Quote has already been converted",
                    "details": "This quote has already been converted to a sales order.",
                    "suggestion": "Check existing sales orders linked to this quote."
                }
            else:
                return {
                    "error": "Quote conversion failed due to validation error",
                    "details": error_details,
                }
        elif status_code == 404:
            return {
                "error": "Quote not found",
                "details": f"No quote exists with ID: {quote_id}"
            }
        elif status_code == 403:
            return {
                "error": "Permission denied",
                "details": "You don't have sufficient permissions to convert quotes or create sales orders.",
                "suggestion": "Contact your system administrator."
            }
        else:
            return {
                "error": "Failed to convert quote to sales order",
                "details": "Dynamics API returned an error",
                "status_code": status_code
            }

    except TimeoutException:
        logger.error("Timeout while calling Dynamics ConvertQuoteToSalesOrder API")
        return {
            "error": "Request timed out while converting quote to sales order",
            "details": "The operation may still complete. Please verify both quote and sales order records.",
            "suggestion": "Check if a sales order was created despite the timeout."
        }

    except Exception as exc:
        logger.exception("Unexpected error during quote to sales order conversion")
        return {
            "error": "An unexpected error occurred while converting quote to sales order",
            "details": str(exc)
        }



if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=6000, path="/mcp")