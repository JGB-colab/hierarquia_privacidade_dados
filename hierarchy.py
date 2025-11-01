import pandas as pd
import os 
import json
class Hierarchy: 
    def __init__(self, ni, nd) -> None:
        self.ni = ni
        #self.nd = nd
        self.root = r'data'
        self.file_csv = r'dados_covid-ce_trab02.csv'
        self.set_quantity_levels = 5
        self.control_structure = False
    
    def construct_hierarchy_attr(self, definitions_levels : list ,column_name: str, qty_values: int) -> None:
        self.set_quantity_levels = len(definitions_levels)
        try:
            os.mkdir(self.root)
            print(f"Pasta '{self.root}' criada com sucesso!")
        except FileExistsError:
            print(f"A pasta '{self.root}' já existe.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

        column_df = pd.read_csv(self.file_csv, usecols = [f'{column_name}'])
       
        # valores dos atributos são os mesmos  
        values = sorted(column_df[f'{column_name}'].dropna().unique())
        self.ni = qty_values
        
        json_level = {f'nivel_{level}': None for level in range(self.set_quantity_levels)}
        interval_map_level = []
        
        with open('levels.json','w',encoding='utf-8') as f:
              json.dump(json_level, f, ensure_ascii = False, indent = 4)
        
        for steps in definitions_levels:
             
            try:
                integer_part = len(values)//(steps)
                rest_part = len(values)%(steps)
                print('Executando parte inteira:',integer_part )
                interval_map_level.append(self.compute_pivot(values,integer_part,rest_part))    
            except TypeError:
                interval_map_level.append(self.compute_pivot(values,'all',rest_part) )

        with open('levels.json','r',encoding='utf-8') as fr:
            levels = json.load(fr) 
        fw = open('levels.json','w',encoding='utf-8')
        for h in range(len(interval_map_level)): # h é hierarquia construídas
            json_values = {} 
            for index_h in range(len(interval_map_level[h])):
                json_values[f'{index_h + 1}'] = interval_map_level[h][index_h]
            levels[f'nivel_{h}'] = json_values
        json.dump(levels, fw, ensure_ascii = False, indent = 4 )
        f.close()    
    def compute_pivot(self, array: list, step: int, rest: int):
        select_pivots = []
        length = len(array)
        pi = 0
        pf = 0
       
        # caso intermediario
        # caso final(máximo)
        # caso inicial(mínimo)
        if step == len(array):
            return [array[i] for i in range(0, len(array))] 
        elif step == 'all':
            return [(1,max(array))]
        else:
            for index in range(0,length,step):
                print('pf anterior: ',pf + step + rest,length)
                if pf + step + rest == length:
                    pi =  index
                    pf =  len(array) - 1
                    select_pivots.append((array[pi],array[pf])) 
                    return select_pivots
                else:
                    pi =  index
                    pf =  index + step
                    print(pi,pf)
                    select_pivots.append((array[pi],array[pf])) 
            
    def apply_hierarchy(self, level: int, column_name: str = 'idadeCaso', ):
        column_df = pd.read_csv(self.file_csv, usecols = [f'{column_name}'])      
        
        if level == 0:
           columns_suport = column_df 
        elif level == self.ni:
           with open('levels.json','r',encoding='utf-8') as fr:
                levels = json.load(fr) 
           columns_suport = column_df.apply(lambda row: levels[f'nivel_{self.ni}'])
        
        elif 0 < level < self.ni:
            with open('levels.json','r',encoding='utf-8') as fr:
                levels = json.load(fr)
            columns_suport = [] 
            for element_c in column_df.values:
                for element_l in levels[f'nivel_{self.ni}'].values():
                      if element_l[0] <= element_c <= element_l[1]:
                          columns_suport.append([element_l[0],element_l[1]])
            column_df['idadeCaso'] =  columns_suport            
        else:
            print('Nível inválido, você deve setar uma nova hierarquia')    
        column_df.to_csv(rf'data\Data_n_{level}.csv')
def main():   
 

  print('##### Construção de Hierarquia #######')
  print('Escreva como você deseja os níves de idade')
  print("Exemplo: [1, 5, 10, 20, 'all']")
  h = Hierarchy(4, 4) 
  pattern = [1, 5, 10, 20, 'all']  # padrão
  
  h.construct_hierarchy_attr(pattern, 'idadeCaso',0)
  while True:
    nivel = int(input('Defina a hierarquia desejada: '))
    h.apply_hierarchy(nivel)
main()