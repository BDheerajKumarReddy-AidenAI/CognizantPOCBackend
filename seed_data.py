"""Seed database with test data."""
import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Fix for Windows asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.database import AsyncSessionLocal
from app.db.models.user import User, UserRole
from app.db.models.client import Client, ClientStatus
from app.db.models.contact import Contact
from app.db.models.product import Product
from app.db.models.opportunity import Opportunity, OpportunityStage
from app.db.models.quote import Quote, QuoteStatus
from app.db.models.quote_item import QuoteItem


async def seed_database():
    """Seed database with comprehensive test data."""
    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Seeding database...")
            
            # ==================== USERS ====================
            print("\n📝 Creating users...")
            users = [
                User(name="John Sales", email="john@company.com", role=UserRole.SALES),
                User(name="Jane Sales", email="jane@company.com", role=UserRole.SALES),
                User(name="Mike Pricing", email="mike@company.com", role=UserRole.PRICING),
                User(name="Sarah Pricing", email="sarah@company.com", role=UserRole.PRICING),
            ]
            session.add_all(users)
            await session.flush()
            print(f"✅ Created {len(users)} users")
            
            # ==================== CLIENTS ====================
            print("\n📝 Creating clients...")
            clients = [
                Client(
                    name="Acme Corporation",
                    industry="Technology",
                    email="contact@acme.com",
                    phone="555-0101",
                    address="123 Tech Street, San Francisco, CA",
                    status=ClientStatus.ACTIVE
                ),
                Client(
                    name="Global Industries",
                    industry="Manufacturing",
                    email="info@global.com",
                    phone="555-0102",
                    address="456 Factory Rd, Detroit, MI",
                    status=ClientStatus.ACTIVE
                ),
                Client(
                    name="TechStart Inc",
                    industry="Technology",
                    email="hello@techstart.com",
                    phone="555-0103",
                    address="789 Startup Ave, Austin, TX",
                    status=ClientStatus.PROSPECT
                ),
                Client(
                    name="Enterprise Solutions",
                    industry="Consulting",
                    email="contact@enterprise.com",
                    phone="555-0104",
                    address="321 Business Blvd, New York, NY",
                    status=ClientStatus.ACTIVE
                ),
                Client(
                    name="LaunchBae",
                    industry="Technology",
                    email="hello@launchbae.com",
                    phone="555-0105",
                    address="999 Innovation Dr, San Jose, CA",
                    status=ClientStatus.PROSPECT
                ),
            ]
            session.add_all(clients)
            await session.flush()
            print(f"✅ Created {len(clients)} clients")
            
            # ==================== CONTACTS ====================
            print("\n📝 Creating contacts...")
            contacts = [
                Contact(
                    client_id=clients[0].id,
                    first_name="Bob",
                    last_name="Smith",
                    email="bob.smith@acme.com",
                    phone="555-0201",
                    job_title="CTO",
                    is_primary=True
                ),
                Contact(
                    client_id=clients[1].id,
                    first_name="Alice",
                    last_name="Johnson",
                    email="alice.j@global.com",
                    phone="555-0203",
                    job_title="VP of Operations",
                    is_primary=True
                ),
                Contact(
                    client_id=clients[4].id,
                    first_name="Emma",
                    last_name="Chen",
                    email="emma@launchbae.com",
                    phone="555-0206",
                    job_title="CEO",
                    is_primary=True
                ),
            ]
            session.add_all(contacts)
            await session.flush()
            print(f"✅ Created {len(contacts)} contacts")
            
            # ==================== PRODUCTS ====================
            print("\n📝 Creating products...")
            products = [
                Product(
                    name="Enterprise License",
                    description="Full-featured enterprise software license",
                    unit_price=Decimal("500.00"),
                    category="Software",
                    is_active=True
                ),
                Product(
                    name="Professional Services",
                    description="Expert consulting and implementation",
                    unit_price=Decimal("200.00"),
                    category="Services",
                    is_active=True
                ),
                Product(
                    name="Cloud Storage",
                    description="Secure cloud storage per GB/month",
                    unit_price=Decimal("10.00"),
                    category="Infrastructure",
                    is_active=True
                ),
                Product(
                    name="Premium Support",
                    description="24/7 premium support package",
                    unit_price=Decimal("150.00"),
                    category="Support",
                    is_active=True
                ),
                Product(
                    name="Training Program",
                    description="Comprehensive training and certification",
                    unit_price=Decimal("100.00"),
                    category="Services",
                    is_active=True
                ),
            ]
            session.add_all(products)
            await session.flush()
            print(f"✅ Created {len(products)} products")
            
            # ==================== OPPORTUNITIES ====================
            print("\n📝 Creating opportunities...")
            opportunities = [
                Opportunity(
                    client_id=clients[0].id,
                    owner_id=users[0].id,  # John Sales
                    name="Acme Q4 Expansion",
                    description="Expand to 500 users with support",
                    estimated_value=Decimal("250000.00"),
                    probability=80,
                    stage=OpportunityStage.PROPOSAL,
                    expected_close_date=date.today() + timedelta(days=30)
                ),
                Opportunity(
                    client_id=clients[4].id,
                    owner_id=users[1].id,  # Jane Sales
                    name="LaunchBae Expansion",
                    description="Initial deployment for startup",
                    estimated_value=Decimal("50000.00"),
                    probability=60,
                    stage=OpportunityStage.PROSPECT,
                    expected_close_date=date.today() + timedelta(days=45)
                ),
            ]
            session.add_all(opportunities)
            await session.flush()
            print(f"✅ Created {len(opportunities)} opportunities")
            
            # ==================== QUOTES ====================
            print("\n📝 Creating quotes...")
            
            # Quote for Acme (Draft)
            quote1 = Quote(
                opportunity_id=opportunities[0].id,
                quote_number="Q-202511-A1B2C3",
                quote_date=date.today(),
                valid_until=date.today() + timedelta(days=30),
                subtotal=Decimal("225000.00"),
                tax_amount=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
                total_amount=Decimal("225000.00"),
                status=QuoteStatus.DRAFT,
                notes="Volume discount applied for 500 licenses",
                created_by_id=users[2].id  # Mike Pricing
            )
            session.add(quote1)
            await session.flush()
            
            # Quote items
            quote1_items = [
                QuoteItem(
                    quote_id=quote1.id,
                    product_id=products[0].id,
                    item_description="Enterprise License x 500",
                    quantity=Decimal("500"),
                    unit_price=Decimal("500.00"),
                    discount_percent=Decimal("10.00"),
                    line_total=Decimal("225000.00")
                ),
            ]
            session.add_all(quote1_items)
            print(f"✅ Created quotes with line items")
            
            # Commit all
            await session.commit()
            
            print("\n" + "="*70)
            print("🎉 Database seeded successfully!")
            print("="*70)
            print(f"\n📊 Summary:")
            print(f"   Users: {len(users)}")
            print(f"   Clients: {len(clients)}")
            print(f"   Contacts: {len(contacts)}")
            print(f"   Products: {len(products)}")
            print(f"   Opportunities: {len(opportunities)}")
            print(f"   Quotes: 1")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding database: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
