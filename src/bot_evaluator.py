import pandas as pd
from langchain.prompts import PromptTemplate

class LLMIntegrator:
    """
    Classe para encapsular chamadas para LLM's a partir de um Dataframe.
    
    """

    def __init__(self, df: pd.DataFrame, prompt_variables_map: dict, prompt: str, llm, response_validator: callable = lambda x: x, retriever: callable = None, max_retry: int = 0, response_col = 'llm_response'):
        """
            Inicializa o Intregador.

            Args:
                df (pd.DataFrame): DataFrame que armazena as perguntas e, opcionalmente, as respostas corretas (ground truth).
                prompt (str): O prompt utilizado para gerar as respostas do bot.
                prompt_variables_map (dict): Mapeamento de variáveis do prompt, onde as chaves são os nomes das variáveis e os valores são os nomes das colunas correspondentes no DataFrame.
                llm: O modelo de linguagem que será utilizado para invocar a API do bot.
                response_validator (callable, opcional): Função responsável por validar as respostas do bot, que deve aceitar uma string e retornar um valor validado. O padrão é uma função identidade.
                retriever (callable, opcional): Função que recupera contexto relevante, aceitando uma string (pergunta) e retornando um contexto associado. O padrão é None.
                max_retry (int, opcional): O número máximo de tentativas para invocar a API do bot em caso de falha, com valor padrão de 0.
                response_col (str, opcional): O nome da coluna que receberá a resposta da LLM. O padrão é 'llm_response'.
            Raises:
                ValueError: Levanta uma exceção se alguma coluna especificada em prompt_variables_map não existir no DataFrame fornecido.
        """
        for col in prompt_variables_map.values():
            if col not in df.columns:
                raise ValueError(f"A coluna {col} não existe no DataFrame")
        self.df = df
        self.response_df = pd.DataFrame()
        self.prompt = PromptTemplate(input_variables=prompt_variables_map.keys(), template=prompt)
        self.llm = llm
        self.max_retry = max_retry
        self.retriever = retriever
        self.response_validator = response_validator
        self.prompt_variables_map = prompt_variables_map
        self.response_col = response_col

    def _chain(self, prompt: str):
        """
        Combina um prompt com o modelo de linguagem para formar uma cadeia de validação.

        Args:
            prompt (str): O prompt a ser combinado com o modelo de linguagem.

        Returns:
            object: A cadeia resultante que combina o prompt e o modelo de linguagem.
        """
        return prompt | self.llm

    @staticmethod
    def _invoke(chain, input_data: dict, max_retry: int) -> str:
        """
        Invoca a cadeia de validação ou resumo com os dados de entrada fornecidos.

        Tenta invocar a cadeia até o número máximo de tentativas especificado. 
        Retorna o resultado da invocação ou None se falhar após todas as tentativas.

        Args:
            chain: Cadeia a ser invocada.
            input_data (dict): Dados de entrada para a cadeia.

        Returns:
            str: Resultado da invocação ou None se todas as tentativas falharem.
        """
        for retry in range(max_retry + 1):
            try:
                return chain.invoke(input_data)
            except Exception as error:
                if retry == max_retry:
                    return None
    
    @staticmethod
    def generate_single_response(prompt_variables: dict, bot_prompt: str, llm, max_retry: int,response_validator : callable = lambda x:x ) -> tuple:
        """
        Gera uma resposta do bot para uma única pergunta, incluindo o contexto, chamando a API do bot.

        Args:
            prompt_variables (dict): Variáveis de entrada para o prompt, incluindo a pergunta e o contexto.
            bot_prompt (str): O prompt a ser usado para gerar a resposta do bot.
            llm: Modelo de linguagem usado para invocar a API do bot.
            max_retry (int): Número máximo de tentativas para invocar a API.

        Returns:
            tuple: Contém a resposta gerada pelo bot (str) e o contexto (str), ou None se falhar.
        """
        chain = bot_prompt | llm
        response = LLMIntegrator._invoke(chain, prompt_variables, max_retry=max_retry)
        return response_validator(response.content)

    def get_context(self, query_column):
        """
        Recupera o contexto relevante para cada pergunta no DataFrame.

        Args:
            query_column (str): Nome da coluna que contém as perguntas para as quais o contexto será recuperado.

        Returns:
            pd.DataFrame: DataFrame contendo as perguntas e seus contextos associados.
        """
        df = self.df.copy()
        df[self.response_col] = df[query_column].apply(lambda q: self.retriever(q))
        return df
    
    def generate_response_df(self):
        """
        Gera um DataFrame com as respostas do bot para cada pergunta no DataFrame original.

        Para cada linha do DataFrame, gera uma resposta e obtém o contexto chamando a API do bot.
        As respostas e contextos são adicionados ao DataFrame, e a avaliação das respostas do bot é realizada.

        Returns:
            pd.DataFrame: O DataFrame atualizado com as respostas do bot e o contexto, se aplicável.
        
        Raises:
            ValueError: Se ocorrer um erro durante a geração das respostas.
        """
        df = self.df.copy()  # Faz uma cópia para evitar modificações indesejadas
        if self.retriever:
            df = self.get_context('question')
        
        try:
            # Gera respostas do bot para cada linha
            df['llm_response'] = df.apply(lambda linha: 
                                        self.generate_single_response(
                                            {**{prompt_variable: linha[column] 
                                                for prompt_variable, column in self.prompt_variables_map.items()},
                                                'context': linha['context'] if self.retriever else None},
                                            self.prompt, 
                                            self.llm, 
                                            self.max_retry,
                                            self.response_validator
                                        ),
                                        axis=1)
        except Exception as e:
            raise ValueError(f"Ocorreu um erro ao gerar as respostas: {e}")

        self.response_df = df

        return df