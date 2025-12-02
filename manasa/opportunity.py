from pydantic import Field, field_validator
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
# from . import DynamicsEntityBase
from mcp_server.models import DynamicsEntityBase, DynamicsBaseModel


class OpportunityBase(DynamicsEntityBase):
    """Base Opportunity model with writable fields"""
    
    # Core fields
    name: str = Field(..., max_length=300, description="Topic - descriptive name for the opportunity")
    customerid: UUID = Field(..., description="Potential Customer (account or contact)")
    customeridtype: Optional[Literal["account", "contact"]] = Field(None, description="Customer Type")
    
    # Financial fields
    estimatedvalue: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Est. revenue")
    actualvalue: Optional[Decimal] = Field(None, ge=-1000000000000, le=1000000000000, description="Actual Revenue")
    budgetamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Budget amount")
    discountamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Opportunity Discount Amount")
    discountpercentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Opportunity Discount %")
    freightamount: Optional[Decimal] = Field(None, ge=0, le=1000000000000, description="Freight Amount")
    totalamount: Optional[Decimal] = Field(None, description="Total Amount")
    totalamountlessfreight: Optional[Decimal] = Field(None, description="Total Amount Less Freight")
    totaldiscountamount: Optional[Decimal] = Field(None, description="Total Discount Amount")
    totallineitemamount: Optional[Decimal] = Field(None, description="Total Line Item Amount")
    totallineitemdiscountamount: Optional[Decimal] = Field(None, description="Total Line Item Discount Amount")
    totaltax: Optional[Decimal] = Field(None, description="Total Tax")
    
    # Revenue calculation
    isrevenuesystemcalculated: Optional[bool] = Field(False, description="Is revenue system calculated")
    
    # Dates
    actualclosedate: Optional[date] = Field(None, description="Actual Close Date")
    estimatedclosedate: Optional[date] = Field(None, description="Est. close date")
    finaldecisiondate: Optional[date] = Field(None, description="Final Decision Date")
    
    # Probability and ratings
    closeprobability: Optional[int] = Field(None, ge=0, le=100, description="Probability of closing")
    opportunityratingcode: Optional[Literal[1, 2, 3]] = Field(2, description="Rating: 1=Hot, 2=Warm, 3=Cold")
    
    # Status fields
    statecode: Optional[Literal[0, 1, 2]] = Field(0, description="Status: 0=Open, 1=Won, 2=Lost")
    statuscode: Optional[Literal[1, 2, 3, 4, 5]] = Field(None, description="Status Reason")
    
    # Relationships
    campaignid: Optional[UUID] = Field(None, description="Source Campaign")
    originatingleadid: Optional[UUID] = Field(None, description="Originating Lead")
    parentaccountid: Optional[UUID] = Field(None, description="Account")
    parentcontactid: Optional[UUID] = Field(None, description="Contact")
    pricelevelid: Optional[UUID] = Field(None, description="Price List")
    transactioncurrencyid: Optional[UUID] = Field(None, description="Currency")
    
    # Sales process fields
    salesstagecode: Optional[Literal[1]] = Field(1, description="Process Code")
    salesstage: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Sales Stage: 0=Qualify, 1=Develop, 2=Propose, 3=Close")
    
    # Budget status
    budgetstatus: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Budget status")
    
    # Purchase information
    purchasetimeframe: Optional[Literal[0, 1, 2, 3, 4]] = Field(None, description="Purchase Timeframe")
    purchaseprocess: Optional[Literal[0, 1, 2]] = Field(None, description="Purchase Process")
    timeline: Optional[Literal[0, 1, 2, 3, 4]] = Field(None, description="Timeline")
    
    # Boolean flags
    captureproposalfeedback: Optional[bool] = Field(False, description="Proposal Feedback Captured")
    completefinalproposal: Optional[bool] = Field(False, description="Final Proposal Ready")
    completeinternalreview: Optional[bool] = Field(False, description="Complete Internal Review")
    confirminterest: Optional[bool] = Field(False, description="Confirm Interest")
    decisionmaker: Optional[bool] = Field(False, description="Decision Maker?")
    developproposal: Optional[bool] = Field(False, description="Develop Proposal")
    evaluatefit: Optional[bool] = Field(False, description="Evaluate Fit")
    filedebrief: Optional[bool] = Field(False, description="File Debrief")
    identifycompetitors: Optional[bool] = Field(False, description="Identify Competitors")
    identifycustomercontacts: Optional[bool] = Field(False, description="Identify Customer Contacts")
    identifypursuitteam: Optional[bool] = Field(False, description="Identify Sales Team")
    presentfinalproposal: Optional[bool] = Field(False, description="Present Final Proposal")
    presentproposal: Optional[bool] = Field(False, description="Presented Proposal")
    pursuitdecision: Optional[bool] = Field(False, description="Decide Go/No-Go")
    resolvefeedback: Optional[bool] = Field(False, description="Feedback Resolved")
    sendthankyounote: Optional[bool] = Field(False, description="Send Thank You Note")
    
    # Text fields
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    currentsituation: Optional[str] = Field(None, max_length=2000, description="Current Situation")
    customerneed: Optional[str] = Field(None, max_length=2000, description="Customer Need")
    customerpainpoints: Optional[str] = Field(None, max_length=2000, description="Customer Pain Points")
    proposedsolution: Optional[str] = Field(None, max_length=2000, description="Proposed Solution")
    qualificationcomments: Optional[str] = Field(None, max_length=2000, description="Qualification Comments")
    quotecomments: Optional[str] = Field(None, max_length=2000, description="Quote Comments")
    
    # Scheduling
    schedulefollowup_prospect: Optional[date] = Field(None, description="Scheduled Follow up (Prospect)")
    schedulefollowup_qualify: Optional[date] = Field(None, description="Scheduled Follow up (Qualify)")
    scheduleproposalmeeting: Optional[date] = Field(None, description="Schedule Proposal Meeting")
    
    # Additional fields
    emailaddress: Optional[str] = Field(None, max_length=100, description="Email Address")
    need: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Need")
    prioritycode: Optional[Literal[1]] = Field(1, description="Priority")
    stepname: Optional[str] = Field(None, max_length=200, description="Pipeline Phase")
    
    # Advanced fields
    msdyn_forecastcategory: Optional[Literal[100000001, 100000002, 100000003, 100000004, 100000005, 100000006]] = Field(100000001, description="Forecast category")
    msdyn_gdproptout: Optional[bool] = Field(False, description="GDPR Optout")
    msdyn_opportunityscore: Optional[int] = Field(None, description="Opportunity Score (Deprecated)")
    msdyn_opportunityscoretrend: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Opportunity Score Trend (Deprecated)")
    msdyn_opportunitygrade: Optional[Literal[0, 1, 2, 3]] = Field(None, description="Opportunity Grade (Deprecated)")
    
    # System fields
    importsequencenumber: Optional[int] = Field(None, description="Import Sequence Number")
    overriddencreatedon: Optional[date] = Field(None, description="Record Created On")
    lastonholdtime: Optional[datetime] = Field(None, description="Last On Hold Time")
    skippricecalculation: Optional[Literal[0, 1]] = Field(0, description="Skip Price Calculation")
    participatesinworkflow: Optional[bool] = Field(None, description="Participates in Workflow")
    teamsfollowed: Optional[int] = Field(None, description="Teams Followed")
    
    # SLA
    slaid: Optional[UUID] = Field(None, description="SLA")
    
    # Pricing error
    pricingerrorcode: Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]] = Field(0, description="Pricing Error")


class OpportunityCreate(OpportunityBase):
    """Model for creating a new opportunity"""
    pass


class OpportunityUpdate(DynamicsEntityBase):
    """Model for updating an opportunity - all fields optional"""
    name: Optional[str] = Field(None, max_length=300)
    customerid: Optional[UUID] = None
    estimatedvalue: Optional[Decimal] = Field(None, ge=0, le=1000000000000)
    actualvalue: Optional[Decimal] = Field(None, ge=-1000000000000, le=1000000000000)
    estimatedclosedate: Optional[date] = None
    closeprobability: Optional[int] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=2000)
    statecode: Optional[Literal[0, 1, 2]] = None
    statuscode: Optional[Literal[1, 2, 3, 4, 5]] = None


class Opportunity(OpportunityBase):
    """Complete Opportunity model including read-only fields"""
    opportunityid: UUID = Field(..., description="Unique identifier of the opportunity")
    
    # Read-only calculated fields
    createdby: Optional[UUID] = Field(None, description="Created By")
    createdonbehalfby: Optional[UUID] = Field(None, description="Created By (Delegate)")
    modifiedby: Optional[UUID] = Field(None, description="Modified By")
    modifiedonbehalfby: Optional[UUID] = Field(None, description="Modified By (Delegate)")
    
    # Base currency fields
    actualvalue_base: Optional[Decimal] = Field(None, description="Actual Revenue (Base)")
    budgetamount_base: Optional[Decimal] = Field(None, description="Budget Amount (Base)")
    discountamount_base: Optional[Decimal] = Field(None, description="Opportunity Discount Amount (Base)")
    estimatedvalue_base: Optional[Decimal] = Field(None, description="Est. Revenue (Base)")
    freightamount_base: Optional[Decimal] = Field(None, description="Freight Amount (Base)")
    totalamount_base: Optional[Decimal] = Field(None, description="Total Amount (Base)")
    totalamountlessfreight_base: Optional[Decimal] = Field(None, description="Total Amount Less Freight (Base)")
    totaldiscountamount_base: Optional[Decimal] = Field(None, description="Total Discount Amount (Base)")
    totallineitemamount_base: Optional[Decimal] = Field(None, description="Total Line Item Amount (Base)")
    totallineitemdiscountamount_base: Optional[Decimal] = Field(None, description="Total Line Item Discount Amount (Base)")
    totaltax_base: Optional[Decimal] = Field(None, description="Total Tax (Base)")
    
    # Exchange rate
    exchangerate: Optional[Decimal] = Field(None, description="Exchange Rate")
    
    # Additional relationships
    msdyn_opportunitykpiid: Optional[UUID] = Field(None, description="KPI")
    msdyn_predictivescoreid: Optional[UUID] = Field(None, description="Predictive Score")
    msdyn_segmentid: Optional[UUID] = Field(None, description="Segment Id")


class OpportunityListResponse(DynamicsBaseModel):
    """Response model for listing opportunities"""
    value: list[Opportunity]
    odata_context: Optional[str] = Field(None, alias="@odata.context")
    odata_count: Optional[int] = Field(None, alias="@odata.count")
    odata_nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
