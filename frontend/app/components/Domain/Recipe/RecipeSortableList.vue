<template>
  <v-table class="RecipeSortableList" hover>
    <thead>
      <tr>
        <th class="RecipeSortableList__handle" />
        <th v-if="!props.useFixedList" :aria-sort="ariaSort('name')">
          <v-btn variant="text" class="px-0" @click="sortBy('name')">
            {{ $t("general.title") }}
            <v-icon v-if="sortField === 'name'" end size="small">
              {{ sortIcon }}
            </v-icon>
          </v-btn>
        </th>
        <th v-else>
          <span variant="text" class="px-0">
            {{ $t("general.title") }}
          </span>
        </th>
        <th v-if="!props.useFixedList" :aria-sort="ariaSort('category')">
          <v-btn variant="text" class="px-0" @click="sortBy('category')">
            {{ $t("category.category") }}
            <v-icon v-if="sortField === 'category'" end size="small">
              {{ sortIcon }}
            </v-icon>
          </v-btn>
        </th>
        <th v-else>
          <span variant="text" class="px-0">
            {{ $t("category.category") }}
          </span>
        </th>
      </tr>
    </thead>
    <VueDraggable
      v-model="displayRecipes"
      tag="tbody"
      handle=".RecipeSortableList__drag-handle"
      :delay="250"
      :delay-on-touch-only="true"
      @end="saveCustomOrder"
    >
      <tr
        v-for="recipe in displayRecipes"
        :key="recipe.id || recipe.slug"
      >
        <td class="RecipeSortableList__handle">
          <v-icon
            v-if="props.useFixedList"
            class="RecipeSortableList__drag-handle"
            :aria-label="$t('general.reorder')"
            tabindex="0"
          >
            {{ $globals.icons.arrowUpDown }}
          </v-icon>
        </td>
        <td>
          <NuxtLink
            class="RecipeSortableList__link"
            :to="`/g/${groupSlug}/r/${recipe.slug}`"
          >
            {{ recipe.name }}
          </NuxtLink>
        </td>
        <td>{{ recipeCategoryLabel(recipe) || "—" }}</td>
      </tr>
    </VueDraggable>
  </v-table>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import type { Recipe } from "~/lib/api/types/recipe";
import {
  applyManualRecipeOrder,
  recipeCategoryLabel,
  sortRecipeList,
  type RecipeListSortDirection,
  type RecipeListSortField,
} from "~/lib/api/user/recipes/recipe-list-order";

interface Props {
  recipes: Recipe[];
  useFixedList: boolean;
  manualOrder: string[];
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
  displayRecipes.value = props.useFixedList
    ? applyManualRecipeOrder(props.recipes, props.manualOrder)
    : sortRecipeList(props.recipes, sortField.value, sortDirection.value);
}

watch(
  [() => props.recipes, () => props.useFixedList, () => props.manualOrder],
  refreshDisplayRecipes,
  { deep: true, immediate: true },
);

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
</script>

<style scoped>
.RecipeSortableList__handle {
  width: 3rem;
}

.RecipeSortableList__drag-handle {
  cursor: grab;
}

.RecipeSortableList__drag-handle:active {
  cursor: grabbing;
}

.RecipeSortableList__link {
  color: inherit;
  font-weight: 500;
  text-decoration: none;
}

.RecipeSortableList__link:hover {
  text-decoration: underline;
}
</style>
