"""Revision to add in no fee service fees.

Revision ID: f4a1388844ed
Revises: d2d9864164d1
Create Date: 2023-03-07 13:22:28.195608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4a1388844ed'
down_revision = 'd2d9864164d1'
branch_labels = None
depends_on = None

def upgrade():
    fee_code_table = sa.table("fee_code", sa.column("code", sa.String),sa.column("amount", sa.Float))
    op.bulk_insert(
        fee_code_table, [
            {"code": "TRF04", "amount": 0.00}
        ]
    )

def downgrade():
    op.execute("delete from fee_code where code = 'TRF04';")
