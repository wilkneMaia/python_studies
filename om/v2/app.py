import dash
import plotly.express as px

from dash import dcc
from dash import html

import pandas as pd


# Carregar os dados do arquivo JSON
df = pd.read_json('./output_pdfs/combined_maintenance_data.json')

# Filtrar colunas relevantes
df_filtered = df[['equipment_fields.criticality', 'order_fields.duration']]

# Converter a coluna 'duration' para float
df_filtered['order_fields.duration'] = df_filtered['order_fields.duration'].astype(
    float)

# Criar a figura do gráfico de boxplot
fig = px.box(df_filtered, x='equipment_fields.criticality', y='order_fields.duration',
             title='Distribuição das Durações das Ordens de Manutenção por Criticidade',
             labels={'equipment_fields.criticality': 'Criticidade',
                     'order_fields.duration': 'Duração (horas)'},
             color='equipment_fields.criticality',
             template='plotly_white')

# Inicializar a aplicação Dash
app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.H1("Dashboard Interativo com Dash"),
    dcc.Graph(
        id='criticidade-graph',
        figure=fig
    )
])

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
