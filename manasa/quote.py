from pydantic import Field
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from mcp_server.models import DynamicsEntityBase, DynamicsBaseModel


class QuoteBase(DynamicsEntityBase):
    """Base Quote model with writable fields"""
    
    # Core fields
    name: Optional[str] = Field(None, max_length=300, description="Name")
    quotenumber: Optional[str] = Field(None, max_length=100, description="Quote ID")
    
    # Customer
    customerid: UUID = Field(..., description="Potential Customer")
    customeridtype: Optional[Literal["account", "contact"]] = Field(None, description="Potential Customer Type")
    
    # Description
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    
    # Financial fields
    totalamount: Optional[Decimal] = Field(None, description="Total Amount")
    totalamountlessfreight: Optional[Decimal] = Field(None, description="Total Pre-Freight Amount")
    totaldiscountamount: Optional[Decimal] = Field(None, description="Total Discount Amount")
    totallineitemamount: Optional[Decimal] = Field(None, description="Total Detail Amount")
    totallineitemdiscountamount: Optional[Decimal] = Field(None, description="Total Line Item Discount Amount")
    totaltax: Optional[Decimal] = Field(None, description="Total Tax")
    discountamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Quote Discount Amount")
    discountpercentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Quote Discount (%)")
    freightamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Freight Amount")
    
    # Dates
    effectivefrom: Optional[date] = Field(None, description="Effective From")
    effectiveto: Optional[date] = Field(None, description="Effective To")
    requestdeliveryby: Optional[date] = Field(None, description="Requested Delivery Date")
    closedon: Optional[datetime] = Field(None, description="Closed On")
    
    # Expiration
    expirationdate: Optional[date] = Field(None, description="Due By")
    
    # Related records
    opportunityid: Optional[UUID] = Field(None, description="Opportunity")
    campaignid: Optional[UUID] = Field(None, description="Source Campaign")
    pricelevelid: Optional[UUID] = Field(None, description="Price List")
    transactioncurrencyid: Optional[UUID] = Field(None, description="Currency")
    
    # Shipping information
    shippingmethodcode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Shipping Method")
    freighttermscode: Optional[Literal[1, 2]] = Field(None, description="Freight Terms")
    paymenttermscode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Payment Terms")
    
    # Bill To Address
    billto_addressid: Optional[UUID] = Field(None, description="Bill To Address ID")
    billto_line1: Optional[str] = Field(None, max_length=250, description="Bill To Street 1")
    billto_line2: Optional[str] = Field(None, max_length=250, description="Bill To Street 2")
    billto_line3: Optional[str] = Field(None, max_length=250, description="Bill To Street 3")
    billto_city: Optional[str] = Field(None, max_length=80, description="Bill To City")
    billto_stateorprovince: Optional[str] = Field(None, max_length=50, description="Bill To State/Province")
    billto_postalcode: Optional[str] = Field(None, max_length=20, description="Bill To ZIP/Postal Code")
    billto_country: Optional[str] = Field(None, max_length=80, description="Bill To Country/Region")
    billto_name: Optional[str] = Field(None, max_length=200, description="Bill To Name")
    billto_contactname: Optional[str] = Field(None, max_length=150, description="Bill To Contact Name")
    billto_telephone: Optional[str] = Field(None, max_length=50, description="Bill To Phone")
    billto_fax: Optional[str] = Field(None, max_length=50, description="Bill To Fax")
    
    # Ship To Address
    shipto_addressid: Optional[UUID] = Field(None, description="Ship To Address ID")
    shipto_line1: Optional[str] = Field(None, max_length=250, description="Ship To Street 1")
    shipto_line2: Optional[str] = Field(None, max_length=250, description="Ship To Street 2")
    shipto_line3: Optional[str] = Field(None, max_length=250, description="Ship To Street 3")
    shipto_city: Optional[str] = Field(None, max_length=80, description="Ship To City")
    shipto_stateorprovince: Optional[str] = Field(None, max_length=50, description="Ship To State/Province")
    shipto_postalcode: Optional[str] = Field(None, max_length=20, description="Ship To ZIP/Postal Code")
    shipto_country: Optional[str] = Field(None, max_length=80, description="Ship To Country/Region")
    shipto_name: Optional[str] = Field(None, max_length=200, description="Ship To Name")
    shipto_contactname: Optional[str] = Field(None, max_length=150, description="Ship To Contact Name")
    shipto_telephone: Optional[str] = Field(None, max_length=50, description="Ship To Phone")
    shipto_fax: Optional[str] = Field(None, max_length=50, description="Ship To Fax")
    shipto_freighttermscode: Optional[Literal[1, 2]] = Field(None, description="Ship To Freight Terms")
    
    # Contact
    contactid: Optional[UUID] = Field(None, description="Contact")
    
    # Status
    statecode: Optional[Literal[0, 1, 2, 3, 4]] = Field(0, description="Status: 0=Draft, 1=Active, 2=Won, 3=Closed, 4=Lost")
    statuscode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Status Reason")
    
    # Pricing
    willcall: Optional[bool] = Field(False, description="Ship To")
    
    # Revision
    revisionnumber: Optional[int] = Field(0, description="Revision ID")
    
    # Email
    emailaddress: Optional[str] = Field(None, max_length=100, description="Email Address")
    
    # SLA
    slaid: Optional[UUID] = Field(None, description="SLA")
    
    # System fields
    importsequencenumber: Optional[int] = Field(None, description="Import Sequence Number")
    overriddencreatedon: Optional[date] = Field(None, description="Record Created On")
    timezoneruleversionnumber: Optional[int] = Field(None, description="Time Zone Rule Version Number")
    utcconversiontimezonecode: Optional[int] = Field(None, ge=-1, le=1500, description="UTC Conversion Time Zone Code")
    
    # Pricing error
    pricingerrorcode: Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]] = Field(0, description="Pricing Error")
    
    # Skip price calculation
    skippricecalculation: Optional[Literal[0, 1]] = Field(0, description="Skip Price Calculation")
    
    # On hold
    lastonholdtime: Optional[datetime] = Field(None, description="Last On Hold Time")
    
    # Entity image
    entityimage: Optional[bytes] = Field(None, description="Entity Image")
    
    # Advanced fields
    msdyn_ordertype: Optional[UUID] = Field(None, description="Order Type")
    msdyn_psastatusreason: Optional[str] = Field(None, max_length=1000, description="Project Status Reason")


class QuoteCreate(QuoteBase):
    """Model for creating a new quote"""
    pass


class QuoteUpdate(DynamicsEntityBase):
    """Model for updating a quote - all fields optional"""
    name: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = Field(None, max_length=2000)
    customerid: Optional[UUID] = None
    effectivefrom: Optional[date] = None
    effectiveto: Optional[date] = None
    expirationdate: Optional[date] = None
    discountamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000)
    discountpercentage: Optional[Decimal] = Field(None, ge=0, le=100)
    freightamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000)
    statecode: Optional[Literal[0, 1, 2, 3, 4]] = None
    statuscode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = None


class Quote(QuoteBase):
    """Complete Quote model including read-only fields"""
    quoteid: UUID = Field(..., description="Unique identifier of the quote")
    
    # Read-only fields
    createdby: Optional[UUID] = Field(None, description="Created By")
    createdonbehalfby: Optional[UUID] = Field(None, description="Created By (Delegate)")
    modifiedby: Optional[UUID] = Field(None, description="Modified By")
    modifiedonbehalfby: Optional[UUID] = Field(None, description="Modified By (Delegate)")
    
    # Base currency fields
    totalamount_base: Optional[Decimal] = Field(None, description="Total Amount (Base)")
    totalamountlessfreight_base: Optional[Decimal] = Field(None, description="Total Pre-Freight Amount (Base)")
    totaldiscountamount_base: Optional[Decimal] = Field(None, description="Total Discount Amount (Base)")
    totallineitemamount_base: Optional[Decimal] = Field(None, description="Total Detail Amount (Base)")
    totallineitemdiscountamount_base: Optional[Decimal] = Field(None, description="Total Line Item Discount Amount (Base)")
    totaltax_base: Optional[Decimal] = Field(None, description="Total Tax (Base)")
    discountamount_base: Optional[Decimal] = Field(None, description="Quote Discount Amount (Base)")
    freightamount_base: Optional[Decimal] = Field(None, description="Freight Amount (Base)")
    
    # Exchange rate
    exchangerate: Optional[Decimal] = Field(None, description="Exchange Rate")
    
    # On hold time
    onholdtime: Optional[int] = Field(None, description="On Hold Time (Minutes)")
    
    # SLA invoked
    slainvokedid: Optional[UUID] = Field(None, description="Last SLA applied")
    
    # Entity image
    entityimage_timestamp: Optional[int] = Field(None, description="Entity Image Timestamp")
    entityimage_url: Optional[str] = Field(None, description="Entity Image URL")
    entityimageid: Optional[UUID] = Field(None, description="Entity Image Id")
    
    # Account
    accountid: Optional[UUID] = Field(None, description="Account")


class QuoteListResponse(DynamicsBaseModel):
    """Response model for listing quotes"""
    value: list[Quote]
    odata_context: Optional[str] = Field(None, alias="@odata.context")
    odata_count: Optional[int] = Field(None, alias="@odata.count")
    odata_nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
