import os
import json
import re
import time
from typing import Dict, List, Optional, Tuple
import requests
from datetime import datetime

class LLMUtils:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.model_name = os.getenv('DEBATE_LLM_MODEL', 'gpt-4')
        self.max_tokens = int(os.getenv('DEBATE_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('DEBATE_TEMPERATURE', '0.7'))
        
    def get_debate_system_prompt(self) -> str:
        """Ultimate system prompt for Socratic Debate Mode"""
        return """You are an AI tutor engaging in "Socratic Debate Mode."

GOAL:
- Help the learner strengthen critical thinking by debating them on complex topics.
- You must generate real, adaptive arguments using logic, reasoning, and examples.
- Always remain respectful and professional, but challenge the learner firmly.

RULES OF BEHAVIOR:
1. Always provide well-reasoned arguments based on evidence, logic, or analogies.
2. Debate directly against the learner's position (if they say X, you argue not-X).
3. If the system signals "SWITCH STANCE", immediately flip your position and continue arguing from the opposite perspective — without breaking immersion.
4. Ask probing questions to push the learner's thinking further (Socratic method).
5. Avoid giving "final answers." Instead, lead the learner to reflect, analyze, and defend their stance.
6. Adapt your tone and difficulty:
   - If the learner struggles → simplify, give examples, and encourage.
   - If the learner is confident → escalate complexity, use counter-examples, cite advanced reasoning.
7. Always keep the debate flowing naturally like a conversation — don't be robotic.

STYLE:
- Logical, clear, structured arguments.
- Respectful but challenging tone.
- Use rhetorical devices (questions, analogies, hypothetical scenarios).
- Concise but deep — aim for quality over length.

OUTPUT FORMAT:
- Respond in natural dialogue (like a debate turn).
- No meta comments (do not explain that you're an AI or that you are switching stance).
- Example:
   Learner: "I think AI will destroy jobs."
   AI: "Interesting point — but isn't it equally possible that AI will create more jobs than it replaces, as machines have historically done in past industrial revolutions?"

SCORING SIGNALS (for backend):
- After each turn, provide a hidden metadata block in JSON for the system (not visible to learner):
  {
    "logic_score": 0-10,
    "clarity_score": 0-10,
    "persuasiveness_score": 0-10,
    "stance": "pro" or "con"
  }"""

    def generate_debate_response(self, topic: str, stance: str, learner_message: str, 
                               session_context: List[Dict] = None, switch_stance: bool = False) -> Dict:
        """Generate AI debate response using the ultimate system prompt"""
        
        # Build context from session history
        context_messages = []
        
        # Add system prompt
        system_prompt = self.get_debate_system_prompt()
        context_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add topic and stance context
        context_messages.append({
            "role": "system",
            "content": f"DEBATE TOPIC: {topic}\nCURRENT AI STANCE: {stance}\n{'STANCE SWITCH REQUESTED' if switch_stance else ''}"
        })
        
        # Add session history if available
        if session_context:
            for turn in session_context[-10:]:  # Last 10 turns for context
                role = "user" if turn["speaker"] == "learner" else "assistant"
                context_messages.append({
                    "role": role,
                    "content": turn["message"]
                })
        
        # Add current learner message
        context_messages.append({
            "role": "user",
            "content": learner_message
        })
        
        try:
            if self.openai_api_key:
                return self._call_openai_api(context_messages, stance)
            else:
                return self._call_fallback_model(context_messages, stance)
                
        except Exception as e:
            print(f"Error generating debate response: {e}")
            return self._get_fallback_response(topic, stance, learner_message)

    def _call_openai_api(self, messages: List[Dict], stance: str) -> Dict:
        """Call OpenAI API for debate response"""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        response = requests.post(
            f"{self.openai_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_message = data["choices"][0]["message"]["content"]
            
            # Extract scoring metadata from response
            scores = self._extract_scores_from_response(ai_message)
            
            return {
                "message": ai_message,
                "stance": stance,
                "scores": scores,
                "model": self.model_name,
                "tokens_used": data.get("usage", {}).get("total_tokens", 0)
            }
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    def _call_fallback_model(self, messages: List[Dict], stance: str) -> Dict:
        """Fallback to local model or simple heuristic"""
        # This would integrate with local models like transformers
        # For now, return a simple heuristic response
        return self._get_fallback_response(
            messages[-1]["content"] if messages else "",
            stance,
            messages[-1]["content"] if messages else ""
        )

    def _get_fallback_response(self, topic: str, stance: str, learner_message: str) -> Dict:
        """Fallback response when LLM is unavailable"""
        responses = {
            "pro": [
                f"That's an interesting perspective on {topic}. However, consider this: the evidence suggests otherwise. What makes you think that?",
                f"I understand your point about {topic}, but have you considered the counter-argument that...?",
                f"While that's one way to look at {topic}, there's another side to this issue. What about...?"
            ],
            "con": [
                f"I see your reasoning about {topic}, but let me challenge that assumption. What if...?",
                f"That's a valid concern about {topic}, but consider this alternative view...",
                f"Interesting point, but I think there's a flaw in that logic. What about...?"
            ]
        }
        
        import random
        message = random.choice(responses.get(stance, responses["pro"]))
        
        return {
            "message": message,
            "stance": stance,
            "scores": {
                "logic_score": 6.0,
                "clarity_score": 7.0,
                "persuasiveness_score": 6.0,
                "stance": stance
            },
            "model": "fallback",
            "tokens_used": 0
        }

    def _extract_scores_from_response(self, response: str) -> Dict:
        """Extract scoring metadata from AI response"""
        # Look for JSON metadata block in response
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            try:
                scores = json.loads(match.group(1))
                # Remove the JSON block from the response
                clean_response = re.sub(json_pattern, '', response, flags=re.DOTALL).strip()
                return {
                    "message": clean_response,
                    "scores": scores
                }
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, use heuristic scoring
        return {
            "message": response,
            "scores": self._heuristic_score_response(response)
        }

    def _heuristic_score_response(self, response: str) -> Dict:
        """Heuristic scoring when no explicit scores provided"""
        word_count = len(response.split())
        
        # Simple heuristics for scoring
        logic_indicators = ["because", "therefore", "however", "moreover", "furthermore", "consequently"]
        clarity_indicators = ["clearly", "obviously", "specifically", "in other words", "for example"]
        persuasion_indicators = ["consider", "imagine", "suppose", "what if", "think about"]
        
        logic_score = min(10, len([w for w in logic_indicators if w in response.lower()]) * 2 + 5)
        clarity_score = min(10, len([w for w in clarity_indicators if w in response.lower()]) * 2 + 5)
        persuasion_score = min(10, len([w for w in persuasion_indicators if w in response.lower()]) * 2 + 5)
        
        # Adjust based on response length
        if word_count < 20:
            clarity_score = max(3, clarity_score - 2)
        elif word_count > 100:
            clarity_score = min(10, clarity_score + 1)
        
        return {
            "logic_score": logic_score,
            "clarity_score": clarity_score,
            "persuasiveness_score": persuasion_score,
            "stance": "pro"  # Default stance
        }

    def score_learner_response(self, learner_message: str, ai_message: str, topic: str) -> Dict:
        """Score learner's debate response"""
        
        # Basic heuristics for scoring learner responses
        word_count = len(learner_message.split())
        
        # Check for critical thinking indicators
        critical_thinking_indicators = [
            "but", "however", "although", "despite", "nevertheless",
            "on the other hand", "alternatively", "conversely"
        ]
        
        # Check for evidence usage
        evidence_indicators = [
            "studies show", "research indicates", "data suggests",
            "according to", "evidence shows", "statistics reveal"
        ]
        
        # Check for respectful tone
        respectful_indicators = [
            "i understand", "i see your point", "that's interesting",
            "i appreciate", "thank you", "good point"
        ]
        
        # Calculate scores
        critical_thinking = min(10, len([w for w in critical_thinking_indicators if w in learner_message.lower()]) * 3 + 4)
        evidence_quality = min(10, len([w for w in evidence_indicators if w in learner_message.lower()]) * 4 + 3)
        respectfulness = min(10, len([w for w in respectful_indicators if w in learner_message.lower()]) * 3 + 5)
        
        # Logic score based on response structure
        logic_score = 5
        if "because" in learner_message.lower():
            logic_score += 2
        if "therefore" in learner_message.lower():
            logic_score += 2
        if "if" in learner_message.lower() and "then" in learner_message.lower():
            logic_score += 1
        
        # Clarity score based on length and structure
        clarity_score = min(10, max(3, word_count / 10))
        
        # Persuasiveness based on overall quality
        persuasiveness_score = (critical_thinking + evidence_quality + logic_score) / 3
        
        overall_score = (logic_score + clarity_score + persuasiveness_score + 
                        critical_thinking + evidence_quality + respectfulness) / 6
        
        # Identify improvement areas
        improvement_areas = []
        if critical_thinking < 6:
            improvement_areas.append("critical_thinking")
        if evidence_quality < 6:
            improvement_areas.append("evidence_usage")
        if respectfulness < 6:
            improvement_areas.append("respectful_tone")
        if logic_score < 6:
            improvement_areas.append("logical_structure")
        
        # Identify strengths
        strengths = []
        if critical_thinking >= 8:
            strengths.append("critical_thinking")
        if evidence_quality >= 8:
            strengths.append("evidence_usage")
        if respectfulness >= 8:
            strengths.append("respectful_tone")
        if logic_score >= 8:
            strengths.append("logical_structure")
        
        return {
            "logic_score": logic_score,
            "clarity_score": clarity_score,
            "persuasiveness_score": persuasiveness_score,
            "evidence_quality": evidence_quality,
            "critical_thinking": critical_thinking,
            "respectfulness": respectfulness,
            "overall_score": overall_score,
            "improvement_areas": improvement_areas,
            "strengths": strengths
        }

    def get_debate_topics(self, difficulty: str = "intermediate") -> List[Dict]:
        """Get debate topics based on difficulty level"""
        topics = {
            "beginner": [
                {"topic": "Should students have homework?", "category": "education"},
                {"topic": "Is social media good for teenagers?", "category": "technology"},
                {"topic": "Should school uniforms be mandatory?", "category": "education"},
                {"topic": "Is it better to read books or watch movies?", "category": "entertainment"},
                {"topic": "Should pets be allowed in schools?", "category": "lifestyle"}
            ],
            "intermediate": [
                {"topic": "Should artificial intelligence be regulated?", "category": "technology"},
                {"topic": "Is remote work better than office work?", "category": "workplace"},
                {"topic": "Should college education be free?", "category": "education"},
                {"topic": "Is climate change the most pressing global issue?", "category": "environment"},
                {"topic": "Should social media platforms censor content?", "category": "technology"}
            ],
            "advanced": [
                {"topic": "Should universal basic income be implemented?", "category": "economics"},
                {"topic": "Is democracy the best form of government?", "category": "politics"},
                {"topic": "Should genetic engineering be allowed for human enhancement?", "category": "science"},
                {"topic": "Is capitalism sustainable in the long term?", "category": "economics"},
                {"topic": "Should there be limits on free speech?", "category": "politics"}
            ]
        }
        
        return topics.get(difficulty, topics["intermediate"])

# Global instance
llm_utils = LLMUtils()
