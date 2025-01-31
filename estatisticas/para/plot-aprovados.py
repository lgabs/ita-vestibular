import re
import matplotlib.pyplot as plt
import pandas as pd

def parse_markdown_table(table_markdown: str) -> pd.DataFrame:
    """
    Parse a two-column Markdown table (Ano de Aprovação, Aprovados)
    and return a pandas DataFrame with integer columns 'Ano' and 'Aprovados'.
    """
    lines = table_markdown.strip().split("\n")
    # Skip the header lines (first two lines with headers and separator)
    content_lines = lines[2:]
    
    data = []
    for line in content_lines:
        columns = line.split("|")
        if len(columns) < 3:
            continue
        
        year_str = columns[1].strip()       # e.g. "1946 (T-51)"
        aprovados_str = columns[2].strip()  # e.g. "1"
        
        # Extract the numerical year from the start of year_str
        match_year = re.match(r"(\d+)", year_str)
        if not match_year:
            continue
        
        year = int(match_year.group(0))
        aprovados = int(aprovados_str)
        data.append((year, aprovados))
    
    df = pd.DataFrame(data, columns=["Ano", "Aprovados"])
    return df

if __name__ == "__main__":
    # Lê o conteúdo de aprovados-para-por-ano.md no mesmo diretório
    with open("aprovados-para-por-ano.md", "r", encoding="utf-8") as f:
        markdown_table = f.read()
    
    # Converte o conteúdo Markdown em DataFrame
    df = parse_markdown_table(markdown_table)
    
    # Ordena por ano
    df.sort_values(by="Ano", inplace=True)
    
    # Configura a figura
    plt.figure(figsize=(10, 6))
    plt.plot(df["Ano"], df["Aprovados"], marker="o", linestyle="-", color="b")
    plt.xlabel("Ano de Aprovação")
    plt.ylabel("Número de Aprovados")
    plt.title("Aprovados por Ano no Estado do Pará")
    
    # Define os rótulos do eixo X em intervalos de 5 anos
    min_year = df["Ano"].min()
    max_year = df["Ano"].max()
    plt.xticks(range(min_year, max_year + 1, 5))
    
    plt.grid(True)
    plt.show()
