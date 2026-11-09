# CUDA 13.4 coherent GPU-memory preflight

## Scope and current decision

CUDA 13.4 with driver r615 changes the default coherent GPU-memory mode from
NUMA to driver-managed memory (CDMM) on coherent NVIDIA systems such as GH200,
GB200, GB300, and Vera Rubin. This is a **Linux-node configuration**; it is not
a general CUDA setting and must not be changed by the desktop application or a
container.

The 2026-10-29 repository audit found no use of CUDA Unified/managed memory
(`cudaMallocManaged`, `cudaMemAdvise`, or `cudaMemPrefetchAsync`), OpenACC,
OpenMP target offload, or NVHPC. The Python toolchain uses ordinary PyTorch
device placement (`model.to(device)` and tensor `.to(device)`) and pinned host
memory for explicit CPU-to-GPU transfer. The "Unified Memory Consolidation"
name in the cognitive documentation describes a model feature, not CUDA Unified
Memory.

**Decision:** no source-level memory-management migration or default NUMA
override is required for the current code. This decision must be revisited if a
new workload introduces Unified Memory, managed allocations, or automatic page
migration.

## What is recorded

`EnvironmentSnapshot.capture()` now records `coherent_gpu_memory_mode` when
the node exposes `/proc/driver/nvidia/params`:

- `"driver"` means CDMM mode;
- `"numa"` means NUMA mode;
- `null` means the setting was not observable. It does **not** imply either
  mode, a compatible GPU, or an NVIDIA driver.

This field makes experiment reports comparable across relevant Linux nodes. It
does not alter a driver setting or determine whether a workload is affected.

## Operator preflight for a coherent Linux node

Before upgrading a relevant node to r615, record its active setting:

```bash
grep Coherent /proc/driver/nvidia/params
```

If the workload audit finds Unified/managed memory or automatic page migration
that must remain enabled, an administrator can persist NUMA mode and re-enable
SAM migration before the upgrade:

```bash
echo 'options nvidia NVreg_CoherentGPUMemoryMode=numa' \
  | sudo tee /etc/modprobe.d/nvidia-openrm.conf
echo 'options nvidia-uvm uvm_disable_sam_migration=false' \
  | sudo tee -a /etc/modprobe.d/nvidia-openrm.conf
sudo reboot
```

The change is node-wide and takes effect only after a reboot or driver reload.
It requires the infrastructure owner to assess co-located workloads; do not
apply it merely because this repository is present.

## Validation after an upgrade

1. Re-run the procfs check and save the reproducibility environment snapshot.
2. Record `torch.__version__`, `torch.version.cuda`, GPU model, driver version,
   and the observed coherent-memory mode alongside the benchmark result.
3. Run the affected training or inference workload with its normal data size;
   compare correctness, memory use, and throughput to its pre-upgrade baseline.
4. For future Unified-Memory workloads, validate both NUMA and CDMM only under
   the node policy approved by the infrastructure owner.

The current local development workstation runs Windows with a discrete PCIe GPU
(RTX 4070) and does not expose Linux `/proc/driver/nvidia/params` or coherent
memory hardware (GH200/GB200/GB300), so `coherent_gpu_memory_mode` evaluates to
`null` here. This check is targeted for coherent Linux compute/cluster nodes.
