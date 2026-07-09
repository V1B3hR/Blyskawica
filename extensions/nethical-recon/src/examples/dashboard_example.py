"""
Dashboard Example - FALA 7: Command Center Demo

This example demonstrates the Tablet Myśliwego (Hunter's Tablet) -
the main command center dashboard for Nethical Hunter.

Usage:
    python examples/dashboard_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.dashboard import Dashboard, create_demo_alerts, create_demo_status
from ui.screens.targeting import Target, TargetingScreen
from ui.widgets.tree_widget import TreeWidget


def demo_main_dashboard():
    """Demonstrate the main dashboard"""
    print("\n" + "=" * 80)
    print("🎯 FALA 7: TABLET MYŚLIWEGO - COMMAND CENTER")
    print("=" * 80 + "\n")

    # Create dashboard
    dashboard = Dashboard()

    # Load demo data
    demo_status = create_demo_status()
    dashboard.update_status(demo_status)

    # Add demo alerts
    for alert in create_demo_alerts():
        dashboard.add_alert(alert)

    print("📱 Main Dashboard View:")
    print("-" * 80)
    dashboard.show()

    return dashboard


def demo_targeting_screen():
    """Demonstrate the targeting screen"""
    print("\n\n" + "=" * 80)
    print("🔫 TARGETING SYSTEM")
    print("=" * 80 + "\n")

    from ui.base import ThreatType

    # Create targeting screen
    targeting = TargetingScreen()

    # Create a demo target
    target = Target(
        ip="192.168.1.105",
        port=4444,
        target_type="SUSPECTED MALWARE C2",
        forest_location={"tree": "web-server-01", "branch": "suspicious-proc", "leaf": "thread-42"},
        threat=ThreatType.CROW,
        confidence=0.87,
        previous_stains=0,
        detected_by="🦅 Falcon (screech alert)",
    )

    targeting.set_target(target)

    # Show targeting screen
    from rich.console import Console

    console = Console()
    targeting.render(console)

    return targeting


def demo_forest_view():
    """Demonstrate the forest view screen"""
    print("\n\n" + "=" * 80)
    print("🌳 FOREST VIEW - Infrastructure Map")
    print("=" * 80 + "\n")

    from ui.base import ThreatType
    from ui.screens.forest_view import ForestViewScreen

    # Create forest view
    forest_view = ForestViewScreen()

    # Create demo trees
    tree1 = TreeWidget("web-server-01")
    tree1.add_branch("nginx-master", 4)
    tree1.add_branch("nginx-worker-1", 12)
    tree1.add_branch("nginx-worker-2", 11)
    tree1.add_threat(ThreatType.CROW, "nginx-worker-1")
    tree1.set_health("warning")

    tree2 = TreeWidget("db-server-01")
    tree2.add_branch("postgresql", 8)
    tree2.add_branch("backup-daemon", 2)
    tree2.set_health("healthy")

    tree3 = TreeWidget("api-server-01")
    tree3.add_branch("flask-app", 6)
    tree3.add_branch("celery-worker", 4)
    tree3.add_threat(ThreatType.SQUIRREL, "flask-app")
    tree3.set_health("warning")

    tree4 = TreeWidget("mail-server-01")
    tree4.add_branch("postfix", 3)
    tree4.set_health("healthy")

    tree5 = TreeWidget("file-server-01")
    tree5.add_branch("samba", 5)
    tree5.add_threat(ThreatType.PARASITE, "samba")
    tree5.set_health("critical")

    forest_view.set_trees([tree1, tree2, tree3, tree4, tree5])

    # Show forest view
    from rich.console import Console

    console = Console()
    forest_view.render(console)

    return forest_view


def demo_stain_report():
    """Demonstrate the stain report screen"""
    print("\n\n" + "=" * 80)
    print("🎨 STAIN REPORT - Hunting Session")
    print("=" * 80 + "\n")

    from ui.screens.stain_report import StainReportScreen

    # Create stain report
    report = StainReportScreen()

    # Set demo statistics
    report.set_statistics(
        {"MALWARE": 3, "EVIL_AI": 1, "SUSPICIOUS_IP": 7, "BACKDOOR": 2, "HIDDEN": 4, "CROW": 5, "SQUIRREL": 2}
    )

    # Set demo forest map
    report.set_forest_map(
        {
            "web-01": ("warning", "🔴"),
            "db-01": ("healthy", "✅"),
            "api-01": ("warning", "🟠"),
            "mail-01": ("healthy", "✅"),
            "file-01": ("warning", "🟡"),
        }
    )

    # Set demo top threats
    report.set_top_threats(
        [
            {
                "detected_by": "🦅",
                "tag": "CRW-trojan-web01",
                "target": "192.168.1.105",
                "score": 9.2,
                "description": "Crow on branch",
            },
            {
                "detected_by": "🦉",
                "tag": "SQR-lateral-api01",
                "target": "internal",
                "score": 8.5,
                "description": "Squirrel jumping",
            },
            {
                "detected_by": "🦅",
                "tag": "MAL-e5f6g7h8",
                "target": "evil.exe",
                "score": 8.8,
                "description": "RAT detected",
            },
        ]
    )

    # Show stain report
    from rich.console import Console

    console = Console()
    report.render(console)

    return report


def demo_settings_screen():
    """Demonstrate the settings screen"""
    print("\n\n" + "=" * 80)
    print("⚙️ SETTINGS - Configuration")
    print("=" * 80 + "\n")

    from ui.screens.settings import SettingsScreen

    # Create settings screen
    settings = SettingsScreen()

    # Show settings
    from rich.console import Console

    console = Console()
    settings.render(console)

    return settings


def interactive_demo():
    """Run an interactive demo"""
    print("\n" + "=" * 80)
    print("🎯 NETHICAL HUNTER COMMAND CENTER - Interactive Demo")
    print("=" * 80 + "\n")

    print("This demo shows different screens of the Command Center:")
    print()
    print("1. Main Dashboard")
    print("2. Targeting System")
    print("3. Forest View")
    print("4. Stain Report")
    print("5. Settings")
    print("6. Exit")
    print()

    while True:
        try:
            choice = input("\nSelect screen (1-6): ").strip()

            if choice == "1":
                demo_main_dashboard()
            elif choice == "2":
                demo_targeting_screen()
            elif choice == "3":
                demo_forest_view()
            elif choice == "4":
                demo_stain_report()
            elif choice == "5":
                demo_settings_screen()
            elif choice == "6":
                print("\n👋 Exiting Command Center Demo\n")
                break
            else:
                print("Invalid choice. Please select 1-6.")

        except KeyboardInterrupt:
            print("\n\n👋 Exiting Command Center Demo\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║  🎯 NETHICAL HUNTER v3.0 - COMMAND CENTER DEMO                            ║
║  FALA 7: TABLET MYŚLIWEGO                                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

This is the central command and control dashboard for Nethical Hunter.
The hunter's tablet - where big decisions are made.

Features:
  • Real-time threat monitoring
  • Sensor and camera status
  • Nanobot swarm control
  • Bird patrol alerts (bird songs)
  • Forest infrastructure mapping
  • Weapon targeting system
  • Stain database reporting
  • Fast, readable, category-organized interface
""")

    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        # Run all demos in sequence
        print("Running demo sequence...\n")
        print("Press Ctrl+C to skip to next demo\n")

        try:
            print("\n[1/5] Main Dashboard...")
            input("Press Enter to continue...")
            demo_main_dashboard()

            print("\n\n[2/5] Targeting System...")
            input("Press Enter to continue...")
            demo_targeting_screen()

            print("\n\n[3/5] Forest View...")
            input("Press Enter to continue...")
            demo_forest_view()

            print("\n\n[4/5] Stain Report...")
            input("Press Enter to continue...")
            demo_stain_report()

            print("\n\n[5/5] Settings...")
            input("Press Enter to continue...")
            demo_settings_screen()

            print("\n\n" + "=" * 80)
            print("✅ Demo Complete!")
            print("=" * 80)
            print("\nTip: Run with --interactive flag for interactive mode:")
            print("     python examples/dashboard_example.py --interactive")
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted\n")


if __name__ == "__main__":
    main()
