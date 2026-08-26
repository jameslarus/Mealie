import { describe, expect, test } from "vitest";
import {
  getRecipeDragData,
  MEALIE_RECIPE_DRAG_TYPE,
  setRecipeDragData,
} from "~/lib/recipe-drag";

function dragEventWithDataTransfer(): DragEvent {
  const values = new Map<string, string>();

  return {
    dataTransfer: {
      effectAllowed: "uninitialized",
      setData(type: string, value: string) {
        values.set(type, value);
      },
      getData(type: string) {
        return values.get(type) ?? "";
      },
    },
  } as unknown as DragEvent;
}

describe("recipe drag data", () => {
  test("round-trips a recipe identifier", () => {
    const event = dragEventWithDataTransfer();

    setRecipeDragData(event, { id: "recipe-id" });

    expect(event.dataTransfer?.effectAllowed).toBe("copy");
    expect(
      event.dataTransfer?.getData(MEALIE_RECIPE_DRAG_TYPE),
    ).toBe("{\"id\":\"recipe-id\"}");
    expect(getRecipeDragData(event)).toEqual({ id: "recipe-id" });
  });

  test("rejects malformed or unrelated drag data", () => {
    const event = dragEventWithDataTransfer();

    event.dataTransfer?.setData(
      MEALIE_RECIPE_DRAG_TYPE,
      "not-json",
    );

    expect(getRecipeDragData(event)).toBeNull();

    const unrelatedEvent = dragEventWithDataTransfer();
    unrelatedEvent.dataTransfer?.setData(
      "text/plain",
      "recipe-id",
    );

    expect(getRecipeDragData(unrelatedEvent)).toBeNull();
  });
});
