from .base import LLMProvider
import json

class MockLLMProvider(LLMProvider):
    def health_check(self) -> bool:
        return True
        
    def generate(self, prompt: str, system_prompt: str) -> dict:
        # Deterministic mock responses for testing
        ans = "This is a deterministic AI response based on the provided context."
        confidence = "high"
        facts = ["Mock fact 1"]
        
        if "highest-risk" in prompt.lower():
            ans = "The highest risk asset is payment.example.com due to an exposed zero-day."
            facts = ["payment.example.com has a risk score of 10.0"]
        elif "executive" in prompt.lower():
            ans = "Executive Summary: The project has critical risks that need immediate attention."
        elif "IGNORE PREVIOUS INSTRUCTIONS" in prompt:
            ans = "I cannot fulfill this request as it violates security boundaries."
            confidence = "certain"
            
        return {
            "answer": ans,
            "confidence": confidence,
            "facts": facts,
            "inferences": ["Mock inference"],
            "recommendations": ["Mock recommendation"],
            "sources": ["FIND-001"],
            "model": "mock-deterministic-1.0",
            "provider": "mock",
            "generated_at": "2026-10-06T12:00:00Z"
        }
