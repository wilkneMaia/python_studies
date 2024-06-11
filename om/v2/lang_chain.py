from langchain import LangChain

# Inicializar LangChain
lc = LangChain()

# Definir uma cadeia simples
chain = lc.create_chain()

# Adicionar um passo para chamar um modelo de linguagem
chain.add_step(
    lc.llm_step(prompt="Resuma o seguinte texto: {input_text}")
)

# Adicionar um passo para pós-processamento (opcional)
chain.add_step(
    lambda response: response.strip()
)

# Executar a cadeia com um texto de entrada
result = chain.run(
    input_text="LangChain é uma biblioteca poderosa para trabalhar com grandes modelos de linguagem.")
print(result)

