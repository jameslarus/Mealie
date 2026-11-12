"""merge upstream and ScratchPad migrations

Revision ID: 7800b1842b9e
Revises: e64ab0dd02bc, 3527efeeec34
Create Date: 2026-09-25 20:15:59.933094

"""

# revision identifiers, used by Alembic.
revision = "7800b1842b9e"
down_revision: str | None = ("e64ab0dd02bc", "3527efeeec34")
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    pass


def downgrade():
    pass
