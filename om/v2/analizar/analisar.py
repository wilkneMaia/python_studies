import json

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd


# Carregar o arquivo JSON
with open('combined_maintenance_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Converter os dados para um DataFrame do pandas
df = pd.json_normalize(data)

# Verificar as primeiras linhas do DataFrame
print(df.head())

# Verificar a distribuição das ordens de manutenção (OM) por centro emissor (issue_center)
issue_center_counts = df['issue_center'].value_counts()

# Analisar a criticidade das ordens de manutenção
criticidade_counts = df['criticality'].value_counts()

# Verificar a distribuição das ordens de manutenção por local de instalação (installation_location)
installation_location_counts = df['installation_location'].value_counts()

# Calcular a duração média das ordens de manutenção
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
mean_duration = df['duration'].mean()

# Identificar quantas ordens possuem equipamentos associados
orders_with_equipment = df[df['equipment_number'] != ""].shape[0]
total_orders = df.shape[0]

# Distribuição de Criticidade por Centro Emissor
crit_by_center = pd.crosstab(df['issue_center'], df['criticality'])

# Análise de Duração por Criticidade e Centro Emissor
mean_duration_by_crit_center = df.groupby(['issue_center', 'criticality'])[
    'duration'].mean().unstack()

# Visualização Gráfica
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='issue_center', hue='criticality')
plt.title('Distribuição de Criticidade por Centro Emissor')
plt.xlabel('Centro Emissor')
plt.ylabel('Contagem')
plt.legend(title='Criticidade')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('crit_by_center.png')

plt.figure(figsize=(10, 6))
mean_duration_by_crit_center.plot(kind='bar', stacked=True)
plt.title('Duração Média por Criticidade e Centro Emissor')
plt.xlabel('Centro Emissor')
plt.ylabel('Duração Média (h)')
plt.legend(title='Criticidade')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('mean_duration_by_crit_center.png')

# Salvar as análises em um arquivo Excel
output_excel_path = 'maintenance_analysis.xlsx'
with pd.ExcelWriter(output_excel_path) as writer:
    df.to_excel(writer, sheet_name='Dados Brutos', index=False)
    issue_center_counts.to_excel(writer, sheet_name='Distribuição por Centro')
    criticidade_counts.to_excel(writer, sheet_name='Distribuição Criticidade')
    installation_location_counts.to_excel(
        writer, sheet_name='Distribuição Local')
    pd.DataFrame({'Duração Média (h)': [mean_duration]}).to_excel(
        writer, sheet_name='Duração Média')
    pd.DataFrame({'Ordens com Equipamento': [orders_with_equipment], 'Total de Ordens': [
                 total_orders]}).to_excel(writer, sheet_name='Ordens com Equipamento')
    crit_by_center.to_excel(writer, sheet_name='Criticidade por Centro')
    mean_duration_by_crit_center.to_excel(
        writer, sheet_name='Duração por Criticidade e Centro')

print(f"Análises salvas em {output_excel_path}")
print("Gráficos salvos em crit_by_center.png e mean_duration_by_crit_center.png")


#


# # Carregar o arquivo JSON
# with open('/mnt/data/combined_maintenance_data.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# # Converter os dados para um DataFrame do pandas
# df = pd.json_normalize(data)

# # Verificar as primeiras linhas do DataFrame
# print(df.head())

# # Verificar a distribuição das ordens de manutenção (OM) por centro emissor (issue_center)
# issue_center_counts = df['issue_center'].value_counts()
# print("Distribuição das ordens de manutenção por centro emissor:")
# print(issue_center_counts)

# # Analisar a criticidade das ordens de manutenção
# criticidade_counts = df['criticality'].value_counts()
# print("\nDistribuição da criticidade das ordens de manutenção:")
# print(criticidade_counts)

# # Verificar a distribuição das ordens de manutenção por local de instalação (installation_location)
# installation_location_counts = df['installation_location'].value_counts()
# print("\nDistribuição das ordens de manutenção por local de instalação:")
# print(installation_location_counts)

# # Calcular a duração média das ordens de manutenção
# df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
# mean_duration = df['duration'].mean()
# print("\nDuração média das ordens de manutenção (em horas):")
# print(mean_duration)

# # Identificar quantas ordens possuem equipamentos associados
# orders_with_equipment = df[df['equipment_number'] != ""].shape[0]
# total_orders = df.shape[0]
# print("\nNúmero de ordens com equipamentos associados:")
# print(f"{orders_with_equipment} de {total_orders}")

# # Salvar as análises em um arquivo Excel
# output_excel_path = '/mnt/data/maintenance_analysis.xlsx'
# with pd.ExcelWriter(output_excel_path) as writer:
#     df.to_excel(writer, sheet_name='Dados Brutos', index=False)
#     issue_center_counts.to_excel(writer, sheet_name='Distribuição por Centro')
#     criticidade_counts.to_excel(writer, sheet_name='Distribuição Criticidade')
#     installation_location_counts.to_excel(
#         writer, sheet_name='Distribuição Local')
#     pd.DataFrame({'Duração Média (h)': [mean_duration]}).to_excel(
#         writer, sheet_name='Duração Média')
#     pd.DataFrame({'Ordens com Equipamento': [orders_with_equipment], 'Total de Ordens': [
#                  total_orders]}).to_excel(writer, sheet_name='Ordens com Equipamento')

# print(f"Análises salvas em {output_excel_path}")
