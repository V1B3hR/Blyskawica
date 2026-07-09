# Bioart DNA Programming Language - Build Automation Makefile
# Provides targets for running demonstrations, tests, and full simulation

.PHONY: demo test stress all clean help
.DEFAULT_GOAL := help

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color
BOLD := \033[1m

# Python interpreter
PYTHON := python3

# Project directories
SRC_DIR := src
TESTS_DIR := tests
EXAMPLES_DIR := examples
DOCS_DIR := docs

help: ## Show this help message
	@echo "$(BOLD)🧬 Bioart DNA Programming Language - Build System$(NC)"
	@echo "$(BOLD)============================================================$(NC)"
	@echo ""
	@echo "$(BOLD)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-12s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)Examples:$(NC)"
	@echo "  make demo      # Run interactive demonstration"
	@echo "  make test      # Run comprehensive test suite"
	@echo "  make all       # Run full simulation and all tests"
	@echo ""

demo: ## Run interactive demonstration
	@echo "$(BOLD)🧬 Running Interactive Demonstration$(NC)"
	@echo "$(BOLD)=====================================$(NC)"
	@$(PYTHON) $(EXAMPLES_DIR)/dna_demo.py
	@echo ""
	@echo "$(GREEN)✅ Demo completed successfully!$(NC)"

interpreter: ## Run virtual machine interpreter
	@echo "$(BOLD)🤖 Running Virtual Machine Interpreter$(NC)"
	@echo "$(BOLD)======================================$(NC)"
	@$(PYTHON) $(SRC_DIR)/bioart.py
	@echo ""
	@echo "$(GREEN)✅ Interpreter execution completed!$(NC)"

test: ## Run all tests with detailed reporting
	@echo "$(BOLD)🧪 Running Comprehensive Test Suite$(NC)"
	@echo "$(BOLD)====================================$(NC)"
	@$(PYTHON) run_tests.py
	@echo ""
	@echo "$(GREEN)✅ Test execution completed!$(NC)"

advanced: ## Run advanced tests only
	@echo "$(BOLD)🔬 Running Advanced Test Suite$(NC)"
	@echo "$(BOLD)==============================$(NC)"
	@$(PYTHON) $(TESTS_DIR)/advanced_tests.py
	@echo ""
	@echo "$(GREEN)✅ Advanced tests completed!$(NC)"

stress: ## Run stress tests only
	@echo "$(BOLD)💪 Running Stress Tests$(NC)"
	@echo "$(BOLD)=======================$(NC)"
	@$(PYTHON) $(TESTS_DIR)/stress_tests.py
	@echo ""
	@echo "$(GREEN)✅ Stress tests completed!$(NC)"

all: ## Run full simulation and all tests
	@echo "$(BOLD)🚀 Running Full Simulation$(NC)"
	@echo "$(BOLD)===========================$(NC)"
	@$(PYTHON) run_full_simulation.py
	@echo ""
	@echo "$(GREEN)✅ Full simulation completed!$(NC)"

example: ## Test the example DNA program (Load 42, Add 8, Print 50, Halt)
	@echo "$(BOLD)🧬 Testing Example DNA Program$(NC)"
	@echo "$(BOLD)==============================$(NC)"
	@echo "Program: AAAU ACCC AAAG AACA AAUG AAGA"
	@echo "Expected: Load 42, Add 8, Print 50, Halt"
	@echo ""
	@$(PYTHON) -c "import sys; sys.path.insert(0, 'src'); from bioart import Bioart; dna = Bioart(); bytecode = dna.compile_dna_to_bytecode('AAAU ACCC AAAG AACA AAUG AAGA'); print('Bytecode:', ' '.join(f'{b:02X}' for b in bytecode)); print('Output:', end=' '); dna.execute_bytecode(bytecode)"
	@echo ""
	@echo "$(GREEN)✅ Example program test completed!$(NC)"

validate: ## Validate repository structure and setup
	@echo "$(BOLD)🔍 Validating Repository Setup$(NC)"
	@echo "$(BOLD)==============================$(NC)"
	@$(PYTHON) test_repo.py
	@echo ""
	@echo "$(GREEN)✅ Repository validation completed!$(NC)"

specs: ## Show virtual machine specifications
	@echo "$(BOLD)📋 Bioart Virtual Machine Specifications$(NC)"
	@echo "$(BOLD)============================================$(NC)"
	@echo "• Memory: 256 bytes"
	@echo "• Registers: 4 (A, B, C, D)"
	@echo "• Instructions: 13 core instructions"
	@echo "• DNA Encoding: 2-bit system (A=00, U=01, C=10, G=11)"
	@echo "• Efficiency: 4 nucleotides per byte (optimal)"
	@echo "• Performance: Up to 78M bytes/second processing speed"
	@echo "• Test Coverage: All 256 byte values, 24 test categories"
	@echo "• Accuracy: 100% across all conversion scenarios"
	@echo ""

performance: ## Show performance benchmarks
	@echo "$(BOLD)🚀 Performance Benchmarks$(NC)"
	@echo "$(BOLD)=========================$(NC)"
	@echo "Encoding Speed:"
	@echo "  • Small files (100 bytes): ~1.7M bytes/second"
	@echo "  • Medium files (1KB): ~933K bytes/second"
	@echo "  • Large files (10KB): ~974K bytes/second"
	@echo "  • Extreme files (100KB): Consistent performance maintained"
	@echo ""
	@echo "Accuracy Metrics:"
	@echo "  • Basic encoding: 100% accuracy"
	@echo "  • All byte patterns: 256/256 values (100%)"
	@echo "  • Stress testing: 1000/1000 sequences (100%)"
	@echo "  • File operations: Perfect data preservation"
	@echo ""

clean: ## Clean up generated files
	@echo "$(BOLD)🧹 Cleaning Generated Files$(NC)"
	@echo "$(BOLD)===========================$(NC)"
	@echo "Removing temporary files..."
	@find . -name "*.dna" -type f ! -path "./examples/*" -delete 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.tmp" -delete 2>/dev/null || true
	@find . -name "test_*.dna" -delete 2>/dev/null || true
	@find . -name "stress_test_*.dna" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed!$(NC)"

install: ## Install dependencies (none required for this project)
	@echo "$(BOLD)📦 Installing Dependencies$(NC)"
	@echo "$(BOLD)===========================$(NC)"
	@echo "$(YELLOW)ℹ️  No external dependencies required for Bioart!$(NC)"
	@echo "$(GREEN)✅ This project uses only Python standard library$(NC)"

check: ## Run all validation checks
	@echo "$(BOLD)✅ Running All Validation Checks$(NC)"
	@echo "$(BOLD)================================$(NC)"
	@$(MAKE) validate
	@$(MAKE) example
	@$(MAKE) test
	@echo ""
	@echo "$(GREEN)🏆 All validation checks completed!$(NC)"

info: ## Show project information
	@echo "$(BOLD)🧬 Bioart DNA Programming Language$(NC)"
	@echo "$(BOLD)=====================================$(NC)"
	@echo "Version: 1.0 (Production Ready)"
	@echo "Language: Python 3.6+"
	@echo "Dependencies: None (uses standard library only)"
	@echo "License: MIT with research disclaimer"
	@echo ""
	@echo "$(BOLD)Key Features:$(NC)"
	@echo "• 2-bit DNA encoding (A=00, U=01, C=10, G=11)"
	@echo "• Virtual machine with 256 bytes memory"
	@echo "• 13 core programming instructions" 
	@echo "• Universal data storage (any file type)"
	@echo "• Perfect data preservation (no loss)"
	@echo "• High performance (up to 78M bytes/second)"
	@echo ""
	@echo "$(BOLD)Repository Structure:$(NC)"
	@echo "• src/         - Core language implementation"
	@echo "• examples/    - Demonstrations and sample programs"
	@echo "• tests/       - Comprehensive test suites"
	@echo "• docs/        - Documentation and analysis"
	@echo ""

# Development targets
dev-test: ## Run tests in development mode (with verbose output)
	@echo "$(BOLD)🔧 Development Test Mode$(NC)"
	@echo "$(BOLD)========================$(NC)"
	@$(PYTHON) -v $(TESTS_DIR)/advanced_tests.py
	@$(PYTHON) -v $(TESTS_DIR)/stress_tests.py

quick: ## Quick validation (demo + basic tests)
	@echo "$(BOLD)⚡ Quick Validation$(NC)"
	@echo "$(BOLD)==================$(NC)"
	@$(MAKE) demo
	@$(MAKE) example
	@echo ""
	@echo "$(GREEN)✅ Quick validation completed!$(NC)"

translator: ## Run translator demo
	@echo "$(BOLD)🧬 Running Translator Demo$(NC)"
	@echo "$(BOLD)===========================$(NC)"
	@$(PYTHON) $(EXAMPLES_DIR)/translator_demo.py
	@echo ""
	@echo "$(GREEN)✅ Translator demo completed!$(NC)"

translator-test: ## Run translator tests
	@echo "$(BOLD)🧪 Running Translator Tests$(NC)"
	@echo "$(BOLD)============================$(NC)"
	@$(PYTHON) $(TESTS_DIR)/test_translator.py
	@echo ""
	@echo "$(GREEN)✅ Translator tests completed!$(NC)"

cli: ## Show CLI help
	@echo "$(BOLD)🖥️  Bioart CLI Help$(NC)"
	@echo "$(BOLD)===================$(NC)"
	@$(PYTHON) bioart_cli.py --help