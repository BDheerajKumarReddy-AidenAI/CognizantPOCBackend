import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from mcp_server.dynamics_auth import get_authenticator
# from mcp_server.models.opportunity import OpportunityCreate, OpportunityUpdate, Opportunity, OpportunityListResponse
# from mcp_server.models.lead import LeadCreate, LeadUpdate, Lead, LeadListResponse
# from mcp_server.models.account import AccountCreate, AccountUpdate, Account, AccountListResponse
# from mcp_server.models.contact import ContactCreate, ContactUpdate, Contact, ContactListResponse
# from mcp_server.models.product import ProductCreate, ProductUpdate, Product, ProductListResponse
# from mcp_server.models.quote import QuoteCreate, QuoteUpdate, Quote, QuoteListResponse
# from mcp_server.models.salesorder import SalesOrderCreate, SalesOrderUpdate, SalesOrder, SalesOrderListResponse

# Initialize FastMCP server
mcp = FastMCP("Dynamics365 CRM")

# Get authenticator instance
auth = get_authenticator()

# Helper function to make API calls
async def make_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None
) -> dict:
    """Make an HTTP request to Dynamics 365 API"""
    base_url = auth.get_base_url()
    headers = auth.get_headers()
    url = f"{base_url}/{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        
        # DELETE returns 204 No Content
        if response.status_code == 204:
            return {"success": True, "message": "Resource deleted successfully"}
        
        return response.json()


# ============================================================================
# OPPORTUNITY TOOLS
# ============================================================================

@mcp.tool()
async def create_opportunity(
    name: str,
    customerid: str,
    estimatedvalue: Optional[float] = None,
    estimatedclosedate: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create a new opportunity in Dynamics 365.
    
    Args:
        name: Topic - descriptive name for the opportunity (required)
        customerid: UUID of the potential customer (account or contact) (required)
        estimatedvalue: Estimated revenue amount
        estimatedclosedate: Expected closing date (YYYY-MM-DD format)
        description: Additional information about the opportunity
        **kwargs: Additional fields from OpportunityCreate model
    
    Returns:
        JSON string with the created opportunity details
    """
    opportunity_data = {
        "name": name,
        "customerid@odata.bind": f"/accounts({customerid})" if kwargs.get("customeridtype") == "account" else f"/contacts({customerid})",
        **kwargs
    }
    
    if estimatedvalue is not None:
        opportunity_data["estimatedvalue"] = estimatedvalue
    if estimatedclosedate:
        opportunity_data["estimatedclosedate"] = estimatedclosedate
    if description:
        opportunity_data["description"] = description
    
    result = await make_request("POST", "opportunities", data=opportunity_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_opportunity(opportunityid: str) -> str:
    """
    Retrieve a specific opportunity by ID.
    
    Args:
        opportunityid: UUID of the opportunity
    
    Returns:
        JSON string with the opportunity details
    """
    result = await make_request("GET", f"opportunities({opportunityid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_opportunities(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List opportunities with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of opportunities
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "opportunities", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_opportunity(
    opportunityid: str,
    name: Optional[str] = None,
    estimatedvalue: Optional[float] = None,
    estimatedclosedate: Optional[str] = None,
    closeprobability: Optional[int] = None,
    description: Optional[str] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing opportunity.
    
    Args:
        opportunityid: UUID of the opportunity to update (required)
        name: Updated name
        estimatedvalue: Updated estimated revenue
        estimatedclosedate: Updated expected closing date (YYYY-MM-DD)
        closeprobability: Updated probability (0-100)
        description: Updated description
        statecode: Status (0=Open, 1=Won, 2=Lost)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated opportunity details
    """
    update_data = {**kwargs}
    
    if name is not None:
        update_data["name"] = name
    if estimatedvalue is not None:
        update_data["estimatedvalue"] = estimatedvalue
    if estimatedclosedate is not None:
        update_data["estimatedclosedate"] = estimatedclosedate
    if closeprobability is not None:
        update_data["closeprobability"] = closeprobability
    if description is not None:
        update_data["description"] = description
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"opportunities({opportunityid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_opportunity(opportunityid: str) -> str:
    """
    Delete an opportunity.
    
    Args:
        opportunityid: UUID of the opportunity to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"opportunities({opportunityid})")
    return json.dumps(result, indent=2)


# ============================================================================
# LEAD TOOLS
# ============================================================================

@mcp.tool()
async def create_lead(
    lastname: str,
    firstname: Optional[str] = None,
    companyname: Optional[str] = None,
    emailaddress1: Optional[str] = None,
    telephone1: Optional[str] = None,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create a new lead in Dynamics 365.
    
    Args:
        lastname: Last name of the lead (required)
        firstname: First name of the lead
        companyname: Company name
        emailaddress1: Email address
        telephone1: Business phone
        subject: Topic describing the lead
        description: Additional information
        **kwargs: Additional fields from LeadCreate model
    
    Returns:
        JSON string with the created lead details
    """
    lead_data = {
        "lastname": lastname,
        **kwargs
    }
    
    if firstname:
        lead_data["firstname"] = firstname
    if companyname:
        lead_data["companyname"] = companyname
    if emailaddress1:
        lead_data["emailaddress1"] = emailaddress1
    if telephone1:
        lead_data["telephone1"] = telephone1
    if subject:
        lead_data["subject"] = subject
    if description:
        lead_data["description"] = description
    
    result = await make_request("POST", "leads", data=lead_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_lead(leadid: str) -> str:
    """
    Retrieve a specific lead by ID.
    
    Args:
        leadid: UUID of the lead
    
    Returns:
        JSON string with the lead details
    """
    result = await make_request("GET", f"leads({leadid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_leads(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List leads with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of leads
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "leads", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_lead(
    leadid: str,
    firstname: Optional[str] = None,
    lastname: Optional[str] = None,
    companyname: Optional[str] = None,
    emailaddress1: Optional[str] = None,
    telephone1: Optional[str] = None,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing lead.
    
    Args:
        leadid: UUID of the lead to update (required)
        firstname: Updated first name
        lastname: Updated last name
        companyname: Updated company name
        emailaddress1: Updated email
        telephone1: Updated phone
        subject: Updated topic
        description: Updated description
        statecode: Status (0=Open, 1=Qualified, 2=Disqualified)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated lead details
    """
    update_data = {**kwargs}
    
    if firstname is not None:
        update_data["firstname"] = firstname
    if lastname is not None:
        update_data["lastname"] = lastname
    if companyname is not None:
        update_data["companyname"] = companyname
    if emailaddress1 is not None:
        update_data["emailaddress1"] = emailaddress1
    if telephone1 is not None:
        update_data["telephone1"] = telephone1
    if subject is not None:
        update_data["subject"] = subject
    if description is not None:
        update_data["description"] = description
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"leads({leadid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_lead(leadid: str) -> str:
    """
    Delete a lead.
    
    Args:
        leadid: UUID of the lead to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"leads({leadid})")
    return json.dumps(result, indent=2)


# ============================================================================
# ACCOUNT TOOLS
# ============================================================================

@mcp.tool()
async def create_account(
    name: str,
    accountnumber: Optional[str] = None,
    emailaddress1: Optional[str] = None,
    telephone1: Optional[str] = None,
    websiteurl: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create a new account in Dynamics 365.
    
    Args:
        name: Account name (required)
        accountnumber: Account number
        emailaddress1: Email address
        telephone1: Main phone
        websiteurl: Website URL
        description: Additional information
        **kwargs: Additional fields from AccountCreate model
    
    Returns:
        JSON string with the created account details
    """
    account_data = {
        "name": name,
        **kwargs
    }
    
    if accountnumber:
        account_data["accountnumber"] = accountnumber
    if emailaddress1:
        account_data["emailaddress1"] = emailaddress1
    if telephone1:
        account_data["telephone1"] = telephone1
    if websiteurl:
        account_data["websiteurl"] = websiteurl
    if description:
        account_data["description"] = description
    
    result = await make_request("POST", "accounts", data=account_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_account(accountid: str) -> str:
    """
    Retrieve a specific account by ID.
    
    Args:
        accountid: UUID of the account
    
    Returns:
        JSON string with the account details
    """
    result = await make_request("GET", f"accounts({accountid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_accounts(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List accounts with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of accounts
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "accounts", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_account(
    accountid: str,
    name: Optional[str] = None,
    emailaddress1: Optional[str] = None,
    telephone1: Optional[str] = None,
    websiteurl: Optional[str] = None,
    description: Optional[str] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing account.
    
    Args:
        accountid: UUID of the account to update (required)
        name: Updated account name
        emailaddress1: Updated email
        telephone1: Updated phone
        websiteurl: Updated website
        description: Updated description
        statecode: Status (0=Active, 1=Inactive)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated account details
    """
    update_data = {**kwargs}
    
    if name is not None:
        update_data["name"] = name
    if emailaddress1 is not None:
        update_data["emailaddress1"] = emailaddress1
    if telephone1 is not None:
        update_data["telephone1"] = telephone1
    if websiteurl is not None:
        update_data["websiteurl"] = websiteurl
    if description is not None:
        update_data["description"] = description
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"accounts({accountid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_account(accountid: str) -> str:
    """
    Delete an account.
    
    Args:
        accountid: UUID of the account to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"accounts({accountid})")
    return json.dumps(result, indent=2)


# ============================================================================
# CONTACT TOOLS
# ============================================================================

@mcp.tool()
async def create_contact(
    lastname: str,
    firstname: Optional[str] = None,
    emailaddress1: Optional[str] = None,
    telephone1: Optional[str] = None,
    mobilephone: Optional[str] = None,
    jobtitle: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create a new contact in Dynamics 365.
    
    Args:
        lastname: Last name (required)
        firstname: First name
        emailaddress1: Email address
        telephone1: Business phone
        mobilephone: Mobile phone
        jobtitle: Job title
        description: Additional information
        **kwargs: Additional fields from ContactCreate model
    
    Returns:
        JSON string with the created contact details
    """
    contact_data = {
        "lastname": lastname,
        **kwargs
    }
    
    if firstname:
        contact_data["firstname"] = firstname
    if emailaddress1:
        contact_data["emailaddress1"] = emailaddress1
    if telephone1:
        contact_data["telephone1"] = telephone1
    if mobilephone:
        contact_data["mobilephone"] = mobilephone
    if jobtitle:
        contact_data["jobtitle"] = jobtitle
    if description:
        contact_data["description"] = description
    
    result = await make_request("POST", "contacts", data=contact_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_contact(contactid: str) -> str:
    """
    Retrieve a specific contact by ID.
    
    Args:
        contactid: UUID of the contact
    
    Returns:
        JSON string with the contact details
    """
    result = await make_request("GET", f"contacts({contactid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_contacts(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List contacts with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of contacts
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "contacts", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_contact(
    contactid: str,
    firstname: Optional[str] = None,
    lastname: Optional[str] = None,
    emailaddress1: Optional[str] = None,
    telephone1: Optional[str] = None,
    mobilephone: Optional[str] = None,
    jobtitle: Optional[str] = None,
    description: Optional[str] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing contact.
    
    Args:
        contactid: UUID of the contact to update (required)
        firstname: Updated first name
        lastname: Updated last name
        emailaddress1: Updated email
        telephone1: Updated business phone
        mobilephone: Updated mobile phone
        jobtitle: Updated job title
        description: Updated description
        statecode: Status (0=Active, 1=Inactive)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated contact details
    """
    update_data = {**kwargs}
    
    if firstname is not None:
        update_data["firstname"] = firstname
    if lastname is not None:
        update_data["lastname"] = lastname
    if emailaddress1 is not None:
        update_data["emailaddress1"] = emailaddress1
    if telephone1 is not None:
        update_data["telephone1"] = telephone1
    if mobilephone is not None:
        update_data["mobilephone"] = mobilephone
    if jobtitle is not None:
        update_data["jobtitle"] = jobtitle
    if description is not None:
        update_data["description"] = description
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"contacts({contactid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_contact(contactid: str) -> str:
    """
    Delete a contact.
    
    Args:
        contactid: UUID of the contact to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"contacts({contactid})")
    return json.dumps(result, indent=2)


# ============================================================================
# PRODUCT TOOLS
# ============================================================================

@mcp.tool()
async def create_product(
    name: str,
    productnumber: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    standardcost: Optional[float] = None,
    currentcost: Optional[float] = None,
    **kwargs
) -> str:
    """
    Create a new product in Dynamics 365.
    
    Args:
        name: Product name (required)
        productnumber: Product ID/SKU
        description: Product description
        price: List price
        standardcost: Standard cost
        currentcost: Current cost
        **kwargs: Additional fields from ProductCreate model
    
    Returns:
        JSON string with the created product details
    """
    product_data = {
        "name": name,
        **kwargs
    }
    
    if productnumber:
        product_data["productnumber"] = productnumber
    if description:
        product_data["description"] = description
    if price is not None:
        product_data["price"] = price
    if standardcost is not None:
        product_data["standardcost"] = standardcost
    if currentcost is not None:
        product_data["currentcost"] = currentcost
    
    result = await make_request("POST", "products", data=product_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_product(productid: str) -> str:
    """
    Retrieve a specific product by ID.
    
    Args:
        productid: UUID of the product
    
    Returns:
        JSON string with the product details
    """
    result = await make_request("GET", f"products({productid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_products(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List products with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of products
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "products", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_product(
    productid: str,
    name: Optional[str] = None,
    productnumber: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    standardcost: Optional[float] = None,
    currentcost: Optional[float] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing product.
    
    Args:
        productid: UUID of the product to update (required)
        name: Updated product name
        productnumber: Updated product ID/SKU
        description: Updated description
        price: Updated list price
        standardcost: Updated standard cost
        currentcost: Updated current cost
        statecode: Status (0=Active, 1=Retired, 2=Draft, 3=Under Revision)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated product details
    """
    update_data = {**kwargs}
    
    if name is not None:
        update_data["name"] = name
    if productnumber is not None:
        update_data["productnumber"] = productnumber
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = price
    if standardcost is not None:
        update_data["standardcost"] = standardcost
    if currentcost is not None:
        update_data["currentcost"] = currentcost
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"products({productid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_product(productid: str) -> str:
    """
    Delete a product.
    
    Args:
        productid: UUID of the product to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"products({productid})")
    return json.dumps(result, indent=2)


# ============================================================================
# QUOTE TOOLS
# ============================================================================

@mcp.tool()
async def create_quote(
    customerid: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    effectivefrom: Optional[str] = None,
    effectiveto: Optional[str] = None,
    expirationdate: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create a new quote in Dynamics 365.
    
    Args:
        customerid: UUID of the customer (account or contact) (required)
        name: Quote name
        description: Quote description
        effectivefrom: Effective from date (YYYY-MM-DD)
        effectiveto: Effective to date (YYYY-MM-DD)
        expirationdate: Expiration date (YYYY-MM-DD)
        **kwargs: Additional fields from QuoteCreate model
    
    Returns:
        JSON string with the created quote details
    """
    quote_data = {
        "customerid@odata.bind": f"/accounts({customerid})" if kwargs.get("customeridtype") == "account" else f"/contacts({customerid})",
        **kwargs
    }
    
    if name:
        quote_data["name"] = name
    if description:
        quote_data["description"] = description
    if effectivefrom:
        quote_data["effectivefrom"] = effectivefrom
    if effectiveto:
        quote_data["effectiveto"] = effectiveto
    if expirationdate:
        quote_data["expirationdate"] = expirationdate
    
    result = await make_request("POST", "quotes", data=quote_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_quote(quoteid: str) -> str:
    """
    Retrieve a specific quote by ID.
    
    Args:
        quoteid: UUID of the quote
    
    Returns:
        JSON string with the quote details
    """
    result = await make_request("GET", f"quotes({quoteid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_quotes(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List quotes with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of quotes
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "quotes", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_quote(
    quoteid: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    effectivefrom: Optional[str] = None,
    effectiveto: Optional[str] = None,
    expirationdate: Optional[str] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing quote.
    
    Args:
        quoteid: UUID of the quote to update (required)
        name: Updated name
        description: Updated description
        effectivefrom: Updated effective from date (YYYY-MM-DD)
        effectiveto: Updated effective to date (YYYY-MM-DD)
        expirationdate: Updated expiration date (YYYY-MM-DD)
        statecode: Status (0=Draft, 1=Active, 2=Won, 3=Closed, 4=Lost)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated quote details
    """
    update_data = {**kwargs}
    
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if effectivefrom is not None:
        update_data["effectivefrom"] = effectivefrom
    if effectiveto is not None:
        update_data["effectiveto"] = effectiveto
    if expirationdate is not None:
        update_data["expirationdate"] = expirationdate
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"quotes({quoteid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_quote(quoteid: str) -> str:
    """
    Delete a quote.
    
    Args:
        quoteid: UUID of the quote to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"quotes({quoteid})")
    return json.dumps(result, indent=2)


# ============================================================================
# SALES ORDER TOOLS
# ============================================================================

@mcp.tool()
async def create_salesorder(
    customerid: str,
    pricelevelid: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    requestdeliveryby: Optional[str] = None,
    **kwargs
) -> str:
    """
    Create a new sales order in Dynamics 365.
    
    Args:
        customerid: UUID of the customer (account or contact) (required)
        pricelevelid: UUID of the price list (required)
        name: Order name
        description: Order description
        requestdeliveryby: Requested delivery date (YYYY-MM-DD)
        **kwargs: Additional fields from SalesOrderCreate model
    
    Returns:
        JSON string with the created sales order details
    """
    order_data = {
        "customerid@odata.bind": f"/accounts({customerid})" if kwargs.get("customeridtype") == "account" else f"/contacts({customerid})",
        "pricelevelid@odata.bind": f"/pricelevels({pricelevelid})",
        **kwargs
    }
    
    if name:
        order_data["name"] = name
    if description:
        order_data["description"] = description
    if requestdeliveryby:
        order_data["requestdeliveryby"] = requestdeliveryby
    
    result = await make_request("POST", "salesorders", data=order_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_salesorder(salesorderid: str) -> str:
    """
    Retrieve a specific sales order by ID.
    
    Args:
        salesorderid: UUID of the sales order
    
    Returns:
        JSON string with the sales order details
    """
    result = await make_request("GET", f"salesorders({salesorderid})")
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_salesorders(
    filter: Optional[str] = None,
    select: Optional[str] = None,
    top: Optional[int] = 50,
    orderby: Optional[str] = None
) -> str:
    """
    List sales orders with optional filtering and pagination.
    
    Args:
        filter: OData filter expression (e.g., "statecode eq 0")
        select: Comma-separated list of fields to retrieve
        top: Maximum number of records to return (default: 50)
        orderby: Field to sort by (e.g., "createdon desc")
    
    Returns:
        JSON string with list of sales orders
    """
    params = {}
    if filter:
        params["$filter"] = filter
    if select:
        params["$select"] = select
    if top:
        params["$top"] = top
    if orderby:
        params["$orderby"] = orderby
    
    result = await make_request("GET", "salesorders", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_salesorder(
    salesorderid: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    requestdeliveryby: Optional[str] = None,
    datefulfilled: Optional[str] = None,
    ispricelocked: Optional[bool] = None,
    statecode: Optional[int] = None,
    statuscode: Optional[int] = None,
    **kwargs
) -> str:
    """
    Update an existing sales order.
    
    Args:
        salesorderid: UUID of the sales order to update (required)
        name: Updated name
        description: Updated description
        requestdeliveryby: Updated requested delivery date (YYYY-MM-DD)
        datefulfilled: Updated date fulfilled (YYYY-MM-DD)
        ispricelocked: Whether prices are locked
        statecode: Status (0=Active, 1=Submitted, 2=Canceled, 3=Fulfilled, 4=Invoiced)
        statuscode: Status reason
        **kwargs: Additional fields to update
    
    Returns:
        JSON string with the updated sales order details
    """
    update_data = {**kwargs}
    
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if requestdeliveryby is not None:
        update_data["requestdeliveryby"] = requestdeliveryby
    if datefulfilled is not None:
        update_data["datefulfilled"] = datefulfilled
    if ispricelocked is not None:
        update_data["ispricelocked"] = ispricelocked
    if statecode is not None:
        update_data["statecode"] = statecode
    if statuscode is not None:
        update_data["statuscode"] = statuscode
    
    result = await make_request("PATCH", f"salesorders({salesorderid})", data=update_data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_salesorder(salesorderid: str) -> str:
    """
    Delete a sales order.
    
    Args:
        salesorderid: UUID of the sales order to delete
    
    Returns:
        JSON string with success message
    """
    result = await make_request("DELETE", f"salesorders({salesorderid})")
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # mcp.run(transport="http", host="127.0.0.1", port=6000, path="/mcp")
    mcp.run()