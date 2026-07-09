"""
🦅 Sky View - Bird's Eye Perspective

Visual representation of the forest from above
"""

from typing import Any


def render_sky_view(forest_data: dict[str, Any], bird_status: dict[str, Any]) -> str:
    """
    Render ASCII art sky view of the forest

    Args:
        forest_data: Forest state data
        bird_status: Bird fleet status

    Returns:
        ASCII art representation
    """
    trees = forest_data.get("trees", [])
    threats = forest_data.get("threats", {})
    overall_health = forest_data.get("overall_health", 1.0)

    # Get bird positions
    eagle_active = bird_status.get("fleet_composition", {}).get("eagle", 0) > 0
    falcons_active = bird_status.get("fleet_composition", {}).get("falcons", 0)
    owls_active = bird_status.get("fleet_composition", {}).get("owls", 0)

    view = []
    view.append("╔═══════════════════════════════════════════════════════════════════════╗")
    view.append("║  🦅 EYE IN THE SKY - FOREST OVERVIEW                      [🔴 LIVE]   ║")
    view.append("╠═══════════════════════════════════════════════════════════════════════╣")
    view.append("║                                                                       ║")

    # Bird status section
    view.append("║  BIRDS ON PATROL:                            FOREST STATUS:           ║")
    view.append("║  ┌─────────────────────────┐               ┌─────────────────────┐   ║")

    eagle_status = "[SOARING]   " if eagle_active else "[OFFLINE]   "
    view.append(f"║  │ 🦅 Eagle    {eagle_status}│               │ 🌳 Trees:   {len(trees):2d} total  │   ║")

    falcon_status = f"[HUNTING x{falcons_active}]" if falcons_active else "[OFFLINE]   "
    health_pct = f"{overall_health*100:5.1f}%"
    view.append(f"║  │ 🦅 Falcon   {falcon_status}│               │ 💚 Health: {health_pct}     │   ║")

    owl_status = f"[WATCHING x{owls_active}]" if owls_active else "[OFFLINE]    "
    crow_count = threats.get("crows", 0)
    view.append(f"║  │ 🦉 Owl      {owl_status}│               │ 🐦‍⬛ Crows:   {crow_count:2d}       │   ║")

    total_threats = sum(threats.values())
    view.append(f"║  └─────────────────────────┘               │ ⚠️  Threats: {total_threats:2d}       │   ║")
    view.append("║                                            └─────────────────────┘   ║")
    view.append("║                                                                       ║")

    # Sky view visualization
    view.append("║  SKY VIEW - THREAT MAP:                                               ║")
    view.append("║  ┌───────────────────────────────────────────────────────────────┐   ║")
    view.append("║  │                          ☁️ ☁️ ☁️                              │   ║")

    if eagle_active:
        view.append("║  │                      🦅                                       │   ║")
        view.append("║  │            ╱ ╲          ← Eagle soaring                      │   ║")
    else:
        view.append("║  │                                                               │   ║")
        view.append("║  │                      (Eagle offline)                          │   ║")

    if falcons_active:
        view.append("║  │           ╱   ╲              🦅 ← Falcon patrolling             │   ║")
    else:
        view.append("║  │           ╱   ╲                                                │   ║")

    view.append("║  │          ╱     ╲                                                 │   ║")

    # Tree visualization
    tree_line = "║  │    🌳────🌳────🌳────🌳────🌳────🌳                          │   ║"
    view.append(tree_line)

    # Threat indicators on trees
    threat_indicators = []
    for i, tree in enumerate(trees[:6]):  # Show max 6 trees
        tree_threats = tree.get("threats", [])
        if tree_threats:
            threat_type = tree_threats[0].get("type", "unknown")
            if "crow" in threat_type or "malware" in threat_type:
                threat_indicators.append((i, "🐦‍⬛"))
            elif "squirrel" in threat_type:
                threat_indicators.append((i, "🐿️"))
            else:
                threat_indicators.append((i, "⚠️"))

    # Create threat line
    threat_line = "║  │    "
    for i in range(6):
        has_threat = any(t[0] == i for t in threat_indicators)
        if has_threat:
            emoji = next(t[1] for t in threat_indicators if t[0] == i)
            threat_line += f"│{emoji}  "
        else:
            threat_line += "││   "

    threat_line += "                           │   ║"
    view.append(threat_line)

    # Tree labels
    tree_labels = []
    for i, tree in enumerate(trees[:6]):
        tree_labels.append(tree.get("name", f"Tree{i+1}")[:6].ljust(6))

    label_line = "║  │   " + "".join(tree_labels) + "                      │   ║"
    view.append(label_line)

    view.append("║  └───────────────────────────────────────────────────────────────┘   ║")
    view.append("║                                                                       ║")

    # Controls
    view.append("║  [E]🦅Eagle View  [F]🦅Falcon Hunt  [O]🦉Owl Night  [T]🌳Tree Detail  ║")
    view.append("╚═══════════════════════════════════════════════════════════════════════╝")

    return "\n".join(view)


def render_mini_sky_view(tree_count: int, threat_count: int, health: float) -> str:
    """
    Render compact sky view

    Args:
        tree_count: Number of trees
        threat_count: Number of threats
        health: Overall health (0-1)

    Returns:
        Compact ASCII view
    """
    health_bar = "█" * int(health * 10) + "░" * (10 - int(health * 10))

    view = []
    view.append("     ☁️ ☁️ ☁️")
    view.append("      🦅")
    view.append("    ╱ ╲")
    view.append("   ╱   ╲")
    view.append(f"🌳 🌳 🌳 🌳 🌳  ({tree_count} total)")
    view.append(f"⚠️ Threats: {threat_count}")
    view.append(f"💚 Health: [{health_bar}] {health*100:.0f}%")

    return "\n".join(view)
