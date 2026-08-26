export const MEALIE_RECIPE_DRAG_TYPE = "application/x-mealie-recipe";

export interface RecipeDragData {
  id: string;
}

// DataTransfer support for custom MIME types varies between browsers. Keep the
// active recipe in memory as a same-page fallback for the lifetime of the drag.
let activeRecipeDragData: RecipeDragData | null = null;

function parseRecipeDragData(rawValue: string): RecipeDragData | null {
  if (!rawValue) {
    return null;
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<RecipeDragData>;
    return typeof parsed.id === "string" && parsed.id ? { id: parsed.id } : null;
  }
  catch {
    return null;
  }
}

export function setRecipeDragData(event: DragEvent, recipe: RecipeDragData): void {
  activeRecipeDragData = { ...recipe };

  if (!event.dataTransfer) {
    return;
  }

  event.dataTransfer.effectAllowed = "copy";

  // Firefox requires plain text to initiate some drag operations. Set it first
  // so a browser that rejects custom MIME types can still start the drag.
  event.dataTransfer.setData("text/plain", recipe.id);
  try {
    event.dataTransfer.setData(MEALIE_RECIPE_DRAG_TYPE, JSON.stringify(recipe));
  }
  catch {
    // The in-memory value above is the fallback for browsers that reject or
    // strip custom DataTransfer types.
  }
}

export function getRecipeDragData(event: DragEvent): RecipeDragData | null {
  const rawValue = event.dataTransfer?.getData(MEALIE_RECIPE_DRAG_TYPE);
  return parseRecipeDragData(rawValue ?? "") ?? activeRecipeDragData;
}

export function clearRecipeDragData(): void {
  activeRecipeDragData = null;
}
