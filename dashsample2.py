import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

df = pd.read_csv('dataset.csv',low_memory=False)
	
def generate_table(dataframe, max_rows=10):
   return html.Table(
      # Header
      [html.Tr([html.Th(col) for col in dataframe.columns])] +
      # Body
      [html.Tr([
         html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
      ]) for i in range(min(len(dataframe), max_rows))]
   )
	
app = dash.Dash()
app.layout = html.Div(children=[
   html.H4(children='US Agriculture Exports (2011)'),
   generate_table(df)
])

if __name__ == '__main__':
   app.run_server(debug=True)