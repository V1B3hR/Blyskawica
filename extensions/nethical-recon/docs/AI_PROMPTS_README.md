# AI Prompt Templates

This directory contains prompt templates for AI-powered analysis and reporting.

## Available Templates

### threat_analysis.txt
Template for comprehensive threat analysis reports.

### executive_summary.txt
Template for executive-level security summaries.

### remediation_plan.txt
Template for step-by-step remediation plans.

### bird_coordination.txt
Template for bird deployment coordination plans.

### forest_health.txt
Template for forest health assessment reports.

## Usage

```python
from ai import AIReporter

reporter = AIReporter()

# Load template
with open('ai/prompts/executive_summary.txt', 'r') as f:
    template = f.read()

# Fill template with data
report = template.format(**report_data)
```

## Template Format

Templates use Python string formatting syntax:
- `{variable_name}` for simple substitution
- `{variable_name:.2f}` for formatted numbers
- `{variable_name:%Y-%m-%d}` for dates

## Adding New Templates

1. Create a new `.txt` file in this directory
2. Use descriptive variable names in `{braces}`
3. Add documentation here
4. Update relevant AI components to use the template
