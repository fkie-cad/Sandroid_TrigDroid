"""Command-line interface implementation for TrigDroid."""

import sys
from typing import Optional, List
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..api import TrigDroidAPI, TestConfiguration, DeviceManager, scan_devices
from ..core.enums import LogLevel
from ..exceptions import TrigDroidError, ConfigurationError, DeviceError

console = Console()


# Main CLI group
@click.group(invoke_without_command=True)
@click.option('-p', '--package', help='Package name to test')
@click.option('-d', '--device', help='Device ID to use')
@click.option('-c', '--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--log-level', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              default='INFO', help='Logging level')
@click.option('--log-file', type=click.Path(), help='Log output file')
@click.option('--suppress-console', is_flag=True, help='Suppress console output')
@click.option('--min-runtime', type=int, default=1, help='Minimum runtime in minutes')
@click.option('--background-time', type=int, default=0, help='Background time in seconds')
@click.option('--acceleration', type=click.IntRange(0, 10), default=0, help='Acceleration sensor level')
@click.option('--gyroscope', type=click.IntRange(0, 10), default=0, help='Gyroscope sensor level')
@click.option('--light', type=click.IntRange(0, 10), default=0, help='Light sensor level')
@click.option('--pressure', type=click.IntRange(0, 10), default=0, help='Pressure sensor level')
@click.option('--battery', type=click.IntRange(0, 4), default=0, help='Battery rotation level')
@click.option('--wifi/--no-wifi', default=None, help='WiFi state')
@click.option('--data/--no-data', default=None, help='Mobile data state')
@click.option('--bluetooth/--no-bluetooth', default=None, help='Bluetooth state')
@click.option('--bluetooth-mac', help='Bluetooth MAC address')
@click.option('--frida/--no-frida', default=False, help='Enable Frida hooks')
@click.option('--install', multiple=True, help='Dummy apps to install')
@click.option('--uninstall', multiple=True, help='Apps to uninstall')
@click.option('--grant-permission', multiple=True, help='Permissions to grant')
@click.option('--revoke-permission', multiple=True, help='Permissions to revoke')
@click.option('--geolocation', help='Geolocation setting')
@click.option('--language', help='System language')
@click.option('--interaction', is_flag=True, help='Enable interaction simulation')
@click.option('--create-config', type=click.Choice(['default', 'interactive']), help='Create configuration file')
@click.option('--create-constants', type=bool, help='Create constants file')
@click.version_option(version='2.0.0', message='TrigDroid %(version)s')
@click.pass_context
def cli(ctx, **kwargs):
    """TrigDroid - Android Sandbox Payload Trigger Framework.
    
    A modern tool for Android security testing and malware analysis.
    Supports both command-line usage and programmatic integration.
    
    Examples:
    
        # Basic test
        trigdroid -p com.example.app
        
        # Advanced test with sensors
        trigdroid -p com.example.app --acceleration 5 --battery 3
        
        # Test with Frida hooks
        trigdroid -p com.example.app --frida --log-level DEBUG
        
        # List available devices
        trigdroid devices
        
        # Create configuration file
        trigdroid --create-config interactive
    """
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj.update(kwargs)
    
    # If no subcommand provided, run main test
    if ctx.invoked_subcommand is None:
        # Handle special commands
        if kwargs.get('create_config'):
            return create_config_file(kwargs['create_config'])
        elif kwargs.get('create_constants') is not None:
            return create_constants_file(kwargs['create_constants'])
        
        # Run main test
        run_test(kwargs)


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed device information')
def devices(verbose):
    """List available Android devices."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning for devices...", total=None)
            device_list = scan_devices()
            progress.remove_task(task)
        
        if not device_list:
            console.print("[red]No Android devices found.[/red]")
            console.print("\nMake sure:")
            console.print("• Android device is connected")
            console.print("• USB debugging is enabled")
            console.print("• ADB is installed and in PATH")
            return
        
        table = Table(title="Available Android Devices")
        table.add_column("Device ID", style="cyan")
        table.add_column("Status", style="green")
        
        if verbose:
            table.add_column("Model")
            table.add_column("Android Version")
        
        for device_info in device_list:
            row = [device_info['id'], device_info['status']]
            if verbose:
                row.extend([
                    device_info.get('model', 'Unknown'),
                    device_info.get('android_version', 'Unknown')
                ])
            table.add_row(*row)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error scanning devices: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('package')
@click.option('--device', '-d', help='Device ID to use')
@click.option('--timeout', type=int, default=30, help='Timeout in seconds')
def info(package, device, timeout):
    """Get information about a package on device."""
    try:
        device_manager = DeviceManager(console)
        android_device = device_manager.connect_to_device(device)
        
        if not android_device:
            console.print(f"[red]Failed to connect to device: {device or 'auto'}[/red]")
            sys.exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(f"Getting info for {package}...", total=None)
            
            installed = android_device.is_app_installed(package)
            progress.remove_task(task)
        
        if not installed:
            console.print(f"[red]Package '{package}' is not installed[/red]")
            return
        
        # Get package information
        result = android_device.execute_command(f"shell dumpsys package {package}")
        if result.success:
            console.print(f"[green]Package '{package}' information:[/green]")
            # Parse and display relevant information
            console.print(result.stdout.decode()[:1000] + "..." if len(result.stdout) > 1000 else result.stdout.decode())
        else:
            console.print(f"[red]Failed to get package information[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path())
@click.pass_context
def test_config(ctx, config_file):
    """Test TrigDroid with configuration file."""
    try:
        config = TestConfiguration.from_yaml_file(config_file)
        
        with TrigDroidAPI(config) as api:
            console.print(f"[green]Testing package: {config.package}[/green]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("Running TrigDroid tests...", total=None)
                result = api.run_tests()
                progress.remove_task(task)
            
            if result.success:
                console.print("[green]✓ Tests completed successfully[/green]")
            else:
                console.print(f"[red]✗ Tests failed: {result.error}[/red]")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def run_test(options):
    """Run TrigDroid test with given options."""
    try:
        # Validate required parameters
        if not options.get('package'):
            console.print("[red]Error: Package name is required[/red]")
            console.print("Use: trigdroid -p <package_name>")
            sys.exit(1)
        
        # Create configuration
        config = TestConfiguration(
            package=options['package'],
            device_id=options.get('device'),
            log_level=LogLevel(options.get('log_level', 'INFO')),
            log_file=options.get('log_file'),
            suppress_console_logs=options.get('suppress_console', False),
            min_runtime=options.get('min_runtime', 1),
            background_time=options.get('background_time', 0),
            acceleration=options.get('acceleration', 0),
            gyroscope=options.get('gyroscope', 0),
            light=options.get('light', 0),
            pressure=options.get('pressure', 0),
            battery_rotation=options.get('battery', 0),
            wifi=options.get('wifi'),
            data=options.get('data'),
            bluetooth=options.get('bluetooth'),
            bluetooth_mac=options.get('bluetooth_mac'),
            frida_hooks=options.get('frida', False),
            install_dummy_apps=list(options.get('install', [])),
            uninstall_apps=list(options.get('uninstall', [])),
            grant_permissions=list(options.get('grant_permission', [])),
            revoke_permissions=list(options.get('revoke_permission', [])),
            geolocation=options.get('geolocation'),
            language=options.get('language'),
            interaction=options.get('interaction', False)
        )
        
        # Validate configuration
        if not config.is_valid():
            console.print("[red]Configuration errors:[/red]")
            for error in config.validation_errors:
                console.print(f"  • {error}")
            sys.exit(1)
        
        # Run test
        console.print(f"[green]Starting TrigDroid test for: {config.package}[/green]")
        
        with TrigDroidAPI(config) as api:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("Running tests...", total=None)
                result = api.run_tests()
                progress.remove_task(task)
            
            if result.success:
                console.print("[green]✓ Tests completed successfully[/green]")
                
                # Show summary
                table = Table(title="Test Summary")
                table.add_column("Parameter", style="cyan")
                table.add_column("Value", style="white")
                
                table.add_row("Package", config.package)
                table.add_row("Runtime", f"{config.min_runtime} minutes")
                table.add_row("Test Phase", result.phase.value)
                
                if config.acceleration > 0:
                    table.add_row("Acceleration", str(config.acceleration))
                if config.gyroscope > 0:
                    table.add_row("Gyroscope", str(config.gyroscope))
                if config.battery_rotation > 0:
                    table.add_row("Battery", str(config.battery_rotation))
                
                console.print(table)
            else:
                console.print(f"[red]✗ Tests failed: {result.error}[/red]")
                sys.exit(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(130)
    except (TrigDroidError, ConfigurationError, DeviceError) as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


def create_config_file(mode):
    """Create a configuration file."""
    console.print(f"[yellow]Creating configuration file in {mode} mode...[/yellow]")
    
    if mode == 'interactive':
        console.print("[blue]Interactive configuration not implemented yet[/blue]")
    else:
        # Create default configuration
        config = TestConfiguration(package="com.example.app")
        config.to_yaml("trigdroid-config.yaml")
        console.print("[green]✓ Created trigdroid-config.yaml with default values[/green]")


def create_constants_file(physical_device):
    """Create a constants file."""
    console.print(f"[yellow]Creating constants file for {'physical device' if physical_device else 'emulator'}...[/yellow]")
    console.print("[blue]Constants file creation not implemented yet[/blue]")


def main():
    """Main entry point for CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()