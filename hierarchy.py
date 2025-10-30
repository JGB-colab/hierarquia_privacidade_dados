import pandas as pd
import os 
import json
class Hierarchy: 
    def __init__(self, ni, nd) -> None:
        self.ni = ni
        self.nd = nd
        self.root = r'data'
        self.file_csv = r'dados_covid-ce_trab02.csv'

    def construct_hierarchy_attr(self, column_name: str, qty_values: int ) -> None:
        try:
            os.mkdir(self.root)
            print(f"Pasta '{self.root}' criada com sucesso!")
        except FileExistsError:
            print(f"A pasta '{self.root}' já existe.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

        column_df = pd.read_csv(self.file_csv, usecols = [f'{column_name}'])
        values = sorted(column_df[f'{column_name}'].unique())
        self.ni = qty_values
        
        if qty_values!=0:
            steps = (values)//(self.ni)
        elif qty_values == 0:
            steps = len(values)
        interval_map_column = []
        json_level = {}
        for index in range(0,steps):
            if qty_values == 0:
               json_level[f'{index}'] = values[index]
        
        #json.dumps(json_level,rf'\data\levels.json')
        with open('levels.json','w',encoding='utf-8') as f:
              json.dump({f'nivel_{qty_values}': json_level}, f, ensure_ascii = False, indent = 4 )
    def apply_hierarchy(self):
        ...

    def compute_pivot(self, array: list):
        levels = {'0':[],'1':[],'2':[],'3':[],'4':[]}
        array = ...

def main():   
  h = Hierarchy(1, 4) 
  h.construct_hierarchy_attr('idadeCaso',0)
main()