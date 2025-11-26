"""Agent tools with intelligent entity resolution."""
from typing import Optional
from datetime import date, timedelta
from langchain.tools import tool
from app.core.database import AsyncSessionLocal
from app.services.opportunity import OpportunityService
from app.services.quote import QuoteService
from app.services.client import ClientService
from app.services.product import ProductService
from app.db.models.opportunity import OpportunityStage
from app.db.models.quote import QuoteStatus
from app.db.models.user import UserRole
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.schemas.quote import QuoteCreate, QuoteItemCreate
from app.schemas.client import ClientCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_agent_tools(user_id: int, user_role: UserRole) -> list:
    """Get all tools available to the agent based on user role."""
    
    tools = []
    
    # ==================== LIST TOOLS (Both Roles) ====================
    
    @tool
    async def list_all_opportunities(stage: Optional[str] = None) -> dict:
        """
        List all opportunities with comprehensive details.
        Sales: See only their own opportunities
        Pricing: See ALL opportunities in the system
        Optional: Filter by stage (Prospect, Qualification, Proposal, Quote Requested, Negotiation, Closed Won, Closed Lost)
        
        USE THIS FIRST when user asks about opportunities.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id, user_role)
                stage_enum = OpportunityStage(stage) if stage else None
                opportunities = await service.list(stage_enum)
                
                result = {
                    "success": True,
                    "total": len(opportunities),
                    "opportunities": [
                        {
                            "id": opp.id,
                            "name": opp.name,
                            "description": opp.description,
                            "client_id": opp.client_id,
                            "client_name": opp.client.name if opp.client else "N/A",
                            "client_industry": opp.client.industry if opp.client else None,
                            "stage": opp.stage.value,
                            "estimated_value": float(opp.estimated_value) if opp.estimated_value else None,
                            "probability": opp.probability,
                            "expected_close_date": str(opp.expected_close_date) if opp.expected_close_date else None,
                            "owner_id": opp.owner_id,
                            "owner_name": opp.owner.name,
                            "created_date": str(opp.created_date),
                            "quote_request_notes": opp.quote_request_notes,
                            "quotes_count": len(opp.quotes) if opp.quotes else 0
                        }
                        for opp in opportunities
                    ]
                }
                
                print(f"\n🔍 LIST ALL OPPORTUNITIES: Found {result['total']} opportunities\n")
                return result
                
            except Exception as e:
                logger.error(f"Error listing opportunities: {e}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": str(e)}
    
    @tool
    async def list_all_clients() -> dict:
        """
        List all clients in the system.
        USE THIS FIRST when user mentions a client or wants to create opportunity.
        Returns: id, name, industry, status for each client.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = ClientService(db)
                clients = await service.list()
                
                result = {
                    "success": True,
                    "total": len(clients),
                    "clients": [
                        {
                            "id": client.id,
                            "name": client.name,
                            "industry": client.industry,
                            "status": client.status.value
                        }
                        for client in clients
                    ]
                }
                
                print(f"\n🔍 LIST ALL CLIENTS: Found {result['total']} clients\n")
                return result
                
            except Exception as e:
                logger.error(f"Error listing clients: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def list_all_products(category: Optional[str] = None) -> dict:
        """
        List all available products with pricing.
        USE THIS before creating quotes to see available products.
        Optional: Filter by category (Software, Services, Infrastructure, Support)
        Returns: id, name, description, unit_price, category
        """
        async with AsyncSessionLocal() as db:
            try:
                service = ProductService(db)
                products = await service.list(active_only=True)
                
                if category:
                    products = [p for p in products if p.category and p.category.lower() == category.lower()]
                
                result = {
                    "success": True,
                    "total": len(products),
                    "products": [
                        {
                            "id": product.id,
                            "name": product.name,
                            "description": product.description,
                            "unit_price": float(product.unit_price),
                            "category": product.category
                        }
                        for product in products
                    ]
                }
                
                print(f"\n🔍 LIST ALL PRODUCTS: Found {result['total']} products\n")
                return result
                
            except Exception as e:
                logger.error(f"Error listing products: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def get_opportunity_details(opportunity_id: int) -> dict:
        """
        Get detailed information about a specific opportunity by its ID.
        Use this AFTER listing opportunities to get full details.
        Sales: Can only view their own opportunities
        Pricing: Can view any opportunity
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id, user_role)
                opp = await service.get_by_id(opportunity_id)
                
                if not opp:
                    return {"success": False, "error": "Opportunity not found or access denied"}
                
                result = {
                    "success": True,
                    "id": opp.id,
                    "name": opp.name,
                    "description": opp.description,
                    "client_id": opp.client_id,
                    "client_name": opp.client.name if opp.client else "N/A",
                    "stage": opp.stage.value,
                    "estimated_value": float(opp.estimated_value) if opp.estimated_value else None,
                    "probability": opp.probability,
                    "expected_close_date": str(opp.expected_close_date) if opp.expected_close_date else None,
                    "owner": opp.owner.name,
                    "created_date": str(opp.created_date),
                    "quote_request_notes": opp.quote_request_notes,
                    "quotes_count": len(opp.quotes)
                }
                
                print(f"\n🔍 GET OPPORTUNITY DETAILS: {result}\n")
                return result
                
            except Exception as e:
                logger.error(f"Error getting opportunity: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def list_quotes_by_opportunity_id(opportunity_id: int) -> dict:
        """
        List all quotes for a specific opportunity using its ID.
        Use this AFTER listing opportunities to get the opportunity ID.
        Shows quote details including status, amounts, and notes.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = QuoteService(db, user_id, user_role)
                quotes = await service.list_by_opportunity(opportunity_id)
                
                result = {
                    "success": True,
                    "opportunity_id": opportunity_id,
                    "total": len(quotes),
                    "quotes": [
                        {
                            "id": quote.id,
                            "quote_number": quote.quote_number,
                            "status": quote.status.value if hasattr(quote.status, 'value') else str(quote.status),
                            "quote_date": str(quote.quote_date),
                            "valid_until": str(quote.valid_until) if quote.valid_until else None,
                            "subtotal": float(quote.subtotal),
                            "tax_amount": float(quote.tax_amount),
                            "discount_amount": float(quote.discount_amount),
                            "total_amount": float(quote.total_amount),
                            "notes": quote.notes,
                            "items_count": len(quote.items),
                            "created_by_id": quote.created_by_id,
                            "created_by_name": quote.creator.name,
                            "created_by_role": quote.creator.role.value,
                            "created_date": str(quote.created_date),
                            "items": [
                                {
                                    "product_name": item.product.name if item.product else "Custom",
                                    "description": item.item_description,
                                    "quantity": float(item.quantity),
                                    "unit_price": float(item.unit_price),
                                    "discount_percent": float(item.discount_percent),
                                    "line_total": float(item.line_total)
                                }
                                for item in quote.items
                            ]
                        }
                        for quote in quotes
                    ]
                }
                
                print(f"\n🔍 LIST QUOTES: Found {result['total']} quotes for opportunity {opportunity_id}\n")
                return result
                
            except Exception as e:
                logger.error(f"Error listing quotes: {e}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": str(e)}
    
    @tool
    async def get_quote_details_by_id(quote_id: int) -> dict:
        """
        Get detailed information about a specific quote by its ID.
        Use this AFTER listing quotes to get the quote ID.
        Shows full quote breakdown with all line items.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = QuoteService(db, user_id, user_role)
                quote = await service.get_by_id(quote_id)
                
                if not quote:
                    return {"success": False, "error": "Quote not found or access denied"}
                
                result = {
                    "success": True,
                    "quote_id": quote.id,
                    "quote_number": quote.quote_number,
                    "opportunity_id": quote.opportunity_id,
                    "opportunity_name": quote.opportunity.name,
                    "quote_date": str(quote.quote_date),
                    "valid_until": str(quote.valid_until) if quote.valid_until else None,
                    "status": quote.status.value if hasattr(quote.status, 'value') else str(quote.status),
                    "subtotal": float(quote.subtotal),
                    "tax_amount": float(quote.tax_amount),
                    "discount_amount": float(quote.discount_amount),
                    "total_amount": float(quote.total_amount),
                    "notes": quote.notes,
                    "created_by": quote.creator.name,
                    "items": [
                        {
                            "description": item.item_description,
                            "quantity": float(item.quantity),
                            "unit_price": float(item.unit_price),
                            "discount_percent": float(item.discount_percent),
                            "line_total": float(item.line_total)
                        }
                        for item in quote.items
                    ]
                }
                
                print(f"\n🔍 GET QUOTE DETAILS: {result}\n")
                return result
                
            except Exception as e:
                logger.error(f"Error getting quote: {e}")
                return {"success": False, "error": str(e)}
    
    # ==================== SALES-ONLY TOOLS ====================
    
    if user_role == UserRole.SALES:
        
        @tool
        async def create_opportunity(
            opportunity_name: str,
            client_id: int,
            estimated_value: Optional[float] = None,
            probability: Optional[int] = None,
            expected_close_date: Optional[str] = None,
            description: Optional[str] = None
        ) -> dict:
            """
            Create a new sales opportunity (Sales role only).
            Use list_all_clients() first to get the client_id.
            Required: opportunity_name, client_id
            Optional: estimated_value, probability (0-100), expected_close_date (YYYY-MM-DD), description
            """
            async with AsyncSessionLocal() as db:
                try:
                    service = OpportunityService(db, user_id, user_role)
                    
                    close_date = None
                    if expected_close_date:
                        from datetime import datetime
                        close_date = datetime.strptime(expected_close_date, "%Y-%m-%d").date()
                    
                    data = OpportunityCreate(
                        name=opportunity_name,
                        client_id=client_id,
                        estimated_value=estimated_value,
                        probability=probability,
                        expected_close_date=close_date,
                        description=description
                    )
                    
                    opp = await service.create(data)
                    await db.commit()
                    
                    result = {
                        "success": True,
                        "opportunity_id": opp.id,
                        "opportunity_name": opp.name,
                        "client_id": opp.client_id,
                        "client_name": opp.client.name if opp.client else "N/A",
                        "stage": opp.stage.value,
                        "message": f"Successfully created opportunity '{opp.name}'"
                    }
                    
                    print(f"\n✅ CREATE OPPORTUNITY: {result}\n")
                    return result
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error creating opportunity: {e}")
                    return {"success": False, "error": str(e)}
        
        @tool
        async def update_opportunity_by_id(
            opportunity_id: int,
            opportunity_name: Optional[str] = None,
            stage: Optional[str] = None,
            estimated_value: Optional[float] = None,
            probability: Optional[int] = None,
            expected_close_date: Optional[str] = None,
            description: Optional[str] = None
        ) -> dict:
            """
            Update an existing opportunity (Sales role only, own opportunities).
            Use list_all_opportunities() first to get the opportunity_id.
            Stage values: Prospect, Qualification, Proposal, Negotiation, Closed Won, Closed Lost
            """
            async with AsyncSessionLocal() as db:
                try:
                    service = OpportunityService(db, user_id, user_role)
                    
                    close_date = None
                    if expected_close_date:
                        from datetime import datetime
                        close_date = datetime.strptime(expected_close_date, "%Y-%m-%d").date()
                    
                    data = OpportunityUpdate(
                        name=opportunity_name,
                        stage=OpportunityStage(stage) if stage else None,
                        estimated_value=estimated_value,
                        probability=probability,
                        expected_close_date=close_date,
                        description=description
                    )
                    
                    opp = await service.update(opportunity_id, data)
                    if not opp:
                        return {"success": False, "error": "Opportunity not found or access denied"}
                    
                    await db.commit()
                    
                    result = {
                        "success": True,
                        "opportunity_id": opp.id,
                        "opportunity_name": opp.name,
                        "stage": opp.stage.value,
                        "estimated_value": float(opp.estimated_value) if opp.estimated_value else None,
                        "message": f"Successfully updated opportunity '{opp.name}'"
                    }
                    
                    print(f"\n✅ UPDATE OPPORTUNITY: {result}\n")
                    return result
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating opportunity: {e}")
                    return {"success": False, "error": str(e)}
        
        @tool
        async def request_quote_from_pricing(
            opportunity_id: int,
            product_ids: list[int],
            quantities: list[int],
            contract_months: int = 12,
            notes: Optional[str] = None
        ) -> dict:
            """
            Request a quote from Pricing team (Sales role only).
            
            **IMPORTANT: This does NOT create a quote - it changes the opportunity stage to "Quote Requested"**
            
            Parameters:
            - opportunity_id: ID from list_all_opportunities()
            - product_ids: Product IDs from list_all_products()
            - quantities: Corresponding quantities for each product
            - contract_months: 12, 24, or 36 months
            - notes: Special instructions for Pricing team
            
            After calling this, Pricing team will see the request and create the actual quote.
            """
            async with AsyncSessionLocal() as db:
                try:
                    service = OpportunityService(db, user_id, user_role)
                    
                    # Get opportunity
                    opp = await service.get_by_id(opportunity_id)
                    if not opp:
                        return {"success": False, "error": "Opportunity not found or access denied"}
                    
                    # Build request notes with product details
                    from app.services.product import ProductService
                    product_service = ProductService(db)
                    
                    product_details = []
                    for pid, qty in zip(product_ids, quantities):
                        product = await product_service.get_by_id(pid)
                        if product:
                            product_details.append(f"- {product.name}: {qty} units @ ${product.unit_price}/unit")
                    
                    request_notes = f"""QUOTE REQUEST from {opp.owner.name}
Contract Term: {contract_months} months

Products Requested:
{chr(10).join(product_details)}

Sales Notes: {notes or 'None'}

Requested on: {date.today()}"""
                    
                    # Update opportunity stage and add notes
                    data = OpportunityUpdate(
                        stage=OpportunityStage.QUOTE_REQUESTED,
                        quote_request_notes=request_notes
                    )
                    
                    updated_opp = await service.update(opportunity_id, data)
                    if not updated_opp:
                        return {"success": False, "error": "Failed to update opportunity"}
                    
                    await db.commit()
                    
                    result = {
                        "success": True,
                        "opportunity_id": opp.id,
                        "opportunity_name": opp.name,
                        "stage": "Quote Requested",
                        "message": f"Quote request submitted for '{opp.name}'. Pricing team will review and create quote."
                    }
                    
                    print(f"\n✅ REQUEST QUOTE FROM PRICING: {result}\n")
                    return result
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error requesting quote: {e}")
                    import traceback
                    traceback.print_exc()
                    return {"success": False, "error": str(e)}
        
        tools.extend([create_opportunity, update_opportunity_by_id, request_quote_from_pricing])
    
    # ==================== PRICING-ONLY TOOLS ====================
    
    if user_role == UserRole.PRICING:
        
        @tool
        async def create_quote_for_opportunity(
            opportunity_id: int,
            product_ids: list[int],
            quantities: list[int],
            contract_months: int = 12,
            notes: Optional[str] = None
        ) -> dict:
            """
            Create a quote for an opportunity (Pricing role only).
            
            **This CREATES the actual quote with automatic discounts applied**
            
            Volume Discounts (auto-applied):
            - 100-499 units: 5% off
            - 500-999 units: 10% off
            - 1000+ units: 15% off
            
            Term Discounts (auto-applied):
            - 12 months: 5% off
            - 24 months: 12% off
            - 36 months: 20% off
            
            Use this after Sales requests a quote (stage = "Quote Requested").
            You can also create quotes proactively for any opportunity.
            
            Parameters:
            - opportunity_id: ID from list_all_opportunities()
            - product_ids: Product IDs from list_all_products()
            - quantities: Corresponding quantities
            - contract_months: 12, 24, or 36
            - notes: Pricing notes/explanation
            """
            async with AsyncSessionLocal() as db:
                try:
                    service = QuoteService(db, user_id, user_role)
                    product_service = ProductService(db)
                    
                    # Verify opportunity exists
                    opp_service = OpportunityService(db, user_id, user_role)
                    opp = await opp_service.get_by_id(opportunity_id)
                    if not opp:
                        return {"success": False, "error": "Opportunity not found"}
                    
                    # Get products and build quote items
                    items = []
                    for product_id, quantity in zip(product_ids, quantities):
                        product = await product_service.get_by_id(product_id)
                        if product:
                            items.append(QuoteItemCreate(
                                product_id=product_id,
                                item_description=product.name,
                                quantity=quantity,
                                unit_price=product.unit_price,
                                discount_percent=0
                            ))
                        else:
                            return {"success": False, "error": f"Product ID {product_id} not found"}
                    
                    if not items:
                        return {"success": False, "error": "No valid products specified"}
                    
                    # Create quote
                    data = QuoteCreate(
                        opportunity_id=opportunity_id,
                        quote_date=date.today(),
                        valid_until=date.today() + timedelta(days=30),
                        notes=notes or f"Created by Pricing team",
                        items=items
                    )
                    
                    quote = await service.create(data, contract_months)
                    await db.commit()
                    
                    result = {
                        "success": True,
                        "quote_id": quote.id,
                        "quote_number": quote.quote_number,
                        "opportunity_id": opportunity_id,
                        "opportunity_name": opp.name,
                        "total_amount": float(quote.total_amount),
                        "status": quote.status.value if hasattr(quote.status, 'value') else str(quote.status),
                        "valid_until": str(quote.valid_until),
                        "items_count": len(quote.items),
                        "message": f"Quote {quote.quote_number} created for ${float(quote.total_amount):,.2f}"
                    }
                    
                    print(f"\n✅ CREATE QUOTE FOR OPPORTUNITY: {result}\n")
                    return result
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error creating quote: {e}")
                    import traceback
                    traceback.print_exc()
                    return {"success": False, "error": str(e)}
        
        @tool
        async def update_quote_pricing_by_id(
            quote_id: int,
            tax_amount: Optional[float] = None,
            discount_amount: Optional[float] = None,
            status: Optional[str] = None,
            notes: Optional[str] = None
        ) -> dict:
            """
            Update quote pricing details (Pricing role only).
            
            **YOU CAN APPROVE/REJECT QUOTES WITH THIS TOOL!**
            
            To APPROVE a quote: Set status="Approved"
            To REJECT a quote: Set status="Rejected"
            
            Parameters:
            - quote_id: ID from list_quotes_by_opportunity_id()
            - tax_amount: Dollar amount of tax (e.g., 5000.00 for $5,000)
            - discount_amount: Dollar amount of additional discount
            - status: Quote status - VALUES:
              * "Draft" - Initial state
              * "Pending Review" - Needs review
              * "Approved" - ✅ APPROVED (use this to approve!)
              * "Sent" - Sent to client
              * "Accepted" - Client accepted
              * "Rejected" - ❌ REJECTED (use this to reject!)
              * "Expired" - Validity expired
            - notes: Add explanation (cumulative with timestamp)
            
            Examples:
            - Approve: update_quote_pricing_by_id(5, status="Approved", notes="Approved for submission")
            - Add tax and approve: update_quote_pricing_by_id(5, tax_amount=5000.00, status="Approved", notes="8% tax applied")
            """
            async with AsyncSessionLocal() as db:
                try:
                    from app.schemas.quote import QuoteUpdate
                    service = QuoteService(db, user_id, user_role)
                    
                    # Get existing quote
                    existing_quote = await service.get_by_id(quote_id)
                    if not existing_quote:
                        return {"success": False, "error": "Quote not found"}
                    
                    # Append notes with timestamp
                    final_notes = existing_quote.notes or ""
                    if notes:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        final_notes += f"\n\n[Pricing Update - {timestamp}] {notes}"
                    
                    # Update
                    data = QuoteUpdate(
                        tax_amount=tax_amount,
                        discount_amount=discount_amount,
                        status=QuoteStatus(status) if status else None,
                        notes=final_notes if notes else None
                    )
                    
                    quote = await service.update(quote_id, data)
                    if not quote:
                        return {"success": False, "error": "Quote not found after update"}
                    
                    await db.commit()
                    
                    # Build message
                    changes = []
                    if tax_amount is not None:
                        changes.append(f"tax ${tax_amount:,.2f}")
                    if discount_amount is not None:
                        changes.append(f"discount ${discount_amount:,.2f}")
                    if status:
                        changes.append(f"status → {status}")
                    
                    message = f"Updated quote {quote.quote_number}"
                    if changes:
                        message += f": {', '.join(changes)}"
                    
                    # Safe status extraction
                    status_str = quote.status.value if hasattr(quote.status, 'value') else str(quote.status)
                    
                    result = {
                        "success": True,
                        "quote_id": quote.id,
                        "quote_number": quote.quote_number,
                        "total_amount": float(quote.total_amount),
                        "status": status_str,
                        "notes": quote.notes,
                        "message": message
                    }
                    
                    print(f"\n✅ UPDATE QUOTE PRICING: {result}\n")
                    return result
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating quote: {e}")
                    import traceback
                    traceback.print_exc()
                    return {"success": False, "error": str(e)}
        
        tools.extend([create_quote_for_opportunity, update_quote_pricing_by_id])
    
    # Add common tools
    tools.extend([
        list_all_opportunities,
        list_all_clients,
        list_all_products,
        get_opportunity_details,
        list_quotes_by_opportunity_id,
        get_quote_details_by_id
    ])
    
    return tools
