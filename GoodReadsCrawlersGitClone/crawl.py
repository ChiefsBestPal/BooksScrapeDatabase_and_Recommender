import json
import click
from rich.progress import Progress, TaskID, Console, track
from rich.live import Live
from rich.progress import SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from GoodreadsScraper.items import BookItem, AuthorItem


@click.group()
@click.option("--log_file",
              help="Log file for scrapy logs",
              type=str,
              default="scrapy.log",
              show_default=True)
@click.pass_context
def crawl(ctx, log_file="scrapy.log"):
    ctx.ensure_object(dict)
    ctx.obj['LOG_FILE'] = log_file
    ctx.max_content_width = 100
    ctx.show_default = True


@crawl.command()
@click.option("--list_name",
              required=True,
              help="Goodreads Listopia list name.",
              prompt=True,
              type=str)
@click.option("--start_page", help="Start page number", default=1, type=int)
@click.option("--end_page",
              required=True,
              help="End page number",
              prompt=True,
              type=int)
@click.option("--output_file_suffix",
              help="The suffix for the output file. [default: list name]",
              type=str)
@click.pass_context
def list(ctx, list_name: str, start_page: int, end_page: int,
         output_file_suffix: str):
    """Crawl a Goodreads Listopia List.

    Crawl all pages between start_page and end_page (inclusive) of a Goodreads Listopia List.

    \b
    The Listopia list name can be determined from the URL of the list.
    For e.g. the name of the list https://www.goodreads.com/list/show/1.Best_Books_Ever is '1.Best_Books_Ever'

    \b
    By default, two files will be created:
      1.   book_{output_file_suffix}.jl, for books from the given list
      2.   author_{output_file_suffix}.jl, for authors of the above books from the given list
    """
    if not output_file_suffix:
        output_file_suffix = list_name
    click.echo(
        f"Crawling Goodreads list {list_name} for pages [{start_page}, {end_page}]"
    )

    # On Goodreads, each page of a list has about 100 books
    # The last page may have less
    books_per_page = 100
    estimated_no_of_books = (end_page - start_page + 1) * books_per_page

    progress_updater = ProgressUpdater()

    with progress_updater.progress:
        progress_updater.add_task_for(BookItem,
                                      description="[red]Scraping books...",
                                      total=estimated_no_of_books)
        progress_updater.add_task_for(AuthorItem,
                                      description="[green]Scraping authors...",
                                      total=estimated_no_of_books)

        _crawl('list',
               ctx.obj["LOG_FILE"],
               output_file_suffix,
               list_name=list_name,
               start_page_no=start_page,
               end_page_no=end_page,
               item_scraped_callback=progress_updater)


@crawl.command()
@click.option("--output_file_suffix",
              help="The suffix for the output file. Defaults to 'all'",
              type=str)
@click.pass_context
def author(ctx, output_file_suffix='all'):
    """Crawl all authors on Goodreads.

    [IMPORTANT]: This command will only complete after it has crawled
    ALL the authors on Goodreads, which may be a long time.
    For all intents and purposes, treat this command as a never-terminating one
    that will block the command-line forever.

    It is STRONGLY RECOMMENDED that you either terminate it manually (with an interrupt) or
    run it in the background.
    """
    click.echo("Crawling Goodreads for all authors")
    click.echo(
        click.style(
            "[WARNING] This command will block the CLI, and never complete (unless interrupted).\n"
            "Run it in the background if you don't want to block your command line.",
            fg='red'))

    progress_updater = ProgressUpdater(infinite=True)

    with progress_updater.progress:
        progress_updater.add_task_for(AuthorItem,
                                      description="[green]Scraping authors...")

        _crawl('author',
               ctx.obj["LOG_FILE"],
               output_file_suffix,
               author_crawl=True,
               item_scraped_callback=progress_updater)


@crawl.command()
@click.option(
    "--user_id",
    required=True,
    help="The user ID. This can be determined from the URL in your profile, and is of the form '123456-foo-bar'",
    prompt=True,
    type=str)
@click.option("--shelf",
              type=click.Choice(
                  ["read", "to-read", "currently-reading", "all"]),
              help="A shelf from the user's 'My Books' tab.",
              default="all")
@click.option("--output_file_suffix",
              help="The suffix for the output file. [default: user_id]",
              type=str)
@click.pass_context
def my_books(ctx, user_id: str, shelf: str, output_file_suffix: str):
    """Crawl shelves from the "My Books" tab for a user."""
    if not output_file_suffix:
        output_file_suffix = user_id
    click.echo(f"Crawling Goodreads profile {user_id} for shelf {shelf}")

    # On "My Books", each page of has about ~30 books
    # The last page may have less
    # However, we don't know how many total books there could be on a shelf
    # So until we can figure it out, show an infinite spinner
    progress_updater = ProgressUpdater(infinite=True)

    with progress_updater.progress:
        progress_updater.add_task_for(BookItem,
                                    description=f"[red]Scraping books for shelf '{shelf}'...")
        progress_updater.add_task_for(AuthorItem,
                                    description=f"[green]Scraping authors for shelf '{shelf}'...")

        _crawl('mybooks',
            ctx.obj["LOG_FILE"],
            f"{output_file_suffix}",
            user_id=user_id,
            shelf=shelf,
            item_scraped_callback=progress_updater)

@crawl.command()
@click.option("--json_file",
              required=True,
              type=click.Path(exists=True),
              help="Path to JSON file containing book data with 'titles' field.")
@click.option("--language",
              required=False,
              help="Optional language filter (e.g. 'en' for English).")
@click.option("--output_file_suffix",
              default="from_json",
              help="Suffix for output files. [default: 'from_json']")
@click.pass_context
def books_from_json(ctx, json_file, language, output_file_suffix):
    """
    Read a JSON file containing book data (including 'titles'),
    search or parse Goodreads for each title, and scrape details.
    """
    log_file = ctx.obj['LOG_FILE']
    click.echo(
        f"Reading book list from JSON ({json_file}) and scraping Goodreads..."
    )

    # Load JSON
    with open(json_file, "r", encoding="utf-8") as f:
        book_data = json.load(f)

    # Expecting book_data to be a list of entries with at least a "titles" field
    # or "title"
    # e.g. [{"titles": "Pride and Prejudice", "language": "en"}, ... ]
    # Adapt to your actual JSON structure as needed.
    titles_to_search = []
    for entry in book_data:
        # If your JSON uses "titles" (plural), or "title" (singular), adapt as needed:
        if "titles" in entry:
            book_title = entry["titles"][0]
        elif "title" in entry:
            book_title = entry["title"]
        else:
            continue  # or raise an error

        # If there's a language in the entry and a user input language, compare
        if language:
            entry_language = entry.get("language", "")
            if entry_language and entry_language != language:
                continue  # skip books not matching desired language filter

        titles_to_search.append(book_title)

    click.echo(f"Found {len(titles_to_search)} titles to scrape from JSON.")
    if not titles_to_search:
        click.echo("No valid titles found in JSON. Exiting.")
        return

    # Now let's run a specialized spider that:
    # 1) Takes these titles
    # 2) Searches Goodreads (or directly builds the /book/show URLs if you already know them)
    # 3) Yields requests to the BookSpider parse method.

    # Build dynamic spider arguments
    spider_kwargs = {
        "titles_to_search": titles_to_search,
        "desired_language": language
    }

    _crawl("search_spider",  # a new spider name we'll define
           log_file,
           output_file_suffix,
           **spider_kwargs)
    
def   _crawl(spider_name, log_file, output_file_suffix, **crawl_kwargs):
    settings = get_project_settings()

    # used by the JsonLineItem pipeline
    settings.set("OUTPUT_FILE_SUFFIX", output_file_suffix)

    # Emit all scrapy logs to log_file instead of stderr
    settings.set("LOG_FILE", log_file)

    process = CrawlerProcess(settings)

    process.crawl(spider_name, **crawl_kwargs)

    # CLI will block until this call completes
    process.start()


class ProgressUpdater():
    """Callback class for updating the progress on the console.

        Internally, this maintains a map from the item type to a TaskID.
        When the callback is invoked, it tries to find a match for the scraped item,
        and advance the corresponding task progress.
    """

    def __init__(self, infinite=False):
        if infinite:
            self.progress = Progress(
                "[progress.description]{task.description}",
                TimeElapsedColumn(),
                TextColumn("{task.completed} items scraped"), SpinnerColumn())
        else:
            self.progress = Progress(
                "[progress.description]{task.description}", BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(), "/", TimeElapsedColumn())
        self.item_type_to_task = {}

    def add_task_for(self, item_type, *args, **kwargs) -> TaskID:
        task = self.progress.add_task(*args, **kwargs)
        self.item_type_to_task[item_type] = task
        return task

    def __call__(self, item, spider):
        item_type = type(item)
        task = self.item_type_to_task.get(item_type, None)
        if task is not None:
            self.progress.advance(task)


if __name__ == "__main__":
    crawl()
