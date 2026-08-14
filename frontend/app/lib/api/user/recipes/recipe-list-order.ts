import type { Recipe } from "~/lib/api/types/recipe";

export type RecipeListSortField = "none" | "name" | "category" | "rating";
export type RecipeListSortDirection = "asc" | "desc";

const collator = new Intl.Collator(undefined, { sensitivity: "base", numeric: true });

export function recipeName(recipe: Recipe): string {
  return recipe.name ?? "";
}

export function recipeCategoryLabel(recipe: Recipe): string {
  return (recipe.recipeCategory ?? [])
    .map(category => category.name?.trim() ?? "")
    .filter(Boolean)
    .sort(collator.compare)
    .join(", ");
}

export function recipeRating(recipe: Recipe): number {
  return recipe.rating ?? 0;
}

export function recipeSortValue(recipe: Recipe, field: RecipeListSortField): string {
  switch (field) {
    case "name":
      return recipeName(recipe);
    case "category":
      return recipeCategoryLabel(recipe);
    case "rating":
      return String(recipeRating(recipe));
    default:
      return "";
  }
}

export function sortRecipeList(
  recipes: Recipe[],
  field: RecipeListSortField,
  direction: RecipeListSortDirection,
): Recipe[] {
  const multiplier = direction === "asc" ? 1 : -1;

  return [...recipes].sort((left, right) => {
    const leftValue = recipeSortValue(left, field);
    const rightValue = recipeSortValue(right, field);
    const comparison = collator.compare(leftValue, rightValue);

    if (comparison !== 0) {
      return comparison * multiplier;
    }

    return collator.compare(left.name ?? "", right.name ?? "");
  });
}

export function mergeVisibleRecipeOrder(savedIds: string[], visibleIds: string[]): string[] {
  const visibleSet = new Set(visibleIds);
  const visibleQueue = [...visibleIds];
  const merged = savedIds.map(id => visibleSet.has(id) ? visibleQueue.shift()! : id);
  const mergedSet = new Set(merged);

  for (const id of visibleQueue) {
    if (!mergedSet.has(id)) {
      merged.push(id);
      mergedSet.add(id);
    }
  }

  return merged;
}
