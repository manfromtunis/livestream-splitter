"""Command-line interface for livestream splitter"""

import click
import logging
from pathlib import Path
from typing import Optional

from .config import Config, OutputConfig, IntroOutroConfig, ProcessingConfig
from .splitter import Splitter
from .utils import parse_time_string

logger = logging.getLogger(__name__)


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '-o', '--output-dir',
    type=click.Path(path_type=Path),
    default='./segments',
    help='Output directory for segments'
)
@click.option(
    '-l', '--max-length',
    default='20m',
    help='Maximum segment length (e.g., 20m, 1200s, 1h30m)'
)
@click.option(
    '--intro',
    type=click.Path(exists=True, path_type=Path),
    help='Path to intro video file'
)
@click.option(
    '--outro',
    type=click.Path(exists=True, path_type=Path),
    help='Path to outro video file'
)
@click.option(
    '-f', '--format',
    default='mp4',
    type=click.Choice(['mp4', 'mkv', 'avi', 'mov']),
    help='Output format for segments'
)
@click.option(
    '--naming-pattern',
    default='{title}_part{index:02d}_{date}',
    help='Naming pattern for output files'
)
@click.option(
    '--quality',
    type=click.Choice(['high', 'medium', 'low']),
    default='high',
    help='Output quality preset'
)
@click.option(
    '--threads',
    type=int,
    default=4,
    help='Number of threads for processing'
)
@click.option(
    '-c', '--config',
    type=click.Path(exists=True, path_type=Path),
    help='Configuration file (YAML or JSON)'
)
@click.option(
    '--save-config',
    type=click.Path(path_type=Path),
    help='Save current configuration to file'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose logging'
)
def main(
    input_file: Path,
    output_dir: Path,
    max_length: str,
    intro: Optional[Path],
    outro: Optional[Path],
    format: str,
    naming_pattern: str,
    quality: str,
    threads: int,
    config: Optional[Path],
    save_config: Optional[Path],
    verbose: bool
):
    """
    Split long livestream recordings into smaller segments.
    
    Example usage:
    
        stream-splitter video.mp4 -o segments/ -l 20m --intro intro.mp4 --outro outro.mp4
    
    The tool will split the input video into segments of maximum 20 minutes each,
    adding the specified intro and outro to each segment.
    """
    
    # Set logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        if config:
            click.echo(f"Loading configuration from: {config}")
            if config.suffix == '.yaml' or config.suffix == '.yml':
                cfg = Config.from_yaml(config)
            elif config.suffix == '.json':
                cfg = Config.from_json(config)
            else:
                raise ValueError(f"Unsupported config format: {config.suffix}")
        else:
            # Build configuration from CLI arguments
            max_length_seconds = parse_time_string(max_length)
            
            cfg = Config(
                input_path=input_file,
                output=OutputConfig(
                    directory=output_dir,
                    format=format,
                    naming_pattern=naming_pattern,
                    max_segment_length=int(max_length_seconds)
                ),
                intro_outro=IntroOutroConfig(
                    intro_path=intro,
                    outro_path=outro
                ),
                processing=ProcessingConfig(
                    quality=quality,
                    threads=threads
                )
            )
        
        # Save configuration if requested
        if save_config:
            if save_config.suffix == '.yaml' or save_config.suffix == '.yml':
                cfg.save_yaml(save_config)
            else:
                cfg.save_json(save_config)
            click.echo(f"Configuration saved to: {save_config}")
        
        # Display processing information
        click.echo(f"Input file: {cfg.input_path}")
        click.echo(f"Output directory: {cfg.output.directory}")
        click.echo(f"Max segment length: {cfg.output.max_segment_length}s")
        
        if cfg.intro_outro.intro_path:
            click.echo(f"Intro: {cfg.intro_outro.intro_path}")
        if cfg.intro_outro.outro_path:
            click.echo(f"Outro: {cfg.intro_outro.outro_path}")
        
        # Create splitter and process
        splitter = Splitter(cfg)
        output_files = splitter.process()
        
        # Generate report
        report_path = splitter.generate_report(output_files)
        
        click.echo("\n" + "="*50)
        click.echo(f"✅ Processing complete!")
        click.echo(f"Created {len(output_files)} segments")
        click.echo(f"Output directory: {cfg.output.directory}")
        click.echo(f"Report: {report_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@click.group()
def cli():
    """Livestream Splitter - Split long videos into smaller segments"""
    pass


@cli.command()
def version():
    """Show version information"""
    from . import __version__
    click.echo(f"Livestream Splitter v{__version__}")


@cli.command()
def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    from .video_processor import VideoProcessor
    
    processor = VideoProcessor()
    if processor.ffmpeg_path:
        click.echo("✅ FFmpeg is installed and accessible")
        
        # Try to get version
        import subprocess
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            version_line = result.stdout.split('\n')[0]
            click.echo(f"Version: {version_line}")
        except Exception:
            pass
    else:
        click.echo("❌ FFmpeg not found. Please install FFmpeg to use this tool.")
        click.echo("Visit https://ffmpeg.org/download.html for installation instructions.")


if __name__ == '__main__':
    main()