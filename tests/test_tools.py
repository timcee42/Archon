"""Tests for specialist tools in the EUC Assessment Agent team."""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.tools.knowledge_base import KnowledgeBaseTool
from src.tools.financial_calculator import FinancialCalculator
from src.tools.document_analyzer import DocumentAnalyzer


class TestKnowledgeBaseTool:
    """Tests for the knowledge base tool."""

    def test_init(self, tmp_path):
        """Test initialization of the knowledge base tool."""
        kb_tool = KnowledgeBaseTool(tmp_path)
        assert kb_tool.kb_path == tmp_path
        assert kb_tool.kb_index == {}

    def test_add_and_lookup_entry(self, tmp_path):
        """Test adding and looking up entries in the knowledge base."""
        kb_tool = KnowledgeBaseTool(tmp_path)
        
        # Add an entry
        entry_id = kb_tool.add_entry(
            category="licensing",
            title="Microsoft 365 Licensing",
            content="Microsoft 365 offers various licensing options including E3 and E5.",
            metadata={"source": "Microsoft documentation"}
        )
        
        assert entry_id is not None
        assert len(entry_id) == 8  # UUID first 8 chars
        
        # Lookup the entry
        results = kb_tool.lookup(category="licensing", query="Microsoft 365")
        
        assert len(results) == 1
        assert results[0]["title"] == "Microsoft 365 Licensing"
        assert "various licensing options" in results[0]["content"]
        assert results[0]["metadata"]["source"] == "Microsoft documentation"
        
        # Lookup with no matching results
        results = kb_tool.lookup(category="licensing", query="Google Workspace")
        assert len(results) == 0
        
        # Lookup in non-existent category
        results = kb_tool.lookup(category="nonexistent", query="Microsoft")
        assert len(results) == 0


class TestFinancialCalculator:
    """Tests for the financial calculator tool."""

    def test_calculate_tco(self):
        """Test calculation of Total Cost of Ownership."""
        calculator = FinancialCalculator()
        
        result = calculator.calculate_tco(
            initial_costs=100000.0,
            recurring_costs={"maintenance": 20000.0, "support": 15000.0},
            timeframe_years=3
        )
        
        assert result["tco"] == 205000.0  # 100000 + (20000 + 15000) * 3
        assert result["initial_costs"] == 100000.0
        assert result["recurring_costs_total"] == 105000.0
        assert result["timeframe_years"] == 3
        assert result["breakdown"]["recurring"]["maintenance"] == 60000.0
        assert result["breakdown"]["recurring"]["support"] == 45000.0

    def test_calculate_roi(self):
        """Test calculation of Return on Investment."""
        calculator = FinancialCalculator()
        
        result = calculator.calculate_roi(
            initial_investment=100000.0,
            annual_benefits=60000.0,
            annual_costs=10000.0,
            timeframe_years=3
        )
        
        # Total benefits: 60000 * 3 = 180000
        # Total costs: 100000 + (10000 * 3) = 130000
        # ROI: (180000 - 130000) / 130000 * 100 = 38.46%
        # Payback period: 100000 / (60000 - 10000) = 2 years
        
        assert result["roi_percentage"] == pytest.approx(38.46, 0.01)
        assert result["total_benefits"] == 180000.0
        assert result["total_costs"] == 130000.0
        assert result["net_benefit"] == 50000.0
        assert result["annual_net_benefit"] == 50000.0
        assert result["payback_period_years"] == 2.0
        assert result["timeframe_years"] == 3

    def test_calculate_npv(self):
        """Test calculation of Net Present Value."""
        calculator = FinancialCalculator()
        
        result = calculator.calculate_npv(
            initial_investment=-100000.0,
            cash_flows=[40000.0, 50000.0, 60000.0],
            discount_rate=10.0
        )
        
        # Manual calculation:
        # NPV = -100000 + 40000/(1.1)^1 + 50000/(1.1)^2 + 60000/(1.1)^3
        # NPV = -100000 + 36363.64 + 41322.31 + 45051.55 = 22737.50
        
        assert result["npv"] == pytest.approx(22737.50, 0.01)
        assert result["discount_rate"] == 10.0
        assert result["initial_investment"] == -100000.0
        assert result["is_profitable"] == True
        assert len(result["discounted_cash_flows"]) == 3

    def test_calculate_license_costs(self):
        """Test calculation of licensing costs."""
        calculator = FinancialCalculator()
        
        result = calculator.calculate_license_costs(
            license_unit_cost=20.0,
            num_licenses=1000,
            years=3,
            discount_percentage=10.0
        )
        
        # Base cost: 20 * 1000 = 20000
        # Discount: 20000 * 0.1 = 2000
        # Discounted cost: 20000 - 2000 = 18000
        # Total cost: 18000 * 3 = 54000
        
        assert result["total_cost"] == 54000.0
        assert result["annual_cost"] == 18000.0
        assert result["unit_cost"] == 20.0
        assert result["num_licenses"] == 1000
        assert result["discount_percentage"] == 10.0
        assert result["discount_amount"] == 2000.0
        assert result["years"] == 3


class TestDocumentAnalyzer:
    """Tests for the document analyzer tool."""

    def test_analyze_text(self):
        """Test analysis of a text document."""
        analyzer = DocumentAnalyzer()
        
        # Mock file content
        text_content = (
            "# Introduction\n"
            "This is a sample document for testing.\n\n"
            "# Requirements\n"
            "1. Must be scalable\n"
            "2. Must be secure\n"
            "3. Must be cost-effective\n\n"
            "# Conclusion\n"
            "This concludes the document."
        )
        
        # Mock open file
        with patch("builtins.open", mock_open(read_data=text_content)):
            # Mock Path.exists and Path.stat
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = len(text_content)
                    
                    # Test analyzing text file
                    result = analyzer._analyze_text(
                        Path("sample.txt"),
                        extract_type="text",
                        target_sections=["Requirements", "Conclusion"]
                    )
        
        assert "content" in result
        assert result["content"] == text_content
        assert "metadata" in result
        assert result["metadata"]["size"] == len(text_content)
        assert "sections" in result
        assert "Requirements" in result["sections"]
        assert "Conclusion" in result["sections"]
        assert "1. Must be scalable" in result["sections"]["Requirements"]
        assert "This concludes the document." in result["sections"]["Conclusion"]

    def test_extract_key_information(self):
        """Test extraction of key information from text."""
        analyzer = DocumentAnalyzer()
        
        # Sample text with various info types
        text = (
            "Contact us at support@example.com or sales@example.com.\n"
            "Call us at (123) 456-7890 or +1-234-567-8901.\n"
            "Visit our website at https://www.example.com or www.example.org.\n"
            "Meeting scheduled for 01/15/2023 and report due by 2023-06-30.\n"
            "The project costs $10,000.00 with a monthly budget of €2,500."
        )
        
        # Extract various types of information
        result = analyzer.extract_key_information(
            text,
            info_types=["email", "phone", "url", "date", "currency"]
        )
        
        assert "emails" in result
        assert len(result["emails"]) == 2
        assert "support@example.com" in result["emails"]
        assert "sales@example.com" in result["emails"]
        
        assert "phones" in result
        assert len(result["phones"]) == 2
        assert "(123) 456-7890" in result["phones"]
        assert "+1-234-567-8901" in result["phones"]
        
        assert "urls" in result
        assert len(result["urls"]) == 2
        assert "https://www.example.com" in result["urls"]
        assert "www.example.org" in result["urls"]
        
        assert "dates" in result
        assert len(result["dates"]) == 2
        assert "01/15/2023" in result["dates"]
        assert "2023-06-30" in result["dates"]
        
        assert "currencies" in result
        assert len(result["currencies"]) == 2
        assert "$10,000.00" in result["currencies"]
        assert "€2,500" in result["currencies"]

    def test_summarize_document(self):
        """Test document summarization."""
        analyzer = DocumentAnalyzer()
        
        # Long document with multiple sentences
        document = (
            "This is the introduction to our document. It provides context for what follows. "
            "The project involves migrating file servers to cloud storage. "
            "This is an important initiative for the organization. "
            "The migration will take place in several phases. "
            "The first phase involves assessment and planning. "
            "The second phase focuses on data migration. "
            "The third phase includes testing and validation. "
            "The final phase is user training and support. "
            "This migration will improve collaboration and access. "
            "It will also reduce infrastructure costs significantly. "
            "The key success factors include proper planning and communication. "
            "In conclusion, this document outlines the main approach to our migration project."
        )
        
        # Generate summary
        summary = analyzer.summarize_document(document, max_length=200)
        
        # Check summary length
        assert len(summary) <= 200
        assert summary.endswith("...") if len(summary) == 200 else True
        
        # Check that summary contains important sentences
        assert "This is the introduction" in summary
        assert "important initiative" in summary or "key success factors" in summary
        assert "conclusion" in summary 