import requests
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    """Handles all LLM interactions using OpenRouter API"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize LLM handler with OpenRouter API key
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: mistral-7b-instruct)
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            raise ValueError("No API key provided. Set OPENROUTER_API_KEY environment variable.")
        
        # Default to Mistral 7B (good balance of quality and speed)
        self.model = model or "mistralai/mistral-7b-instruct:free"
        
        # OpenRouter API endpoint
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        print(f"✅ LLM Handler initialized with model: {self.model}")
    
    def _call_api(self, prompt: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
        """
        Make a request to OpenRouter API
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Model's response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the response text
            return result['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected API response format: {str(e)}")
    
    def generate_user_response(self, rating: int, review_text: str) -> str:
        """
        Generate a friendly response for the user based on their review
        
        Args:
            rating: Star rating (1-5)
            review_text: User's review text
            
        Returns:
            AI-generated response message
        """
        prompt = f"""You are a friendly customer service representative for a business. 
A customer has left a {rating}-star review with the following feedback:

"{review_text}"

Generate a warm, empathetic, and professional response that:
1. Thanks them for their feedback
2. Acknowledges their specific points (positive or negative)
3. For negative reviews: Apologizes and shows commitment to improvement
4. For positive reviews: Expresses gratitude and encourages return visits
5. Is concise (2-3 sentences max)

Keep the tone friendly and genuine. Do not use generic corporate language.

Response:"""

        try:
            response = self._call_api(prompt, temperature=0.7, max_tokens=200)
            return response
        except Exception as e:
            # Fallback response
            return f"Thank you for your {rating}-star review! We appreciate your feedback and will use it to improve our service."
    
    def generate_admin_summary(self, rating: int, review_text: str) -> str:
        """
        Generate a concise summary for admin dashboard
        
        Args:
            rating: Star rating (1-5)
            review_text: User's review text
            
        Returns:
            Concise summary of the review
        """
        prompt = f"""Summarize this {rating}-star customer review in 1-2 sentences for a manager's dashboard. 
Focus on the key points and overall sentiment.

Review: "{review_text}"

Summary:"""

        try:
            response = self._call_api(prompt, temperature=0.3, max_tokens=150)
            return response
        except Exception as e:
            # Fallback summary
            if rating <= 2:
                return f"Customer expressed dissatisfaction ({rating} stars). Review requires attention."
            elif rating == 3:
                return f"Mixed review ({rating} stars). Customer had both positive and negative experiences."
            else:
                return f"Positive review ({rating} stars). Customer had a good experience."
    
    def generate_recommended_actions(self, rating: int, review_text: str) -> str:
        """
        Generate specific action items based on the review
        
        Args:
            rating: Star rating (1-5)
            review_text: User's review text
            
        Returns:
            Bullet-pointed list of recommended actions
        """
        prompt = f"""Based on this {rating}-star customer review, suggest 2-3 specific, actionable steps 
the business should take. Format as bullet points.

Review: "{review_text}"

Consider:
- For low ratings (1-2): Immediate damage control, specific fixes
- For medium ratings (3): Identify areas for improvement
- For high ratings (4-5): Reinforce what's working, small enhancements

Recommended Actions:"""

        try:
            response = self._call_api(prompt, temperature=0.4, max_tokens=250)
            return response
        except Exception as e:
            # Fallback recommendations
            if rating <= 2:
                return "• Contact customer directly to address concerns\n• Review and fix mentioned issues\n• Implement quality control measures"
            elif rating == 3:
                return "• Analyze feedback for improvement areas\n• Follow up with customer on experience\n• Train staff on customer service"
            else:
                return "• Thank customer for positive feedback\n• Continue current practices\n• Share success with team"
    
    def process_feedback(self, rating: int, review_text: str) -> Dict[str, str]:
        """
        Process feedback and generate all AI responses at once
        
        Args:
            rating: Star rating (1-5)
            review_text: User's review text
            
        Returns:
            Dictionary with user_response, admin_summary, and recommended_actions
        """
        return {
            'user_response': self.generate_user_response(rating, review_text),
            'admin_summary': self.generate_admin_summary(rating, review_text),
            'recommended_actions': self.generate_recommended_actions(rating, review_text)
        }


# Singleton instance
_llm_instance = None

def get_llm_handler(api_key: str = None, model: str = None) -> LLMHandler:
    """Get the LLM handler instance (singleton pattern)"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMHandler(api_key, model)
    return _llm_instance