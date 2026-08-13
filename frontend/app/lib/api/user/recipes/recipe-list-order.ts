import type { Recipe } from "~/lib/api/types/recipe";

export type RecipeListSortField = "none" | "name" | "category";
export type RecipeListSortDirection = "asc" | "desc";

const collator = new Intl.Collator(undefined, { sensitivity: "base", numeric: true });

export function recipeCategoryLabel(recipe: Recipe): string {
  return (recipe.recipeCategory ?? [])
    .map(category => category.name?.trim() ?? "")
    .filter(Boolean)
    .sort(collator.compare)
    .join(", ");
}

export function sortRecipeList(
  recipes: Recipe[],
  field: RecipeListSortField,
  direction: RecipeListSortDirection,
): Recipe[] {
  const multiplier = direction === "asc" ? 1 : -1;

  return [...recipes].sort((left, right) => {
    const leftValue = field === "name" ? left.name ?? "" : recipeCategoryLabel(left);
    const rightValue = field === "name" ? right.name ?? "" : recipeCategoryLabel(right);
    const comparison = collator.compare(leftValue, rightValue);

    if (comparison !== 0) {
      return comparison * multiplier;
    }

    return collator.compare(left.name ?? "", right.name ?? "");
  });
}

export function applyManualRecipeOrder(recipes: Recipe[], orderedIds: string[]): Recipe[] {
  const positions = orderedIds ? new Map(orderedIds.map((id, index) => [id, index])) : new Map();

  return recipes
    .map((recipe, index) => ({ recipe, index }))
    .sort((left, right) => {
      const leftPosition = left.recipe.id ? positions.get(left.recipe.id) : undefined;
      const rightPosition = right.recipe.id ? positions.get(right.recipe.id) : undefined;

      if (leftPosition !== undefined && rightPosition !== undefined) {
        return leftPosition - rightPosition;
      }
      if (leftPosition !== undefined) {
        return -1;
      }
      if (rightPosition !== undefined) {
        return 1;
      }
      return left.index - right.index;
    })
    .map(({ recipe }) => recipe);
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
