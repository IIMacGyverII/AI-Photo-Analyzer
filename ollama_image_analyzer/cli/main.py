"""Command-line interface for Ollama Image Analyzer.

Provides a powerful CLI for batch processing images with Ollama vision models.
"""

import logging
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from ollama_image_analyzer.core import (
    Config,
    OllamaAnalyzer,
    PromptManager,
    get_config,
)
from ollama_image_analyzer.core.logging_config import setup_logging

# Create Typer app
app = typer.Typer(
    name="ollama-image-analyzer",
    help="Modern CLI for analyzing images with Ollama vision models",
    add_completion=False,
)

console = Console()
logger = logging.getLogger(__name__)


@app.command()
def analyze(
    images: List[Path] = typer.Argument(
        ...,
        help="Image files to analyze (supports wildcards)",
        exists=True,
        dir_okay=False,
    ),
    host: Optional[str] = typer.Option(
        None,
        "--host",
        "-h",
        help="Ollama server URL (e.g., http://192.168.1.100:11434)",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Vision model to use (e.g., llava, moondream, bakllava)",
    ),
    prompt: Optional[Path] = typer.Option(
        None,
        "--prompt",
        "-p",
        help="Path to custom prompt file",
        exists=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for results (default: same as image)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all output except errors",
    ),
    no_overwrite: bool = typer.Option(
        False,
        "--no-overwrite",
        help="Create numbered versions (_1, _2) instead of overwriting existing files",
    ),
) -> None:
    """
    Analyze one or more images using Ollama vision models.
    
    Examples:
    
        # Analyze a single image
        ollama-image-analyzer analyze photo.jpg
        
        # Batch process with custom settings
        ollama-image-analyzer analyze *.jpg --model llava --output-dir ./results
        
        # Use remote Ollama server
        ollama-image-analyzer analyze image.png --host http://192.168.1.100:11434
        
        # Custom prompt
        ollama-image-analyzer analyze photo.jpg --prompt prompts/custom.txt
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.WARNING if quiet else logging.INFO
    setup_logging(level=log_level, console=not quiet)

    # Load configuration
    config = get_config()
    
    # Use CLI args or fall back to config
    ollama_host = host or config.ollama_host
    ollama_model = model or config.ollama_model
    
    # Initialize components
    prompt_manager = PromptManager()
    analyzer = OllamaAnalyzer(
        host=ollama_host,
        model=ollama_model,
        timeout=config.timeout_seconds,
    )

    # Load prompt
    try:
        if prompt:
            analysis_prompt = prompt_manager.load_prompt(prompt)
        else:
            analysis_prompt = prompt_manager.get_current_prompt()
    except Exception as e:
        console.print(f"[red]Error loading prompt: {e}[/red]")
        raise typer.Exit(1)

    # Test connection
    if not quiet:
        console.print(f"[cyan]Connecting to Ollama at {ollama_host}...[/cyan]")
    
    if not analyzer.test_connection():
        console.print(f"[red]Failed to connect to Ollama server at {ollama_host}[/red]")
        console.print("[yellow]Make sure Ollama is running and the host/port are correct.[/yellow]")
        raise typer.Exit(1)

    if not quiet:
        console.print(f"[green]✓[/green] Connected to Ollama")
        console.print(f"[cyan]Using model:[/cyan] {ollama_model}")
        console.print(f"[cyan]Processing {len(images)} image(s)[/cyan]\n")

    # Process images
    success_count = 0
    error_count = 0
    results_table = Table(title="Analysis Results" if not quiet else None, show_header=True)
    results_table.add_column("Image", style="cyan")
    results_table.add_column("Status", style="bold")
    results_table.add_column("Output", style="dim")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("[cyan]Analyzing images...", total=len(images))

        for image_path in images:
            # Filter out non-image files
            if not analyzer.is_supported_image(image_path):
                if not quiet:
                    console.print(f"[yellow]Skipping unsupported file: {image_path.name}[/yellow]")
                progress.advance(task)
                continue
            
            # Check if output file exists when overwrite protection is enabled
            if no_overwrite:
                if output_dir:
                    output_path = output_dir / f"{image_path.stem}.txt"
                else:
                    output_path = image_path.with_suffix(".txt")
                
                if output_path.exists():
                    if not quiet:
                        console.print(f"[yellow]Skipping {image_path.name} - output file already exists[/yellow]")
                    progress.advance(task)
                    continue

            progress.update(task, description=f"[cyan]Analyzing {image_path.name}...")
            
            # Analyze image
            result = analyzer.analyze_image(image_path, analysis_prompt)

            if result.success:
                # Determine output path
                if output_dir:
                    output_path = output_dir / f"{image_path.stem}.txt"
                else:
                    output_path = image_path.with_suffix(".txt")

                # Save result
                try:
                    saved_path = analyzer.save_result(result, output_path, overwrite=not no_overwrite)
                    success_count += 1
                    results_table.add_row(
                        image_path.name,
                        "[green]✓ Success[/green]",
                        str(saved_path.relative_to(Path.cwd()) if saved_path.is_relative_to(Path.cwd()) else saved_path)
                    )
                except ValueError as e:
                    # Validation error
                    error_count += 1
                    results_table.add_row(
                        image_path.name,
                        "[red]✗ Validation failed[/red]",
                        str(e)
                    )
                except Exception as e:
                    error_count += 1
                    results_table.add_row(
                        image_path.name,
                        "[red]✗ Save failed[/red]",
                        str(e)
                    )
            else:
                error_count += 1
                results_table.add_row(
                    image_path.name,
                    "[red]✗ Analysis failed[/red]",
                    result.error or "Unknown error"
                )

            progress.advance(task)

    # Display results
    if not quiet:
        console.print()
        console.print(results_table)
        console.print()
        
        # Summary panel
        summary = f"[green]✓ {success_count} succeeded[/green]"
        if error_count > 0:
            summary += f"  [red]✗ {error_count} failed[/red]"
        
        console.print(Panel(summary, title="Summary", border_style="cyan"))

    # Exit with error code if any failed
    if error_count > 0:
        raise typer.Exit(1)


@app.command()
def models(
    host: Optional[str] = typer.Option(
        None,
        "--host",
        "-h",
        help="Ollama server URL",
    ),
) -> None:
    """List available vision models from Ollama server."""
    config = get_config()
    ollama_host = host or config.ollama_host

    console.print(f"[cyan]Connecting to Ollama at {ollama_host}...[/cyan]")
    
    analyzer = OllamaAnalyzer(host=ollama_host)
    
    if not analyzer.test_connection():
        console.print(f"[red]Failed to connect to Ollama server at {ollama_host}[/red]")
        raise typer.Exit(1)

    try:
        all_models = analyzer.list_models()
        vision_models = analyzer.get_vision_models()

        console.print(f"\n[green]✓[/green] Connected to Ollama\n")
        
        # Display vision models
        if vision_models:
            table = Table(title="Vision Models", show_header=True)
            table.add_column("Model Name", style="cyan")
            table.add_column("Type", style="dim")
            
            for model in vision_models:
                table.add_row(model, "Vision")
            
            console.print(table)
        
        # Display all models if different
        if set(all_models) != set(vision_models):
            console.print(f"\n[dim]Total models available: {len(all_models)}[/dim]")
            console.print(f"[dim]Use 'ollama list' to see all models[/dim]")

    except Exception as e:
        console.print(f"[red]Error fetching models: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config_show() -> None:
    """Show current configuration."""
    config = get_config()
    
    table = Table(title="Current Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Ollama Host", config.ollama_host)
    table.add_row("Ollama Model", config.ollama_model)
    table.add_row("Prompt File", config.prompt_file)
    table.add_row("Output Directory", config.output_directory or "[dim]Same as image[/dim]")
    table.add_row("Timeout", f"{config.timeout_seconds}s")
    table.add_row("Config File", str(config.config_file))
    
    console.print(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
    ),
) -> None:
    """Ollama Image Analyzer - Analyze images with AI vision models."""
    if version:
        from ollama_image_analyzer import __version__
        console.print(f"Ollama Image Analyzer v{__version__}")
        raise typer.Exit(0)
    
    # If no command specified, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
