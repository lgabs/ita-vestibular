import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Use 'fivethirtyeight' style for plots
plt.style.use('fivethirtyeight')

PROCESSED_DATA_DIR = 'estatisticas/processed'
OUTPUT_DIR = 'estatisticas/geral'

def parse_percentage(p_str):
    """Converts a percentage string (e.g., '10,7%') to a float."""
    if p_str is None:
        return np.nan
    return float(p_str.replace('%', '').replace(',', '.'))

def load_all_data():
    """Loads all JSON reports from the processed data directory."""
    all_reports = []
    for filename in sorted(os.listdir(PROCESSED_DATA_DIR)):
        if filename.endswith('.json'):
            filepath = os.path.join(PROCESSED_DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    report = json.load(f)
                    all_reports.append(report)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {filename}")
    return all_reports

def plot_total_registrations(reports):
    """
    Plots the total number of 'Efetivos' vs 'Treineiros' over the years.
    'Efetivos' is a consolidated category including 'Ativa', 'Optantes', 'Reserva', etc.
    """
    years = [r['year'] for r in reports]

    data = {'Efetivos': [], 'Treineiros': []}

    # Aliases for different candidate types
    efetivos_aliases = ['Efetivos', 'Ativa', 'Optantes', 'Reserva', 'Não Optantes']
    treineiros_aliases = ['Treineiros']

    for report in reports:
        registrations_list = report.get('registrations', [])
        if registrations_list is None:
            registrations_list = []

        efetivos_total = 0
        treineiros_total = 0

        for item in registrations_list:
            category = item.get('category')
            total = item.get('total', 0)

            if category in efetivos_aliases:
                efetivos_total += total
            elif category in treineiros_aliases:
                treineiros_total += total

        # Fallback for older data where totals are in exam_locations
        if efetivos_total == 0 and treineiros_total == 0:
            locations_data = report.get('exam_locations', [])
            if locations_data and isinstance(locations_data, list) and len(locations_data) > 0:
                total_loc = next((loc for loc in locations_data[0].get('locations', []) if loc.get('location') == 'Total'), None)
                if total_loc:
                    # Assume all are 'Efetivos' if no other breakdown is available
                    efetivos_total = total_loc.get('registered_total', 0)

        data['Efetivos'].append(efetivos_total if efetivos_total > 0 else np.nan)
        data['Treineiros'].append(treineiros_total if treineiros_total > 0 else np.nan)

    plt.figure(figsize=(12, 8))
    plt.plot(years, data['Efetivos'], marker='o', linestyle='-', label='Efetivos')
    plt.plot(years, data['Treineiros'], marker='o', linestyle='--', label='Treineiros')

    plt.title('Inscritos no Vestibular do ITA: Efetivos vs. Treineiros')
    plt.xlabel('Ano')
    plt.ylabel('Número de Inscritos')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, '1a_total_registrations_overview.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")

def plot_efetivos_breakdown(reports):
    """Plots the breakdown of 'Efetivos' candidates over time."""
    years = []
    data = {'Ativa/Optantes': [], 'Reserva/Não Optantes': []}

    # Aliases
    ativa_aliases = ['Ativa', 'Optantes']
    reserva_aliases = ['Reserva', 'Não Optantes']

    for report in reports:
        registrations_list = report.get('registrations', [])
        if registrations_list is None:
            continue

        ativa_total = 0
        reserva_total = 0
        has_breakdown = False

        for item in registrations_list:
            category = item.get('category')
            total = item.get('total', 0)
            if category in ativa_aliases:
                ativa_total += total
                has_breakdown = True
            elif category in reserva_aliases:
                reserva_total += total
                has_breakdown = True

        if has_breakdown:
            years.append(report['year'])
            data['Ativa/Optantes'].append(ativa_total)
            data['Reserva/Não Optantes'].append(reserva_total)

    if not years:
        print("No breakdown data found for 'Efetivos' candidates. Skipping plot.")
        return

    plt.figure(figsize=(12, 8))
    plt.stackplot(years, data['Ativa/Optantes'], data['Reserva/Não Optantes'],
                  labels=['Ativa / Optantes', 'Reserva / Não Optantes'], alpha=0.8)

    plt.title('Composição dos Candidatos "Efetivos" ao Longo do Tempo')
    plt.xlabel('Ano')
    plt.ylabel('Número de Inscritos')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, '1b_efetivos_breakdown.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")

def plot_gender_dynamics(reports):
    """Plots the gender dynamics of candidates over the years."""
    years = [r['year'] for r in reports]
    men = []
    women = []

    for report in reports:
        registrations_list = report.get('registrations', [])
        if registrations_list is None:
            registrations_list = []
        total_reg = next((item for item in registrations_list if item['category'] == 'Total'), None)
        if total_reg:
            men.append(total_reg.get('men', 0))
            women.append(total_reg.get('women', 0))
        else:
            men.append(0)
            women.append(0)

    plt.figure(figsize=(12, 8))
    plt.stackplot(years, women, men, labels=['Mulheres', 'Homens'], alpha=0.8)

    plt.title('Dinâmica de Gênero dos Candidatos ao ITA')
    plt.xlabel('Ano')
    plt.ylabel('Número de Candidatos')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, '2_gender_dynamics.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")

def plot_registrations_by_state(reports):
    """Plots registrations by state for the most recent year."""
    if not reports:
        print("No reports to process.")
        return

    latest_report = reports[-1]
    year = latest_report['year']

    locations_data = latest_report.get('exam_locations', [])
    if not locations_data:
        print(f"No exam locations data for {year}.")
        return

    # The data can be nested, get the actual list of locations
    locations = locations_data[0].get('locations', [])

    state_counts = {}
    for loc in locations:
        if loc['location'] == 'Total':
            continue

        parts = loc['location'].replace(' -', '-').split('-')
        if len(parts) > 1:
            state = parts[-1].strip().upper()
            total = loc.get('registered_total', 0)
            state_counts[state] = state_counts.get(state, 0) + total

    if not state_counts:
        print(f"Could not extract any state data for {year}.")
        return

    df = pd.DataFrame(list(state_counts.items()), columns=['State', 'Count'])
    df = df.sort_values('Count', ascending=True)

    plt.figure(figsize=(12, 10))
    plt.barh(df['State'], df['Count'])

    plt.title(f'Número de Inscritos por Estado ({year})')
    plt.xlabel('Número de Inscritos')
    plt.ylabel('Estado')
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, '3_registrations_by_state.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")


def plot_school_origins(reports):
    """Plots the educational background of candidates."""
    records = []
    for report in reports:
        year = report['year']
        school_origins_list = report.get('school_origins', [])
        if school_origins_list is None:
            school_origins_list = []
        for origin in school_origins_list:
            if origin.get('category') == 'Efetivos':
                records.append({
                    'year': year,
                    'school_type': origin['school_type'],
                    'percentage': parse_percentage(origin['percentage'])
                })

    if not records:
        print("No school origin data for 'Efetivos' found.")
        return

    df = pd.DataFrame(records)

    # Group schools into Public/Private
    public_types = ['Federal', 'Estadual', 'Municipal']
    df['type_agg'] = df['school_type'].apply(lambda x: 'Pública' if x in public_types else ('Particular' if x == 'Particular' else 'Preparatório'))

    # Pivot for stacked bar
    pivot_df = df[df['type_agg'].isin(['Pública', 'Particular'])].pivot_table(
        index='year', columns='type_agg', values='percentage', aggfunc='sum'
    ).fillna(0)

    # Ensure we have both columns, even if one is all zero for some datasets
    if 'Pública' not in pivot_df: pivot_df['Pública'] = 0
    if 'Particular' not in pivot_df: pivot_df['Particular'] = 0

    # Normalize to 100%
    pivot_df_normalized = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

    # Pivot for preparatory course
    prep_df = df[df['type_agg'] == 'Preparatório'].pivot_table(
        index='year', columns='type_agg', values='percentage'
    ).fillna(0)

    if 'Preparatório' not in prep_df: prep_df['Preparatório'] = 0

    fig, ax = plt.subplots(figsize=(14, 8))

    pivot_df_normalized[['Particular', 'Pública']].plot(
        kind='bar', stacked=True, ax=ax, width=0.7,
        label=['Particular', 'Pública']
    )

    ax.set_title('Origem Escolar dos Candidatos (Efetivos)')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Proporção de Candidatos (%)')
    ax.legend(title='Tipo de Escola')
    ax.tick_params(axis='x', rotation=45)

    # Line plot for preparatory courses
    ax2 = ax.twinx()
    ax2.plot(ax.get_xticks(), prep_df['Preparatório'], color='green', marker='o', linestyle='--', label='Fizeram Curso Preparatório')
    ax2.set_ylabel('Candidatos com Curso Preparatório (%)', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, '4_school_origins.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")

def main():
    """Main function to generate all plots for part 1."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    reports = load_all_data()
    if not reports:
        print("No data found in 'estatisticas/processed/'. Exiting.")
        return

    plot_total_registrations(reports)
    plot_efetivos_breakdown(reports)
    plot_gender_dynamics(reports)
    plot_registrations_by_state(reports)
    plot_school_origins(reports)

    print("\nAll Part 1 plots have been generated in 'estatisticas/geral/'.")

if __name__ == '__main__':
    main()
