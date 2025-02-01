"""Initial migration

Revision ID: 462b3a698d5d
Revises: 
Create Date: 2025-01-30 15:34:29.073394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '462b3a698d5d'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        INSERT INTO shipping_methods_prices (shipping_method_id, price) 
        VALUES 
            (0, 3.9),
            (1, 7.9),
            (2, 6.9),
            (3, 14.9),
            (4, 3.9),
            (5, 0.0)
        ON CONFLICT (shipping_method_id) DO NOTHING;
    """)


def downgrade():
    op.execute("DELETE FROM shipping_methods_prices;")