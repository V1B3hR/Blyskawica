"""
Demo for Phase 7.2: MAML-style Meta-Learning in a Neuromorphic System.

This demo showcases how the FewShotLearningSystem can adapt to new tasks 
using gradient-through-gradient (MAML) updates.
"""  # noqa: W291

import logging

import torch

from adaptiveneuralnetwork.applications.few_shot_learning import (
    FewShotLearningConfig,
    FewShotLearningSystem,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_episode(n_way=5, k_shot=1, query_size=15, feature_dim=784):
    """Generate a synthetic few-shot classification episode."""
    # Support set
    support_x = torch.randn(n_way * k_shot, feature_dim)
    support_y = torch.tensor([i for i in range(n_way) for _ in range(k_shot)], dtype=torch.long)

    # Query set (same classes, different noise)
    query_x = support_x.repeat(query_size, 1) + torch.randn(n_way * query_size, feature_dim) * 0.1
    query_y = torch.tensor([i for i in range(n_way) for _ in range(query_size)], dtype=torch.long)

    return support_x, support_y, query_x, query_y

def run_meta_learning_demo():
    logger.info("Starting Phase 7.2 Meta-Learning Demo (MAML mode)")

    config = FewShotLearningConfig(
        n_way=5,
        k_shot=1,
        query_size=5,
        input_size=784,
        feature_dim=64,
        meta_learning_mode='maml',
        inner_loop_steps=5,
        inner_lr=0.01,
        meta_learning_rate=0.001
    )

    model = FewShotLearningSystem(config)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.meta_learning_rate)

    # Initial evaluation
    logger.info("Evaluating initial model (before meta-learning)...")
    s_x, s_y, q_x, q_y = generate_synthetic_episode(config.n_way, config.k_shot, config.query_size, config.input_size)
    initial_stats = model.evaluate_episode(s_x, s_y, q_x, q_y)
    logger.info(f"Initial Accuracy: {initial_stats['accuracy']:.3f}, Loss: {initial_stats['loss']:.3f}")

    # Meta-training loop
    num_episodes = 50
    logger.info(f"Running meta-training for {num_episodes} episodes...")

    for i in range(num_episodes):
        s_x, s_y, q_x, q_y = generate_synthetic_episode(config.n_way, config.k_shot, config.query_size, config.input_size)

        stats = model.meta_learn_maml(s_x, s_y, q_x, q_y, optimizer)

        if (i+1) % 10 == 0:
             load_val = model.cognitive_load.item()
             logger.info(f"Episode {i+1}/{num_episodes} - Meta-Loss: {stats['meta_loss']:.4f}, Accuracy: {stats['accuracy']:.4f}, Load: {load_val:.4f}")

    # Final evaluation
    logger.info("Evaluating final model...")
    s_x, s_y, q_x, q_y = generate_synthetic_episode(config.n_way, config.k_shot, config.query_size, config.input_size)
    final_stats = model.evaluate_episode(s_x, s_y, q_x, q_y)
    logger.info(f"Final Accuracy: {final_stats['accuracy']:.3f}, Loss: {final_stats['loss']:.3f}")

    if final_stats['accuracy'] > initial_stats['accuracy']:
        logger.info("SUCCESS: The model learned how to learn!")
    else:
        logger.warning("The model did not show improved meta-adaptation.")

if __name__ == "__main__":
    run_meta_learning_demo()
