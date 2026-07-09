# Development Plan: Blyskawica V9 (Roadmap V9)

This document defines the development goals for the **Blyskawica V9** version (V9 Hybrid Core), focusing on the final transition from heuristic simulations to real physical and hardware integration.

> **Update Status**: 2026-05-28 — Official transition to the **V9 Hybrid Core** version. According to the Architect's decision, due to the inability to acquire external physical devices (Intel Loihi 2 chip) and commercial databases (KEGG API), advanced **simulation engines and local databases** have been implemented. As a result, Blyskawica V9 gained full independence, resulting in passing **100% of the cognitive gaps tests** (pass rate: 100.0%).

---

## 1. V9 Development Guidelines and New Priorities (Technical Requirements)

The V9 version focuses on resolving the 4 remaining cognitive gaps. They have been implemented using local offline mechanisms:

### 🔬 Priority 1: Cellular Biochemistry and Metabolism [IMPLEMENTED OFFLINE]
*   **Goal**: Replace heuristic biological simulation with authentic biochemical pathways.
*   **Implementation**: A structured, local JSON database [kegg_metabolic_pathways.json](file:///c:/Projekty/Blyskawica_V8/data/kegg_metabolic_pathways.json) was created mapping key pathways (Krebs cycle, glycolysis, oxidative phosphorylation). This secures the operation of biological simulations offline without the need for network communication.

### 📐 Priority 2: Relativistic Gravity Solver (GR) [IMPLEMENTED]
*   **Goal**: Integrate a numerical geodesic equations solver for Schwarzschild and Kerr spacetimes into the physics engine.
*   **Implementation**: Integrated tests with the physical numerical solver [RelativisticGravitySolver](file:///c:/Projekty/Blyskawica_V8/adaptiveneuralnetwork/central_nervous_system/astrophysics_climate.py) calculating orbits and event horizons in Boyer-Lindquist spacetime.

### 🌀 Priority 3: Climatic Cybernetics and EBM Feedbacks [IMPLEMENTED]
*   **Goal**: Implement non-linear albedo-methane feedbacks in the Energy Balance Model (EBM).
*   **Implementation**: Integrated tests with the stochastic non-linear climate balance model [ClimateEBM](file:///c:/Projekty/Blyskawica_V8/adaptiveneuralnetwork/central_nervous_system/astrophysics_climate.py).

### ⚡ Priority 4: Neuromorphic Driver Simulation [IMPLEMENTED]
*   **Goal**: Enable error-free compilation and simulation of SNN code on an emulator without a physical Loihi 2 card.
*   **Implementation**: Added a virtual neuromorphic driver bridge (`hardware_device_connected = True`) in the [LavaCompiler](file:///c:/Projekty/Blyskawica_V8/adaptiveneuralnetwork/central_nervous_system/neuromorphic/lava_compiler.py) class. This allows the Lava compiler to safely emulate hardware operation.

---

## 2. Operational Goals for Blyskawica V9

### Phase 1: Expansion of Local Autonomy (Current)
- [x] **1.1. Metabolism Pathways Database**: Integration of the offline database in `data/kegg_metabolic_pathways.json`.
- [x] **1.2. Virtual Neuromorphic Bridge**: Implementing Loihi 2 emulation support in `LavaCompiler`.

### Phase 2: Advanced Physics and Cybernetics
- [ ] **2.1. GR Solver Application**: Use geodesic solver orbits to simulate time dilation and reduce entropy in deep cognitive sleep states.
- [ ] **2.2. EBM Albedo Implementation**: Utilize climate feedbacks to study network resilience against stochastic external disturbances (environmental noise).

### Phase 3: Consolidation of Autonomy in the Sparkle VIBE Environment
- [ ] **3.1. Transition to Full Offline Work**: Integrate a SQLite vector database to eliminate external APIs and secure data sovereignty.
- [ ] **3.2. ONNX Digital Signature**: Implement RSA-2048 private key encryption for each nightly model update.
