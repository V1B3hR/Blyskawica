"""
Forest View Screen - Detailed forest visualization
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..base import UIColors
from ..widgets.tree_widget import TreeWidget


class ForestViewScreen:
    """Screen for detailed forest visualization"""

    def __init__(self):
        self.trees: list[TreeWidget] = []
        self.selected_tree: int = 0

    def add_tree(self, tree: TreeWidget):
        """Add a tree to the forest"""
        self.trees.append(tree)

    def set_trees(self, trees: list[TreeWidget]):
        """Set all trees"""
        self.trees = trees

    def select_tree(self, index: int):
        """Select a tree by index"""
        if 0 <= index < len(self.trees):
            self.selected_tree = index

    def next_tree(self):
        """Select next tree"""
        if self.trees:
            self.selected_tree = (self.selected_tree + 1) % len(self.trees)

    def prev_tree(self):
        """Select previous tree"""
        if self.trees:
            self.selected_tree = (self.selected_tree - 1) % len(self.trees)

    def render_overview(self) -> Panel:
        """Render forest overview"""
        if not self.trees:
            return Panel(
                Text("No trees in forest", style=UIColors.DIM), title="FOREST OVERVIEW", border_style=UIColors.FOREST
            )

        text = Text()

        # Statistics
        healthy = sum(1 for t in self.trees if t.health == "healthy")
        total_threats = sum(len(t.threats) for t in self.trees)
        total_branches = sum(len(t.branches) for t in self.trees)

        text.append(f"🌳 Trees: {len(self.trees)} ({healthy} healthy)\n", style=UIColors.FOREST)
        text.append(f"🌿 Branches: {total_branches}\n", style=UIColors.FOREST)
        text.append(f"⚠️ Threats: {total_threats}", style=UIColors.WARNING if total_threats > 0 else UIColors.SAFE)

        return Panel(text, title="FOREST OVERVIEW", border_style=UIColors.FOREST, padding=(0, 1))

    def render_tree_list(self) -> Panel:
        """Render list of trees"""
        if not self.trees:
            return Panel(Text("No trees", style=UIColors.DIM), title="TREES", border_style=UIColors.FOREST)

        text = Text()

        for i, tree in enumerate(self.trees):
            selected = "► " if i == self.selected_tree else "  "
            status = "🌳" if tree.health == "healthy" else "⚠️"
            threat_count = len(tree.threats)
            threat_text = f" ({threat_count} threats)" if threat_count > 0 else ""

            line = f"{selected}{status} {tree.name}{threat_text}\n"

            if i == self.selected_tree:
                text.append(line, style="bold " + UIColors.HIGHLIGHT)
            else:
                text.append(line, style=UIColors.TEXT)

        return Panel(text, title="TREES", border_style=UIColors.FOREST, padding=(0, 1))

    def render_selected_tree(self) -> Panel:
        """Render details of selected tree"""
        if not self.trees or self.selected_tree >= len(self.trees):
            return Panel(
                Text("No tree selected", style=UIColors.DIM), title="TREE DETAILS", border_style=UIColors.FOREST
            )

        tree = self.trees[self.selected_tree]

        # Use the rich tree widget
        return Panel(
            tree.render_rich_tree(), title=f"TREE DETAILS - {tree.name}", border_style=UIColors.FOREST, padding=(0, 1)
        )

    def render(self, console: Console):
        """Render the complete forest view screen"""
        console.clear()

        # Title
        console.print(
            Panel(
                Text("🌳 FOREST VIEW - Infrastructure Map", justify="center", style="bold"),
                border_style=UIColors.BORDER,
            )
        )
        console.print()

        # Overview
        console.print(self.render_overview())
        console.print()

        # Tree list (left) and details (right)
        from rich.columns import Columns

        console.print(Columns([self.render_tree_list(), self.render_selected_tree()]))
        console.print()

        # Controls
        console.print("[↑/↓] Navigate    [ENTER] Details    [T] Target    [B] Back", style=UIColors.DIM)
