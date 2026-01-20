"""
Bias-Free Service - Core Business Logic
Handles GPT-4 integration for bias removal
"""

import openai
import json
from typing import Dict
from fastapi import HTTPException
from com.mhire.app.config.config import Config
from com.mhire.app.services.bias_free.bias_free_schema import BiasMetadata


class BiasFreeService:
    """Service class for bias removal operations"""
    
    def __init__(self):
        """Initialize the service with OpenAI API key from config"""
        config = Config()
        openai.api_key = config.openai_api_key
        
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured in environment")
    
    def _create_rewrite_prompt(self, text: str, bias_metadata: BiasMetadata) -> str:
        """
        Create the prompt for GPT-4 bias removal.
        
        Args:
            text: The original text containing biases
            bias_metadata: Bias analysis metadata from the /analyze endpoint
            
        Returns:
            Formatted prompt string
        """
        # Extract problematic categories (score < 67)
        problematic_categories = [
            item for item in bias_metadata.bias_breakdown 
            if item.score < 67
        ]
        
        categories_list = "\n".join([
            f"- {cat.category_name} (Score: {cat.score}/100 - {'High Bias' if cat.score < 34 else 'Moderate Bias'})"
            for cat in problematic_categories
        ])
        
        prompt = f"""You are SEEV Intelligence™, an expert at rewriting text to remove biases while preserving meaning.

**ORIGINAL TEXT:**
---
{text}
---

**BIAS ANALYSIS RESULTS:**
- Overall SEEV Score: {bias_metadata.overall_seev_score}/100
- Bias Classification: {bias_metadata.bias_type}
- Number of Detected Biases: {bias_metadata.detected_bias_count}
- Analysis Summary: {bias_metadata.analysis_summary}

**PROBLEMATIC BIAS CATEGORIES DETECTED:**
{categories_list}

**YOUR TASK:**
Rewrite the text to remove ALL detected biases while:

1. **Preserving Core Meaning**: Keep the essential message and intent intact
2. **Maintaining Professional Tone**: Use neutral, professional language
3. **Removing Biased Language**: Specifically address each detected bias category:
   - Remove loaded/emotionally charged words
   - Eliminate stereotypes and generalizations
   - Replace biased terms with neutral alternatives
   - Remove age, gender, racial, cultural, or other identity-based language
   - Ensure balanced, fair representation
   - Use inclusive language

4. **Keeping Structure**: Maintain similar length and format when possible
5. **Being Specific**: Make concrete changes based on the detected bias categories

**IMPORTANT GUIDELINES:**
- If the text is a job posting, use inclusive, skills-focused language
- If it's news/article content, ensure balanced, factual presentation
- Remove sensationalism and appeal to emotion
- Replace vague generalizations with specific, neutral descriptions
- Avoid overcorrection - keep natural language flow

Return your response as valid JSON in this EXACT structure:
{{
  "bias_free_text": "The complete rewritten text with all biases removed...",
  "changes_made": "Brief summary of the specific changes made (2-3 sentences explaining what biases were addressed and how)"
}}

Return ONLY valid JSON, no markdown formatting."""

        return prompt
    
    async def rewrite_with_gpt4(self, text: str, bias_metadata: BiasMetadata) -> Dict:
        """
        Call GPT-4 API for bias removal.
        
        Args:
            text: The original text containing biases
            bias_metadata: Bias analysis metadata
            
        Returns:
            Dictionary containing rewritten text and changes summary
            
        Raises:
            HTTPException: If OpenAI API call fails
        """
        try:
            prompt = self._create_rewrite_prompt(text, bias_metadata)
            
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
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
    
    async def remove_bias(self, text: str, bias_metadata: BiasMetadata) -> Dict:
        """
        Main method to remove bias from text.
        
        Args:
            text: The original text containing biases
            bias_metadata: Bias analysis metadata from /analyze endpoint
            
        Returns:
            Dictionary with original text, bias-free text, metadata, and changes
            
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
        gpt_response = await self.rewrite_with_gpt4(text, bias_metadata)
        
        return {
            "bias_free_text": gpt_response["bias_free_text"]
        }
