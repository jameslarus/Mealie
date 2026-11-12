import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { UserScratchPadRecipe } from "~/lib/api/types/user";

const scratchPadRecipes = ref<UserScratchPadRecipe[]>([]);
const loading = ref(false);
const loadedForUserId = ref<string | null>(null);

export function resetUserScratchPad() {
  scratchPadRecipes.value = [];
  loading.value = false;
  loadedForUserId.value = null;
}

export function useUserScratchPad() {
  const auth = useMealieAuth();
  const i18n = useI18n();

  function reportError(error: unknown) {
    console.error("ScratchPad request failed", error);
    alert.error(i18n.t("recipe.scratchpad-update-failed"));
  }

  async function refresh() {
    const userId = auth.user.value?.id;
    if (!userId || loading.value) {
      return;
    }

    loading.value = true;
    const { data, error } = await useUserApi().users.getScratchPad();
    loading.value = false;

    if (error || !data) {
      reportError(error);
      return;
    }

    scratchPadRecipes.value = data;
    loadedForUserId.value = userId;
  }

  async function add(recipeId: string) {
    const { data, error } = await useUserApi().users.addToScratchPad(recipeId);
    if (error || !data) {
      reportError(error);
      return;
    }

    const existingIndex = scratchPadRecipes.value.findIndex(
      item => item.recipeId === data.recipeId,
    );

    if (existingIndex === -1) {
      scratchPadRecipes.value.push(data);
    }
    else {
      scratchPadRecipes.value[existingIndex] = data;
    }
  }

  async function reorder(recipeIds: string[]) {
    const { data, error } = await useUserApi().users.reorderScratchPad(recipeIds);

    if (error || !data) {
      reportError(error);
      await refresh();
      return;
    }

    scratchPadRecipes.value = data;
  }

  async function remove(recipeId: string) {
    const { error } = await useUserApi().users.removeFromScratchPad(recipeId);

    if (error) {
      reportError(error);
      return;
    }

    scratchPadRecipes.value = scratchPadRecipes.value.filter(
      item => item.recipeId !== recipeId,
    );
  }

  if (
    auth.user.value?.id
    && loadedForUserId.value !== auth.user.value.id
  ) {
    void refresh();
  }

  return {
    scratchPadRecipes,
    loading,
    refresh,
    add,
    reorder,
    remove,
  };
}
