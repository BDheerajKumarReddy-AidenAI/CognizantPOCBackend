from pydantic import Field
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from mcp_server.models import DynamicsEntityBase, DynamicsBaseModel


class AccountBase(DynamicsEntityBase):
    """Base Account model with writable fields"""
    
    # Core fields
    name: str = Field(..., max_length=160, description="Account Name")
    accountnumber: Optional[str] = Field(None, max_length=20, description="Account Number")
    
    # Contact information
    emailaddress1: Optional[str] = Field(None, max_length=100, description="Email")
    emailaddress2: Optional[str] = Field(None, max_length=100, description="Email Address 2")
    emailaddress3: Optional[str] = Field(None, max_length=100, description="Email Address 3")
    telephone1: Optional[str] = Field(None, max_length=50, description="Main Phone")
    telephone2: Optional[str] = Field(None, max_length=50, description="Other Phone")
    telephone3: Optional[str] = Field(None, max_length=50, description="Telephone 3")
    fax: Optional[str] = Field(None, max_length=50, description="Fax")
    websiteurl: Optional[str] = Field(None, max_length=200, description="Website")
    ftpsiteurl: Optional[str] = Field(None, max_length=200, description="FTP Site")
    
    # Yomi fields
    yominame: Optional[str] = Field(None, max_length=160, description="Yomi Account Name")
    
    # Address 1 - Primary Address
    address1_line1: Optional[str] = Field(None, max_length=250, description="Street 1")
    address1_line2: Optional[str] = Field(None, max_length=250, description="Street 2")
    address1_line3: Optional[str] = Field(None, max_length=250, description="Street 3")
    address1_city: Optional[str] = Field(None, max_length=80, description="City")
    address1_stateorprovince: Optional[str] = Field(None, max_length=50, description="State/Province")
    address1_postalcode: Optional[str] = Field(None, max_length=20, description="ZIP/Postal Code")
    address1_country: Optional[str] = Field(None, max_length=80, description="Country/Region")
    address1_county: Optional[str] = Field(None, max_length=50, description="Address 1: County")
    address1_postofficebox: Optional[str] = Field(None, max_length=20, description="Address 1: Post Office Box")
    address1_name: Optional[str] = Field(None, max_length=200, description="Address 1: Name")
    address1_primarycontactname: Optional[str] = Field(None, max_length=100, description="Address 1: Primary Contact Name")
    address1_telephone1: Optional[str] = Field(None, max_length=50, description="Address Phone")
    address1_telephone2: Optional[str] = Field(None, max_length=50, description="Address 1: Telephone 2")
    address1_telephone3: Optional[str] = Field(None, max_length=50, description="Address 1: Telephone 3")
    address1_fax: Optional[str] = Field(None, max_length=50, description="Address 1: Fax")
    address1_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Address 1: Latitude")
    address1_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Address 1: Longitude")
    address1_upszone: Optional[str] = Field(None, max_length=4, description="Address 1: UPS Zone")
    address1_utcoffset: Optional[int] = Field(None, ge=-1500, le=1500, description="Address 1: UTC Offset")
    address1_freighttermscode: Optional[Literal[1, 2]] = Field(None, description="Address 1: Freight Terms")
    address1_shippingmethodcode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Address 1: Shipping Method")
    address1_addresstypecode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Address 1: Address Type")
    
    # Address 2 - Other Address
    address2_line1: Optional[str] = Field(None, max_length=250, description="Other Street 1")
    address2_line2: Optional[str] = Field(None, max_length=250, description="Other Street 2")
    address2_line3: Optional[str] = Field(None, max_length=250, description="Other Street 3")
    address2_city: Optional[str] = Field(None, max_length=80, description="Other City")
    address2_stateorprovince: Optional[str] = Field(None, max_length=50, description="Other State/Province")
    address2_postalcode: Optional[str] = Field(None, max_length=20, description="Other ZIP/Postal Code")
    address2_country: Optional[str] = Field(None, max_length=80, description="Other Country/Region")
    address2_county: Optional[str] = Field(None, max_length=50, description="Address 2: County")
    address2_postofficebox: Optional[str] = Field(None, max_length=20, description="Address 2: Post Office Box")
    address2_name: Optional[str] = Field(None, max_length=200, description="Address 2: Name")
    address2_primarycontactname: Optional[str] = Field(None, max_length=100, description="Address 2: Primary Contact Name")
    address2_telephone1: Optional[str] = Field(None, max_length=50, description="Address 2: Telephone 1")
    address2_telephone2: Optional[str] = Field(None, max_length=50, description="Address 2: Telephone 2")
    address2_telephone3: Optional[str] = Field(None, max_length=50, description="Address 2: Telephone 3")
    address2_fax: Optional[str] = Field(None, max_length=50, description="Address 2: Fax")
    address2_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Address 2: Latitude")
    address2_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Address 2: Longitude")
    address2_upszone: Optional[str] = Field(None, max_length=4, description="Address 2: UPS Zone")
    address2_utcoffset: Optional[int] = Field(None, ge=-1500, le=1500, description="Address 2: UTC Offset")
    address2_freighttermscode: Optional[Literal[1, 2]] = Field(None, description="Address 2: Freight Terms")
    address2_shippingmethodcode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Address 2: Shipping Method")
    address2_addresstypecode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Address 2: Address Type")
    
    # Business information
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    sic: Optional[str] = Field(None, max_length=20, description="SIC Code")
    tickersymbol: Optional[str] = Field(None, max_length=10, description="Ticker Symbol")
    stockexchange: Optional[str] = Field(None, max_length=20, description="Stock Exchange")
    numberofemployees: Optional[int] = Field(None, ge=0, le=1000000000, description="Number of Employees")
    revenue: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000, description="Annual Revenue")
    
    # Classification
    accountcategorycode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Category")
    accountclassificationcode: Optional[Literal[1, 2, 3, 4, 5]] = Field(None, description="Classification")
    industrycode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]] = Field(None, description="Industry")
    businesstypecode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = Field(None, description="Business Type")
    
    # Ratings and ownership
    accountratingcode: Optional[Literal[1, 2, 3]] = Field(None, description="Account Rating")
    customertypecode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = Field(None, description="Relationship Type")
    ownershipcode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Ownership")
    
    # Shipping and payment
    shippingmethodcode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Shipping Method")
    freighttermscode: Optional[Literal[1, 2]] = Field(None, description="Freight Terms")
    paymenttermscode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Payment Terms")
    
    # Credit
    creditlimit: Optional[Decimal] = Field(None, ge=0, le=100000000000, description="Credit Limit")
    creditonhold: Optional[bool] = Field(False, description="Credit Hold")
    
    # Preferences
    preferredcontactmethodcode: Optional[Literal[1, 2, 3, 4, 5]] = Field(None, description="Preferred Method of Contact")
    preferredappointmentdaycode: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = Field(None, description="Preferred Day")
    preferredappointmenttimecode: Optional[Literal[1, 2, 3]] = Field(None, description="Preferred Time")
    preferredsystemuserid: Optional[UUID] = Field(None, description="Preferred User")
    preferredserviceid: Optional[UUID] = Field(None, description="Preferred Service")
    preferredequipmentid: Optional[UUID] = Field(None, description="Preferred Facility/Equipment")
    
    # Communication preferences
    donotbulkemail: Optional[bool] = Field(False, description="Do not allow Bulk Emails")
    donotemail: Optional[bool] = Field(False, description="Do not allow Emails")
    donotfax: Optional[bool] = Field(False, description="Do not allow Faxes")
    donotphone: Optional[bool] = Field(False, description="Do not allow Phone Calls")
    donotpostalmail: Optional[bool] = Field(False, description="Do not allow Mails")
    donotsendmm: Optional[bool] = Field(False, description="Send Marketing Materials")
    followemail: Optional[bool] = Field(True, description="Follow Email Activity")
    
    # Marketing
    participatesinworkflow: Optional[bool] = Field(None, description="Participates in Workflow")
    marketingonly: Optional[bool] = Field(False, description="Marketing Only")
    
    # Territory and relationships
    territorycode: Optional[Literal[1]] = Field(1, description="Territory Code")
    territoryid: Optional[UUID] = Field(None, description="Territory")
    parentaccountid: Optional[UUID] = Field(None, description="Parent Account")
    primarycontactid: Optional[UUID] = Field(None, description="Primary Contact")
    masterid: Optional[UUID] = Field(None, description="Master ID")
    originatingleadid: Optional[UUID] = Field(None, description="Originating Lead")
    defaultpricelevelid: Optional[UUID] = Field(None, description="Price List")
    transactioncurrencyid: Optional[UUID] = Field(None, description="Currency")
    slaid: Optional[UUID] = Field(None, description="SLA")
    slainvokedid: Optional[UUID] = Field(None, description="Last SLA applied")
    
    # Status
    statecode: Optional[Literal[0, 1]] = Field(0, description="Status: 0=Active, 1=Inactive")
    statuscode: Optional[Literal[1, 2]] = Field(None, description="Status Reason")
    
    # Advanced fields
    customersizecode: Optional[Literal[1, 2, 3]] = Field(None, description="Customer Size")
    
    # Merged
    merged: Optional[bool] = Field(None, description="Merged")
    
    # Dates
    lastonholdtime: Optional[datetime] = Field(None, description="Last On Hold Time")
    lastusedincampaign: Optional[date] = Field(None, description="Last Date Included in Campaign")
    opendeals: Optional[int] = Field(None, description="Open Deals")
    opendeals_date: Optional[datetime] = Field(None, description="Open Deals (Last Updated On)")
    opendeals_state: Optional[int] = Field(None, description="Open Deals (State)")
    openrevenue: Optional[Decimal] = Field(None, description="Open Revenue")
    openrevenue_date: Optional[datetime] = Field(None, description="Open Revenue (Last Updated On)")
    openrevenue_state: Optional[int] = Field(None, description="Open Revenue (State)")
    
    # System fields
    importsequencenumber: Optional[int] = Field(None, description="Import Sequence Number")
    overriddencreatedon: Optional[date] = Field(None, description="Record Created On")
    timezoneruleversionnumber: Optional[int] = Field(None, description="Time Zone Rule Version Number")
    utcconversiontimezonecode: Optional[int] = Field(None, ge=-1, le=1500, description="UTC Conversion Time Zone Code")
    
    # Teams
    teamsfollowed: Optional[int] = Field(None, description="TeamsFollowed")
    
    # Advanced Dynamics fields
    msdyn_gdproptout: Optional[bool] = Field(False, description="GDPR Optout")
    msdyn_salesaccelerationinsightid: Optional[UUID] = Field(None, description="Sales Acceleration Insights ID")
    msdyn_segmentid: Optional[UUID] = Field(None, description="Segment Id")


class AccountCreate(AccountBase):
    """Model for creating a new account"""
    pass


class AccountUpdate(DynamicsEntityBase):
    """Model for updating an account - all fields optional"""
    name: Optional[str] = Field(None, max_length=160)
    accountnumber: Optional[str] = Field(None, max_length=20)
    emailaddress1: Optional[str] = Field(None, max_length=100)
    telephone1: Optional[str] = Field(None, max_length=50)
    websiteurl: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    revenue: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000)
    numberofemployees: Optional[int] = Field(None, ge=0, le=1000000000)
    industrycode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]] = None
    statecode: Optional[Literal[0, 1]] = None
    statuscode: Optional[Literal[1, 2]] = None


class Account(AccountBase):
    """Complete Account model including read-only fields"""
    accountid: UUID = Field(..., description="Unique identifier for account")
    
    # Read-only fields
    createdby: Optional[UUID] = Field(None, description="Created By")
    createdonbehalfby: Optional[UUID] = Field(None, description="Created By (Delegate)")
    modifiedby: Optional[UUID] = Field(None, description="Modified By")
    modifiedonbehalfby: Optional[UUID] = Field(None, description="Modified By (Delegate)")
    
    # Computed fields
    aging30: Optional[Decimal] = Field(None, description="Aging 30")
    aging30_base: Optional[Decimal] = Field(None, description="Aging 30 (Base)")
    aging60: Optional[Decimal] = Field(None, description="Aging 60")
    aging60_base: Optional[Decimal] = Field(None, description="Aging 60 (Base)")
    aging90: Optional[Decimal] = Field(None, description="Aging 90")
    aging90_base: Optional[Decimal] = Field(None, description="Aging 90 (Base)")
    
    # Base currency fields
    creditlimit_base: Optional[Decimal] = Field(None, description="Credit Limit (Base)")
    revenue_base: Optional[Decimal] = Field(None, description="Annual Revenue (Base)")
    openrevenue_base: Optional[Decimal] = Field(None, description="Open Revenue (Base)")
    marketcap: Optional[Decimal] = Field(None, description="Market Capitalization")
    marketcap_base: Optional[Decimal] = Field(None, description="Market Capitalization (Base)")
    
    # Exchange rate
    exchangerate: Optional[Decimal] = Field(None, description="Exchange Rate")
    
    # Address IDs
    address1_addressid: Optional[UUID] = Field(None, description="Address 1: ID")
    address2_addressid: Optional[UUID] = Field(None, description="Address 2: ID")
    
    # Composite address
    address1_composite: Optional[str] = Field(None, description="Address 1")
    address2_composite: Optional[str] = Field(None, description="Address 2")
    
    # On hold time
    onholdtime: Optional[int] = Field(None, description="On Hold Time (Minutes)")
    
    # Entity image
    entityimage: Optional[bytes] = Field(None, description="Entity Image")
    entityimage_timestamp: Optional[int] = Field(None, description="Entity Image Timestamp")
    entityimage_url: Optional[str] = Field(None, description="Entity Image URL")
    entityimageid: Optional[UUID] = Field(None, description="Entity Image Id")


class AccountListResponse(DynamicsBaseModel):
    """Response model for listing accounts"""
    value: list[Account]
    odata_context: Optional[str] = Field(None, alias="@odata.context")
    odata_count: Optional[int] = Field(None, alias="@odata.count")
    odata_nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
