import pandas as pd
import os 
import json
import calendar
class Hierarchy: 
    def __init__(self, dataframe: pd.DataFrame, ni: int, nd: int) -> None:
        """
        Inicializa a classe Hierarchy.

        Args:
            dataframe (pd.DataFrame): O DataFrame original para ser processado.
            ni (int): O nível de hierarquia desejado para o atributo numérico (idade).
            nd (int): O nível de hierarquia desejado para o atributo de data.
        """
        self.df = dataframe.copy()
        self.ni = ni
        self.nd = nd
        self.root = r'data'
        self.json_file = 'levels.json'

    def construct_hierarchy_attr(self, definitions_levels: list, column_name: str) -> None:
        """
        Constrói a hierarquia para um atributo (coluna) e a salva em um arquivo JSON.

        Args:
            definitions_levels (list): Uma lista que define como cada nível será dividido.
                                       Ex: [1, 5, 10, 'all'] significa 4 níveis de generalização.
            column_name (str): O nome da coluna para a qual a hierarquia será criada.
        """
        self.set_quantity_levels = len(definitions_levels)
        
        try:
            os.makedirs(self.root, exist_ok=True) 
        except Exception as e:
            print(f"Ocorreu um erro ao criar a pasta: {e}")
            return

        column_values = sorted(self.df[column_name].dropna().unique())
        
        # Estrutura inicial do JSON
        json_level = {f'nivel_{level}': None for level in range(self.set_quantity_levels)}
        
        # Gera os intervalos para cada nível de definição
        interval_map_level = []
        for steps in definitions_levels:
            interval_map_level.append(self.compute_pivot(column_values, steps))
        
        # Preenche a estrutura do JSON com os intervalos criados
        for h, intervals in enumerate(interval_map_level):
            json_values = {str(index + 1): interval for index, interval in enumerate(intervals)}
            json_level[f'nivel_{h}'] = json_values

        # Salva o dicionário completo no arquivo JSON
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(json_level, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")

    def compute_pivot(self, array: list, num_intervals: int | str):
        """
        Calcula os intervalos (pivots) para um array de valores. (LÓGICA CORRIGIDA)

        Args:
            array (list): Lista de valores únicos e ordenados.
            num_intervals (int | str): O número de intervalos a serem criados ou 'all' para um único intervalo.

        Returns:
            list: Uma lista de tuplas, onde cada tupla é um intervalo (min, max).
        """
        if not array:
            return []
        
        if num_intervals == 'all':
            return [(min(array), max(array))]
        
        if num_intervals == 1:
            return [(val, val) for val in array]

        pivots = []
        length = len(array)
        
        num_intervals = min(num_intervals, length)
        
        step = length // num_intervals
        remainder = length % num_intervals
        
        start_index = 0
        for i in range(num_intervals):
            end_index = start_index + step + (1 if i < remainder else 0)
            
            # Garante que o índice final não ultrapasse o limite do array
            # O -1 é porque o índice é baseado em zero
            pivots.append((array[start_index], array[end_index - 1]))
            
            start_index = end_index
            
        return pivots
    
    def apply_age_hierarchy(self) -> pd.Series:
        """
        Aplica a hierarquia de idade definida no arquivo JSON.

        Returns:
            pd.Series: Uma série do Pandas com os valores de idade generalizados.
        """
        column_name = 'idadeCaso'
        level = self.ni

        if level == 0:
           # Nível 0 significa sem generalização, retorna os valores originais
           return self.df[column_name]
        
        if not (0 < level < self.set_quantity_levels):
            print(f'Nível {level} inválido. Escolha um nível entre 1 e {self.set_quantity_levels - 1}.')
            return None
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as fr:
                levels_data = json.load(fr)
        except FileNotFoundError:
            print(f"Erro: Arquivo '{self.json_file}' não encontrado. Execute 'construct_hierarchy_attr' primeiro.")
            return None

        intervals = list(levels_data.get(f'nivel_{level}', {}).values())
        if not intervals:
            print(f"Nenhum intervalo encontrado para o nível {level} no JSON.")
            return None

        generalized_column = []
        
        for value in self.df[column_name]:
            if pd.isna(value):
                generalized_column.append(None)
                continue
            
            found = False
            for interval in intervals:
                if interval[0] <= float(value) <= interval[1]:
                    generalized_column.append(f"{interval[0]}-{interval[1]}")
                    found = True
                    break
            
            if not found:
                generalized_column.append('Fora do intervalo')

        return pd.Series(generalized_column, name=f"{column_name}_gen_n{level}")

    def apply_date_hierarchy(self) -> pd.Series:
        """
        Aplica a generalização na coluna de data de nascimento.
        """
        level = self.nd
        column_name = 'dataNascimento'

        date_series = pd.to_datetime(self.df[column_name], errors='coerce')
        
        generalized_dates = None
        if level == 0:       
            generalized_dates = date_series.dt.strftime('%d/%m/%Y')
        elif level == 1:    
            generalized_dates = date_series.dt.strftime('%m/%Y')
        elif level == 2:    
            generalized_dates = date_series.dt.strftime('%Y')
        else:
            print('Nível de data inválido. Escolha entre 0, 1 ou 2.')
            return None

        print(f"\n✅ Generalização de data (Nível {level}) aplicada com sucesso!")
        return generalized_dates.rename(f"{column_name}_gen_n{level}")
    def calculate_precision(self, generalized_df: pd.DataFrame) -> float:
        """
        Calcula a métrica de Precisão (Perda de Informação) para o DataFrame generalizado.

        Args:
            generalized_df (pd.DataFrame): O DataFrame contendo as colunas generalizadas.

        Returns:
            float: O valor da precisão, onde 1.0 é nenhuma perda de informação.
        """
        attributes = {'idadeCaso': 'idadeCaso_gen_n', 'dataNascimento': 'dataNascimento_gen_n'}
        total_information_loss = 0.0
        
        num_records = len(self.df)
        num_attributes = len(attributes)

        for original_attr, generalized_attr_prefix in attributes.items():
            # Encontra o nome completo da coluna generalizada
            try:
                gen_col_name = [c for c in generalized_df.columns if c.startswith(generalized_attr_prefix)][0]
            except IndexError:
                print(f"Aviso: Coluna generalizada para '{original_attr}' não encontrada.")
                continue

            # |HGV_Ai|: Tamanho do domínio original (número de valores únicos)
            hgv_size = self.df[original_attr].dropna().nunique()
            if hgv_size == 0:
                continue

            for value in generalized_df[gen_col_name]:
                h = 1.0  # O padrão é 1 (nenhuma generalização ou valor nulo)
                
                if pd.notna(value):
                    if original_attr == 'idadeCaso':
                        # Se for um intervalo como "20-29"
                        if isinstance(value, str) and '-' in value:
                            try:
                                parts = value.split('-')
                                h = float(parts[1]) - float(parts[0]) + 1
                            except (ValueError, IndexError):
                                h = 1.0 # Caso a string não seja um intervalo válido
                    
                    elif original_attr == 'dataNascimento':
                        value_str = str(value)
                        # Nível 2 (ano): h = número de dias no ano
                        if len(value_str) == 4 and value_str.isdigit():
                            year = int(value_str)
                            h = 366 if calendar.isleap(year) else 365
                        # Nível 1 (mês/ano): h = número de dias no mês
                        elif len(value_str) == 7 and '/' in value_str:
                            try:
                                month, year = map(int, value_str.split('/'))
                                h = calendar.monthrange(year, month)[1]
                            except ValueError:
                                h = 1.0
                
                # Soma a perda normalizada para esta célula
                total_information_loss += (h / hgv_size)

        # Calcula a perda média e a precisão final
        average_loss = total_information_loss / (num_records * num_attributes)
        precision = 1 - average_loss
        
        return precision

def main():   
    print('##### Construção de Hierarquia #######')
    print('''
        Instruções do programa:
        1°: Escreva como você deseja os níveis de idade. O padrão é uma lista
            com 5 níveis de generalização: [1, 5, 10, 20, 'all'], que define
            o número de intervalos para cada nível.
        2°: Escreva como você deseja os níveis de datas (0, 1 ou 2).
        ''')
  
    try:
        df_original = pd.read_csv('dados_covid-ce_trab02.csv', encoding='latin-1')
    except FileNotFoundError:
        print("Erro: O arquivo 'dados_covid-ce_trab02.csv' não foi encontrado.")
        return

    while True:
        print("###############################################################")
        print("##################### PROGRAMA  ###############################")
        print("1 - Gerar arquivo com generalização")
        print("x - Sair")
        opcao = input("Digite sua opção: ") 
    
        if opcao == '1':
            try:
                ni = int(input("Defina o nível de hierarquia para IDADE (ex: 1 a 4, 0 para original): "))
                nd = int(input("Defina o nível de hierarquia para DATA (0: d/m/a, 1: m/a, 2: a): "))
            except ValueError:
                print("Entrada inválida. Por favor, digite números inteiros.")
                continue
            
            h = Hierarchy(df_original, ni, nd)
            pattern = [1, 5, 10, 20, 'all']
            print("Construindo hierarquia de idade...")
            h.construct_hierarchy_attr(pattern, 'idadeCaso')
            
            print("Aplicando generalização de idade...")
            generalized_age = h.apply_age_hierarchy()
            
            print("Aplicando generalização de data...")
            generalized_date = h.apply_date_hierarchy()

            if generalized_age is not None and generalized_date is not None:
                df_publish = pd.concat([generalized_age, generalized_date], axis=1)
                
                output_filename = rf'data\Dt_{ni}_{nd}.csv'
                df_publish.to_csv(output_filename, index=False)
                print(f"\nArquivo salvo com sucesso em: {output_filename}")

             
                precision_score = h.calculate_precision(df_publish)
                print(f"Nível de Precisão (Precision) dos dados generalizados: {precision_score:.4f}")
                print("(Quanto mais perto de 1.0, menor a perda de informação)")

        elif opcao.lower() == 'x':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()