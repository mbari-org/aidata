# mbari_aidata, Apache-2.0 license
# Filename: __main__.py
# Description: Main entry point for the mbari_aidata command line interface
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import click

from mbari_aidata import __version__

if "LOG_PATH" not in locals():
    LOG_PATH = Path.home().as_posix()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version", message="%(prog)s, version %(version)s")
def cli():
    """
    Load data to tator database from a command line.
    """
    pass


class LazyGroup(click.Group):
    """A click Group that imports commands lazily on first access"""
    
    def __init__(self, *args, lazy_subcommands=None, **kwargs):
        super().__init__(*args, **kwargs)
        # lazy_subcommands is a dict of {command_name: module_path.function_name}
        self.lazy_subcommands = lazy_subcommands or {}
        
    def get_command(self, ctx, cmd_name):
        # First check if already loaded
        if cmd_name in self.commands:
            return self.commands[cmd_name]
            
        # Check if it's a lazy command we need to import
        if cmd_name in self.lazy_subcommands:
            import_path = self.lazy_subcommands[cmd_name]
            module_name, func_name = import_path.rsplit('.', 1)
            
            # Import the module and get the command
            import importlib
            module = importlib.import_module(module_name)
            cmd = getattr(module, func_name)
            
            # Add it to the group
            self.add_command(cmd, cmd_name)
            return cmd
            
        return None
    
    def list_commands(self, ctx):
        # Return all commands including lazy ones
        return sorted(list(self.commands.keys()) + list(self.lazy_subcommands.keys()))


@click.group(name="load", cls=LazyGroup, lazy_subcommands={
    'images': 'mbari_aidata.commands.load_images.load_images',
    'video': 'mbari_aidata.commands.load_video.load_video',
    'boxes': 'mbari_aidata.commands.load_boxes.load_boxes',
    'tracks': 'mbari_aidata.commands.load_tracks.load_tracks',
    'queue': 'mbari_aidata.commands.load_queue.load_queue',
    'exemplars': 'mbari_aidata.commands.load_exemplars.load_exemplars',
    'clusters': 'mbari_aidata.commands.load_clusters.load_clusters',
})
def cli_load():
    """
    Load data, such as images, boxes, and exemplars into either a Postgres or REDIS database
    """
    pass


cli.add_command(cli_load)


@click.group(name="download", cls=LazyGroup, lazy_subcommands={
    'dataset': 'mbari_aidata.commands.download.download',
})
def cli_download():
    """
    Download data, such as images, boxes, into various formats for machine learning e,g, COCO, CIFAR, or PASCAL VOC format
    """
    pass


cli.add_command(cli_download)


@click.group(name="db", cls=LazyGroup, lazy_subcommands={
    'reset-redis': 'mbari_aidata.commands.db_utils.reset_redis',
})
def cli_db():
    """
    Commands related to database management
    """
    pass


cli.add_command(cli_db)


@click.group(name="transform", cls=LazyGroup, lazy_subcommands={
    'voc': 'mbari_aidata.commands.transform.transform',
    'voc-to-yolo': 'mbari_aidata.commands.transform.voc_to_yolo',
    'split': 'mbari_aidata.commands.split.split_command',
})
def cli_transform():
    """
    Commands related to transforming downloaded data
    """
    pass


cli.add_command(cli_transform)

if __name__ == "__main__":
    try:
        # Import these only when actually running the CLI, not when importing for testing
        from datetime import datetime
        import pytz
        from mbari_aidata.logger import err, info
        
        start = datetime.now(pytz.utc)
        cli()
        end = datetime.now(pytz.utc)
        info(f"Done. Elapsed time: {end - start} seconds")
    except Exception as e:
        # Import err here too in case it wasn't imported above
        try:
            from mbari_aidata.logger import err
        except ImportError:
            import sys
            print(f"Exiting. Error: {e}", file=sys.stderr)
        else:
            err(f"Exiting. Error: {e}")
        exit(-1)
