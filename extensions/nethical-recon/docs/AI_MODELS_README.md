# AI Models Configuration

This directory contains configuration files for AI models used in Nethical Recon.

## Configuration Files

### threat_scoring.json
Configuration for threat score calculation weights and thresholds.

### classification_rules.json
Rules for threat classification (Crow, Magpie, Squirrel, etc.).

### baseline_learning.json
Configuration for baseline learning and adjustment.

### prediction_models.json
Settings for threat prediction models.

## Structure

```json
{
  "model_name": "threat_analyzer",
  "version": "1.0",
  "parameters": {
    "threshold": 0.7,
    "weights": {
      "severity": 0.3,
      "confidence": 0.25
    }
  }
}
```

## Usage

```python
import json

# Load configuration
with open('ai/models/threat_scoring.json', 'r') as f:
    config = json.load(f)

# Use in AI component
analyzer = ThreatAnalyzer(config)
```

## Customization

You can adjust these configurations to tune the AI behavior for your environment:

- Increase/decrease thresholds for stricter/looser detection
- Adjust weights to prioritize certain factors
- Add custom rules for specific threat patterns

## Best Practices

1. Keep backups of working configurations
2. Test changes in a dev environment first
3. Document any modifications
4. Version control your custom configs
