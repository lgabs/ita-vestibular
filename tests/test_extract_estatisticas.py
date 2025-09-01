"""Unit tests for extract_estatisticas.py module."""

import json
import pytest
import responses
from unittest.mock import patch, mock_open
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from extract_estatisticas import fetch_sections, main, URL


class TestFetchSections:
    """Test cases for the fetch_sections function."""

    @responses.activate
    def test_fetch_sections_basic_structure(self):
        """Test that fetch_sections correctly parses basic HTML structure."""
        # Sample HTML that mimics the ITA statistics page structure
        # Using ASCII-safe characters to avoid encoding issues in tests
        sample_html = """
        <html>
        <body>
            <a id="dados2023">2023</a>
            <div>
                <strong>1 - Numero de candidatos inscritos</strong>
                <table>
                    <tr><th>Categoria</th><th>Homens</th><th>Mulheres</th><th>Total</th></tr>
                    <tr><td>Efetivos</td><td>5000</td><td>1500</td><td>6500</td></tr>
                </table>
            </div>
            <a id="dados2022">2022</a>
            <div>
                <strong>1 - Numero de candidatos inscritos</strong>
                <table>
                    <tr><th>Categoria</th><th>Homens</th><th>Mulheres</th><th>Total</th></tr>
                    <tr><td>Efetivos</td><td>4800</td><td>1400</td><td>6200</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        # Check that we got data for both years
        assert "2023" in result
        assert "2022" in result
        
        # Check structure of 2023 data
        assert len(result["2023"]) == 1
        assert result["2023"][0]["heading"] == "1 - Numero de candidatos inscritos"
        assert len(result["2023"][0]["table"]) == 2  # Header + 1 data row
        
        # Check table content
        table_2023 = result["2023"][0]["table"]
        assert table_2023[0] == ["Categoria", "Homens", "Mulheres", "Total"]
        assert table_2023[1] == ["Efetivos", "5000", "1500", "6500"]

    @responses.activate
    def test_fetch_sections_multiple_tables_per_year(self):
        """Test handling of multiple tables within a single year section."""
        sample_html = """
        <html>
        <body>
            <a name="dados2023">2023</a>
            <div>
                <strong>1 - Numero de candidatos inscritos</strong>
                <table>
                    <tr><th>Categoria</th><th>Total</th></tr>
                    <tr><td>Efetivos</td><td>6500</td></tr>
                </table>
                <strong>2 - Especialidade escolhida</strong>
                <table>
                    <tr><th>Curso</th><th>Percentual</th></tr>
                    <tr><td>Aeroespacial</td><td>25%</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        assert "2023" in result
        assert len(result["2023"]) == 2
        
        # Verify we have both tables with expected content (order doesn't matter)
        tables = result["2023"]
        
        # Check that we have the expected data in the tables
        found_efetivos = False
        found_aeroespacial = False
        
        for table in tables:
            for row in table["table"]:
                if "Efetivos" in row and "6500" in row:
                    found_efetivos = True
                if "Aeroespacial" in row and "25%" in row:
                    found_aeroespacial = True
        
        assert found_efetivos, "Should find Efetivos data"
        assert found_aeroespacial, "Should find Aeroespacial data"

    @responses.activate
    def test_fetch_sections_encoding_handling(self):
        """Test that the function correctly handles ISO-8859-1 encoding."""
        # HTML with Portuguese characters that require proper encoding
        sample_html = """
        <html>
        <body>
            <a id="dados2023">2023</a>
            <div>
                <strong>1 - Número de candidatos inscritos</strong>
                <table>
                    <tr><th>Categoria</th><th>Total</th></tr>
                    <tr><td>Efetivos</td><td>6500</td></tr>
                </table>
            </div>
        </body>
        </html>
        """.encode('iso-8859-1')
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        assert "2023" in result
        assert result["2023"][0]["heading"] == "1 - Número de candidatos inscritos"

    @responses.activate
    def test_fetch_sections_no_matching_anchors(self):
        """Test behavior when no matching anchor tags are found."""
        sample_html = """
        <html>
        <body>
            <a id="other-anchor">Other</a>
            <div>Some content</div>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        assert result == {}

    @responses.activate
    def test_fetch_sections_empty_tables(self):
        """Test handling of empty tables."""
        sample_html = """
        <html>
        <body>
            <a id="dados2023">2023</a>
            <div>
                <strong>1 - Test heading</strong>
                <table></table>
                <table>
                    <tr><th>Header</th></tr>
                    <tr><td>Data</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        assert "2023" in result
        # Should only include the non-empty table
        assert len(result["2023"]) == 1
        assert len(result["2023"][0]["table"]) == 2

    @responses.activate
    def test_fetch_sections_network_error(self):
        """Test handling of network errors."""
        responses.add(
            responses.GET,
            URL,
            body=responses.ConnectionError("Network error")
        )
        
        with pytest.raises(Exception):  # requests will raise an exception
            fetch_sections(URL)

    @responses.activate
    def test_fetch_sections_malformed_html(self):
        """Test handling of malformed HTML."""
        sample_html = """
        <html>
        <body>
            <a id="dados2023">2023</a>
            <div>
                <strong>1 - Test heading</strong>
                <table>
                    <tr><th>Header</th>
                    <tr><td>Data</td></tr>
                </table>
            </div>
        </body>
        """  # Missing closing </th> tag
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        # BeautifulSoup should handle malformed HTML gracefully
        result = fetch_sections(URL)
        
        assert "2023" in result
        assert len(result["2023"]) == 1

    @responses.activate
    def test_fetch_sections_nested_elements(self):
        """Test handling of nested elements within table cells."""
        sample_html = """
        <html>
        <body>
            <a id="dados2023">2023</a>
            <div>
                <strong>1 - Test heading</strong>
                <table>
                    <tr>
                        <th>Header</th>
                        <th>Complex Header</th>
                    </tr>
                    <tr>
                        <td>Simple Data</td>
                        <td><span>Nested</span> <strong>Content</strong></td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        assert "2023" in result
        table = result["2023"][0]["table"]
        # Should extract text from nested elements with spaces
        assert table[1] == ["Simple Data", "Nested Content"]

    @responses.activate
    def test_fetch_sections_multiple_years_ordering(self):
        """Test that multiple years are processed correctly."""
        sample_html = """
        <html>
        <body>
            <a id="dados2025">2025</a>
            <div>
                <strong>1 - Data 2025</strong>
                <table>
                    <tr><td>2025 Data</td></tr>
                </table>
            </div>
            <a name="dados2024">2024</a>
            <div>
                <strong>1 - Data 2024</strong>
                <table>
                    <tr><td>2024 Data</td></tr>
                </table>
            </div>
            <a id="dados2023">2023</a>
            <div>
                <strong>1 - Data 2023</strong>
                <table>
                    <tr><td>2023 Data</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=sample_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        assert "2025" in result
        assert "2024" in result
        assert "2023" in result
        
        assert result["2025"][0]["table"][0] == ["2025 Data"]
        assert result["2024"][0]["table"][0] == ["2024 Data"]
        assert result["2023"][0]["table"][0] == ["2023 Data"]


class TestMainFunction:
    """Test cases for the main function."""

    @patch('extract_estatisticas.fetch_sections')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_main_function_success(self, mock_makedirs, mock_file, mock_fetch):
        """Test successful execution of main function."""
        # Mock the fetch_sections return value
        mock_data = {
            "2023": [
                {
                    "heading": "1 - Test heading",
                    "table": [["Header"], ["Data"]]
                }
            ]
        }
        mock_fetch.return_value = mock_data
        
        # Call main function
        main()
        
        # Verify fetch_sections was called with correct URL
        mock_fetch.assert_called_once_with(URL)
        
        # Verify file was opened for writing
        mock_file.assert_called_once_with(
            "estatisticas/estatisticas.json", "w", encoding="utf-8"
        )
        
        # Verify JSON was written
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        written_data = json.loads(written_content)
        assert written_data == mock_data

    @patch('extract_estatisticas.fetch_sections')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_function_empty_data(self, mock_file, mock_fetch):
        """Test main function with empty data."""
        mock_fetch.return_value = {}
        
        main()
        
        mock_fetch.assert_called_once_with(URL)
        mock_file.assert_called_once()
        
        # Verify empty dict was written
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        written_data = json.loads(written_content)
        assert written_data == {}

    @patch('extract_estatisticas.fetch_sections')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_main_function_file_error(self, mock_file, mock_fetch):
        """Test main function when file writing fails."""
        mock_fetch.return_value = {"2023": []}
        
        with pytest.raises(IOError):
            main()

    @patch('extract_estatisticas.fetch_sections', side_effect=Exception("Network error"))
    def test_main_function_fetch_error(self, mock_fetch):
        """Test main function when fetch_sections fails."""
        with pytest.raises(Exception):
            main()


class TestIntegration:
    """Integration tests that test the full pipeline with realistic data."""

    @responses.activate
    @patch('builtins.open', new_callable=mock_open)
    def test_full_pipeline_realistic_data(self, mock_file):
        """Test the full pipeline with realistic ITA statistics HTML."""
        # Based on actual ITA HTML structure - using ASCII characters to avoid encoding issues
        realistic_html = """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
        <head>
        <title>Estatisticas de Vestibulares Anteriores</title>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
        </head>
        <body>
            <A id=dados2023 name=dados2023></A><br> 
            <div align="center"><font size="5"><STRONG>Dados 
            Estatisticos Relativos ao Exame Vestibular de 2023</STRONG></font></div>
            <FONT size=2><strong><br>
            1 - Numero de candidatos inscritos</strong><br>
            </FONT><br> 
            <table width="60%" border="1" align="center" cellspacing="0">
                <tr bgcolor="#f3f3f3"> 
                    <td width="28%"><div align="center"><font size="2"><strong>Tipo de Vaga</strong></font></div></td>
                    <td width="18%"><div align="center"><font size="2"><strong>Homens</strong></font></div></td>
                    <td width="18%"><div align="center"><font size="2"><strong>Mulheres</strong></font></div></td>
                    <td width="18%"><div align="center"><font size="2"><strong>Total</strong></font></div></td>
                    <td width="18%"><font size="2">&nbsp;</font></td>
                </tr>
                <tr> 
                    <td><div align="left"><font size="2">Optantes</font></div></td>
                    <td><div align="center"><font size="2">2.747</font></div></td>
                    <td><div align="center"><font size="2">944</font></div></td>
                    <td><div align="center"><font size="2">3.691</font></div></td>
                    <td><div align="center"><font size="2">39,4%</font></div></td>
                </tr>
                <tr> 
                    <td><div align="left"><font size="2">Nao Optantes</font></div></td>
                    <td><div align="center"><font size="2">3.399</font></div></td>
                    <td><div align="center"><font size="2">931</font></div></td>
                    <td><div align="center"><font size="2">4.330</font></div></td>
                    <td><div align="center"><font size="2">46,2%</font></div></td>
                </tr>
                <tr> 
                    <td><div align="left"><font size="2">Treineiros</font></div></td>
                    <td><div align="center"><font size="2">1.000</font></div></td>
                    <td><div align="center"><font size="2">343</font></div></td>
                    <td><div align="center"><font size="2">1.343</font></div></td>
                    <td><div align="center"><font size="2">14,3%</font></div></td>
                </tr>
            </table>
            <br>
            <FONT size=2><strong>2 - Especialidade escolhida em primeira opcao</strong><br>
            </FONT><br>
            <TABLE width=75% border=1 align="center" cellSpacing=0>
                <TR bgColor=#f3f3f3> 
                    <TD width="40%"><div align="center"><strong><font size="2">Curso</font></strong></div></TD>
                    <TD width="20%"><div align="center"><strong><font size="2">Efetivos</font></strong></div></TD>
                    <TD width="20%"><div align="center"><strong><font size="2">Treineiros</font></strong></div></TD>
                </TR>
                <TR> 
                    <TD><FONT size=2>Engenharia Aeroespacial</FONT></TD>
                    <TD><div align="center"><FONT size=2>18,5%</FONT></div></TD>
                    <TD><div align="center"><FONT size=2>22,1%</FONT></div></TD>
                </TR>
            </TABLE>
            
            <A id=dados2022 name=dados2022></A><br> 
            <div align="center"><font size="5"><STRONG>Dados 
            Estatisticos Relativos ao Exame Vestibular de 2022</STRONG></font></div>
            <FONT size=2><strong><br>
            1 - Numero de candidatos inscritos</strong><br>
            </FONT><br> 
            <table width="60%" border="1" align="center" cellspacing="0">
                <tr bgcolor="#f3f3f3"> 
                    <td><div align="center"><font size="2"><strong>Categoria</strong></font></div></td>
                    <td><div align="center"><font size="2"><strong>Homens</strong></font></div></td>
                    <td><div align="center"><font size="2"><strong>Mulheres</strong></font></div></td>
                    <td><div align="center"><font size="2"><strong>Total</strong></font></div></td>
                </tr>
                <tr> 
                    <td><div align="left"><font size="2">Efetivos</font></div></td>
                    <td><div align="center"><font size="2">5.123</font></div></td>
                    <td><div align="center"><font size="2">1.398</font></div></td>
                    <td><div align="center"><font size="2">6.521</font></div></td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            URL,
            body=realistic_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        # Run the main function
        main()
        
        # Verify the file was written
        mock_file.assert_called_once_with(
            "estatisticas/estatisticas.json", "w", encoding="utf-8"
        )
        
        # Parse the written content
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        result = json.loads(written_content)
        
        # Verify structure
        assert "2023" in result
        assert "2022" in result
        
        # Verify 2023 data structure
        assert len(result["2023"]) == 2  # Two tables
        
        # Check that we have the expected table data (order doesn't matter)
        tables_2023 = result["2023"]
        
        # Find the registration table (has columns like Tipo de Vaga, Homens, Mulheres, Total)
        registration_table = None
        specialization_table = None
        
        for table in tables_2023:
            if any("Tipo de Vaga" in row for row in table["table"]):
                registration_table = table
            elif any("Curso" in row for row in table["table"]):
                specialization_table = table
        
        # Verify registration table exists and has expected data
        assert registration_table is not None, "Should have registration table"
        assert len(registration_table["table"]) == 4  # Header + 3 data rows
        assert any("Optantes" in row for row in registration_table["table"])
        assert any("2.747" in row for row in registration_table["table"])
        
        # Verify specialization table exists and has expected data  
        assert specialization_table is not None, "Should have specialization table"
        assert any("Engenharia Aeroespacial" in row for row in specialization_table["table"])
        
        # Verify 2022 data
        assert len(result["2022"]) == 1
        # Check that 2022 has the expected data content
        table_2022 = result["2022"][0]
        assert any("Efetivos" in row for row in table_2022["table"])
        assert any("5.123" in row for row in table_2022["table"])

    @responses.activate
    def test_with_actual_ita_html(self):
        """Test with actual downloaded ITA HTML to ensure real-world compatibility."""
        # Read the actual HTML file if it exists
        try:
            with open('/tmp/ita_estatisticas.html', 'r', encoding='iso-8859-1') as f:
                actual_html = f.read()
        except FileNotFoundError:
            pytest.skip("Actual ITA HTML file not available")
        
        responses.add(
            responses.GET,
            URL,
            body=actual_html,
            status=200,
            content_type='text/html; charset=iso-8859-1'
        )
        
        result = fetch_sections(URL)
        
        # Basic structure validation - should have multiple years
        assert len(result) > 10  # ITA has data from 2012 onwards
        
        # Check that recent years are present
        assert "2025" in result
        assert "2024" in result
        assert "2023" in result
        
        # Each year should have some data
        for year, data in result.items():
            assert len(data) > 0, f"Year {year} should have some data"
            for table_data in data:
                assert "heading" in table_data
                assert "table" in table_data
                assert len(table_data["table"]) > 0, f"Table in {year} should have rows"


if __name__ == "__main__":
    pytest.main([__file__])
