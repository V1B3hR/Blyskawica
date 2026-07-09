import sys
import argparse
from adaptiveneuralnetwork.core.assimilation_chain import AssimilationChain

def main():
    parser = argparse.ArgumentParser(description="Assimilate a node in the Hyper-Synthesis Chain v4.0")
    parser.add_argument("--phase", type=int, required=True, help="Phase index (1-25)")
    parser.add_argument("--node", type=int, required=True, help="Node index (1-25)")
    parser.add_argument("--mastery", type=float, default=100.0, help="Mastery increment (default 100)")
    
    args = parser.parse_args()
    
    chain = AssimilationChain()
    node = chain.get_node(args.phase, args.node)
    
    if not node:
        print(f"Error: Node {args.node} in Phase {args.phase} not found.")
        sys.exit(1)
        
    print(f"Assimilating: FAZA {args.phase} | Node {args.node}: {node['title']}")
    chain.update_mastery(args.phase, args.node, args.mastery)
    
    # Sync with tracking.md
    import os
    track_path = os.path.join(os.path.dirname(chain.matrix_path), "tracking.md")
    chain.sync_to_tracking_md(track_path)
    
    stats = chain.get_overall_stats()
    print(f"Current Global Mastery: {stats['overall_mastery']:.2f}%")
    print(f"Updated tracking at {track_path}")

if __name__ == "__main__":
    main()
