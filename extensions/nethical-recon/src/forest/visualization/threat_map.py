"""
🗺️ Threat Map - Visual Threat Distribution

Shows threat locations and types across the forest
"""

from typing import Any


def render_threat_map(forest_data: dict[str, Any]) -> str:
    """
    Render threat distribution map

    Args:
        forest_data: Forest state data

    Returns:
        ASCII threat map
    """
    trees = forest_data.get("trees", [])
    threats = forest_data.get("threats", {})

    map_view = []
    map_view.append("╔═══════════════════════════════════════════════════════════════╗")
    map_view.append("║  🗺️  THREAT MAP - Distribution Across Forest                 ║")
    map_view.append("╠═══════════════════════════════════════════════════════════════╣")
    map_view.append("║                                                               ║")

    # Threat legend
    map_view.append("║  LEGEND:                                                      ║")
    map_view.append("║  🐦‍⬛ Crow (Malware)    🐿️ Squirrel (Lateral)                  ║")
    map_view.append("║  🐛 Parasite (Miner)  🦇 Bat (Night Attack)                   ║")
    map_view.append("║  🐍 Snake (Rootkit)   ✅ Clean                                ║")
    map_view.append("║                                                               ║")
    map_view.append("║  THREAT DISTRIBUTION:                                         ║")
    map_view.append("║  ┌─────────────────────────────────────────────────────────┐ ║")

    # Show each tree with its threats
    for tree in trees[:10]:  # Max 10 trees
        tree_name = tree.get("name", "unknown")[:15].ljust(15)
        tree_health = tree.get("health", 1.0)
        tree_threats = tree.get("threats", [])

        # Health indicator
        if tree_health > 0.8:
            health_emoji = "💚"
        elif tree_health > 0.5:
            health_emoji = "💛"
        else:
            health_emoji = "❤️"

        # Threat icons
        threat_icons = []
        for threat in tree_threats[:3]:  # Max 3 threats shown
            threat_type = threat.get("type", "unknown")
            if "crow" in threat_type or "malware" in threat_type:
                threat_icons.append("🐦‍⬛")
            elif "squirrel" in threat_type:
                threat_icons.append("🐿️")
            elif "parasite" in threat_type:
                threat_icons.append("🐛")
            elif "bat" in threat_type:
                threat_icons.append("🦇")
            elif "snake" in threat_type or "rootkit" in threat_type:
                threat_icons.append("🐍")
            else:
                threat_icons.append("⚠️")

        if not threat_icons:
            threat_icons = ["✅"]

        threat_str = " ".join(threat_icons[:3])
        health_pct = f"{tree_health*100:3.0f}%"

        line = f"║  │  🌳 {tree_name} {health_emoji} {health_pct}  {threat_str.ljust(12)} │ ║"
        map_view.append(line)

    map_view.append("║  └─────────────────────────────────────────────────────────┘ ║")
    map_view.append("║                                                               ║")

    # Threat summary
    map_view.append("║  THREAT SUMMARY:                                              ║")
    map_view.append("║  ┌─────────────────────────────────────────────────────────┐ ║")

    crow_count = threats.get("crows", 0)
    squirrel_count = threats.get("squirrels", 0)
    parasite_count = threats.get("parasites", 0)
    bat_count = threats.get("bats", 0)
    total = sum(threats.values())

    map_view.append(f"║  │  🐦‍⬛ Crows (Malware):        {crow_count:3d}                        │ ║")
    map_view.append(f"║  │  🐿️ Squirrels (Lateral):     {squirrel_count:3d}                        │ ║")
    map_view.append(f"║  │  🐛 Parasites (Miners):      {parasite_count:3d}                        │ ║")
    map_view.append(f"║  │  🦇 Bats (Night Attacks):    {bat_count:3d}                        │ ║")
    map_view.append("║  │  ────────────────────────────────────────────────────── │ ║")
    map_view.append(f"║  │  ⚠️  TOTAL THREATS:          {total:3d}                        │ ║")
    map_view.append("║  └─────────────────────────────────────────────────────────┘ ║")
    map_view.append("║                                                               ║")
    map_view.append("╚═══════════════════════════════════════════════════════════════╝")

    return "\n".join(map_view)


def render_simple_threat_map(threats: dict[str, int]) -> str:
    """
    Render simple threat count visualization

    Args:
        threats: Dictionary of threat counts

    Returns:
        Simple ASCII visualization
    """
    total = sum(threats.values())

    lines = []
    lines.append("🗺️  THREAT MAP")
    lines.append("═" * 30)
    lines.append(f"🐦‍⬛ Crows:     {threats.get('crows', 0):3d} {'█' * threats.get('crows', 0)}")
    lines.append(f"🐿️ Squirrels:  {threats.get('squirrels', 0):3d} {'█' * threats.get('squirrels', 0)}")
    lines.append(f"🐛 Parasites:  {threats.get('parasites', 0):3d} {'█' * threats.get('parasites', 0)}")
    lines.append(f"🦇 Bats:       {threats.get('bats', 0):3d} {'█' * threats.get('bats', 0)}")
    lines.append("─" * 30)
    lines.append(f"⚠️  TOTAL:     {total:3d}")

    return "\n".join(lines)
