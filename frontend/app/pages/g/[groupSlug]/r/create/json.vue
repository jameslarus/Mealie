<template>
  <div>
    <v-card-title class="headline">
      {{ $t("recipe.bulk-json-import") }}
    </v-card-title>
    <v-card-text>
      <p>{{ $t("recipe.bulk-json-import-description") }}</p>
      <p>
        {{ $t("recipe.json-import-format-description-colon") }}
        <a href="https://schema.org/Recipe" target="_blank" class="text-primary">https://schema.org/Recipe</a>
      </p>

      <div class="d-flex align-center flex-wrap ga-2 mt-6">
        <AppButtonUpload
          accept=".json,application/json,.jpg,.jpeg,image/jpeg,.png,image/png,.gif,image/gif"
          :text="$t('recipe.select-json-files')"
          :text-btn="false"
          :post="false"
          :multiple="true"
          :disabled="state.loading"
          @uploaded="selectFiles"
        />
        <BaseButton v-if="selectedFiles.length" delete :disabled="state.loading" @click="clearFiles">
          {{ $t("general.clear") }}
        </BaseButton>
      </div>

      <p v-if="selectedFiles.length" class="mt-4 mb-2">
        {{ $t("recipe.selected-json-files-count", { count: selectedFiles.length }) }}
      </p>
      <v-list v-if="selectedFiles.length" density="compact" class="mb-4">
        <v-list-item
          v-for="file in selectedFiles"
          :key="file.name"
          :title="`${file.name} - ${file.size} bytes - ${new Date(file.lastModified).toLocaleString()}`"
        >
          <template #prepend>
            <v-icon>{{ $globals.icons.codeJson }}</v-icon>
          </template>
        </v-list-item>
      </v-list>

      <v-checkbox
        v-model="importKeywordsAsTags"
        color="primary"
        hide-details
        :disabled="state.loading"
        :label="$t('recipe.import-original-keywords-as-tags')"
      />
      <v-checkbox
        v-model="importCategories"
        color="primary"
        hide-details
        :disabled="state.loading"
        :label="$t('recipe.import-original-categories')"
      />
    </v-card-text>

    <v-card-actions class="justify-center">
      <div style="width: 250px">
        <BaseButton
          rounded
          block
          :loading="state.loading"
          :disabled="!selectedFiles.length || state.loading"
          @click="importFiles"
        >
          {{ $t("recipe.import-json-files") }}
        </BaseButton>
      </div>
    </v-card-actions>

    <section class="mt-12 px-4">
      <BaseCardSectionTitle :title="$t('recipe.bulk-imports')" />
      <ReportTable :items="reports" @delete="deleteReport" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { alert } from "~/composables/use-toast";
import type { ReportSummary } from "~/lib/api/types/reports";

const state = reactive({ loading: false });
const selectedFiles = ref<File[]>([]);
const reports = ref<ReportSummary[]>([]);

const api = useUserApi();
const i18n = useI18n();
const { importKeywordsAsTags, importCategories } = useNewRecipeOptions({
  enableImportKeywords: true,
  enableImportCategories: true,
  enableStayInEditMode: false,
  enableParseRecipe: false,
});

function selectFiles(payload: File | File[] | unknown | null) {
  if (Array.isArray(payload)) {
    selectedFiles.value = payload;
  }
}

function clearFiles() {
  selectedFiles.value = [];
}

async function importFiles() {
  if (!selectedFiles.value.length || state.loading) return;

  state.loading = true;
  try {
    const inputs = await Promise.all(selectedFiles.value.map(async file => ({
      data: await file.text(),
      file_name: file.name,
      include_tags: importKeywordsAsTags.value,
      include_categories: importCategories.value,
    })));
    const { response } = await api.recipes.createManyByHtmlOrJson({
      inputs: inputs,
    });

    if (response?.status !== 202) throw new Error("Bulk JSON import request failed");

    alert.success(i18n.t("recipe.bulk-import-process-has-started"));
    clearFiles();
    await fetchReports();
  }
  catch (error) {
    console.error(error);
    alert.error(i18n.t("recipe.bulk-import-process-has-failed"));
  }
  finally {
    state.loading = false;
  }
}

async function fetchReports() {
  const { data } = await api.groupReports.getAll("bulk_import");
  reports.value = data ?? [];
}

async function deleteReport(id: string) {
  const { response } = await api.groupReports.deleteOne(id);
  if (response?.status === 200) {
    await fetchReports();
  }
  else {
    alert.error(i18n.t("recipe.report-deletion-failed"));
  }
}

fetchReports();
</script>
