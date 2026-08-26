from pydantic import UUID4
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from mealie.db.models.users.user_scratchpad_recipe import UserScratchPadRecipe
from mealie.schema.user.user import UserScratchPadRecipeOut


class RepositoryUserScratchPad:
    """Persistence operations for a user's ordered ScratchPad recipes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user(self, user_id: UUID4) -> list[UserScratchPadRecipeOut]:
        statement = (
            select(UserScratchPadRecipe)
            .where(UserScratchPadRecipe.user_id == user_id)
            .options(joinedload(UserScratchPadRecipe.recipe))
            .order_by(UserScratchPadRecipe.position, UserScratchPadRecipe.id)
        )
        entries = self.session.execute(statement).scalars().all()
        return [UserScratchPadRecipeOut.model_validate(entry) for entry in entries]

    def get_by_user_and_recipe(
        self,
        user_id: UUID4,
        recipe_id: UUID4,
    ) -> UserScratchPadRecipe | None:
        statement = select(UserScratchPadRecipe).where(
            UserScratchPadRecipe.user_id == user_id,
            UserScratchPadRecipe.recipe_id == recipe_id,
        )
        return self.session.execute(statement).scalars().one_or_none()

    def add(self, user_id: UUID4, recipe_id: UUID4) -> UserScratchPadRecipeOut:
        existing = self.get_by_user_and_recipe(user_id, recipe_id)
        if existing is not None:
            return UserScratchPadRecipeOut.model_validate(existing)

        maximum_position = self.session.scalar(
            select(func.max(UserScratchPadRecipe.position)).where(UserScratchPadRecipe.user_id == user_id)
        )
        entry = UserScratchPadRecipe(
            user_id=user_id,
            recipe_id=recipe_id,
            position=(maximum_position if maximum_position is not None else -1) + 1,
            session=self.session,
        )
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return UserScratchPadRecipeOut.model_validate(entry)

    def reorder(self, user_id: UUID4, recipe_ids: list[UUID4]) -> list[UserScratchPadRecipeOut]:
        statement = select(UserScratchPadRecipe).where(UserScratchPadRecipe.user_id == user_id)
        entries = self.session.execute(statement).scalars().all()
        entries_by_recipe_id = {entry.recipe_id: entry for entry in entries}

        if len(recipe_ids) != len(set(recipe_ids)) or set(recipe_ids) != set(entries_by_recipe_id):
            raise ValueError("The ScratchPad order must contain every current recipe exactly once")

        for position, recipe_id in enumerate(recipe_ids):
            entries_by_recipe_id[recipe_id].position = position

        self.session.commit()
        return self.get_by_user(user_id)

    def remove(self, user_id: UUID4, recipe_id: UUID4) -> bool:
        entry = self.get_by_user_and_recipe(user_id, recipe_id)
        if entry is None:
            return False

        self.session.delete(entry)
        self.session.commit()
        return True
