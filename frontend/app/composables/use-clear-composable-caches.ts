import { resetGroupRecipeActions } from "~/composables/use-group-recipe-actions";
import { resetGroupSelf } from "~/composables/use-groups";
import { resetHouseholdSelf } from "~/composables/use-households";
import { resetUserSelfRatings } from "~/composables/use-users/user-ratings";
import { resetUserScratchPad } from "~/composables/use-users/user-scratchpad";
import { resetBackups } from "~/composables/use-backups";
import { resetRecipes } from "~/composables/recipes/use-recipes";
import { resetUserRegistrationForm } from "~/composables/use-users/user-registration-form";

export function clearComposableCaches() {
  resetGroupRecipeActions();
  resetGroupSelf();
  resetHouseholdSelf();
  resetUserSelfRatings();
  resetUserScratchPad();
  resetBackups();
  resetRecipes();
  resetUserRegistrationForm();
}
