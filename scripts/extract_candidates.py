import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from rich.pretty import pprint
from prompts import YEARLY_REPORT_SYSTEM_PROMPT
from models import YearlyReport


# Load environment variables
load_dotenv()

# Initialize OpenAI async client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_data() -> Dict[str, List[Dict[str, Any]]]:
    """Load the raw data from the JSON file."""
    # Note: Using a local copy for development to avoid re-downloading
    with open('estatisticas/estatisticas.json', 'r', encoding='utf-8') as fh:
        return json.load(fh)

def convert_tables_to_text(tables: List[Dict[str, Any]]) -> str:
    """Converts a list of table dictionaries into a formatted string."""
    text_representation = []
    for table_data in tables:
        heading = table_data.get('heading', 'No Heading')
        table = table_data.get('table', [])

        text_representation.append(f"--- TABLE: {heading} ---")
        if table:
            # Convert each row to a CSV-like string
            for row in table:
                text_representation.append(",".join(map(str, row)))
        text_representation.append("--- END TABLE ---\n")
    return "\n".join(text_representation)


async def process_year_data(year: str, tables: List[Dict[str, Any]]) -> Optional[YearlyReport]:
    """Process all data for a specific year using OpenAI API."""

    print(f"-> Processing year: {year}")
    all_tables_text = convert_tables_to_text(tables)

    if not YEARLY_REPORT_SYSTEM_PROMPT:
        print(f"Skipping year {year} due to missing system prompt.")
        return None

    user_prompt = f"**Tables for year {year}:**\n\n{all_tables_text}"

    try:
        response = await client.responses.parse(
            model="o4-mini",
            input=[
                {"role": "system", "content": YEARLY_REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            text_format=YearlyReport,
        )
        print(f"<- Finished processing year: {year}")
        return response.output_parsed

    except Exception as e:
        print(f"An error occurred while processing year {year}: {e}")
        print(f"<- Finished processing year: {year} (with error)")
        return None


async def extract_all_data(data: Dict[str, List[Dict[str, Any]]]):
    """Extracts all report data from the raw JSON data in parallel."""
    tasks = [process_year_data(year, tables) for year, tables in data.items() if int(year) < 2024]
    yearly_reports = await asyncio.gather(*tasks)
    return [report for report in yearly_reports if report is not None]


def save_reports_to_json(reports: List[YearlyReport], output_dir: str = 'estatisticas/processed'):
    """Saves each yearly report to its own JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    for report in reports:
        output_path = os.path.join(output_dir, f"{report.year}_report.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            # Use Pydantic's model_dump_json for clean, indented output
            f.write(report.model_dump_json(indent=2))
        print(f"Saved report for year {report.year} to {output_path}")


async def main():
    """Main function to run the data extraction process."""
    print("Loading raw data...")
    raw_data = load_data()

    print("\nExtracting structured data from tables for all years...")
    yearly_reports = await extract_all_data(raw_data)

    print("\nSample of extracted data for the first report:")
    if yearly_reports:
        pprint(yearly_reports[0], max_length=20)
    else:
        print("No reports were extracted.")

    print("\nSaving yearly reports to individual JSON files...")
    save_reports_to_json(yearly_reports)

    print("\nExtraction process complete.")


if __name__ == "__main__":
    asyncio.run(main())
