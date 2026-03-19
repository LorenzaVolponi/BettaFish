import streamlit as st
import sys
import os

# Adiciona o diretório raiz ao path para importar o copilot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copilot.github_ingestor import GitHubIngestor
from copilot.agent_copilot import CopilotAgent

# Configuração da Página
st.set_page_config(page_title="BettaFish Copilot", page_icon="🐟")

st.title("🐟 Community Mirror Mode")
st.markdown("### Analyze BettaFish's own GitHub Community Health")
st.info("This tool uses BettaFish's agents to analyze the project's Issues and PRs to generate actionable insights.", icon="💡")

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configuration")
    repo_name = st.text_input("Repository", value="666ghj/BettaFish")
    limit = st.slider("Items to Analyze", min_value=10, max_value=100, value=30)
    
    st.divider()
    st.write("Made with ❤️ by Contributor")

# Botão principal
if st.button("🔄 Generate Community Report", type="primary"):
    
    # Placeholder para mostrar progresso
    status_placeholder = st.empty()
    
    try:
        # 1. Coleta de dados
        status_placeholder.info("📡 Fetching data from GitHub...")
        ingestor = GitHubIngestor(repo_name=repo_name)
        documents = ingestor.fetch_community_feedback(limit=limit)
        
        if not documents:
            st.warning("No documents found or API limit reached.")
        else:
            # 2. Análise
            status_placeholder.info("🧠 Agent analyzing community sentiment...")
            agent = CopilotAgent(use_engine="report")
            analysis = agent.analyze_sentiment(documents)
            
            status_placeholder.success("✅ Analysis Complete!")
            
            # 3. Exibir Resultados em Cards Visuais
            col1, col2 = st.columns(2)
            
            with col1:
                # Card de Humor
                mood_emoji = {"positive": "😊", "neutral": "😐", "tense": "😫", "chaotic": "🔥"}
                st.metric(
                    label="Overall Community Mood", 
                    value=f"{mood_emoji.get(analysis.get('mood', 'unknown'), '🤔')} {analysis.get('mood', 'unknown').upper()}"
                )
                
            with col2:
                # Card de Feature
                st.metric(
                    label="Top Feature Request", 
                    value=analysis.get('top_feature_request', 'N/A')
                )

            st.divider()
            
            # Exibir Dores
            st.subheader("🔥 Top Pain Points")
            pains = analysis.get('main_pains', [])
            for i, pain in enumerate(pains, 1):
                st.warning(f"**{i}.** {pain}")

            # Exibir Ação
            st.subheader("🚀 Suggested Immediate Action")
            st.success(f"👉 {analysis.get('suggested_action', 'No suggestion')}")

            # Expander para ver dados brutos (opcional, para debug)
            with st.expander("See Raw Data"):
                st.json(documents[:5])  # Mostra os 5 primeiros docs para não poluir

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("💡 Tip: Make sure you have GITHUB_TOKEN and LLM keys configured in your .env file.")