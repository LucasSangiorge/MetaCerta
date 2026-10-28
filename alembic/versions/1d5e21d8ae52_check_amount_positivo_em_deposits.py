"""check amount positivo em deposits

Revision ID: 1d5e21d8ae52
Revises: 2b9fdcff1747
Create Date: 2026-10-23 10:03:12.793727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d5e21d8ae52'
down_revision: Union[str, Sequence[str], None] = '2b9fdcff1747'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        op.f("ck_deposits_amount_positive"),
        "deposits",
        "amount > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_deposits_amount_positive"),
        "deposits",
        type_="check",
    )
