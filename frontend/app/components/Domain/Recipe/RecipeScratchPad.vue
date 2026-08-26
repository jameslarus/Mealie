<template>
  <section
    class="recipe-scratchpad mx-2 mb-2 rounded"
    :class="{ 'recipe-scratchpad--drop-target': dragDepth > 0 }"
    @dragenter.prevent="dragDepth++"
    @dragleave.prevent="dragDepth = Math.max(0, dragDepth - 1)"
    @dragover.prevent
    @drop.prevent="onDrop"
  >
    <v-divider class="mb-1" />
    <v-list-subheader class="font-weight-bold">
      <v-icon start size="small">
        {{ $globals.icons.clipboardCheck }}
      </v-icon>
      {{ $t("sidebar.scratchpad") }}
    </v-list-subheader>

    <div v-if="loading" class="d-flex justify-center py-3">
      <v-progress-circular indeterminate size="24" />
    </div>

    <VueDraggable
      v-else-if="scratchPadRecipes.length"
      v-model="scratchPadRecipes"
      handle=".recipe-scratchpad__handle"
      :delay="250"
      :delay-on-touch-only="true"
      @end="saveOrder"
    >
      <v-list-item
        v-for="item in scratchPadRecipes"
        :key="item.recipeId"
        :to="`/g/${groupSlug}/r/${item.recipe.slug}`"
        density="compact"
        class="px-1"
      >
        <template #prepend>
          <v-icon class="recipe-scratchpad__handle mr-1" size="small">
            {{ $globals.icons.arrowUpDown }}
          </v-icon>
        </template>
        <v-list-item-title>{{ item.recipe.name }}</v-list-item-title>
        <template #append>
          <v-btn
            :aria-label="$t('recipe.remove-from-scratchpad')"
            :title="$t('recipe.remove-from-scratchpad')"
            :icon="$globals.icons.close"
            size="x-small"
            variant="text"
            @click.prevent.stop="remove(item.recipeId)"
          />
        </template>
      </v-list-item>
    </VueDraggable>

    <div v-else class="text-caption text-medium-emphasis text-center px-3 pb-3">
      {{ $t("recipe.drag-recipes-to-scratchpad") }}
    </div>
  </section>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { useUserScratchPad } from "~/composables/use-users";
import { getRecipeDragData } from "~/lib/recipe-drag";

const auth = useMealieAuth();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const dragDepth = ref(0);
const { scratchPadRecipes, loading, add, reorder, remove } = useUserScratchPad();

async function onDrop(event: DragEvent) {
  dragDepth.value = 0;
  const recipe = getRecipeDragData(event);
  if (recipe) {
    await add(recipe.id);
  }
}

async function saveOrder() {
  await reorder(scratchPadRecipes.value.map(item => item.recipeId));
}
</script>

<style scoped>
.recipe-scratchpad {
  border: 1px solid transparent;
  min-height: 5rem;
  transition:
    background-color 120ms ease,
    border-color 120ms ease;
}

.recipe-scratchpad--drop-target {
  background-color: rgb(var(--v-theme-primary), 0.12);
  border-color: rgb(var(--v-theme-primary));
}

.recipe-scratchpad__handle {
  cursor: grab;
}

.recipe-scratchpad__handle:active {
  cursor: grabbing;
}
</style>
