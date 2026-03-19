# copilot/github_ingestor.py

from github import Github
import os
from typing import List, Dict

class GitHubIngestor:
    """
    Coleta feedback do GitHub do próprio BettaFish
    (Issues e PRs) para analisar com o LLM.
    """

    def __init__(self, repo_name: str = "666ghj/BettaFish"):
        self.repo_name = repo_name
        self.token = os.getenv("GITHUB_TOKEN")
        if self.token:
            self.g = Github(self.token)
        else:
            print("AVISO: GITHUB_TOKEN não configurado. Você pode bater limite de taxa da API.")
            self.g = Github()

        try:
            self.repo = self.g.get_repo(self.repo_name)
        except Exception as e:
            print(f"Erro ao acessar repositório {self.repo_name}: {e}")
            self.repo = None

    def fetch_community_feedback(self, limit: int = 30) -> List[Dict]:
        """
        Coleta Issues e PRs recentes como "posts de rede social".
        """
        if not self.repo:
            return []

        documents = []

        # 1) Issues abertas recentes
        issues = self.repo.get_issues(state="open", sort="created", direction="desc")
        count = 0
        for issue in issues:
            if count >= limit:
                break
            # Ignorar PRs que aparecem como issues
            if issue.pull_request:
                continue

            text = f"User {issue.user.login} opened an issue: {issue.title}\n\n{issue.body}"
            documents.append({
                "source": "github_issue",
                "id": str(issue.number),
                "content": text,
                "created_at": str(issue.created_at),
                "labels": [label.name for label in issue.labels],
            })
            count += 1

        # 2) Comentários em PRs recentes
        pulls = self.repo.get_pulls(state="all", sort="created", direction="desc")
        count_prs = 0
        for pr in pulls:
            if count_prs >= limit // 2:
                break

            comments = pr.get_issue_comments()
            for comment in comments:
                text = (
                    f"Dev {comment.user.login} commented on PR #{pr.number}: "
                    f"{comment.body}"
                )
                documents.append({
                    "source": "github_pr_comment",
                    "id": f"{pr.number}_{comment.id}",
                    "content": text,
                    "created_at": str(comment.created_at),
                    "pr_state": pr.state,
                })
            count_prs += 1

        print(f"Coletados {len(documents)} documentos do GitHub.")
        return documents