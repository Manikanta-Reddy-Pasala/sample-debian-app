"""Jinja2 template rendering utilities."""

import os
from jinja2 import Environment, FileSystemLoader, Template


class TemplateRenderer:
    """Handles rendering of Jinja2 templates."""

    def __init__(self, template_dir: str):
        """
        Initialize template renderer.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render_template(self, template_name: str, context: dict) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: Name of the template file
            context: Dictionary of template variables

        Returns:
            Rendered template as string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_to_file(self, template_name: str, output_path: str, context: dict):
        """
        Render a template and write to file.

        Args:
            template_name: Name of the template file
            output_path: Path where rendered content will be written
            context: Dictionary of template variables
        """
        content = self.render_template(template_name, context)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
