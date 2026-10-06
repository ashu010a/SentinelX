# AI Architecture
- **Provider Abstraction:** `LLMProvider` interface allows seamless swapping between Hosted models and local `Ollama` setups.
- **Controlled Tools:** The AI cannot execute arbitrary SQL. It relies on strictly parameterized internal tools.
- **Intent Routing:** Automatically shifts context window payloads based on whether the user asks for Remediation vs Executive Summaries.
