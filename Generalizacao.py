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

    def chamada(self):
        print("Digite: 1 para Sim e 0 para Não")
        idade = float(input("Deseja generalizar idade"))
        data = float(input("Deseja generalizar data de Nascimento"))
        if idade == 1:
            pass
        if data == 1:
            Hierarchy.generalizar()

    def construct_hierarchy_attr(self, definitions_levels : list ,column_name: str) -> None:
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
        #self.ni = qty_values
        
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
                if pf + step + rest == length:
                    pi =  index
                    pf =  len(array) - 1
                    select_pivots.append((array[pi],array[pf])) 
                    return select_pivots
                else:
                    pi =  index
                    pf =  index + step
                    select_pivots.append((array[pi],array[pf])) 
            
    def apply_hierarchy(self, level: int, column_name: str = 'idadeCaso', ):
        column_df = pd.read_csv(self.file_csv, usecols = [f'{column_name}'])  
        columns_suport = []    
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
                find = False
                if pd.isna(element_c):
                    columns_suport.append(None) # Adiciona None ou um valor de erro
                    continue # Pula para o próximo elemento
                for element_l in levels[f'nivel_{level}'].values():
                    if find:
                        break
                    if element_l[0] <= element_c <= element_l[1]:
                          columns_suport.append([element_l[0],element_l[1]])
                          find = True
                if not find:
                    # Adiciona um marcador (ex: [-1, -1] ou None) para garantir que a lista tenha o mesmo tamanho
                    columns_suport.append([-1, -1] )  
                
            if len(columns_suport) != len(column_df):
                 print(f"ERRO DE LÓGICA: Comprimento da lista de suporte ({len(columns_suport)}) não coincide com o DF ({len(column_df)}).")
                 return          
            column_df['idadeCaso'] = columns_suport            
        else:
            print('Nível inválido, você deve setar uma nova hierarquia')    
        column_df.to_csv(rf'data\Data_n_{level}.csv')

    def generalizar(self):

        print("Informe a porcentagem de cada nível de generalização (total deve somar 100%)")
        n0 = float(input("Nível 0 (dia/mês/ano): "))
        n1 = float(input("Nível 1 (mês/ano): "))
        n2 = float(input("Nível 2 (ano): "))

        # Verificar se realmente o total daa 100% do dataframe
        total = n0 + n1 + n2
        if total != 100:
            print(f"❌ A soma deve ser 100%, mas foi {total}%. Tente novamente.")
            return

        # Calcula o número de linhas para cada nível
        n = len(df)
        line_n0 = int(n * n0 / 100)
        line_n1 = int(n * n1 / 100)
        line_n2 = n - line_n0 - line_n1 # Calculate line_n2 to account for potential rounding issues

        #Cria um index para classificar o nivel de acordo com a quantidade de linhas que é preciso.
        index0 = df.index[:line_n0]#Totas as linhas até a quantidade de linhas de nivel0
        index1 = df.index[line_n0:line_n0+line_n1]#A partir do line_n0 preenche com o nivel 1 até o line_n0+line_n1
        index2 = df.index[line_n0+line_n1:line_n0+line_n1+line_n2]#Todas as linhas após line_n0 + line_n1, preenche com o nivel2

        # Aplica as generalizações com base no index
        valn0 = df.loc[index0, 'dataNascimento'].dt.strftime('%d/%m/%Y') #Localiza as linhas com o index do nivel 0 e aplica a generalização dia/mês/ano
        valn1 = df.loc[index1, 'dataNascimento'].dt.strftime('%m/%Y') #Localiza as linhas com o index do nivel 1 e aplica a generalização mês/ano
        valn2 = df.loc[index2, 'dataNascimento'].dt.strftime('%Y') ##Localiza as linhas com o index do nivel 2 e aplica a generalização ano

        # 2. Passar a coluna para 'object' para aceitar as strings
        df['data_gen'] = pd.Series(dtype=object)

        # 3. Realizar a alteração na coluna (atribuindo as strings)
        df.loc[index0, 'data_gen'] = valn0
        df.loc[index1, 'data_gen'] = valn1
        df.loc[index2, 'data_gen'] = valn2

        print("\n✅ Generalização aplicada com sucesso!")
        print(f"- Nível 0: {line_n0} linhas ({n0}%)")
        print(f"- Nível 1: {line_n1} linhas ({n1}%)")
        print(f"- Nível 2: {line_n2} linhas ({n2}%)")
        return df
    
def main():   
 

  print('##### Construção de Hierarquia #######')
  print('Escreva como você deseja os níves de idade')
  print("Exemplo: [1, 5, 10, 20, 'all']")
  h = Hierarchy(4, 4) 
  pattern = [1, 5, 10, 20, 'all']  # padrão
  
  h.construct_hierarchy_attr(pattern, 'idadeCaso')
  while True:
    nivel = int(input('Defina a hierarquia desejada: '))
    h.apply_hierarchy(level=int(nivel))
main()