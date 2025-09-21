"""
main.py
ETL pipeline for TechCrunch startup articles with Corporate BS API enrichment.
Finds the article with highest keyword count, gets corporate jargon,
and uses DeepSeek AI to create a VC pitch incorporating the phrase.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from datetime import datetime
from deepseek_enrichment import generate_vc_pitch


def setup_directories():
    """Create necessary directories for data storage."""
    directories = ['data/raw', 'data/enriched', 'examples']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
        # If directory exists, just continue silently


def get_user_keyword():
    """Prompt the user for a keyword to search articles for."""
    keyword = input("Enter a keyword to search for in TechCrunch startups articles: ").strip()
    return keyword


def scrape_best_article(keyword):
    """
    Scrape TechCrunch and return the article with the highest keyword frequency.
    """
    print(f"Searching for articles containing '{keyword}'...")
    
    category_url = "https://techcrunch.com/category/startups/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(category_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching TechCrunch: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Find article links
    article_links = []
    for link in soup.find_all("a", href=True):
        href = link.get('href')
        if (href and 'techcrunch.com' in href and 
            ('/2024/' in href or '/2025/' in href)):
            if href not in article_links:
                article_links.append(href)

    print(f"Found {len(article_links)} potential articles")
    
    if not article_links:
        return None

    # Scrape articles and find best match
    articles = []
    for i, link in enumerate(article_links[:10]):  # Check first 10
        print(f"Checking article {i+1}/10...")
        
        try:
            time.sleep(1)
            res = requests.get(link, headers=headers, timeout=10)
            res.raise_for_status()
        except:
            continue

        try:
            art_soup = BeautifulSoup(res.text, "html.parser")

            # Extract title
            title_tag = art_soup.find("h1")
            title = title_tag.get_text().strip() if title_tag else "No title"

            # Extract author
            author_tag = art_soup.find("a", rel="author")
            author = author_tag.get_text().strip() if author_tag else "Unknown"

            # Extract date
            date_tag = art_soup.find("time")
            date = date_tag.get("datetime", "Unknown") if date_tag else "Unknown"

            # Extract body text
            paragraphs = art_soup.find_all("p")
            body_text = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Clean text
            body_text = re.sub(r'\s+', ' ', body_text).strip()

            # Count keyword occurrences
            if body_text and len(body_text) > 100:
                keyword_count = body_text.lower().count(keyword.lower())
                
                if keyword_count > 0:
                    articles.append({
                        "title": title,
                        "author": author,
                        "date": date,
                        "body_text": body_text,
                        "keyword_count": keyword_count,
                        "word_count": len(body_text.split()),
                        "url": link,
                        "extracted_at": datetime.now().isoformat()
                    })
                    print(f"  ✓ Found '{keyword}' {keyword_count} times")

        except Exception as e:
            print(f"  ✗ Error parsing article: {e}")
            continue

    if not articles:
        print(f"No articles found containing '{keyword}'")
        return None

    # Return article with highest keyword count
    best_article = max(articles, key=lambda x: x["keyword_count"])
    print(f"\nBest article: '{best_article['title']}' ({best_article['keyword_count']} mentions)")
    return best_article


def get_corporate_phrase():
    """Get a corporate jargon phrase from the API."""
    print("Getting corporate jargon phrase...")
    
    try:
        response = requests.get("http://127.0.0.1:3000/", timeout=5)
        response.raise_for_status()
        data = response.json()
        phrase = data.get("phrase", "leveraging synergistic opportunities")
        print(f"Corporate phrase: '{phrase}'")
        return phrase
    except Exception as e:
        print(f"Corporate API error: {e}")
        fallback = "leveraging synergistic opportunities"
        print(f"Using fallback phrase: '{fallback}'")
        return fallback


def clean_with_pandas(article_data, corporate_phrase):
    """Clean data with pandas and prepare for enrichment."""
    print("Cleaning data with pandas...")
    
    # Create DataFrames
    article_df = pd.DataFrame([article_data])
    phrase_df = pd.DataFrame([{
        "phrase": corporate_phrase,
        "phrase_length": len(corporate_phrase),
        "word_count": len(corporate_phrase.split())
    }])
    
    # Clean article data
    article_df['title'] = article_df['title'].str.strip()
    article_df['author'] = article_df['author'].str.strip()
    article_df['body_text'] = article_df['body_text'].str.strip()
    
    return article_df, phrase_df


def enrich_with_deepseek(article_data, corporate_phrase):
    """Use DeepSeek to create VC pitch incorporating corporate phrase."""
    print("Generating VC pitch with DeepSeek AI...")
    print(f"Incorporating phrase: '{corporate_phrase}'")
    
    try:
        vc_pitch = generate_vc_pitch(article_data, corporate_phrase)
        if vc_pitch and "Error" not in vc_pitch:
            print(f"✓ Generated pitch: {vc_pitch[:100]}...")
            return vc_pitch
        else:
            print(f"✗ Failed to generate pitch: {vc_pitch}")
            return "Error generating pitch"
    except Exception as e:
        print(f"✗ Error with DeepSeek: {e}")
        return f"Error: {str(e)}"


def save_results(article_df, phrase_df, enriched_article, vc_pitch):
    """Save raw and enriched data."""
    print("Saving results...")
    
    # Save raw data
    article_df.to_csv('data/raw/best_article.csv', index=False)
    article_df.to_json('data/raw/best_article.json', orient='records', indent=2)
    
    phrase_df.to_csv('data/raw/corporate_phrase.csv', index=False)
    phrase_df.to_json('data/raw/corporate_phrase.json', orient='records', indent=2)
    
    # Create enriched version
    enriched_df = article_df.copy()
    enriched_df['corporate_phrase'] = phrase_df.iloc[0]['phrase']
    enriched_df['vc_pitch'] = vc_pitch
    
    # Save enriched data
    enriched_df.to_csv('data/enriched/enriched_article.csv', index=False)
    enriched_df.to_json('data/enriched/enriched_article.json', orient='records', indent=2)
    
    # Create example file
    with open('examples/vc_pitch_example.txt', 'w') as f:
        f.write("VC PITCH WITH CORPORATE JARGON INTEGRATION\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Article: {enriched_article['title']}\n")
        f.write(f"Author: {enriched_article['author']}\n")
        f.write(f"Keyword Mentions: {enriched_article['keyword_count']}\n\n")
        f.write(f"Corporate Phrase Used: '{phrase_df.iloc[0]['phrase']}'\n\n")
        f.write(f"AI-Generated VC Pitch:\n{vc_pitch}\n\n")
        f.write(f"Original Article Excerpt:\n{enriched_article['body_text'][:300]}...\n")
    
    print("✓ Results saved to:")
    print("  - examples/vc_pitch_example.txt (main result)")
    print("  - data/enriched/enriched_article.json")
    print("  - data/raw/ (original data)")


def main():
    """Main ETL pipeline."""
    print("TechCrunch Article → Corporate Jargon → VC Pitch Pipeline")
    print("=" * 55)
    
    # Create directories if they don't exist
    try:
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('data/enriched', exist_ok=True)  
        os.makedirs('examples', exist_ok=True)
    except:
        pass  # Directories probably exist, continue anyway
    
    # Get keyword
    keyword = get_user_keyword()
    if not keyword:
        print("No keyword provided. Exiting.")
        return
    
    # EXTRACT: Find best article and get corporate phrase
    print("\n=== EXTRACTION ===")
    best_article = scrape_best_article(keyword)
    if not best_article:
        print("No suitable article found. Exiting.")
        return
    
    corporate_phrase = get_corporate_phrase()
    
    # TRANSFORM: Clean with pandas
    print("\n=== TRANSFORMATION ===")
    article_df, phrase_df = clean_with_pandas(best_article, corporate_phrase)
    
    # ENRICH: Generate VC pitch with DeepSeek
    print("\n=== ENRICHMENT ===")
    vc_pitch = enrich_with_deepseek(best_article, corporate_phrase)
    
    # LOAD: Save results
    print("\n=== RESULTS ===")
    save_results(article_df, phrase_df, best_article, vc_pitch)
    
    print(f"\n=== FINAL RESULT ===")
    print(f"Best Article: '{best_article['title']}'")
    print(f"Keyword '{keyword}' mentioned {best_article['keyword_count']} times")
    print(f"Corporate Phrase: '{corporate_phrase}'")
    print(f"\nVC Pitch:")
    print(f"{vc_pitch}")
    print(f"\n📄 Full results saved to: examples/vc_pitch_example.txt")


if __name__ == "__main__":
    main()
