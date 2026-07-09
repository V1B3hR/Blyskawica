"""
Tree widget for forest visualization
"""

from rich.tree import Tree as RichTree

from ..base import ThreatType


class TreeWidget:
    """Widget for displaying forest tree structure"""

    def __init__(self, name: str = "Unknown"):
        self.name = name
        self.branches: list[dict[str, any]] = []
        self.threats: list[tuple[ThreatType, str]] = []
        self.health: str = "healthy"

    def add_branch(self, name: str, leaves_count: int = 0):
        """Add a branch to the tree"""
        self.branches.append({"name": name, "leaves": leaves_count})

    def add_threat(self, threat: ThreatType, location: str = ""):
        """Add a threat to the tree"""
        self.threats.append((threat, location))

    def set_health(self, health: str):
        """Set tree health status"""
        self.health = health

    def render_simple(self) -> str:
        """Render simple text representation"""
        status = "🌳" if self.health == "healthy" else "⚠️"
        threat_icons = "".join([t[0].icon for t in self.threats])
        return f"{status} {self.name} {threat_icons if threat_icons else '✅'}"

    def render_rich_tree(self) -> RichTree:
        """Render as Rich Tree structure"""
        # Tree health icon
        if self.health == "healthy":
            tree_icon = "🌳"
            style = "green"
        elif self.health == "warning":
            tree_icon = "⚠️"
            style = "yellow"
        else:
            tree_icon = "🔴"
            style = "red"

        # Create root
        tree = RichTree(f"{tree_icon} [bold {style}]{self.name}[/bold {style}]", guide_style=style)

        # Add trunk info
        trunk = tree.add("🪵 Trunk (OS/Kernel)")

        # Add branches
        if self.branches:
            branches_node = tree.add("🌿 Branches")
            for branch in self.branches:
                branch_text = f"{branch['name']} ({branch['leaves']} leaves)"
                branches_node.add(f"🌿 {branch_text}")

        # Add threats if any
        if self.threats:
            threats_node = tree.add("⚠️ Threats Detected", style="bold red")
            for threat, location in self.threats:
                threat_text = f"{threat.icon} {threat.description}"
                if location:
                    threat_text += f" @ {location}"
                threats_node.add(threat_text)

        return tree

    def __str__(self) -> str:
        return self.render_simple()


def create_forest_map(trees: list[TreeWidget]) -> str:
    """
    Create a simple ASCII forest map

    Args:
        trees: List of tree widgets

    Returns:
        ASCII art forest map
    """
    if not trees:
        return "No trees in forest"

    lines = []

    # Header
    lines.append("FOREST MAP:")
    lines.append("─" * 60)

    # Trees in a row
    tree_displays = []
    for tree in trees:
        status = "🌳" if tree.health == "healthy" else "⚠️"
        threat_icons = "".join([t[0].icon for t in tree.threats[:2]])  # Max 2 threats shown
        tree_displays.append(f"{status} {tree.name[:8]}\n  {threat_icons if threat_icons else '✅'}")

    # Display trees side by side (max 5 per row)
    for i in range(0, len(tree_displays), 5):
        row = tree_displays[i : i + 5]
        lines.append("  ".join(row))
        if i + 5 < len(tree_displays):
            lines.append("")

    return "\n".join(lines)


def render_forest_status(trees_count: int, branches_count: int, leaves_count: int, threats: dict[str, int]) -> str:
    """
    Render forest status summary

    Args:
        trees_count: Number of trees
        branches_count: Number of branches
        leaves_count: Number of leaves
        threats: Dictionary of threat type to count

    Returns:
        Formatted forest status string
    """
    lines = []
    lines.append(f"🌳 Trees: {trees_count} healthy  🌿 Branches: {branches_count}  🍃 Leaves: {leaves_count:,}")

    if threats:
        threat_str = "  ".join([f"{ThreatType[k].icon}x{v} ({k.lower()}s)" for k, v in threats.items() if v > 0])
        if threat_str:
            lines.append(f"⚠️ Threats: {threat_str}")
        else:
            lines.append("✅ No threats detected")
    else:
        lines.append("✅ No threats detected")

    return "\n".join(lines)
