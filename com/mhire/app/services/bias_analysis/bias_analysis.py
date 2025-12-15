"""
SEEV Bias Analysis - Core Business Logic
Handles GPT-4 integration and bias analysis logic
"""

import openai
import json
from typing import Dict, List
from fastapi import HTTPException
from com.mhire.app.config.config import Config
from com.mhire.app.services.bias_analysis.bias_analysis_schema import BiasBreakdownItem


# ============================================================================
# BIAS CATEGORIES DEFINITION
# ============================================================================

BIAS_CATEGORIES = {
    "B1": "Source Attribution Bias",
    "B2": "Statistical Misrepresentation",
    "B3": "Cherry-Picking Evidence",
    "B4": "False Equivalence",
    "B5": "Omission Bias",
    "B6": "Framing Bias",
    "B7": "Loaded Language / Labeling Bias",
    "B8": "Sensationalism",
    "B9": "Stereotyping",
    "B10": "Gender Bias",
    "B11": "Racial/Ethnic Bias",
    "B12": "Age Bias",
    "B13": "Socioeconomic Bias",
    "B14": "Geographic/Regional Bias",
    "B15": "Cultural Bias",
    "B16": "Religious Bias",
    "B17": "Political Bias",
    "B18": "Corporate/Commercial Bias",
    "B19": "Authority/Credential Bias",
    "B20": "Temporal Bias",
    "B21": "Confirmation Bias Indicators",
    "B22": "Appeal to Emotion",
    "B23": "False Dichotomy",
    "B24": "Ad Hominem Elements",
    "B25": "Hasty Generalization"
}


class BiasAnalysisService:
    """Service class for bias analysis operations"""
    
    def __init__(self):
        """Initialize the service with OpenAI API key from config"""
        config = Config()
        openai.api_key = config.openai_api_key
        
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not configured in environment")
    
    def _create_analysis_prompt(self, text: str) -> str:
        """
        Create the prompt for GPT-4 bias analysis.
        
        Args:
            text: The text content to analyze
            
        Returns:
            Formatted prompt string
        """
        categories_list = "\n".join([f"{k}: {v}" for k, v in BIAS_CATEGORIES.items()])
        
        prompt = f"""You are SEEV Intelligence™, an expert bias detection AI.

Analyze this text for bias. Here are the 25 possible bias categories:

{categories_list}

Text to analyze:
---
{text}
---

CRITICAL INSTRUCTIONS:
1. **ONLY INCLUDE CATEGORIES THAT ARE RELEVANT** to this specific text.
   - If the text doesn't contain statistics, DON'T include "Statistical Misrepresentation"
   - If the text doesn't cite sources, DON'T include "Source Attribution Bias"
   - If the text doesn't mention politics, DON'T include "Political Bias"
   - If the text doesn't mention religion, DON'T include "Religious Bias"
   - Only include categories where the text actually addresses that topic/dimension

2. For RELEVANT categories only, assign a score from 0-100 where:
   - 0-33 = High Bias (severely problematic)
   - 34-66 = Moderate Bias (some concerns)
   - 67-100 = Low Bias (trustworthy, neutral)
   
3. IMPORTANT: Higher scores = better/more neutral content.

4. Be SELECTIVE - only return 5-15 categories that are actually applicable to this text.

5. Think about the text type:
   - Job posting → likely relevant: Gender, Age, Racial/Ethnic, Cultural, Socioeconomic biases
   - News article → likely relevant: Source Attribution, Political, Framing, Loaded Language
   - Research paper → likely relevant: Statistical Misrepresentation, Cherry-Picking, Confirmation Bias
   - Opinion piece → likely relevant: Political, Appeal to Emotion, Ad Hominem, False Dichotomy

6. Look carefully for:
   - Loaded Language: emotionally charged words
   - Sensationalism: exaggeration, drama, alarmist language
   - Appeal to Emotion: manipulating feelings rather than presenting facts
   - Stereotyping: generalizations about groups of people
   - Identity-based biases: Gender, Age, Race, Culture, Religion, etc.

Calculate an overall SEEV score (weighted average of ONLY the relevant categories you include).

Generate a concise title (3-7 words) for this analysis session based on the text content.
Examples:
- "Job Posting - Developer Role"
- "News Article - Climate Policy"
- "Product Review - Smartphone"
- "Opinion Piece - Healthcare Reform"

Provide a brief 2-3 sentence summary of the main bias issues found.

Return response as valid JSON in this EXACT structure:
{{
  "overall_score": 45,
  "title": "Job Posting - Developer Role",
  "categories": [
    {{"category_name": "Gender Bias", "score": 15}},
    {{"category_name": "Age Bias", "score": 20}},
    {{"category_name": "Loaded Language / Labeling Bias", "score": 35}},
    ... (ONLY relevant categories - typically 5-15 total)
  ],
  "summary": "Brief analysis summary explaining the main biases found..."
}}

Return ONLY valid JSON, no markdown formatting."""

        return prompt
    
    async def analyze_with_gpt4(self, text: str) -> Dict:
        """
        Call GPT-4 API for bias analysis.
        
        Args:
            text: The text content to analyze
            
        Returns:
            Dictionary containing analysis results from GPT-4
            
        Raises:
            HTTPException: If OpenAI API call fails
        """
        try:
            prompt = self._create_analysis_prompt(text)
            
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are SEEV Intelligence™. Return only valid JSON."
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
    
    @staticmethod
    def determine_bias_type(score: int) -> str:
        """
        Determine bias type classification based on overall score.
        
        Args:
            score: Overall SEEV score (0-100)
            
        Returns:
            String classification: "Low Bias", "Moderate Bias", or "High Bias"
        """
        if score >= 67:
            return "Low Bias"
        elif score >= 34:
            return "Moderate Bias"
        else:
            return "High Bias"
    
    @staticmethod
    def count_detected_biases(categories: List[Dict]) -> int:
        """
        Count how many categories show significant bias.
        Since we now only return relevant categories, count those with moderate to high bias.
        
        Args:
            categories: List of category dictionaries with scores
            
        Returns:
            Count of categories with scores < 67 (moderate to high bias)
        """
        return sum(1 for cat in categories if cat["score"] < 67)
    
    @staticmethod
    def format_bias_breakdown(categories: List[Dict]) -> List[BiasBreakdownItem]:
        """
        Format category data into BiasBreakdownItem models.
        Excludes categories with score 0 (not detected).
        
        Args:
            categories: List of raw category dictionaries
            
        Returns:
            List of BiasBreakdownItem models
        """
        return [
            BiasBreakdownItem(
                category_name=cat["category_name"],
                score=cat["score"]
            )
            for cat in categories
            if cat["score"] > 0
        ]
    
    async def analyze_text(self, text: str) -> Dict:
        """
        Main analysis method - orchestrates the entire bias analysis process.
        
        Args:
            text: The text content to analyze
            
        Returns:
            Dictionary with complete analysis results
            
        Raises:
            HTTPException: If text is empty or analysis fails
        """
        # Validate input
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        # Call GPT-4 for analysis
        gpt_response = await self.analyze_with_gpt4(text)
        
        # Extract data
        overall_score = gpt_response["overall_score"]
        title = gpt_response.get("title", "Bias Analysis Session")  # Default if not provided
        categories = gpt_response["categories"]
        summary = gpt_response["summary"]
        
        # Process results
        bias_breakdown = self.format_bias_breakdown(categories)
        bias_type = self.determine_bias_type(overall_score)
        detected_count = self.count_detected_biases(categories)
        
        return {
            "overall_seev_score": overall_score,
            "title": title,
            "bias_breakdown": bias_breakdown,
            "bias_type": bias_type,
            "analysis_summary": summary,
            "detected_bias_count": detected_count
        }