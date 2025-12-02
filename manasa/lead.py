from pydantic import Field, EmailStr
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from mcp_server.models import DynamicsEntityBase, DynamicsBaseModel


class LeadBase(DynamicsEntityBase):
    """Base Lead model with writable fields"""
    
    # Core fields - Name components
    firstname: Optional[str] = Field(None, max_length=50, description="First Name")
    lastname: str = Field(..., max_length=50, description="Last Name")
    middlename: Optional[str] = Field(None, max_length=50, description="Middle Name")
    salutation: Optional[str] = Field(None, max_length=100, description="Salutation")
    yomifirstname: Optional[str] = Field(None, max_length=150, description="Yomi First Name")
    yomilastname: Optional[str] = Field(None, max_length=150, description="Yomi Last Name")
    yomimiddlename: Optional[str] = Field(None, max_length=150, description="Yomi Middle Name")
    
    # Company information
    companyname: Optional[str] = Field(None, max_length=100, description="Company Name")
    yomicompanyname: Optional[str] = Field(None, max_length=200, description="Yomi Company Name")
    jobtitle: Optional[str] = Field(None, max_length=100, description="Job Title")
    numberofemployees: Optional[int] = Field(None, description="Number of Employees")
    revenue: Optional[Decimal] = Field(None, description="Annual Revenue")
    sic: Optional[str] = Field(None, max_length=20, description="SIC Code")
    
    # Contact information
    emailaddress1: Optional[str] = Field(None, max_length=100, description="Email")
    emailaddress2: Optional[str] = Field(None, max_length=100, description="Email Address 2")
    emailaddress3: Optional[str] = Field(None, max_length=100, description="Email Address 3")
    telephone1: Optional[str] = Field(None, max_length=50, description="Business Phone")
    telephone2: Optional[str] = Field(None, max_length=50, description="Home Phone")
    telephone3: Optional[str] = Field(None, max_length=50, description="Telephone 3")
    mobilephone: Optional[str] = Field(None, max_length=20, description="Mobile Phone")
    pager: Optional[str] = Field(None, max_length=20, description="Pager")
    fax: Optional[str] = Field(None, max_length=50, description="Fax")
    websiteurl: Optional[str] = Field(None, max_length=200, description="Website")
    
    # Address 1
    address1_line1: Optional[str] = Field(None, max_length=250, description="Street 1")
    address1_line2: Optional[str] = Field(None, max_length=250, description="Street 2")
    address1_line3: Optional[str] = Field(None, max_length=250, description="Street 3")
    address1_city: Optional[str] = Field(None, max_length=80, description="City")
    address1_stateorprovince: Optional[str] = Field(None, max_length=50, description="State/Province")
    address1_postalcode: Optional[str] = Field(None, max_length=20, description="ZIP/Postal Code")
    address1_country: Optional[str] = Field(None, max_length=80, description="Country/Region")
    address1_county: Optional[str] = Field(None, max_length=50, description="County")
    address1_postofficebox: Optional[str] = Field(None, max_length=20, description="Post Office Box")
    address1_name: Optional[str] = Field(None, max_length=100, description="Address 1: Name")
    address1_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Address 1: Latitude")
    address1_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Address 1: Longitude")
    address1_fax: Optional[str] = Field(None, max_length=50, description="Address 1: Fax")
    address1_telephone1: Optional[str] = Field(None, max_length=50, description="Address 1: Telephone 1")
    address1_telephone2: Optional[str] = Field(None, max_length=50, description="Address 1: Telephone 2")
    address1_telephone3: Optional[str] = Field(None, max_length=50, description="Address 1: Telephone 3")
    address1_upszone: Optional[str] = Field(None, max_length=4, description="Address 1: UPS Zone")
    address1_utcoffset: Optional[int] = Field(None, ge=-1500, le=1500, description="Address 1: UTC Offset")
    address1_addresstypecode: Optional[Literal[1]] = Field(1, description="Address 1: Address Type")
    address1_shippingmethodcode: Optional[Literal[1]] = Field(1, description="Address 1: Shipping Method")
    
    # Address 2 (similar structure)
    address2_line1: Optional[str] = Field(None, max_length=250, description="Address 2: Street 1")
    address2_line2: Optional[str] = Field(None, max_length=250, description="Address 2: Street 2")
    address2_line3: Optional[str] = Field(None, max_length=250, description="Address 2: Street 3")
    address2_city: Optional[str] = Field(None, max_length=80, description="Address 2: City")
    address2_stateorprovince: Optional[str] = Field(None, max_length=50, description="Address 2: State/Province")
    address2_postalcode: Optional[str] = Field(None, max_length=20, description="Address 2: ZIP/Postal Code")
    address2_country: Optional[str] = Field(None, max_length=80, description="Address 2: Country/Region")
    address2_county: Optional[str] = Field(None, max_length=50, description="Address 2: County")
    address2_postofficebox: Optional[str] = Field(None, max_length=20, description="Address 2: Post Office Box")
    address2_name: Optional[str] = Field(None, max_length=100, description="Address 2: Name")
    address2_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Address 2: Latitude")
    address2_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Address 2: Longitude")
    address2_fax: Optional[str] = Field(None, max_length=50, description="Address 2: Fax")
    address2_telephone1: Optional[str] = Field(None, max_length=50, description="Address 2: Telephone 1")
    address2_telephone2: Optional[str] = Field(None, max_length=50, description="Address 2: Telephone 2")
    address2_telephone3: Optional[str] = Field(None, max_length=50, description="Address 2: Telephone 3")
    address2_upszone: Optional[str] = Field(None, max_length=4, description="Address 2: UPS Zone")
    address2_utcoffset: Optional[int] = Field(None, ge=-1500, le=1500, description="Address 2: UTC Offset")
    address2_addresstypecode: Optional[Literal[1]] = Field(1, description="Address 2: Address Type")
    address2_shippingmethodcode: Optional[Literal[1]] = Field(1, description="Address 2: Shipping Method")
    
    # Lead qualification fields
    subject: Optional[str] = Field(None, max_length=300, description="Topic")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    estimatedamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Est. Value")
    estimatedclosedate: Optional[date] = Field(None, description="Est. Close Date")
    estimatedvalue: Optional[float] = Field(None, ge=0, le=1000000000, description="Est. Value (deprecated)")
    
    # Budget
    budgetamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Budget Amount")
    budgetstatus: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Budget: 0=No Budget, 1=May Buy, 2=Can Buy, 3=Will Buy")
    
    # Lead source and campaign
    leadsourcecode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]] = Field(None, description="Lead Source")
    campaignid: Optional[UUID] = Field(None, description="Source Campaign")
    
    # Rating and quality
    leadqualitycode: Optional[Literal[1, 2, 3]] = Field(2, description="Rating: 1=Hot, 2=Warm, 3=Cold")
    
    # Industry
    industrycode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]] = Field(None, description="Industry")
    
    # Status
    statecode: Optional[Literal[0, 1, 2]] = Field(0, description="Status: 0=Open, 1=Qualified, 2=Disqualified")
    statuscode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Status Reason")
    
    # Communication preferences
    donotbulkemail: Optional[bool] = Field(False, description="Do not allow Bulk Emails")
    donotemail: Optional[bool] = Field(False, description="Do not allow Emails")
    donotfax: Optional[bool] = Field(False, description="Do not allow Faxes")
    donotphone: Optional[bool] = Field(False, description="Do not allow Phone Calls")
    donotpostalmail: Optional[bool] = Field(False, description="Do not allow Mails")
    donotsendmm: Optional[bool] = Field(False, description="Do Not Send Marketing Material")
    followemail: Optional[bool] = Field(True, description="Follow Email Activity")
    preferredcontactmethodcode: Optional[Literal[1, 2, 3, 4, 5]] = Field(None, description="Preferred Method of Contact")
    
    # Qualification flags
    confirminterest: Optional[bool] = Field(False, description="Confirm Interest")
    decisionmaker: Optional[bool] = Field(False, description="Decision Maker?")
    evaluatefit: Optional[bool] = Field(False, description="Evaluate Fit")
    
    # Purchase information
    need: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Need")
    purchaseprocess: Optional[Literal[0, 1, 2]] = Field(None, description="Purchase Process")
    purchasetimeframe: Optional[Literal[0, 1, 2, 3, 4]] = Field(None, description="Purchase Timeframe")
    initialcommunication: Optional[Literal[0, 1]] = Field(None, description="Initial Communication")
    
    # Sales process
    salesstage: Optional[Literal[0, 1]] = Field(None, description="Sales Stage")
    salesstagecode: Optional[Literal[1]] = Field(1, description="Sales Stage Code")
    prioritycode: Optional[Literal[1, 2, 3]] = Field(None, description="Priority")
    
    # Related records
    customerid: Optional[UUID] = Field(None, description="Customer")
    customeridtype: Optional[Literal["account", "contact"]] = Field(None, description="Customer Type")
    parentaccountid: Optional[UUID] = Field(None, description="Account")
    parentcontactid: Optional[UUID] = Field(None, description="Contact")
    originatingcaseid: Optional[UUID] = Field(None, description="Originating Case")
    qualifyingopportunityid: Optional[UUID] = Field(None, description="Qualifying Opportunity")
    transactioncurrencyid: Optional[UUID] = Field(None, description="Currency")
    
    # Comments and notes
    qualificationcomments: Optional[str] = Field(None, max_length=2000, description="Qualification Comments")
    
    # Scheduling
    schedulefollowup_prospect: Optional[date] = Field(None, description="Scheduled Follow Up - Prospect")
    schedulefollowup_qualify: Optional[date] = Field(None, description="Scheduled Follow Up - Qualify")
    lastusedincampaign: Optional[date] = Field(None, description="Last Campaign Date")
    lastonholdtime: Optional[datetime] = Field(None, description="Last On Hold Time")
    
    # Business card
    businesscard: Optional[str] = Field(None, description="Business Card")
    businesscardattributes: Optional[str] = Field(None, max_length=4000, description="Business Card Attributes")
    
    # Advanced fields
    msdyn_gdproptout: Optional[bool] = Field(False, description="GDPR Optout")
    msdyn_leadscore: Optional[int] = Field(None, description="Lead Score (Deprecated)")
    msdyn_leadscoretrend: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Lead Score Trend (Deprecated)")
    msdyn_leadgrade: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Lead Grade (Deprecated)")
    msdyn_leadkpiid: Optional[UUID] = Field(None, description="KPI")
    msdyn_predictivescoreid: Optional[UUID] = Field(None, description="Predictive Score")
    msdyn_segmentid: Optional[UUID] = Field(None, description="Segment Id")
    msdyn_salesassignmentresult: Optional[UUID] = Field(None, description="Sales Assignment Result")
    msdyn_scorehistory: Optional[str] = Field(None, max_length=2000, description="Score History (Deprecated)")
    msdyn_scorereasons: Optional[str] = Field(None, max_length=2000, description="Score Reasons (Deprecated)")
    
    # System fields
    importsequencenumber: Optional[int] = Field(None, description="Import Sequence Number")
    overriddencreatedon: Optional[date] = Field(None, description="Record Created On")
    participatesinworkflow: Optional[bool] = Field(None, description="Participates in Workflow")
    teamsfollowed: Optional[int] = Field(None, description="Teams Followed")
    slaid: Optional[UUID] = Field(None, description="SLA")


class LeadCreate(LeadBase):
    """Model for creating a new lead"""
    pass


class LeadUpdate(DynamicsEntityBase):
    """Model for updating a lead - all fields optional"""
    firstname: Optional[str] = Field(None, max_length=50)
    lastname: Optional[str] = Field(None, max_length=50)
    companyname: Optional[str] = Field(None, max_length=100)
    emailaddress1: Optional[str] = Field(None, max_length=100)
    telephone1: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = Field(None, max_length=2000)
    estimatedamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000)
    estimatedclosedate: Optional[date] = None
    statecode: Optional[Literal[0, 1, 2]] = None
    statuscode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = None


class Lead(LeadBase):
    """Complete Lead model including read-only fields"""
    leadid: UUID = Field(..., description="Unique identifier of the lead")
    
    # Computed name field
    fullname: Optional[str] = Field(None, max_length=160, description="Full Name")
    
    # Read-only fields
    createdby: Optional[UUID] = Field(None, description="Created By")
    createdonbehalfby: Optional[UUID] = Field(None, description="Created By (Delegate)")
    modifiedby: Optional[UUID] = Field(None, description="Modified By")
    modifiedonbehalfby: Optional[UUID] = Field(None, description="Modified By (Delegate)")
    
    # Base currency fields
    budgetamount_base: Optional[Decimal] = Field(None, description="Budget Amount (Base)")
    estimatedamount_base: Optional[Decimal] = Field(None, description="Est. Value (Base)")
    revenue_base: Optional[Decimal] = Field(None, description="Annual Revenue (Base)")
    
    # Exchange rate
    exchangerate: Optional[Decimal] = Field(None, description="Exchange Rate")
    
    # Address IDs
    address1_addressid: Optional[UUID] = Field(None, description="Address 1: ID")
    address2_addressid: Optional[UUID] = Field(None, description="Address 2: ID")
    
    # Composite fields
    address1_composite: Optional[str] = Field(None, description="Address 1")
    address2_composite: Optional[str] = Field(None, description="Address 2")


class LeadListResponse(DynamicsBaseModel):
    """Response model for listing leads"""
    value: list[Lead]
    odata_context: Optional[str] = Field(None, alias="@odata.context")
    odata_count: Optional[int] = Field(None, alias="@odata.count")
    odata_nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
