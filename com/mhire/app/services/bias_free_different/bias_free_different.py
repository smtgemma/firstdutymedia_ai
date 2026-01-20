"""
Bias-Free Service - Core Business Logic
Handles GPT-4 integration for bias removal
"""

import openai
import json
from typing import Dict, List
from fastapi import HTTPException
from com.mhire.app.config.config import Config
from com.mhire.app.services.bias_free_different.bias_free_different_schema import BiasType


class BiasFreeService:
    """Service class for bias removal operations"""
    
    def __init__(self):
        """Initialize the service with OpenAI API key from config"""
        config = Config()
        openai.api_key = config.openai_api_key
        
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured in environment")
    
    def _get_bias_classification(self, score: int) -> str:
        """
        Convert score to bias classification.
        
        Args:
            score: Bias score (0-100)
            
        Returns:
            Bias classification string
        """
        if score <= 33:
            return "High Bias (severely problematic)"
        elif score <= 66:
            return "Moderate Bias (some concerns)"
        else:
            return "Low Bias (trustworthy, neutral)"
    
    def _create_rewrite_prompt(
        self, 
        text: str, 
        score: int, 
        flags: str,
        bias_types: List[BiasType],
        explanation: str
    ) -> str:
        """
        Create the prompt for GPT-4 bias removal.
        
        Args:
            text: The original text containing biases
            score: Bias score (0-100)
            flags: Flag color indicator
            bias_types: List of detected bias types
            explanation: Explanation of detected biases
            
        Returns:
            Formatted prompt string
        """
        bias_classification = self._get_bias_classification(score)
        
        # Format bias types list
        bias_types_list = "\n".join([
            f"- {bt.code}: {bt.label}"
            for bt in bias_types
        ])
        
        prompt = f"""You are SEEV Intelligence™, an expert at rewriting text to remove biases while preserving meaning.

**ORIGINAL TEXT:**
---
{text}
---

**BIAS ANALYSIS RESULTS:**
- Bias Score: {score}/100
- Bias Classification: {bias_classification}
- Flag Status: {flags}
- Number of Detected Bias Types: {len(bias_types)}
- Explanation: {explanation}

**DETECTED BIAS TYPES:**
{bias_types_list}

**YOUR TASK:**
Rewrite the text to remove ALL detected biases while:

1. **Preserving Core Meaning**: Keep the essential message and intent intact
2. **Maintaining Professional Tone**: Use neutral, professional language
3. **Removing Biased Language**: Address the detected bias types by:
   - Removing loaded/emotionally charged words
   - Eliminating stereotypes and generalizations
   - Replacing biased terms with neutral alternatives
   - Removing age, gender, racial, cultural, or other identity-based language
   - Ensuring balanced, fair representation
   - Using inclusive language

4. **Keeping Structure**: Maintain similar length and format when possible
5. **Being Specific**: Make concrete changes based on the detected bias types

**IMPORTANT GUIDELINES:**
- If the text is a job posting, use inclusive, skills-focused language
- If it's news/article content, ensure balanced, factual presentation
- Remove sensationalism and appeal to emotion
- Replace vague generalizations with specific, neutral descriptions
- Avoid overcorrection - keep natural language flow
- Make the text generic and neutral so no bias is held

Return your response as valid JSON in this EXACT structure:
{{
  "bias_free_text": "The complete rewritten text with all biases removed..."
}}

Return ONLY valid JSON, no markdown formatting."""

        return prompt
    
    async def rewrite_with_gpt4(
        self, 
        text: str, 
        score: int,
        flags: str,
        bias_types: List[BiasType],
        explanation: str
    ) -> Dict:
        """
        Call GPT-4 API for bias removal.
        
        Args:
            text: The original text containing biases
            score: Bias score
            flags: Flag color
            bias_types: List of bias types
            explanation: Bias explanation
            
        Returns:
            Dictionary containing rewritten text
            
        Raises:
            HTTPException: If OpenAI API call fails
        """
        try:
            prompt = self._create_rewrite_prompt(text, score, flags, bias_types, explanation)
            
            response = openai.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are SEEV Intelligence™. Return only valid JSON with bias-free rewritten text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {str(e)}"
            )
    
    async def remove_bias(
        self, 
        text: str, 
        score: int,
        flags: str,
        bias_types: List[BiasType],
        explanation: str
    ) -> Dict:
        """
        Main method to remove bias from text.
        
        Args:
            text: The original text containing biases
            score: Bias score (0-100)
            flags: Flag color indicator
            bias_types: List of detected bias types
            explanation: Explanation of detected biases
            
        Returns:
            Dictionary with bias-free text
            
        Raises:
            HTTPException: If text is empty or processing fails
        """
        # Validate input
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        # Call GPT-4 for rewriting
        gpt_response = await self.rewrite_with_gpt4(text, score, flags, bias_types, explanation)
        
        return {
            "bias_free_text": gpt_response["bias_free_text"]
        }

