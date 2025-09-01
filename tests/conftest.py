"""Shared test fixtures and configuration for the test suite."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_ita_html():
    """Provide sample ITA statistics HTML for testing."""
    return """
    <html>
    <body>
        <a id="dados2023">2023</a>
        <div>
            <strong>1 - Número de candidatos inscritos</strong>
            <table>
                <tr><th>Categoria</th><th>Homens</th><th>Mulheres</th><th>Total</th></tr>
                <tr><td>Efetivos</td><td>5000</td><td>1500</td><td>6500</td></tr>
                <tr><td>Treineiros</td><td>800</td><td>200</td><td>1000</td></tr>
            </table>
        </div>
        <a name="dados2022">2022</a>
        <div>
            <strong>1 - Número de candidatos inscritos</strong>
            <table>
                <tr><th>Categoria</th><th>Homens</th><th>Mulheres</th><th>Total</th></tr>
                <tr><td>Efetivos</td><td>4800</td><td>1400</td><td>6200</td></tr>
            </table>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def expected_parsed_data():
    """Provide expected parsed data structure for testing."""
    return {
        "2023": [
            {
                "heading": "1 - Número de candidatos inscritos",
                "table": [
                    ["Categoria", "Homens", "Mulheres", "Total"],
                    ["Efetivos", "5000", "1500", "6500"],
                    ["Treineiros", "800", "200", "1000"]
                ]
            }
        ],
        "2022": [
            {
                "heading": "1 - Número de candidatos inscritos", 
                "table": [
                    ["Categoria", "Homens", "Mulheres", "Total"],
                    ["Efetivos", "4800", "1400", "6200"]
                ]
            }
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # Ensure we're in the correct directory for relative imports
    original_cwd = os.getcwd()
    test_dir = Path(__file__).parent.parent
    os.chdir(test_dir)
    
    yield
    
    # Restore original directory
    os.chdir(original_cwd)
