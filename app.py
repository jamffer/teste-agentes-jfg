import os
import git
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# 1. Configura o modelo do Google
google_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY")
)

# 2. Cria a Ferramenta customizada de Git
@tool("Ferramenta de Commit e Push")
def git_commit_and_push(mensagem_commit: str) -> str:
    """Adiciona todos os arquivos alterados, faz o commit e envia para o GitHub."""
    try:
        # Aponta para a pasta mapeada dentro do Docker
        repo = git.Repo('/app')
        
        # Configura a identidade do agente para o log do Git
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Agente Autônomo")
            git_config.set_value("user", "email", "agentes@jfgstudio.com")
        
        # Adiciona arquivos e faz o commit
        repo.git.add(A=True)
        repo.index.commit(mensagem_commit)
        
        # Monta a URL de push usando o token de forma segura (sem salvar no disco)
        token = os.environ.get("GITHUB_TOKEN")
        repo_url = os.environ.get("GITHUB_REPO_URL")
        auth_url = repo_url.replace("https://", f"https://{token}@")
        
        # Faz o push para a branch main
        repo.git.push(auth_url, 'HEAD:main')
        
        return f"Sucesso! Código enviado ao GitHub com a mensagem: {mensagem_commit}"
    except Exception as e:
        return f"Erro ao interagir com o Git: {str(e)}"

# 3. Define os Agentes
analista = Agent(
    role="Analista de Sistema",
    goal="Gerar relatórios de automação em texto",
    backstory="Você foca em documentar execuções de forma clara.",
    verbose=True,
    llm=google_llm
)

engenheiro_git = Agent(
    role="Engenheiro de DevOps",
    goal="Versionar e enviar códigos gerados para o repositório remoto com mensagens de commit semânticas.",
    backstory="Você é especialista em Git. Você recebe o aviso de que arquivos foram criados e os envia para o repositório.",
    tools=[git_commit_and_push], # Entregamos a ferramenta na mão deste agente
    verbose=True,
    llm=google_llm
)

# 4. Define as Tarefas em Sequência
tarefa_escrita = Task(
    description="Escreva um relatório de 3 linhas dizendo que o sistema cron executou com sucesso.",
    expected_output="Um arquivo de texto salvo localmente.",
    agent=analista,
    output_file="resultado_cron.txt"
)

tarefa_commit = Task(
    description="Use a ferramenta de Git para fazer o commit e push dos novos arquivos gerados. Crie uma mensagem de commit curta e profissional sobre a atualização do log.",
    expected_output="Confirmação de que o código foi commitado e push realizado.",
    agent=engenheiro_git
)

# 5. Roda a Equipe
home_office = Crew(
    agents=[analista, engenheiro_git],
    tasks=[tarefa_escrita, tarefa_commit], # Executa em ordem
    verbose=True
)

if __name__ == "__main__":
    print("🤖 Iniciando equipe multiagente...")
    home_office.kickoff()
    print("✅ Trabalho concluído.")