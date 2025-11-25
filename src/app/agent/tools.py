"""Agent tools wrapping service layer functions."""
from typing import Optional
from langchain.tools import tool
from app.core.database import AsyncSessionLocal
from app.services.opportunity import OpportunityService
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.db.models.opportunity import Stage, Location
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_opportunity_tools(user_id: int) -> list:
    """Get all opportunity management tools for the agent."""
    
    @tool
    async def create_opportunity(
        oppurtunity_name: str,
        contract_months: int,
        users_count: int,
        location: str = "USA"
    ) -> dict:
        """Create a new sales opportunity."""
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id)
                data = OpportunityCreate(
                    oppurtunity_name=oppurtunity_name,
                    contract_months=contract_months,
                    users_count=users_count,
                    location=Location(location)
                )
                opp = await service.create(data)
                await db.commit()
                
                return {
                    "success": True,
                    "opp_id": opp.id,
                    "oppurtunity_name": opp.name,
                    "stage": opp.stage.value,
                    "quote_amount": opp.quote_amount
                }
            except Exception as e:
                await db.rollback()
                logger.error(f"Error creating opportunity: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def list_opportunities(stage: Optional[str] = None) -> dict:
        """
        List all opportunities created by the current user, optionally filtered by stage.
        Only shows opportunities where the user is the creator.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id)
                stage_enum = Stage(stage) if stage else None
                # Service already filters by user_id (creator_id)
                opportunities = await service.list(stage_enum)
                
                return {
                    "success": True,
                    "total": len(opportunities),
                    "opportunities": [
                        {
                            "opp_id": opp.id,
                            "oppurtunity_name": opp.name,
                            "stage": opp.stage.value,
                            "quote_amount": opp.quote_amount,
                            "contract_months": opp.contract_months,
                            "users_count": opp.user_count,
                            "location": opp.location.value
                        }
                        for opp in opportunities
                    ]
                }
            except Exception as e:
                logger.error(f"Error listing opportunities: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def get_opportunity(opp_id: int) -> dict:
        """
        Get details of a specific opportunity by ID.
        Only returns the opportunity if the current user is the creator.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id)
                opp = await service.get_by_id(opp_id)
                if not opp:
                    return {"success": False, "error": f"Opportunity {opp_id} not found or you don't have access"}
                
                return {
                    "success": True,
                    "opp_id": opp.id,
                    "oppurtunity_name": opp.name,
                    "location": opp.location.value,
                    "stage": opp.stage.value,
                    "quote_amount": opp.quote_amount,
                    "contract_months": opp.contract_months,
                    "users_count": opp.user_count,
                    "sales_person": opp.sales_person,
                    "client_id": opp.client_id
                }
            except Exception as e:
                logger.error(f"Error getting opportunity: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def update_opportunity(
        opp_id: int,
        oppurtunity_name: Optional[str] = None,
        stage: Optional[str] = None,
        contract_months: Optional[int] = None,
        users_count: Optional[int] = None,
        location: Optional[str] = None
    ) -> dict:
        """
        Update an existing opportunity.
        Only allows updating opportunities created by the current user.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id)
                data = OpportunityUpdate(
                    oppurtunity_name=oppurtunity_name,
                    stage=Stage(stage) if stage else None,
                    contract_months=contract_months,
                    users_count=users_count,
                    location=Location(location) if location else None
                )
                
                opp = await service.update(opp_id, data)
                if not opp:
                    return {"success": False, "error": f"Opportunity {opp_id} not found or you don't have access"}
                
                await db.commit()
                
                return {
                    "success": True,
                    "opp_id": opp.id,
                    "oppurtunity_name": opp.name,
                    "stage": opp.stage.value,
                    "quote_amount": opp.quote_amount,
                    "message": "Opportunity updated successfully"
                }
            except Exception as e:
                await db.rollback()
                logger.error(f"Error updating opportunity: {e}")
                return {"success": False, "error": str(e)}
    
    # Removed delete_opportunity tool
    
    return [
        create_opportunity,
        list_opportunities,
        get_opportunity,
        update_opportunity,
    ]
