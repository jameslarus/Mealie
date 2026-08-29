<template>
  <v-table class="recipe-sortable-list" hover>
    <thead>
      <tr>
        <th :aria-sort="ariaSort('name')">
          <v-btn variant="text" size="large" @click="sortBy('name')">
            {{ $t("general.title") }}
            <v-icon v-if="sortField === 'name'" end size="large">
              {{ sortIcon }}
            </v-icon>
          </v-btn>
        </th>
        <th :aria-sort="ariaSort('category')">
          <v-btn variant="text" size="large" @click="sortBy('category')">
            {{ $t("category.categories") }}
            <v-icon v-if="sortField === 'category'" end size="large">
              {{ sortIcon }}
            </v-icon>
          </v-btn>
        </th>
        <th :aria-sort="ariaSort('rating')">
          <v-btn variant="text" size="large" @click="sortBy('rating:asc')">
            {{ $t("general.rating") }}
            <v-icon v-if="sortField === 'rating'" end size="large">
              {{ sortIcon }}
            </v-icon>
          </v-btn>
        </th>
      </tr>
    </thead>
    <VueDraggable
      v-model="displayRecipes"
      tag="tbody"
      handle=".recipe-sortable-list__drag-handle"
      :delay="250"
      :delay-on-touch-only="true"
      @end="saveCustomOrder"
    >
      <tr
        v-for="recipe in displayRecipes"
        :key="recipe.id || recipe.slug"
        @click="goToRecipe(recipe)"
      >
        <td>
          <NuxtLink
            class="recipe-sortable-list__link"
            :to="`/g/${groupSlug}/r/${recipe.slug}`"
            draggable="true"
            @dragstart="startRecipeDrag($event, recipe)"
          >
            {{ recipe.name }}
          </NuxtLink>
        </td>
        <td>{{ recipeCategoryLabel(recipe) || "—" }}</td>
        <td>
          <v-rating
            v-if="recipe.rating !== undefined"
            v-model="recipe.rating"
            readonly
            density="compact"
            size="small"
          />
          <span v-else>—</span>
        </td>
      </tr>
    </VueDraggable>
  </v-table>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import type { Recipe } from "~/lib/api/types/recipe";
import { setRecipeDragData } from "~/lib/recipe-drag";
import {
  recipeCategoryLabel,
  type RecipeListSortDirection,
  type RecipeListSortField,
  sortRecipeList,
} from "~/lib/api/user/recipes/recipe-list-order";

interface Props {
  recipes: Recipe[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
  reorder: [recipeIds: string[]];
}>();

const auth = useMealieAuth();
const route = useRoute();
const { $globals } = useNuxtApp();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const sortField = ref<RecipeListSortField>("none");
const sortDirection = ref<RecipeListSortDirection>("asc");
const displayRecipes = ref<Recipe[]>([]);

const sortIcon = computed(() => sortDirection.value === "asc"
  ? $globals.icons.sortAlphabeticalAscending
  : $globals.icons.sortAlphabeticalDescending);

function refreshDisplayRecipes() {
  displayRecipes.value = sortRecipeList(props.recipes, sortField.value, sortDirection.value);
}

watch(
  [() => props.recipes, sortField, sortDirection],
  refreshDisplayRecipes,
  { deep: true, immediate: true },
);

function goToRecipe(recipe: Recipe) {
  location.href = `/g/${groupSlug.value}/r/${recipe.slug}`;
}

function sortBy(field: RecipeListSortField) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
  }
  else {
    sortField.value = field;
    sortDirection.value = "asc";
  }
  refreshDisplayRecipes();
}

function ariaSort(field: RecipeListSortField) {
  if (sortField.value !== field) {
    return "none";
  }
  return sortDirection.value === "asc" ? "ascending" : "descending";
}

function saveCustomOrder() {
  emit(
    "reorder",
    displayRecipes.value
      .map(recipe => recipe.id)
      .filter((id): id is string => Boolean(id)),
  );
}

function startRecipeDrag(event: DragEvent, recipe: Recipe) {
  if (recipe.id) {
    setRecipeDragData(event, { id: recipe.id });
  }
}
</script>

<style scoped>
.recipe-sortable-list__drag-handle:active {
  cursor: grabbing;
}

.recipe-sortable-list__link {
  color: inherit;
  font-weight: 500;
  text-decoration: none;
}

.recipe-sortable-list__link:hover {
  text-decoration: underline;
}
</style>
