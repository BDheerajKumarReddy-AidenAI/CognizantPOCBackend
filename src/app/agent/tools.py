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
                
                result = {
                    "success": True,
                    "opportunity_id": opp.id,  # Include ID for state tracking
                    "name": opp.name,
                    "stage": opp.stage.value,
                    "quote_amount": opp.quote_amount,
                    "contract_months": opp.contract_months,
                    "users_count": opp.user_count,
                    "location": opp.location.value
                }
                print(f"\n🔍 CREATE TOOL OUTPUT:\n{result}\n")
                return result
            except Exception as e:
                await db.rollback()
                logger.error(f"Error creating opportunity: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def list_opportunities(stage: Optional[str] = None) -> dict:
        """
        List all opportunities created by the current user, optionally filtered by stage.
        Only shows opportunities where the user is the creator.
        Returns opportunities WITHOUT internal IDs for user-facing display.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id)
                stage_enum = Stage(stage) if stage else None
                opportunities = await service.list(stage_enum)
                
                result = {
                    "success": True,
                    "total": len(opportunities),
                    "opportunities": [
                        {
                            "internal_id": opp.id,  # Keep for state tracking, but don't show to user
                            "name": opp.name,
                            "stage": opp.stage.value,
                            "contract_months": opp.contract_months,
                            "users_count": opp.user_count,
                            "location": opp.location.value,
                            "quote_amount": opp.quote_amount if opp.quote_amount else None
                        }
                        for opp in opportunities
                    ]
                }
                
                print(f"\n🔍 LIST TOOL OUTPUT:\n{result}\n")
                return result
                
            except Exception as e:
                logger.error(f"Error listing opportunities: {e}")
                return {"success": False, "error": str(e)}
    
    @tool
    async def get_opportunity(opp_id: int) -> dict:
        """
        Get details of a specific opportunity by ID.
        Only returns the opportunity if the current user is the creator.
        Returns opportunity details WITHOUT the internal ID for user display.
        """
        async with AsyncSessionLocal() as db:
            try:
                service = OpportunityService(db, user_id)
                opp = await service.get_by_id(opp_id)
                if not opp:
                    return {"success": False, "error": f"Opportunity not found or you don't have access"}
                
                result = {
                    "success": True,
                    "opportunity_id": opp.id,  # Include for state tracking
                    "name": opp.name,
                    "location": opp.location.value,
                    "stage": opp.stage.value,
                    "quote_amount": opp.quote_amount,
                    "contract_months": opp.contract_months,
                    "users_count": opp.user_count,
                    "sales_person": opp.sales_person,
                    "client_id": opp.client_id
                }
                
                print(f"\n🔍 GET TOOL OUTPUT:\n{result}\n")
                return result
                
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
        Returns updated opportunity WITHOUT internal ID.
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
                    return {"success": False, "error": f"Opportunity not found or you don't have access"}
                
                await db.commit()
                
                result = {
                    "success": True,
                    "opportunity_id": opp.id,  # Include for state tracking
                    "name": opp.name,
                    "stage": opp.stage.value,
                    "quote_amount": opp.quote_amount,
                    "contract_months": opp.contract_months,
                    "users_count": opp.user_count,
                    "location": opp.location.value,
                    "message": "Opportunity updated successfully"
                }
                
                print(f"\n🔍 UPDATE TOOL OUTPUT:\n{result}\n")
                return result
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Error updating opportunity: {e}")
                return {"success": False, "error": str(e)}
    
    return [
        create_opportunity,
        list_opportunities,
        get_opportunity,
        update_opportunity,
    ]
