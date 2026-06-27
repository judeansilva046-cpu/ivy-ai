#!/usr/bin/env python3
"""
Ivy AI Plugin CLI Tool
Manage plugins from command line
"""
import click
import json
import os
import shutil
from pathlib import Path
from typing import Optional
import requests
from datetime import datetime

REGISTRY_API = "https://registry.ivyai.dev/api"
PLUGIN_TEMPLATE = """
from app.plugins.base import BasePlugin, PluginMetadata, PluginType

class {class_name}(BasePlugin):
    \"\"\"Your plugin description\"\"\"

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)

    @staticmethod
    def create_metadata() -> PluginMetadata:
        return PluginMetadata(
            name="{plugin_name}",
            version="1.0.0",
            description="Your plugin description",
            author="Your Name",
            plugin_type=PluginType.TOOL,
            entry_point="{class_name}",
            dependencies=[]
        )

    async def initialize(self, config: dict) -> bool:
        \"\"\"Initialize plugin\"\"\"
        return True

    async def execute(self, **kwargs) -> dict:
        \"\"\"Execute plugin\"\"\"
        return {{"success": True, "data": {{}}}}

    async def shutdown(self) -> bool:
        \"\"\"Shutdown plugin\"\"\"
        return True
"""


@click.group()
def cli():
    """Ivy AI Plugin CLI"""
    pass


@cli.command()
@click.argument('name')
def create(name: str):
    """Create a new plugin"""
    click.echo(f"🔌 Creating plugin: {name}")

    plugin_dir = Path(f"plugins/{name}")
    if plugin_dir.exists():
        click.echo(f"❌ Plugin directory already exists: {plugin_dir}")
        return

    # Create directory structure
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "src").mkdir()
    (plugin_dir / "tests").mkdir()

    # Create main plugin file
    class_name = "".join(word.capitalize() for word in name.split("_"))
    plugin_content = PLUGIN_TEMPLATE.format(
        class_name=class_name,
        plugin_name=name
    )

    (plugin_dir / "src" / "plugin.py").write_text(plugin_content)

    # Create __init__.py
    (plugin_dir / "src" / "__init__.py").write_text(
        f"from .plugin import {class_name}\n\n__all__ = ['{class_name}']\n"
    )

    # Create tests
    (plugin_dir / "tests" / "test_plugin.py").write_text(f"""
import pytest
from src.plugin import {class_name}
from app.plugins.base import PluginMetadata

@pytest.mark.asyncio
async def test_{name}_initialization():
    metadata = {class_name}.create_metadata()
    plugin = {class_name}(metadata)
    assert await plugin.initialize({{}}) is True

@pytest.mark.asyncio
async def test_{name}_execution():
    metadata = {class_name}.create_metadata()
    plugin = {class_name}(metadata)
    await plugin.initialize({{}})
    result = await plugin.execute()
    assert result["success"] is True
""")

    # Create plugin.json
    plugin_config = {{
        "name": name,
        "version": "1.0.0",
        "description": "Your plugin description",
        "author": "Your Name",
        "license": "MIT",
        "repository": "https://github.com/yourusername/ivy-{name}",
        "keywords": ["ivy-ai", "plugin"],
        "homepage": f"https://github.com/yourusername/ivy-{name}",
        "main": "src/plugin.py",
        "entry_point": class_name,
        "dependencies": [],
        "permissions": [],
        "metadata": {{
            "category": "tool",
            "tags": ["example"],
            "icon": "https://example.com/icon.png"
        }}
    }}

    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_config, indent=2))

    # Create README
    (plugin_dir / "README.md").write_text(f"""
# {name.replace("_", " ").title()} Plugin

Your plugin description

## Installation

```bash
ivy plugin install {name}
```

## Usage

```python
from {name} import {class_name}

plugin = {class_name}()
await plugin.initialize({{}})
result = await plugin.execute()
```

## Configuration

Configure your plugin in `plugin.json`

## License

MIT
""")

    click.echo(f"✅ Plugin created: {plugin_dir}")
    click.echo(f"📁 Structure:")
    click.echo(f"   {plugin_dir}/src/plugin.py")
    click.echo(f"   {plugin_dir}/tests/")
    click.echo(f"   {plugin_dir}/plugin.json")
    click.echo(f"   {plugin_dir}/README.md")


@cli.command()
@click.option('--path', default='.', help='Plugin directory')
def build(path: str):
    """Build plugin"""
    click.echo(f"🔨 Building plugin from {path}")

    plugin_dir = Path(path)
    plugin_config_path = plugin_dir / "plugin.json"

    if not plugin_config_path.exists():
        click.echo(f"❌ plugin.json not found in {path}")
        return

    with open(plugin_config_path) as f:
        config = json.load(f)

    plugin_name = config.get('name')
    plugin_version = config.get('version')

    # Build
    dist_dir = plugin_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()

    # Copy files
    shutil.copytree(plugin_dir / "src", dist_dir / "src")
    shutil.copy(plugin_config_path, dist_dir / "plugin.json")
    shutil.copy(plugin_dir / "README.md", dist_dir / "README.md")

    # Create package
    package_name = f"{plugin_name}-{plugin_version}.tar.gz"
    shutil.make_archive(
        str(dist_dir / plugin_name),
        'gztar',
        dist_dir
    )

    click.echo(f"✅ Plugin built: {package_name}")
    click.echo(f"📦 Package: {dist_dir / package_name}")


@cli.command()
@click.option('--path', default='.', help='Plugin directory')
@click.option('--token', envvar='IVY_API_TOKEN', help='API token')
def publish(path: str, token: str):
    """Publish plugin to registry"""
    click.echo(f"📤 Publishing plugin from {path}")

    if not token:
        click.echo("❌ API token required (set IVY_API_TOKEN)")
        return

    plugin_dir = Path(path)
    plugin_config_path = plugin_dir / "plugin.json"

    if not plugin_config_path.exists():
        click.echo(f"❌ plugin.json not found")
        return

    with open(plugin_config_path) as f:
        config = json.load(f)

    # Prepare payload
    payload = {
        "name": config.get('name'),
        "version": config.get('version'),
        "description": config.get('description'),
        "author": config.get('author'),
        "license": config.get('license'),
        "repository": config.get('repository'),
        "keywords": config.get('keywords', []),
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{REGISTRY_API}/plugins/publish",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 201:
            result = response.json()
            click.echo(f"✅ Plugin published!")
            click.echo(f"   URL: {result.get('url')}")
            click.echo(f"   ID: {result.get('id')}")
        else:
            click.echo(f"❌ Publish failed: {response.text}")

    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.option('--path', default='.', help='Plugin directory')
def test(path: str):
    """Test plugin"""
    click.echo(f"🧪 Testing plugin from {path}")

    plugin_dir = Path(path)
    tests_dir = plugin_dir / "tests"

    if not tests_dir.exists():
        click.echo(f"❌ tests directory not found")
        return

    # Run pytest
    import subprocess
    result = subprocess.run(
        ["pytest", str(tests_dir), "-v"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        click.echo(f"❌ Tests failed")
    else:
        click.echo(f"✅ Tests passed")


@cli.command()
@click.option('--query', default='', help='Search query')
@click.option('--category', default='', help='Filter by category')
@click.option('--limit', default=10, help='Results limit')
def search(query: str, category: str, limit: int):
    """Search plugins in registry"""
    click.echo(f"🔍 Searching plugins: {query or 'all'}")

    try:
        params = {
            'q': query,
            'category': category,
            'limit': limit
        }

        response = requests.get(
            f"{REGISTRY_API}/plugins/search",
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            plugins = response.json()
            if not plugins:
                click.echo("No plugins found")
                return

            click.echo(f"\n📦 Found {len(plugins)} plugin(s):\n")
            for plugin in plugins:
                click.echo(f"  {plugin['name']} v{plugin['version']}")
                click.echo(f"    {plugin['description']}")
                click.echo(f"    By: {plugin['author']}")
                click.echo()
        else:
            click.echo(f"❌ Search failed: {response.text}")

    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.argument('name')
@click.option('--version', default='latest', help='Plugin version')
def install(name: str, version: str):
    """Install plugin"""
    click.echo(f"📥 Installing {name}@{version}")

    try:
        response = requests.get(
            f"{REGISTRY_API}/plugins/{name}/download",
            params={'version': version},
            timeout=30
        )

        if response.status_code == 200:
            # Save plugin
            plugins_dir = Path("plugins")
            plugins_dir.mkdir(exist_ok=True)

            plugin_file = plugins_dir / f"{name}.tar.gz"
            with open(plugin_file, 'wb') as f:
                f.write(response.content)

            click.echo(f"✅ Plugin installed: {plugin_file}")
        else:
            click.echo(f"❌ Installation failed: {response.text}")

    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
def list():
    """List installed plugins"""
    click.echo("📦 Installed plugins:\n")

    plugins_dir = Path("plugins")
    if not plugins_dir.exists():
        click.echo("No plugins installed")
        return

    for plugin_file in plugins_dir.glob("*.tar.gz"):
        click.echo(f"  {plugin_file.stem}")


if __name__ == '__main__':
    cli()
