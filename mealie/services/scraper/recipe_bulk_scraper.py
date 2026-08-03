import asyncio
from base64 import b64decode

from pydantic import UUID4

from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import CreateRecipeByDataBulk, CreateRecipeByUrlBulk, Recipe
from mealie.schema.reports.reports import (
    ReportCategory,
    ReportCreate,
    ReportEntryCreate,
    ReportEntryOut,
    ReportSummaryStatus,
)
from mealie.schema.user.user import GroupInDB
from mealie.services._base_service import BaseService
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.scraper.scraped_extras import ScrapedExtras, ScraperContext
from mealie.services.scraper.scraper import create_from_html, create_from_html_bulk
from mealie.services.scraper.scraper_strategies import RecipeScraperPackage


class RecipeBulkScraperService(BaseService):
    report_entries: list[ReportEntryCreate]

    def __init__(
        self, service: RecipeService, repos: AllRepositories, group: GroupInDB, translator: Translator
    ) -> None:
        self.service = service
        self.repos = repos
        self.group = group
        self.report_entries = []
        self.translator = translator

        super().__init__()

    def get_report_id(self, name: str = "Bulk Import") -> UUID4:
        import_report = ReportCreate(
            name=name,
            category=ReportCategory.bulk_import,
            status=ReportSummaryStatus.in_progress,
            group_id=self.group.id,
        )

        self.report = self.repos.group_reports.create(import_report)
        return self.report.id

    def _add_error_entry(self, message: str, exception: str = "") -> None:
        self.report_entries.append(
            ReportEntryCreate(
                report_id=self.report.id,
                success=False,
                message=message,
                exception=exception,
            )
        )

    def _save_all_entries(self) -> None:
        is_success = True
        is_failure = True

        new_entries: list[ReportEntryOut] = []
        for entry in self.report_entries:
            if is_failure and entry.success:
                is_failure = False

            if is_success and not entry.success:
                is_success = False

            new_entries.append(self.repos.group_report_entries.create(entry))

        if is_success:
            self.report.status = ReportSummaryStatus.success

        if is_failure:
            self.report.status = ReportSummaryStatus.failure

        if not is_success and not is_failure:
            self.report.status = ReportSummaryStatus.partial

        self.report.entries = new_entries
        self.repos.group_reports.update(self.report.id, self.report)

    async def scrape(self, urls: CreateRecipeByUrlBulk) -> None:
        sem = asyncio.Semaphore(3)

        async def _do(url: str) -> Recipe | None:
            async with sem:
                try:
                    recipe, _ = await create_from_html(url, self.repos, self.translator)
                    return recipe
                except Exception as e:
                    self.service.logger.error(f"failed to scrape url during bulk url import {url}")
                    self.service.logger.exception(e)
                    self._add_error_entry(f"failed to scrape url {url}", str(e))
                    return None

        if self.report is None:
            self.get_report_id()
        tasks = [_do(b.url) for b in urls.imports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for b, recipe in zip(urls.imports, results, strict=True):
            if not recipe or isinstance(recipe, BaseException):
                continue

            if b.tags:
                recipe.tags = b.tags

            if b.categories:
                recipe.recipe_category = b.categories

            try:
                self.service.create_one(recipe)
            except Exception as e:
                self.service.logger.error(f"Failed to save recipe to database during bulk url import {b.url}")
                self.service.logger.exception(e)
                self._add_error_entry(f"Failed to save recipe to database during bulk url import {b.url}", str(e))
                continue

            self.report_entries.append(
                ReportEntryCreate(
                    report_id=self.report.id,
                    success=True,
                    message=f"Successfully imported recipe {recipe.name}",
                    exception="",
                )
            )

        self._save_all_entries()

    async def scrape_data_bulk(self, bulk: CreateRecipeByDataBulk) -> None:
        sem = asyncio.Semaphore(3)

        async def _do(file_name: str, data: str) -> tuple[Recipe, ScrapedExtras | None] | None:
            async with sem:
                try:
                    if file_name.lower().endswith(".json"):
                        decoded_data = b64decode(data).decode("utf-8")
                        stripped_data = decoded_data.lstrip()
                        html = (
                            RecipeScraperPackage.ld_json_to_html(stripped_data)
                            if stripped_data.startswith("{")
                            else decoded_data
                        )
                        recipe, extras = await create_from_html_bulk("", self.repos, self.translator, html, bulk)
                        return recipe, extras
                    else:
                        return None
                except Exception as e:
                    self.service.logger.error(f"Failed to parse recipe from bulk import file {file_name}")
                    self.service.logger.exception(e)
                    self._add_error_entry(f"Failed to import {file_name}", str(e))
                    return None

        if self.report is None:
            self.get_report_id("Bulk JSON Import")

        tasks = [_do(item.file_name, item.data) for item in bulk.inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for item, result in zip(bulk.inputs, results, strict=True):
            if not result or isinstance(result, BaseException):
                continue

            recipe, extras = result
            ctx = ScraperContext(self.repos)
            if item.include_tags and extras:
                recipe.tags = extras.use_tags(ctx)
            if item.include_categories and extras:
                recipe.recipe_category = extras.use_categories(ctx)

            try:
                self.service.create_one(recipe)
            except Exception as e:
                self.service.logger.error(f"Failed to save recipe from bulk import file {item.file_name}")
                self.service.logger.exception(e)
                self._add_error_entry(f"Failed to import {item.file_name}", str(e))
                continue

            self.report_entries.append(
                ReportEntryCreate(
                    report_id=self.report.id,
                    success=True,
                    message=f"Successfully imported {item.file_name} as {recipe.name}",
                    exception="",
                )
            )

        self._save_all_entries()
