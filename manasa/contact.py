from pydantic import Field
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from mcp_server.models import DynamicsEntityBase, DynamicsBaseModel


class ContactBase(DynamicsEntityBase):
    """Base Contact model with writable fields"""
    
    # Name fields
    firstname: Optional[str] = Field(None, max_length=50, description="First Name")
    lastname: str = Field(..., max_length=50, description="Last Name")
    middlename: Optional[str] = Field(None, max_length=50, description="Middle Name")
    salutation: Optional[str] = Field(None, max_length=100, description="Salutation")
    suffix: Optional[str] = Field(None, max_length=10, description="Suffix")
    nickname: Optional[str] = Field(None, max_length=100, description="Nickname")
    
    # Yomi fields
    yomifirstname: Optional[str] = Field(None, max_length=150, description="Yomi First Name")
    yomilastname: Optional[str] = Field(None, max_length=150, description="Yomi Last Name")
    yomimiddlename: Optional[str] = Field(None, max_length=150, description="Yomi Middle Name")
    
    # Job information
    jobtitle: Optional[str] = Field(None, max_length=100, description="Job Title")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    
    # Personal information
    anniversary: Optional[date] = Field(None, description="Anniversary")
    birthdate: Optional[date] = Field(None, description="Birthday")
    spousesname: Optional[str] = Field(None, max_length=100, description="Spouse/Partner Name")
    assistantname: Optional[str] = Field(None, max_length=100, description="Assistant")
    assistantphone: Optional[str] = Field(None, max_length=50, description="Assistant Phone")
    childrensnames: Optional[str] = Field(None, max_length=255, description="Children's Names")
    
    # Gender and family
    gendercode: Optional[Literal[1, 2]] = Field(None, description="Gender: 1=Male, 2=Female")
    familystatuscode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Marital Status")
    haschildrencode: Optional[Literal[1, 2, 3]] = Field(None, description="Has Children")
    
    # Education
    educationcode: Optional[Literal[1, 2, 3, 4, 5]] = Field(None, description="Education")
    
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
    
    # Web information
    websiteurl: Optional[str] = Field(None, max_length=200, description="Website")
    ftpsiteurl: Optional[str] = Field(None, max_length=200, description="FTP Site")
    
    # Government ID
    governmentid: Optional[str] = Field(None, max_length=50, description="Government")
    
    # Address 1 - Business
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
    address1_addresstypecode: Optional[Literal[1, 2, 3]] = Field(None, description="Address 1: Address Type")
    
    # Address 2 - Home
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
    address2_addresstypecode: Optional[Literal[1, 2, 3]] = Field(None, description="Address 2: Address Type")
    
    # Address 3
    address3_line1: Optional[str] = Field(None, max_length=250, description="Address 3: Street 1")
    address3_line2: Optional[str] = Field(None, max_length=250, description="Address 3: Street 2")
    address3_line3: Optional[str] = Field(None, max_length=250, description="Address 3: Street 3")
    address3_city: Optional[str] = Field(None, max_length=80, description="Address 3: City")
    address3_stateorprovince: Optional[str] = Field(None, max_length=50, description="Address 3: State/Province")
    address3_postalcode: Optional[str] = Field(None, max_length=20, description="Address 3: ZIP/Postal Code")
    address3_country: Optional[str] = Field(None, max_length=80, description="Address 3: Country/Region")
    address3_county: Optional[str] = Field(None, max_length=50, description="Address 3: County")
    address3_postofficebox: Optional[str] = Field(None, max_length=20, description="Address 3: Post Office Box")
    address3_name: Optional[str] = Field(None, max_length=200, description="Address 3: Name")
    address3_primarycontactname: Optional[str] = Field(None, max_length=100, description="Address 3: Primary Contact Name")
    address3_telephone1: Optional[str] = Field(None, max_length=50, description="Address 3: Telephone 1")
    address3_telephone2: Optional[str] = Field(None, max_length=50, description="Address 3: Telephone 2")
    address3_telephone3: Optional[str] = Field(None, max_length=50, description="Address 3: Telephone 3")
    address3_fax: Optional[str] = Field(None, max_length=50, description="Address 3: Fax")
    address3_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Address 3: Latitude")
    address3_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Address 3: Longitude")
    address3_upszone: Optional[str] = Field(None, max_length=4, description="Address 3: UPS Zone")
    address3_utcoffset: Optional[int] = Field(None, ge=-1500, le=1500, description="Address 3: UTC Offset")
    address3_freighttermscode: Optional[Literal[1, 2]] = Field(None, description="Address 3: Freight Terms")
    address3_shippingmethodcode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Address 3: Shipping Method")
    address3_addresstypecode: Optional[Literal[1, 2, 3]] = Field(None, description="Address 3: Address Type")
    
    # Description and notes
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    
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
    
    # Relationships
    parentcustomerid: Optional[UUID] = Field(None, description="Company Name")
    parentcustomeridtype: Optional[Literal["account", "contact"]] = Field(None, description="Parent Customer Type")
    accountid: Optional[UUID] = Field(None, description="Account")
    originatingleadid: Optional[UUID] = Field(None, description="Originating Lead")
    masterid: Optional[UUID] = Field(None, description="Master ID")
    defaultpricelevelid: Optional[UUID] = Field(None, description="Price List")
    transactioncurrencyid: Optional[UUID] = Field(None, description="Currency")
    slaid: Optional[UUID] = Field(None, description="SLA")
    slainvokedid: Optional[UUID] = Field(None, description="Last SLA applied")
    
    # Status
    statecode: Optional[Literal[0, 1]] = Field(0, description="Status: 0=Active, 1=Inactive")
    statuscode: Optional[Literal[1, 2]] = Field(None, description="Status Reason")
    
    # Credit
    creditlimit: Optional[Decimal] = Field(None, ge=0, le=100000000000, description="Credit Limit")
    creditonhold: Optional[bool] = Field(False, description="Credit Hold")
    
    # Payment
    paymenttermscode: Optional[Literal[1, 2, 3, 4]] = Field(None, description="Payment Terms")
    shippingmethodcode: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = Field(None, description="Shipping Method")
    
    # Territory
    territorycode: Optional[Literal[1]] = Field(1, description="Territory")
    
    # Customer type
    customertypecode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = Field(None, description="Relationship Type")
    customersizecode: Optional[Literal[1, 2, 3]] = Field(None, description="Customer Size")
    
    # Account role
    accountrolecode: Optional[Literal[1, 2, 3]] = Field(None, description="Role")
    
    # Lead source
    leadsourcecode: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]] = Field(None, description="Lead Source")
    
    # Business card
    business2: Optional[str] = Field(None, max_length=50, description="Business Phone 2")
    callback: Optional[str] = Field(None, max_length=50, description="Callback Number")
    company: Optional[str] = Field(None, max_length=50, description="Company Phone")
    home2: Optional[str] = Field(None, max_length=50, description="Home Phone 2")
    
    # Manager
    managerphone: Optional[str] = Field(None, max_length=50, description="Manager Phone")
    managername: Optional[str] = Field(None, max_length=100, description="Manager")
    
    # Employment
    employeeid: Optional[str] = Field(None, max_length=50, description="Employee")
    
    # External user
    externaluseridentifier: Optional[str] = Field(None, max_length=50, description="External User Identifier")
    isbackofficecustomer: Optional[bool] = Field(False, description="Back Office Customer")
    
    # Merged
    merged: Optional[bool] = Field(None, description="Merged")
    
    # Dates
    lastonholdtime: Optional[datetime] = Field(None, description="Last On Hold Time")
    lastusedincampaign: Optional[date] = Field(None, description="Last Date Included in Campaign")
    
    # System fields
    importsequencenumber: Optional[int] = Field(None, description="Import Sequence Number")
    overriddencreatedon: Optional[date] = Field(None, description="Record Created On")
    timezoneruleversionnumber: Optional[int] = Field(None, description="Time Zone Rule Version Number")
    utcconversiontimezonecode: Optional[int] = Field(None, ge=-1, le=1500, description="UTC Conversion Time Zone Code")
    
    # Teams
    teamsfollowed: Optional[int] = Field(None, description="TeamsFollowed")
    
    # GDPR
    msdyn_gdproptout: Optional[bool] = Field(False, description="GDPR Optout")
    msdyn_orgchangestatus: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Not at Company")
    
    # Advanced Dynamics fields
    msdyn_salesaccelerationinsightid: Optional[UUID] = Field(None, description="Sales Acceleration Insights ID")
    msdyn_segmentid: Optional[UUID] = Field(None, description="Segment Id")
    
    # Subscription
    subscriptionid: Optional[UUID] = Field(None, description="Subscription")
    
    # Aging
    aging30: Optional[Decimal] = Field(None, description="Aging 30")
    aging60: Optional[Decimal] = Field(None, description="Aging 60")
    aging90: Optional[Decimal] = Field(None, description="Aging 90")


class ContactCreate(ContactBase):
    """Model for creating a new contact"""
    pass


class ContactUpdate(DynamicsEntityBase):
    """Model for updating a contact - all fields optional"""
    firstname: Optional[str] = Field(None, max_length=50)
    lastname: Optional[str] = Field(None, max_length=50)
    emailaddress1: Optional[str] = Field(None, max_length=100)
    telephone1: Optional[str] = Field(None, max_length=50)
    mobilephone: Optional[str] = Field(None, max_length=20)
    jobtitle: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    statecode: Optional[Literal[0, 1]] = None
    statuscode: Optional[Literal[1, 2]] = None


class Contact(ContactBase):
    """Complete Contact model including read-only fields"""
    contactid: UUID = Field(..., description="Unique identifier of the contact")
    
    # Computed name field
    fullname: Optional[str] = Field(None, max_length=160, description="Full Name")
    yomifullname: Optional[str] = Field(None, max_length=450, description="Yomi Full Name")
    
    # Read-only fields
    createdby: Optional[UUID] = Field(None, description="Created By")
    createdonbehalfby: Optional[UUID] = Field(None, description="Created By (Delegate)")
    modifiedby: Optional[UUID] = Field(None, description="Modified By")
    modifiedonbehalfby: Optional[UUID] = Field(None, description="Modified By (Delegate)")
    
    # Base currency fields
    creditlimit_base: Optional[Decimal] = Field(None, description="Credit Limit (Base)")
    aging30_base: Optional[Decimal] = Field(None, description="Aging 30 (Base)")
    aging60_base: Optional[Decimal] = Field(None, description="Aging 60 (Base)")
    aging90_base: Optional[Decimal] = Field(None, description="Aging 90 (Base)")
    annualincome: Optional[Decimal] = Field(None, description="Annual Income")
    annualincome_base: Optional[Decimal] = Field(None, description="Annual Income (Base)")
    
    # Exchange rate
    exchangerate: Optional[Decimal] = Field(None, description="Exchange Rate")
    
    # Address IDs
    address1_addressid: Optional[UUID] = Field(None, description="Address 1: ID")
    address2_addressid: Optional[UUID] = Field(None, description="Address 2: ID")
    address3_addressid: Optional[UUID] = Field(None, description="Address 3: ID")
    
    # Composite address
    address1_composite: Optional[str] = Field(None, description="Address 1")
    address2_composite: Optional[str] = Field(None, description="Address 2")
    address3_composite: Optional[str] = Field(None, description="Address 3")
    
    # On hold time
    onholdtime: Optional[int] = Field(None, description="On Hold Time (Minutes)")
    
    # Entity image
    entityimage: Optional[bytes] = Field(None, description="Entity Image")
    entityimage_timestamp: Optional[int] = Field(None, description="Entity Image Timestamp")
    entityimage_url: Optional[str] = Field(None, description="Entity Image URL")
    entityimageid: Optional[UUID] = Field(None, description="Entity Image Id")
    
    # Portal user info
    isautocreate: Optional[bool] = Field(None, description="Auto-created")
    isprivate: Optional[bool] = Field(None, description="Private")


class ContactListResponse(DynamicsBaseModel):
    """Response model for listing contacts"""
    value: list[Contact]
    odata_context: Optional[str] = Field(None, alias="@odata.context")
    odata_count: Optional[int] = Field(None, alias="@odata.count")
    odata_nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
