"""merge upstream and ScratchPad migrations

Revision ID: e835fd374ba3
Revises: 7800b1842b9e, 3697d65c5f92
Create Date: 2026-10-14 17:05:45.147766

"""

# revision identifiers, used by Alembic.
revision = "e835fd374ba3"
down_revision: str | None = ("7800b1842b9e", "3697d65c5f92")
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    pass


def downgrade():
    pass
