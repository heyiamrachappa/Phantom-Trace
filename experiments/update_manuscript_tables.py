import re

with open('results/metrics/v3/compiled_manuscript_tables.md', 'r') as f:
    compiled_text = f.read()

with open('manuscript.md', 'r') as f:
    man_text = f.read()

def extract_table(compiled_text, section_header):
    match = re.search(section_header + r'.*?(\| Model \|.*?)\n\n', compiled_text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find table for {section_header}")
    table_lines = match.group(1).strip().split('\n')
    
    # Remove 'Prev. Baseline' column if it exists
    new_table_lines = []
    for line in table_lines:
        parts = line.split('|')
        if len(parts) > 2:
            new_line = '|'.join(parts[:-2]) + '|'
            # Shorten model names
            new_line = new_line.replace('Random Forest (RF)', '**RF**')
            new_line = new_line.replace('XGBoost (XGB)', '**XGB**')
            new_line = new_line.replace('Support Vector Machine (SVM)', 'SVM')
            new_line = new_line.replace('Isolation Forest (IF)', 'IF')
            new_line = new_line.replace('Multi-Layer Perceptron (MLP)', 'MLP')
            new_table_lines.append(new_line)
    return '\n'.join(new_table_lines)

table_time = extract_table(compiled_text, r'### 1\.1 In-Distribution Holdout \(`time_wise`\)')
table_pcap = extract_table(compiled_text, r'### 1\.2 Synthetic-to-Real Transfer \(`pcap_wise`\)')
table_cic_unsw = extract_table(compiled_text, r'### 1\.5 Reverse Cross-Dataset Transfer: CIC → UNSW \(`cic_to_unsw`\)')
table_unsw_cic = extract_table(compiled_text, r'### 1\.4 Primary Cross-Dataset Transfer: UNSW → CIC \(`unsw_to_cic`\)')

def replace_table_in_manuscript(man_text, section_header, new_table):
    # Find the section header, then replace the first markdown table after it
    # Find start of section
    start_idx = man_text.find(section_header)
    if start_idx == -1:
        raise ValueError(f"Section {section_header} not found in manuscript")
        
    # Find start of table
    table_start = man_text.find('| Model |', start_idx)
    if table_start == -1:
        raise ValueError("Table start not found")
        
    # Find end of table (double newline)
    table_end = man_text.find('\n\n', table_start)
    if table_end == -1:
        table_end = len(man_text)
        
    return man_text[:table_start] + new_table + man_text[table_end:]

man_text = replace_table_in_manuscript(man_text, '### 5.1 In-Distribution Performance (Time-Wise Split)', table_time)
man_text = replace_table_in_manuscript(man_text, '### 5.2 Cross-Corpus Generalization (Pcap-Wise Split)', table_pcap)
man_text = replace_table_in_manuscript(man_text, '### 5.3 Reverse Cross-Dataset Split (Train: CIC → Test: UNSW)', table_cic_unsw)
man_text = replace_table_in_manuscript(man_text, '### 5.4 Cross-Dataset Split (Train: UNSW → Test: CIC)', table_unsw_cic)

with open('manuscript.md', 'w') as f:
    f.write(man_text)

print("Tables updated in manuscript.md")
