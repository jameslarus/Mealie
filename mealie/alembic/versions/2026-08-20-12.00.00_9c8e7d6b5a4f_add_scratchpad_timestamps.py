"""add missing ScratchPad timestamps

Revision ID: 9c8e7d6b5a4f
Revises: 7d4c9b2a1e6f
Create Date: 2026-08-20 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "9c8e7d6b5a4f"
down_revision: str | None = "7d4c9b2a1e6f"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # UserScratchpadRecipeModel inherits these fields from SqlAlchemyBase. The
    # original ScratchPad migration omitted them, so SQLAlchemy included columns
    # in SELECT statements that did not exist in the database.
    with op.batch_alter_table("users_to_scratchpad_recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True))
        batch_op.add_column(sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_users_to_scratchpad_recipes_created_at"),
            ["created_at"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("users_to_scratchpad_recipes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_to_scratchpad_recipes_created_at"))
        batch_op.drop_column("update_at")
        batch_op.drop_column("created_at")
