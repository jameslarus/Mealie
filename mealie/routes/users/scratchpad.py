from functools import cached_property

from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.response.responses import ErrorResponse, SuccessResponse
from mealie.schema.user.user import UserScratchPadRecipeOrder, UserScratchPadRecipeOut

router = UserAPIRouter(prefix="/users/self/scratchpad", tags=["Users: ScratchPad"])


@controller(router)
class UserScratchPadController(BaseUserController):
    @cached_property
    def group_recipes(self):
        return get_repositories(self.session, group_id=self.group_id, household_id=None).recipes

    @router.get("", response_model=list[UserScratchPadRecipeOut])
    def get_scratchpad(self):
        return self.repos.user_scratchpad.get_by_user(self.user.id)

    @router.put("/order", response_model=list[UserScratchPadRecipeOut])
    def reorder_scratchpad(self, order: UserScratchPadRecipeOrder):
        try:
            return self.repos.user_scratchpad.reorder(self.user.id, order.recipe_ids)
        except ValueError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    @router.post("/{recipe_id}", response_model=UserScratchPadRecipeOut)
    def add_to_scratchpad(self, recipe_id: UUID4):
        recipe = self.group_recipes.get_one(recipe_id, key="id")
        if recipe is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse.respond(message="Recipe not found"),
            )

        return self.repos.user_scratchpad.add(self.user.id, recipe.id)

    @router.delete("/{recipe_id}")
    def remove_from_scratchpad(self, recipe_id: UUID4):
        if not self.repos.user_scratchpad.remove(self.user.id, recipe_id):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse.respond(message="Recipe is not in the ScratchPad"),
            )
        return SuccessResponse.respond("Recipe removed from ScratchPad")
