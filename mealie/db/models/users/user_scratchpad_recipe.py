from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..recipe import RecipeModel


class UserScratchPadRecipe(SqlAlchemyBase, BaseMixins):
    """A recipe saved in a user's ordered ScratchPad."""

    __tablename__ = "users_to_scratchpad_recipes"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="user_id_recipe_id_scratchpad_key"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipe_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recipe: Mapped["RecipeModel"] = relationship("RecipeModel")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
