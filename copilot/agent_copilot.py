# copilot/agent_copilot.py

import json
from typing import Dict, Any
from openai import OpenAI
from config import settings

class CopilotAgent:
    """
    Agente que usa um dos LLMs configurados no BettaFish
    para analisar o feedback do GitHub.
    """

    def __init__(self, use_engine: str = "report"):
        """
        use_engine: qual engine do BettaFish usar:
          - "report"  -> REPORT_ENGINE_*
          - "insight" -> INSIGHT_ENGINE_*
          - "query"   -> QUERY_ENGINE_*
        """
        if use_engine == "report":
            api_key = settings.REPORT_ENGINE_API_KEY
            base_url = settings.REPORT_ENGINE_BASE_URL
            model_name = settings.REPORT_ENGINE_MODEL_NAME
        elif use_engine == "insight":
            api_key = settings.INSIGHT_ENGINE_API_KEY
            base_url = settings.INSIGHT_ENGINE_BASE_URL
            model_name = settings.INSIGHT_ENGINE_MODEL_NAME
        elif use_engine == "query":
            api_key = settings.QUERY_ENGINE_API_KEY
            base_url = settings.QUERY_ENGINE_BASE_URL
            model_name = settings.QUERY_ENGINE_MODEL_NAME
        else:
            raise ValueError(f"Engine desconhecido: {use_engine}")

        if not api_key:
            raise ValueError(f"API key não configurada para engine {use_engine}")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.role = "Community Mirror Analyst"

    def analyze_sentiment(self, documents):
        """
        documents: lista de dicts com "content" (texto de cada issue/comentário).
        Retorna um JSON estruturado com a análise.
        """

        # Junta os textos em um único prompt (pode limitar para não explodir tokens)
        combined = "\n\n---\n\n".join(doc["content"] for doc in documents[:20])

        prompt = f"""
You are a Senior Product Manager analyzing GitHub feedback for an open-source project.

Below is a collection of recent GitHub issues and PR comments for the project:

{combined}

Your tasks:
1. Identify the 3 main pain points users are complaining about.
2. Identify the most requested feature.
3. Classify the overall community mood in one of:
   - "positive"
   - "neutral"
   - "tense"
   - "chaotic"
4. Suggest ONE concrete, immediate action the maintainer could take.

Return your answer as STRICT JSON:
{{
  "main_pains": ["pain1", "pain2", "pain3"],
  "top_feature_request": "feature description",
  "mood": "tense",
  "suggested_action": "what to do now"
}}
Only return the JSON, no extra text.
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    def generate_report(self, analysis: Dict[str, Any]):
        """
        Gera um relatório no terminal, estilo BettaFish.
        """
        print("\n" + "=" * 60)
        print("🐟 BETTAFISH COPILOT – COMMUNITY MIRROR REPORT")
        print("=" * 60)

        mood = analysis.get("mood", "unknown")
        print(f"\n😊 Overall community mood: {mood.upper()}")

        pains = analysis.get("main_pains", [])
        print("\n🔥 Top pain points:")
        for i, pain in enumerate(pains, 1):
            print(f"   {i}. {pain}")

        feature = analysis.get("top_feature_request", "")
        print(f"\n💡 Most requested feature: {feature}")

        action = analysis.get("suggested_action", "")
        print(f"\n🚀 Suggested immediate action: {action}")

        print("\n" + "=" * 60)