"""
deepseek_enrichment.py
Handles all AI-related logic using DeepSeek API for data enrichment.
Provides VC pitch generation and article categorization functionality.
"""

import requests
import json
import time


# DeepSeek API configuration
DEEPSEEK_API_KEY = "sk-a7f42564324a433b836f39b479e4dfa8"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def generate_vc_pitch(article, corporate_phrase):
    """
    Generate a VC-style investment pitch using DeepSeek AI.
    
    Args:
        article (dict): Article data containing title, body_text, etc.
        corporate_phrase (str): Corporate jargon phrase to incorporate
        
    Returns:
        str: AI-generated VC pitch or error message
    """
    # Truncate article body to avoid token limits
    article_body = str(article.get('body_text', ''))
    if len(article_body) > 2000:
        article_body = article_body[:2000] + "..."
    
    prompt = f"""You are a seasoned venture capital analyst. Based on this TechCrunch article, write a compelling 2-3 sentence investment pitch that would excite VCs about this startup opportunity.

Your pitch MUST naturally incorporate this corporate phrase: "{corporate_phrase}"

Make the corporate phrase flow naturally - don't force it awkwardly.

Article Title: {article.get('title', 'N/A')}
Article Content: {article_body}

Write a concise, exciting VC pitch highlighting the investment opportunity:"""

    return _call_deepseek_api(prompt, max_tokens=200)


def categorize_article(article):
    """
    Use DeepSeek AI to categorize the startup article and assess investment potential.
    
    Args:
        article (dict): Article data containing title, body_text, etc.
        
    Returns:
        dict: Category and investment potential assessment
    """
    article_body = str(article.get('body_text', ''))
    if len(article_body) > 1500:
        article_body = article_body[:1500] + "..."
    
    prompt = f"""Analyze this TechCrunch startup article and provide:
1. A specific startup category (e.g., "FinTech", "HealthTech", "AI/ML", "E-commerce", "SaaS", etc.)
2. Investment potential on a scale of 1-10 with brief reasoning

Article Title: {article.get('title', 'N/A')}
Article Content: {article_body}

Respond in this exact JSON format:
{{
    "category": "specific category name",
    "potential": "X/10 - brief reasoning"
}}"""

    response = _call_deepseek_api(prompt, max_tokens=150)
    
    try:
        # Try to parse JSON response
        if response and '{' in response:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except:
        pass
    
    # Fallback parsing
    return {
        "category": "Technology Startup",
        "potential": "5/10 - Unable to assess due to parsing error"
    }


def _call_deepseek_api(prompt, max_tokens=200, temperature=0.7):
    """
    Internal function to make API calls to DeepSeek.
    
    Args:
        prompt (str): The prompt to send to DeepSeek
        max_tokens (int): Maximum tokens in response
        temperature (float): Creativity level (0.0 - 1.0)
        
    Returns:
        str: API response or error message
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(
            DEEPSEEK_URL, 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 401:
            return "Error: Invalid DeepSeek API key"
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response content
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"].strip()
            return content
        else:
            return "Error: Unexpected API response format"
            
    except requests.exceptions.Timeout:
        return "Error: DeepSeek API timeout"
    except requests.exceptions.RequestException as e:
        return f"Error: DeepSeek API request failed - {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON response from DeepSeek API"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"


def test_deepseek_connection():
    """
    Test the DeepSeek API connection and credentials.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    test_prompt = "Respond with exactly: 'DeepSeek API connection successful'"
    
    result = _call_deepseek_api(test_prompt, max_tokens=20)
    
    if "successful" in result.lower():
        print("✓ DeepSeek API connection test passed")
        return True
    else:
        print(f"✗ DeepSeek API connection test failed: {result}")
        return False


def estimate_api_cost(num_articles):
    """
    Estimate the cost of API calls for enrichment.
    
    Args:
        num_articles (int): Number of articles to process
        
    Returns:
        str: Cost estimation
    """
    # Rough estimation based on typical token usage
    tokens_per_article = 400  # Estimated average
    total_tokens = num_articles * tokens_per_article * 2  # 2 calls per article
    
    return f"Estimated {total_tokens:,} tokens for {num_articles} articles"


if __name__ == "__main__":
    # Test the API connection when running this file directly
    print("Testing DeepSeek API connection...")
    
    if test_deepseek_connection():
        print("Ready to use DeepSeek API for enrichment!")
        
        # Demo enrichment
        sample_article = {
            "title": "New AI Startup Raises $10M Series A",
            "body_text": "A new artificial intelligence startup focused on enterprise automation has raised $10 million in Series A funding."
        }
        
        sample_phrase = "leveraging synergistic opportunities"
        
        print("\nDemo VC Pitch Generation:")
        pitch = generate_vc_pitch(sample_article, sample_phrase)
        print(f"Generated Pitch: {pitch}")
        
        print("\nDemo Article Categorization:")
        category = categorize_article(sample_article)
        print(f"Category Analysis: {category}")
        
    else:
        print("Please check your DeepSeek API key and internet connection.")
