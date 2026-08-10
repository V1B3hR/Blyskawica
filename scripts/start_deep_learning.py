import argparse
import os
import sys
import time

from adaptiveneuralnetwork.core.assimilation_chain import AssimilationChain


def main():
    parser = argparse.ArgumentParser(description="Run Deep Non-linear Learning session")
    parser.add_argument("--max-steps", type=int, default=1000, help="Maximum steps to run")
    parser.add_argument("--target", type=float, default=80.0, help="Mastery target (%%) to stop at")

    args = parser.parse_args()

    chain = AssimilationChain()
    track_path = os.path.join(os.path.dirname(chain.matrix_path), "tracking.md")

    print(f"⚡ [BŁYSKAWICA] Initiating Deep Non-linear Learning Mode (Limit: {args.max_steps} steps, Target: {args.target}%)...")
    print(f"Tracking progress at: {track_path}")
    print("-" * 50)

    steps = 0

    try:
        while steps < args.max_steps:
            message = chain.simulate_step()
            print(f"[{time.strftime('%H:%M:%S')}] Step {steps+1}: {message}")

            # Every 5 steps, sync to markdown
            if steps % 5 == 0:
                chain.sync_to_tracking_md(track_path)

            stats = chain.get_overall_stats()
            if stats['overall_mastery'] >= args.target:
                print(f"!!! [{args.target}% MASTERY REACHED] READY FOR SINGULARITY AUDIT !!!")
                break

            steps += 1
            time.sleep(0.05) # Even faster

        # Final sync
        chain.sync_to_tracking_md(track_path)
        print("-" * 50)
        final_stats = chain.get_overall_stats()
        print("Deep Learning Session Complete.")
        print(f"Final Global Mastery: {final_stats['overall_mastery']:.2f}%")

    except KeyboardInterrupt:
        print("\nLearning paused by Architect.")
        chain.sync_to_tracking_md(track_path)

if __name__ == "__main__":
    # Ensure UTF-8
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    main()
