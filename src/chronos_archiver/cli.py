"""Command-line interface for ChronosArchiver."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """ChronosArchiver - Archive websites from the Wayback Machine."""
    pass


@cli.command()
@click.argument("urls", nargs=-1)
@click.option("--input", "-i", type=click.Path(exists=True), help="File with URLs (one per line)")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--workers", "-w", default=4, help="Number of workers")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def archive(urls: tuple, input: Optional[str], config: Optional[str], workers: int, output: Optional[str]) -> None:
    """Archive URLs from the Wayback Machine.

    Examples:
        chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
        chronos archive --input urls.txt --workers 8
        chronos archive --config custom_config.yaml --input urls.txt
    """
    # Load configuration
    config_dict = load_config(config) if config else load_config()

    # Override output directory if specified
    if output:
        config_dict["archive"]["output_dir"] = output

    # Collect URLs
    url_list = list(urls)
    if input:
        with open(input, "r") as f:
            url_list.extend(line.strip() for line in f if line.strip())

    if not url_list:
        click.echo("Error: No URLs provided. Use arguments or --input file.", err=True)
        sys.exit(1)

    click.echo(f"Archiving {len(url_list)} URLs with {workers} workers...")

    # Run archiver
    archiver = ChronosArchiver(config_dict)

    async def run():
        try:
            await archiver.archive_urls(url_list)
            click.echo("✓ Archiving complete!")
        except KeyboardInterrupt:
            click.echo("\n⚠ Interrupted by user")
            await archiver.shutdown()
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            await archiver.shutdown()
            sys.exit(1)

    asyncio.run(run())


@cli.group()
def workers() -> None:
    """Manage background workers."""
    pass


@workers.command()
@click.option("--count", "-c", default=4, help="Number of workers to start")
@click.option("--config", type=click.Path(exists=True), help="Configuration file")
def start(count: int, config: Optional[str]) -> None:
    """Start background workers for async processing.

    Examples:
        chronos workers start --count 8
        chronos workers start --config custom_config.yaml
    """
    config_dict = load_config(config) if config else load_config()
    archiver = ChronosArchiver(config_dict)

    click.echo(f"Starting {count} workers...")

    async def run():
        try:
            await archiver.start_workers(count)
            click.echo("✓ Workers started. Press Ctrl+C to stop.")
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            click.echo("\n⚠ Shutting down workers...")
            await archiver.shutdown()
            click.echo("✓ Workers stopped")

    asyncio.run(run())


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
def init(config: Optional[str]) -> None:
    """Initialize a new ChronosArchiver project.

    Creates necessary directories and configuration files.
    """
    # Create directories
    dirs = ["archive", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        click.echo(f"✓ Created directory: {dir_name}/")

    # Create config if it doesn't exist
    config_path = Path(config) if config else Path("config.yaml")
    if not config_path.exists():
        # Copy example config
        example_config = Path(__file__).parent.parent.parent / "config.yaml.example"
        if example_config.exists():
            import shutil
            shutil.copy(example_config, config_path)
            click.echo(f"✓ Created configuration file: {config_path}")
        else:
            click.echo(f"⚠ Example config not found, please create {config_path} manually")
    else:
        click.echo(f"⚠ Configuration already exists: {config_path}")

    click.echo("\n✓ Initialization complete!")
    click.echo("\nNext steps:")
    click.echo("  1. Edit config.yaml to customize settings")
    click.echo("  2. Start Redis: redis-server")
    click.echo("  3. Run: chronos archive <url>")


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
def validate_config(config: Optional[str]) -> None:
    """Validate configuration file."""
    try:
        config_dict = load_config(config)
        click.echo("✓ Configuration is valid")
        click.echo(f"\nLoaded settings:")
        click.echo(f"  Output directory: {config_dict['archive']['output_dir']}")
        click.echo(f"  Queue backend: {config_dict['queue']['backend']}")
        click.echo(f"  Workers: {config_dict['processing']['workers']}")
    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()