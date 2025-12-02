from pydantic import Field
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from mcp_server.models import DynamicsEntityBase, DynamicsBaseModel


class ProductBase(DynamicsEntityBase):
    """Base Product model with writable fields"""
    
    # Core fields
    name: str = Field(..., max_length=100, description="Name")
    productnumber: Optional[str] = Field(None, max_length=100, description="Product ID")
    productstructure: Optional[Literal[1, 2, 3]] = Field(1, description="Product Structure: 1=Product, 2=Product Family, 3=Product Bundle")
    producttypecode: Optional[Literal[1, 2, 3, 4, 5]] = Field(1, description="Product Type")
    
    # Description
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    
    # Parent product
    parentproductid: Optional[UUID] = Field(None, description="Parent")
    
    # Pricing
    price: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000, description="List Price")
    standardcost: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000, description="Standard Cost")
    currentcost: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000, description="Current Cost")
    
    # Pricing method
    pricelevelid: Optional[UUID] = Field(None, description="Default Price List")
    
    # Quantity
    quantitydecimal: Optional[int] = Field(5, ge=0, le=5, description="Decimals Supported")
    quantityonhand: Optional[Decimal] = Field(0, description="Quantity On Hand")
    stockvolume: Optional[Decimal] = Field(None, description="Stock Volume")
    stockweight: Optional[Decimal] = Field(None, description="Stock Weight")
    
    # Unit of measure
    defaultuomid: Optional[UUID] = Field(None, description="Default Unit")
    defaultuomscheduleid: Optional[UUID] = Field(None, description="Unit Group")
    
    # Supplier
    vendorid: Optional[str] = Field(None, max_length=100, description="Vendor ID")
    vendorname: Optional[str] = Field(None, max_length=100, description="Vendor Name")
    vendorpartnumber: Optional[str] = Field(None, max_length=100, description="Vendor Name")
    
    # Sales and support
    iskit: Optional[bool] = Field(False, description="Is Kit")
    isstockitem: Optional[bool] = Field(True, description="Stock Item")
    
    # Product hierarchy
    producturl: Optional[str] = Field(None, max_length=255, description="URL")
    
    # Dimensions
    size: Optional[str] = Field(None, max_length=200, description="Size")
    
    # Subject
    subjectid: Optional[UUID] = Field(None, description="Subject")
    
    # Conversion
    dmtimportstate: Optional[int] = Field(None, description="Internal Use Only")
    
    # Dates
    validfromdate: Optional[datetime] = Field(None, description="Valid From")
    validtodate: Optional[datetime] = Field(None, description="Valid To")
    
    # State
    statecode: Optional[Literal[0, 1, 2, 3]] = Field(0, description="Status: 0=Active, 1=Retired, 2=Draft, 3=Under Revision")
    statuscode: Optional[Literal[1, 2, 3]] = Field(None, description="Status Reason")
    
    # Hierarchy path
    hierarchypath: Optional[str] = Field(None, max_length=450, description="Hierarchy Path")
    
    # Currency
    transactioncurrencyid: Optional[UUID] = Field(None, description="Currency")
    
    # System fields
    importsequencenumber: Optional[int] = Field(None, description="Import Sequence Number")
    overriddencreatedon: Optional[date] = Field(None, description="Record Created On")
    timezoneruleversionnumber: Optional[int] = Field(None, description="Time Zone Rule Version Number")
    utcconversiontimezonecode: Optional[int] = Field(None, ge=-1, le=1500, description="UTC Conversion Time Zone Code")
    
    # Advanced fields
    msdyn_fieldserviceproducttype: Optional[Literal[690970000, 690970001, 690970002]] = Field(690970000, description="Field Service Product Type")
    msdyn_purchasename: Optional[str] = Field(None, max_length=100, description="Purchase Name")
    msdyn_taxable: Optional[bool] = Field(True, description="Taxable")
    msdyn_transactioncategory: Optional[UUID] = Field(None, description="Transaction Category")
    msdyn_upccode: Optional[str] = Field(None, max_length=100, description="UPC Code")
    msdyn_productiontrackingenabled: Optional[bool] = Field(False, description="Production Tracking Enabled")
    
    # Financials
    msdyn_costdate: Optional[date] = Field(None, description="Cost Date")
    msdyn_costofsalespercent: Optional[Decimal] = Field(None, ge=0, le=100000000000, description="Cost of Sales %")
    msdyn_taxableamount: Optional[Decimal] = Field(None, description="Taxable Amount")
    
    # Fields from Dynamics
    entityimage: Optional[bytes] = Field(None, description="Entity Image")


class ProductCreate(ProductBase):
    """Model for creating a new product"""
    pass


class ProductUpdate(DynamicsEntityBase):
    """Model for updating a product - all fields optional"""
    name: Optional[str] = Field(None, max_length=100)
    productnumber: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000)
    standardcost: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000)
    currentcost: Optional[Decimal] = Field(None, ge=-100000000000, le=100000000000)
    quantityonhand: Optional[Decimal] = None
    statecode: Optional[Literal[0, 1, 2, 3]] = None
    statuscode: Optional[Literal[1, 2, 3]] = None


class Product(ProductBase):
    """Complete Product model including read-only fields"""
    productid: UUID = Field(..., description="Unique identifier of the product")
    
    # Read-only fields
    createdby: Optional[UUID] = Field(None, description="Created By")
    createdonbehalfby: Optional[UUID] = Field(None, description="Created By (Delegate)")
    modifiedby: Optional[UUID] = Field(None, description="Modified By")
    modifiedonbehalfby: Optional[UUID] = Field(None, description="Modified By (Delegate)")
    
    # Organization
    organizationid: Optional[UUID] = Field(None, description="Organization")
    
    # Base currency fields
    price_base: Optional[Decimal] = Field(None, description="List Price (Base)")
    standardcost_base: Optional[Decimal] = Field(None, description="Standard Cost (Base)")
    currentcost_base: Optional[Decimal] = Field(None, description="Current Cost (Base)")
    
    # Exchange rate
    exchangerate: Optional[Decimal] = Field(None, description="Exchange Rate")
    
    # Entity image
    entityimage_timestamp: Optional[int] = Field(None, description="Entity Image Timestamp")
    entityimage_url: Optional[str] = Field(None, description="Entity Image URL")
    entityimageid: Optional[UUID] = Field(None, description="Entity Image Id")
    
    # Supplier info
    suppliername: Optional[str] = Field(None, max_length=100, description="Supplier Name")


class ProductListResponse(DynamicsBaseModel):
    """Response model for listing products"""
    value: list[Product]
    odata_context: Optional[str] = Field(None, alias="@odata.context")
    odata_count: Optional[int] = Field(None, alias="@odata.count")
    odata_nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
