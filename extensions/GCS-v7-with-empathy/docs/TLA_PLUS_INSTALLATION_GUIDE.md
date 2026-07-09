# TLA+ Installation Guide for GCS v7 Phase 21

This guide provides step-by-step instructions for installing TLA+ tools to achieve 90%+ verification coverage for Phase 21 formal verification.

## Overview

TLA+ (Temporal Logic of Actions Plus) is a formal specification language used for designing, modeling, documenting, and verifying programs, especially concurrent systems and distributed algorithms. For GCS v7, we use TLA+ to verify:

- System safety properties (bad states never reached)
- Liveness properties (good states eventually reached)
- Temporal properties (ordering constraints)
- Crisis detection correctness
- Privacy enforcement guarantees
- Fairness across demographics

## Prerequisites

- Java Runtime Environment (JRE) 8 or later
- Basic understanding of formal methods (optional but helpful)
- Access to terminal/command line

## Installation Methods

### Method 1: TLA+ Toolbox (Recommended for GUI)

The TLA+ Toolbox provides a graphical IDE for working with TLA+ specifications.

#### Windows
1. Download TLA+ Toolbox from: https://lamport.azurewebsites.net/tla/toolbox.html
2. Extract the ZIP file to a directory (e.g., `C:\TLA+Toolbox`)
3. Run `TLA+ Toolbox.exe`
4. Add to PATH (optional):
   ```cmd
   setx PATH "%PATH%;C:\TLA+Toolbox"
   ```

#### macOS
1. Download TLA+ Toolbox DMG from: https://lamport.azurewebsites.net/tla/toolbox.html
2. Open the DMG and drag TLA+ Toolbox to Applications
3. Open Terminal and create an alias:
   ```bash
   echo 'alias tlc="/Applications/TLA+Toolbox.app/Contents/Eclipse/tla2tools.jar"' >> ~/.bashrc
   source ~/.bashrc
   ```

#### Linux
1. Download TLA+ Toolbox from: https://lamport.azurewebsites.net/tla/toolbox.html
2. Extract to `/opt/TLA+Toolbox` or `~/TLA+Toolbox`
3. Make executable:
   ```bash
   chmod +x ~/TLA+Toolbox/toolbox
   ```
4. Add to PATH:
   ```bash
   echo 'export PATH="$PATH:$HOME/TLA+Toolbox"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Method 2: Standalone TLC (Recommended for Automation)

TLC (TLA+ model checker) can be run standalone for automated verification.

#### All Platforms (Recommended)
```bash
# Create TLA+ directory
mkdir -p ~/.tla
cd ~/.tla

# Download tla2tools.jar (latest version)
wget https://github.com/tlaplus/tlaplus/releases/download/v1.8.0/tla2tools.jar

# Create wrapper script
cat > tlc << 'EOF'
#!/bin/bash
java -cp ~/.tla/tla2tools.jar tlc2.TLC "$@"
EOF

chmod +x tlc

# Add to PATH
echo 'export PATH="$PATH:$HOME/.tla"' >> ~/.bashrc
source ~/.bashrc
```

#### Alternative: Use package managers

**Homebrew (macOS)**
```bash
brew install tla-plus
```

**APT (Debian/Ubuntu)**
```bash
# Add TLA+ repository
sudo add-apt-repository ppa:tlaplus/ppa
sudo apt update
sudo apt install tla-toolbox
```

**Chocolatey (Windows)**
```powershell
choco install tla-plus-toolbox
```

## Verification

### Test TLC Installation
```bash
# Check Java version (must be 8+)
java -version

# Test TLC
tlc -help

# Expected output:
# TLC2 Version 2.x.x of Day Month Year
# Usage: tlc [-option] inputfile
```

### Test with GCS Specifications

```bash
# Navigate to GCS project
cd /path/to/GCS-v7-with-empathy

# Run Phase 21 validation
python3 src/demo/validate_phases_19_22.py

# Expected output:
# Phase 21 Status: ✓ COMPLETE
# Verification Coverage: 90%+ (9/10 properties verified)
```

## GCS v7 TLA+ Specifications

The GCS empathy system includes TLA+ specifications for:

1. **EmpathySystem.tla** - Main empathy processing system
   - Emotion recognition safety
   - Privacy enforcement
   - Crisis detection properties

2. **CrisisDetection.tla** - Crisis detection and escalation
   - False negative bounds
   - Liveness (intervention provided)
   - Professional notification timing

3. **PrivacyEnforcement.tla** - Data privacy guarantees
   - Consent enforcement
   - Data minimization
   - Revocation handling

4. **FairnessProperties.tla** - Demographic fairness
   - Equitable accuracy across groups
   - Bias prevention
   - Accessibility guarantees

5. **MultiUserSession.tla** - Brain-to-brain communication
   - Session integrity
   - Cross-user privacy
   - Identity verification

## Running Verification

### Manual Verification
```bash
# Verify a single specification
tlc -simulate -workers auto backend/gcs/specs/EmpathySystem.tla

# Verify all specifications
for spec in backend/gcs/specs/*.tla; do
    echo "Verifying $spec..."
    tlc -simulate -workers auto "$spec"
done
```

### Automated Verification (Integrated)
```bash
# Run GCS Phase 21 verification suite
python3 backend/gcs/phase21_formal_tools.py

# Run complete Phase 19-22 validation
python3 src/demo/validate_phases_19_22.py
```

## Troubleshooting

### Issue: "TLC not found"
- Verify Java installation: `java -version`
- Check PATH includes TLC directory
- Try absolute path: `java -cp ~/.tla/tla2tools.jar tlc2.TLC -help`

### Issue: "Out of memory"
- Increase Java heap size:
  ```bash
  tlc -Xmx4G spec.tla  # Allocate 4GB RAM
  ```

### Issue: "Module not found"
- Ensure TLA+ standard modules are in classpath
- Check `CLASSPATH` environment variable includes tla2tools.jar

### Issue: Verification times out
- Use smaller state space: Reduce CONSTANTS in .cfg file
- Use simulation mode: `tlc -simulate` instead of full model checking
- Increase timeout: Add `-timeout` parameter

## Next Steps After Installation

1. **Verify Installation**
   ```bash
   python3 src/demo/validate_phases_19_22.py
   ```
   Expected: Phase 21 shows ✓ COMPLETE with 90%+ coverage

2. **Review Verification Results**
   - Check `backend/gcs/verification_results/` for detailed reports
   - Review any property violations or counterexamples

3. **Update Documentation**
   - Mark Phase 21 as COMPLETE in ROADMAP.md
   - Update ROADMAP_STATUS.md with verification evidence

4. **Proceed to Pilot Activation**
   - Phase 20: Activate Q1 2026 pilots
   - Phase 22: Begin regional rollout

## Additional Resources

- **TLA+ Homepage**: https://lamport.azurewebsites.net/tla/tla.html
- **TLA+ Tutorial**: https://learntla.com/
- **TLA+ Examples**: https://github.com/tlaplus/Examples
- **TLA+ Book**: "Specifying Systems" by Leslie Lamport (free PDF)
- **TLA+ Community**: https://groups.google.com/g/tlaplus

## Support

For GCS-specific TLA+ questions:
- Review `backend/gcs/phase21_formal_tools.py` for integration details
- Check specification templates in `backend/gcs/specs/`
- Consult ROADMAP.md Section 6 Phase 21 for verification requirements

For TLA+ tool issues:
- TLA+ Google Group: https://groups.google.com/g/tlaplus
- GitHub Issues: https://github.com/tlaplus/tlaplus/issues

---

**Last Updated**: 2025-10-17  
**Version**: 1.0  
**Phase**: 21 - Formal Verification & Assurance
