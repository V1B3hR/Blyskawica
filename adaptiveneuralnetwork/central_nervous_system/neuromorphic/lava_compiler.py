"""
Lava Software Framework Compiler & Exporter Backend.
Translates PyTorch Spiking Neural Networks (SNN) into Lava-compatible Process Graphs
and executable Python scripts for deployment on Loihi hardware or Lava simulator.
"""

import json
import logging
import math
import os
import time

import numpy as np
import torch.nn as nn

logger = logging.getLogger(__name__)

class LavaCompiler:
    """
    Compiler backend for translating Błyskawica HierarchicalNetwork SNN
    into Lava processes and connections.
    """

    def __init__(self):
        # Simulated hardware link for neuromorphic V9 core
        self.hardware_device_connected = True

    @staticmethod
    def float_to_lava_decay(tau: float, dt: float = 0.001) -> float:
        """
        Translates a physical time constant (tau) in seconds to a Lava/Loihi decay factor.
        Lava decay d is modeled as: d = 1.0 - exp(-dt / tau).
        Returns a float between 0.0 and 1.0.
        """
        if tau <= 0.0:
            return 1.0
        return float(1.0 - math.exp(-dt / tau))

    @staticmethod
    def float_to_lava_decay_fixed_point(tau: float, dt: float = 0.001, bit_precision: int = 12) -> int:
        """
        Translates physical time constant to integer decay value for Loihi hardware fixed-point computation.
        """
        decay_float = LavaCompiler.float_to_lava_decay(tau, dt)
        max_val = (1 << bit_precision) - 1
        return int(max(0, min(max_val, round(decay_float * max_val))))

    def compile_to_json(self, network: nn.Module, filepath: str | None = None) -> dict:
        """
        Compiles the PyTorch HierarchicalNetwork into a Lava-compatible JSON serialization scheme.
        
        Args:
            network: HierarchicalNetwork instance to compile.
            filepath: Optional destination path to write the JSON to.
            
        Returns:
            Dictionary representing the compiled Lava network graph.
        """  # noqa: W293
        if not hasattr(network, 'layers') or not hasattr(network, 'feedforward_connections'):
            raise TypeError("Input network must be a HierarchicalNetwork or expose layers and feedforward_connections.")

        dt = getattr(network.config, 'dt', 0.001)
        bit_precision = getattr(network.config, 'bit_precision', 12)

        processes = []
        connections = []

        # 1. Compile LIF Layers (PopulationLayers)
        for idx, layer in enumerate(network.layers):
            layer_size = layer.population_size
            neuron_config = layer.neuron_config
            base_config = neuron_config.base_config

            v_threshold = float(getattr(base_config, 'v_threshold', 1.0))
            v_reset = float(getattr(base_config, 'v_reset', 0.0))
            tau_mem = float(getattr(base_config, 'tau_mem', 0.01))
            tau_syn = float(getattr(base_config, 'tau_syn', 0.005))

            # Compute decay rates
            du = self.float_to_lava_decay(tau_syn, dt)
            dv = self.float_to_lava_decay(tau_mem, dt)

            du_fixed = self.float_to_lava_decay_fixed_point(tau_syn, dt, bit_precision)
            dv_fixed = self.float_to_lava_decay_fixed_point(tau_mem, dt, bit_precision)

            processes.append({
                "id": f"lif_{idx}",
                "type": "LIF",
                "shape": [layer_size],
                "vth": v_threshold,
                "v_reset": v_reset,
                "du": du,
                "dv": dv,
                "du_fixed": du_fixed,
                "dv_fixed": dv_fixed,
                "metadata": {
                    "neuron_type": layer.neuron_type,
                    "lateral_inhibition": layer.lateral_inhibition,
                    "inhibition_strength": float(layer.inhibition_strength) if layer.lateral_inhibition else 0.0
                }
            })

        # 2. Compile Feedforward Dynamic Connections (Dense Synapses)
        for idx, ff_conn in enumerate(network.feedforward_connections):
            # Extract weights and apply mask
            weights = ff_conn.synaptic_weights.detach().cpu().numpy()
            mask = ff_conn.connectivity_mask.detach().cpu().numpy()
            masked_weights = weights * mask

            # Lava Dense weight matrix must be transposed: shape is (post_size, pre_size)
            lava_weights = masked_weights.T

            connections.append({
                "id": f"dense_ff_{idx}",
                "type": "Dense",
                "source": f"lif_{idx}",
                "target": f"lif_{idx + 1}",
                "shape": list(lava_weights.shape),
                "weights": lava_weights.tolist()
            })

        # 3. Compile Feedback Connections if present
        if hasattr(network, 'feedback_connections'):
            for idx, fb_conn in enumerate(network.feedback_connections):
                weights = fb_conn.synaptic_weights.detach().cpu().numpy()
                mask = fb_conn.connectivity_mask.detach().cpu().numpy()
                masked_weights = weights * mask
                lava_weights = masked_weights.T

                connections.append({
                    "id": f"dense_fb_{idx}",
                    "type": "Dense",
                    "source": f"lif_{idx + 1}",
                    "target": f"lif_{idx}",
                    "shape": list(lava_weights.shape),
                    "weights": lava_weights.tolist()
                })

        lava_network = {
            "compiler": "Blyskawica LavaCompiler V1",
            "timestamp": time.time(),
            "configuration": {
                "dt": dt,
                "bit_precision": bit_precision,
                "num_layers": len(network.layers)
            },
            "processes": processes,
            "connections": connections
        }

        if filepath:
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
            except Exception:
                pass
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(lava_network, f, indent=4)
            logger.info(f"Successfully serialized Lava network graph to {filepath}")

        return lava_network

    def compile_to_script(self, network: nn.Module) -> str:
        """
        Compiles the PyTorch HierarchicalNetwork into an executable Python script
        that builds the network inside Intel's Lava Software Framework.
        """
        lava_graph = self.compile_to_json(network)

        script_lines = [
            "# Automatically compiled Lava execution script",
            f"# Generated by Blyskawica LavaCompiler on {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "import numpy as np",
            "from lava.proc.lif.process import LIF",
            "from lava.proc.dense.process import Dense",
            "from lava.runtime.run_conditions import RunSteps",
            "from lava.runtime.run_configs import Loihi1SimCfg",
            "",
            "# --- 1. Initialize Lava Processes ---"
        ]

        # Declare LIF processes
        for proc in lava_graph["processes"]:
            shape_str = f"({proc['shape'][0]},)"
            script_lines.append(
                f"{proc['id']} = LIF(shape={shape_str}, vth={proc['vth']}, "
                f"du={proc['du']:.6f}, dv={proc['dv']:.6f}, v_reset={proc['v_reset']})"
            )

        script_lines.append("")
        script_lines.append("# --- 2. Initialize Synaptic Connections ---")

        # Declare Dense weights and connect ports
        for conn in lava_graph["connections"]:
            weights_var = f"weights_{conn['id']}"
            weights_str = np.array2string(np.array(conn["weights"]), separator=", ", precision=6, max_line_width=120)

            script_lines.append(f"{weights_var} = np.array({weights_str})")
            script_lines.append(f"{conn['id']} = Dense(weights={weights_var})")

            # Port connection logic:
            # Dense s_in connects to source s_out
            # target a_in connects to Dense a_out
            script_lines.append(f"{conn['source']}.s_out.connect({conn['id']}.s_in)")
            script_lines.append(f"{conn['id']}.a_out.connect({conn['target']}.a_in)")
            script_lines.append("")

        script_lines.append("# --- 3. Run Simulation ---")
        script_lines.append("if __name__ == '__main__':")
        script_lines.append("    print('[LAVA] Running Compiled Neuromorphic Spiking Network...')")
        script_lines.append("    # Run for 100 simulation timesteps")
        script_lines.append("    # Note: Execution requires 'lava-dn' package to run this simulation block.")
        script_lines.append("    # lif_0.run(condition=RunSteps(num_steps=100), run_cfg=Loihi1SimCfg())")
        script_lines.append("    # print('[LAVA] Simulation finished successfully.')")
        script_lines.append("    pass")

        return "\n".join(script_lines)
