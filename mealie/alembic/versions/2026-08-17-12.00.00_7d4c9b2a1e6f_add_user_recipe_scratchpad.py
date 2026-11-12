"""add user recipe ScratchPad

Revision ID: 7d4c9b2a1e6f
Revises: 2187537c52b8
Create Date: 2026-08-17 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

from mealie.db.models._model_utils.guid import GUID

# revision identifiers, used by Alembic.
revision = "7d4c9b2a1e6f"
down_revision: str | None = "2187537c52b8"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.create_table(
        "users_to_scratchpad_recipes",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("recipe_id", GUID(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "recipe_id", name="user_id_recipe_id_scratchpad_key"),
    )
    op.create_index(
        op.f("ix_users_to_scratchpad_recipes_recipe_id"),
        "users_to_scratchpad_recipes",
        ["recipe_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_users_to_scratchpad_recipes_user_id"),
        "users_to_scratchpad_recipes",
        ["user_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_users_to_scratchpad_recipes_user_id"), table_name="users_to_scratchpad_recipes")
    op.drop_index(op.f("ix_users_to_scratchpad_recipes_recipe_id"), table_name="users_to_scratchpad_recipes")
    op.drop_table("users_to_scratchpad_recipes")
