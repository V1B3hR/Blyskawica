import tensorflow as tf
import logging

class OnlineLearningModule:
    """
    Adaptive system for incremental learning updates based on real-time user feedback.
    Supports both reinforcement (policy gradient) and corrective (supervised) updates.
    """

    def __init__(self, model: tf.keras.Model, config: dict):
        self.model = model
        self.config = config
        self.optimizer = tf.keras.optimizers.Adam(
            learning_rate=config.get('online_learning_rate', 1e-4)
        )
        self.mi_output_key = config.get("mi_output_key", "mi_output")
        self.adversary_output_key = config.get("adversary_output_key", "adversary_output")
        self.train_subjects = config.get("train_subjects", 2)
        logging.info(
            f"Online Learning Module Initialized with LR: {self.optimizer.learning_rate.numpy():.6f}"
        )

    @tf.function
    def reinforcement_update(self, state, action_index, reward):
        """
        Policy gradient update for implicit feedback (Reinforcement Learning).
        Nudges the model towards actions that receive positive feedback.
        """
        try:
            with tf.GradientTape() as tape:
                # Supports models with tuple or dict output
                outputs = self.model(state, training=False)
                if isinstance(outputs, (tuple, list)):
                    mi_output = outputs[0]
                elif isinstance(outputs, dict):
                    mi_output = outputs[self.mi_output_key]
                else:
                    mi_output = outputs

                prob_of_action = mi_output[0, action_index]
                loss = -tf.math.log(prob_of_action + 1e-9) * reward

            grads = tape.gradient(loss, self.model.trainable_variables)
            self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
            tf.print("[LEARN] Reinforcement update. Reward:", reward, "Loss:", loss)
        except Exception as e:
            tf.print("[ERROR] Reinforcement update failed:", e)

    def corrective_update(self, state, correct_action_index):
        """
        Single supervised learning step for explicit error correction.
        Directly teaches the correct label.
        """
        try:
            targets = {
                self.mi_output_key: tf.constant([[correct_action_index]]),
                self.adversary_output_key: tf.zeros((1, self.train_subjects))
            }
            loss = self.model.train_on_batch(
                state,
                targets,
                return_dict=True
            )
            logging.warning(
                f"[LEARN] Corrective update. MI Loss: {loss.get(self.mi_output_key + '_loss', 0):.4f}"
            )
            return loss
        except Exception as e:
            logging.error(f"[ERROR] Corrective update failed: {e}", exc_info=True)
            return None
