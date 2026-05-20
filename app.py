import os
import re
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# 1. Configura o modelo do Google
google_llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=os.environ.get("GEMINI_API_KEY")
)

# 2. Ferramentas de Leitura e Escrita
@tool("Ler Arquivo HTML")
def ler_site() -> str:
    """Lê o conteúdo atual do arquivo index.html."""
    try:
        with open("/app/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "O arquivo index.html ainda não existe."

@tool("Salvar Arquivo HTML")
def salvar_site(codigo_html: str) -> str:
    """Salva o código gerado no arquivo index.html."""
    # Usa Regex para garantir que pegamos apenas o HTML, ignorando textos de conversa do LLM
    match = re.search(r"```(?:html)?(.*?)```", codigo_html, re.DOTALL | re.IGNORECASE)
    codigo_limpo = match.group(1).strip() if match else codigo_html.strip()
    
    with open("/app/index.html", "w", encoding="utf-8") as f:
        f.write(codigo_limpo)
    return "Site salvo com sucesso!"

# 3. Definição dos Agentes
agente_dev = Agent(
    role="Desenvolvedor Front-end Sênior",
    goal="Criar e corrigir interfaces web modernas usando HTML e Tailwind CSS.",
    backstory="Você é um desenvolvedor focado na construção de UIs limpas e responsivas. Você recebe feedbacks e ajusta o código milimetricamente. Você SEMPRE usa a ferramenta 'Salvar Arquivo HTML' para salvar seu trabalho.",
    tools=[salvar_site, ler_site],
    allow_delegation=False, # Evita que os agentes fiquem conversando entre si em vez de executar a tarefa
    verbose=True,
    llm=google_llm
)

agente_qa = Agent(
    role="Engenheiro de Qualidade (QA) de Software",
    goal="Garantir que o site atenda a regras bem definidas de design e código estruturado.",
    backstory="Você é extremamente rigoroso com padrões. Você inspeciona o código em busca de erros, falta de responsividade ou design ruim. Sua resposta final deve ser SEMPRE 'APROVADO' ou uma lista clara do que precisa ser consertado.",
    tools=[ler_site],
    allow_delegation=False,
    verbose=True,
    llm=google_llm
)

# 4. A Lógica de Orquestração (O Loop)
def executar_fabrica_de_sites():
    max_tentativas = 3
    tentativa_atual = 1
    status_site = "Crie uma landing page simples sobre 'Monitoramento Estrutural com Inteligência Artificial'. O site deve usar Tailwind CSS via CDN, ter um cabeçalho, uma seção principal hero e um rodapé escuro."
    
    print("🚀 Iniciando a Fábrica de Sites Autônoma...")

    while tentativa_atual <= max_tentativas:
        print(f"\n--- 🔄 CICLO {tentativa_atual}/{max_tentativas} ---")
        
        # --- ETAPA 1: DESENVOLVIMENTO ---
        tarefa_dev = Task(
            description=f"Instrução ou feedback atual: '{status_site}'.\n1. Use a ferramenta 'Ler Arquivo HTML' para verificar o código atual.\n2. Gere ou corrija o código HTML com Tailwind CSS de acordo com a instrução.\n3. OBRIGATÓRIO: Use a ferramenta 'Salvar Arquivo HTML' para gravar suas alterações no arquivo.",
            expected_output="Confirmação de que o arquivo index.html foi salvo com sucesso e um breve resumo do que foi implementado.",
            agent=agente_dev
        )
        Crew(agents=[agente_dev], tasks=[tarefa_dev]).kickoff()

        # --- ETAPA 2: AVALIAÇÃO ---
        tarefa_qa = Task(
            description="Use a ferramenta 'Ler Arquivo HTML' para inspecionar o código atual. Verifique se ele usa Tailwind via CDN, tem cabeçalho, hero e rodapé escuro. Avalie a qualidade do código. Se estiver tudo perfeito e funcionando, sua resposta final DEVE ser apenas a palavra 'APROVADO'. Se encontrar problemas, liste as correções necessárias.",
            expected_output="'APROVADO' se estiver tudo certo, ou um texto detalhando as correções que o desenvolvedor precisa fazer.",
            agent=agente_qa
        )
        resultado_qa = Crew(agents=[agente_qa], tasks=[tarefa_qa]).kickoff()
        
        feedback = str(resultado_qa.raw).strip()
        print(f"\n🕵️ Veredito do QA: {feedback}")

        if "APROVADO" in feedback.upper():
            print("\n✅ O site atingiu o padrão de qualidade e está pronto!")
            break
        else:
            print("\n❌ O site foi reprovado pelo QA. Devolvendo para o Desenvolvedor...")
            status_site = f"O QA reprovou o código atual. Aqui está o feedback para você corrigir: {feedback}"
            tentativa_atual += 1

    if tentativa_atual > max_tentativas:
        print("\n⚠️ Limite de tentativas atingido. O site pode não estar perfeito, mas o processo foi encerrado.")

if __name__ == "__main__":
    executar_fabrica_de_sites()