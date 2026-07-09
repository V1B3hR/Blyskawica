#!/usr/bin/env python3
"""
Research Article Analysis Tool for GCS System

This script provides functionality to analyze research articles and determine
their relevance to specific GCS modules. It can be used to systematically
evaluate new brain medicine research for potential integration.

Usage:
    python research_analyzer.py --article-url <URL> --output-format json
    python research_analyzer.py --keywords "neuromodulation,emotion" --module affective
"""

import argparse
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class GCSModule(Enum):
    """Enumeration of GCS system modules"""
    AFFECTIVE_STATE_CLASSIFIER = "affective_state_classifier"
    NEUROMODULATION_CONTROLLER = "neuromodulation_controller"
    CLOSED_LOOP_AGENT = "closed_loop_agent"
    FEEDBACK_DETECTOR = "feedback_detector"
    ONLINE_LEARNING_MODULE = "online_learning_module"
    DATA_PIPELINE = "data_pipeline"

@dataclass
class ResearchRelevance:
    """Data class for research relevance assessment"""
    module: GCSModule
    relevance_score: float  # 0.0 to 1.0
    key_concepts: List[str]
    potential_benefits: List[str]
    implementation_priority: str  # "HIGH", "MEDIUM", "LOW"

class ResearchAnalyzer:
    """Analyzes research articles for relevance to GCS modules"""
    
    def __init__(self):
        self.module_keywords = self._initialize_module_keywords()
        self.module_descriptions = self._initialize_module_descriptions()
        
    def _initialize_module_keywords(self) -> Dict[GCSModule, List[str]]:
        """Initialize keyword mappings for each module"""
        return {
            GCSModule.AFFECTIVE_STATE_CLASSIFIER: [
                "emotion", "affective", "valence", "arousal", "EEG emotion", 
                "physiological emotion", "voice prosody", "multi-modal emotion",
                "emotional state", "mood recognition", "affective computing",
                "heart rate variability", "galvanic skin response", "autonomic"
            ],
            GCSModule.NEUROMODULATION_CONTROLLER: [
                "neuromodulation", "brain stimulation", "ultrasound therapy",
                "electrical stimulation", "vagus nerve stimulation", "TUS",
                "therapeutic stimulation", "closed-loop stimulation",
                "neurostimulation", "transcranial", "focused ultrasound"
            ],
            GCSModule.CLOSED_LOOP_AGENT: [
                "closed-loop", "adaptive therapy", "therapeutic decision",
                "biomarker-guided", "real-time intervention", "automated therapy",
                "personalized treatment", "adaptive algorithm", "therapeutic AI"
            ],
            GCSModule.FEEDBACK_DETECTOR: [
                "real-time EEG", "neurofeedback", "online signal processing",
                "adaptive filtering", "EEG artifacts", "brain state detection",
                "continuous monitoring", "signal quality", "real-time analysis"
            ],
            GCSModule.ONLINE_LEARNING_MODULE: [
                "neuroplasticity", "adaptive learning", "personalization",
                "reinforcement learning", "user adaptation", "continual learning",
                "incremental learning", "brain adaptation", "meta-learning"
            ],
            GCSModule.DATA_PIPELINE: [
                "source localization", "eLORETA", "multi-modal fusion",
                "EEG preprocessing", "cortical mapping", "brain connectivity",
                "signal preprocessing", "data fusion", "beamforming"
            ]
        }
    
    def _initialize_module_descriptions(self) -> Dict[GCSModule, str]:
        """Initialize descriptions for each module"""
        return {
            GCSModule.AFFECTIVE_STATE_CLASSIFIER: 
                "Multi-modal emotion recognition using EEG, physiological signals, and voice prosody",
            GCSModule.NEUROMODULATION_CONTROLLER: 
                "Controls therapeutic interventions via ultrasound and electrical stimulation",
            GCSModule.CLOSED_LOOP_AGENT: 
                "Orchestrates SENSE → DECIDE → ACT → LEARN therapeutic cycle",
            GCSModule.FEEDBACK_DETECTOR: 
                "Real-time EEG feedback detection with adaptive signal processing",
            GCSModule.ONLINE_LEARNING_MODULE: 
                "Incremental learning from user feedback and corrective updates",
            GCSModule.DATA_PIPELINE: 
                "EEG source localization and multi-modal data preprocessing"
        }
    
    def analyze_keywords(self, keywords: List[str]) -> List[ResearchRelevance]:
        """Analyze keywords and return relevance for each module"""
        results = []
        
        for module in GCSModule:
            module_keywords = self.module_keywords[module]
            
            # Calculate relevance score based on keyword matches
            matches = [kw for kw in keywords if any(mk.lower() in kw.lower() or kw.lower() in mk.lower() 
                      for mk in module_keywords)]
            relevance_score = len(matches) / max(len(module_keywords), 1)
            
            if relevance_score > 0:
                # Determine implementation priority
                if relevance_score >= 0.3:
                    priority = "HIGH"
                elif relevance_score >= 0.15:
                    priority = "MEDIUM"
                else:
                    priority = "LOW"
                
                potential_benefits = self._generate_potential_benefits(module, matches)
                
                results.append(ResearchRelevance(
                    module=module,
                    relevance_score=relevance_score,
                    key_concepts=matches,
                    potential_benefits=potential_benefits,
                    implementation_priority=priority
                ))
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
    
    def _generate_potential_benefits(self, module: GCSModule, matched_concepts: List[str]) -> List[str]:
        """Generate potential benefits based on module and matched concepts"""
        benefit_map = {
            GCSModule.AFFECTIVE_STATE_CLASSIFIER: [
                "Improved emotion recognition accuracy",
                "Enhanced multi-modal data fusion",
                "Better physiological signal interpretation",
                "Cross-cultural emotion validation"
            ],
            GCSModule.NEUROMODULATION_CONTROLLER: [
                "Updated safety protocols",
                "New therapeutic targets",
                "Optimized stimulation parameters",
                "Enhanced treatment efficacy"
            ],
            GCSModule.CLOSED_LOOP_AGENT: [
                "Improved decision-making algorithms",
                "Enhanced safety protocols",
                "Better therapeutic timing",
                "More effective intervention selection"
            ],
            GCSModule.FEEDBACK_DETECTOR: [
                "Better real-time signal processing",
                "Improved artifact rejection",
                "Enhanced biomarker detection",
                "More responsive adaptation"
            ],
            GCSModule.ONLINE_LEARNING_MODULE: [
                "More efficient personalization",
                "Better learning from feedback",
                "Enhanced adaptation mechanisms",
                "Improved retention of learned patterns"
            ],
            GCSModule.DATA_PIPELINE: [
                "Improved source localization",
                "Better data preprocessing",
                "Enhanced signal quality",
                "More robust cortical mapping"
            ]
        }
        return benefit_map.get(module, ["General system improvement"])
    
    def generate_report(self, relevance_results: List[ResearchRelevance], 
                       output_format: str = "text") -> str:
        """Generate a formatted report of the analysis"""
        if output_format == "json":
            return self._generate_json_report(relevance_results)
        else:
            return self._generate_text_report(relevance_results)
    
    def _generate_text_report(self, results: List[ResearchRelevance]) -> str:
        """Generate a text-formatted report"""
        report = "GCS Module Relevance Analysis\n"
        report += "=" * 35 + "\n\n"
        
        if not results:
            report += "No relevant modules identified for the given research.\n"
            return report
        
        for result in results:
            report += f"Module: {result.module.value}\n"
            report += f"Description: {self.module_descriptions[result.module]}\n"
            report += f"Relevance Score: {result.relevance_score:.2f}\n"
            report += f"Priority: {result.implementation_priority}\n"
            report += f"Key Concepts: {', '.join(result.key_concepts)}\n"
            report += "Potential Benefits:\n"
            for benefit in result.potential_benefits:
                report += f"  - {benefit}\n"
            report += "\n" + "-" * 50 + "\n\n"
        
        return report
    
    def _generate_json_report(self, results: List[ResearchRelevance]) -> str:
        """Generate a JSON-formatted report"""
        json_data = {
            "analysis_results": []
        }
        
        for result in results:
            json_data["analysis_results"].append({
                "module": result.module.value,
                "module_description": self.module_descriptions[result.module],
                "relevance_score": result.relevance_score,
                "implementation_priority": result.implementation_priority,
                "key_concepts": result.key_concepts,
                "potential_benefits": result.potential_benefits
            })
        
        return json.dumps(json_data, indent=2)

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Analyze research relevance to GCS modules")
    parser.add_argument("--keywords", type=str, required=True,
                       help="Comma-separated list of research keywords")
    parser.add_argument("--output-format", choices=["text", "json"], default="text",
                       help="Output format for the analysis report")
    parser.add_argument("--module", type=str, choices=[m.value for m in GCSModule],
                       help="Focus analysis on specific module")
    
    args = parser.parse_args()
    
    # Parse keywords
    keywords = [kw.strip() for kw in args.keywords.split(",")]
    
    # Initialize analyzer
    analyzer = ResearchAnalyzer()
    
    # Perform analysis
    results = analyzer.analyze_keywords(keywords)
    
    # Filter by specific module if requested
    if args.module:
        target_module = GCSModule(args.module)
        results = [r for r in results if r.module == target_module]
    
    # Generate and print report
    report = analyzer.generate_report(results, args.output_format)
    print(report)

if __name__ == "__main__":
    main()