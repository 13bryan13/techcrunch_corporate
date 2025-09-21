# TechCrunch Startup Article ETL Pipeline with AI-Enhanced VC Pitch Generation

An ETL pipeline that identifies the most relevant TechCrunch startup article based on keyword frequency, extracts corporate jargon from an API, and uses DeepSeek AI to generate compelling VC investment pitches that naturally incorporate business buzzwords.

## Project Purpose

This pipeline transforms raw startup news into investment-ready content by combining article analysis with AI-powered pitch generation. The unique value proposition is the natural integration of corporate jargon phrases into serious investment pitches, creating a bridge between business communication styles and venture capital decision-making.

## Data Sources

### 1. TechCrunch Website (Web Scraping)
- **Source**: https://techcrunch.com/category/startups/
- **Purpose**: Extract startup articles and identify the most relevant based on keyword frequency
- **Data Extracted**: Article title, author, publication date, full content, keyword counts
- **Selection Criteria**: Article with highest frequency of user-specified keyword

### 2. Corporate BS Generator API
- **Source**: Local API endpoint (http://127.0.0.1:3000/)
- **Purpose**: Provide authentic corporate jargon phrases for creative enhancement
- **Data Extracted**: Business buzzword phrases ("leveraging synergistic opportunities", etc.)
- **Fallback Strategy**: Built-in corporate phrases when API unavailable

### 3. DeepSeek AI API (Enrichment Source)
- **Purpose**: AI-powered content generation and natural language integration
- **Enhancement**: Creates VC investment pitches incorporating corporate jargon naturally

## AI Enhancements

### Primary Enhancement: VC Pitch Generation
DeepSeek AI analyzes the selected TechCrunch article and generates a compelling 2-3 sentence venture capital investment pitch that naturally incorporates corporate jargon phrases. The AI is specifically prompted to integrate business buzzwords in a way that sounds professional and contextually appropriate.

**Example Enhancement:**
- **Original Article**: "TechCorp raised $5M Series A for their AI automation platform..."
- **Corporate Phrase**: "leveraging synergistic opportunities"
- **AI-Generated VC Pitch**: "TechCorp is leveraging synergistic opportunities in the $50B automation market, positioning their AI platform as the definitive enterprise solution with validated product-market fit and a seasoned team poised for rapid scaling."

### Value Added by AI
- **Time Efficiency**: Transforms hours of manual analysis into seconds
- **Consistency**: Standardized investment pitch format across all articles
- **Creative Integration**: Naturally weaves corporate jargon into professional content
- **Investment Focus**: Converts news articles into actionable investment intelligence

## Installation and Usage

### Prerequisites
```bash
pip install beautifulsoup4 requests pandas
```

### Required Dependencies
- **Python 3.11+** (recommended for pandas compatibility)
- **DeepSeek API key** (configured in `deepseek_enrichment.py`)
- **Corporate BS API** running on `http://127.0.0.1:3000/`

### Running the Pipeline
```bash
python main.py
```

The pipeline will:
1. Prompt for a keyword to search TechCrunch articles
2. Identify the article with highest keyword frequency
3. Extract a corporate jargon phrase from the API
4. Generate an AI-enhanced VC pitch incorporating the phrase
5. Save all raw and enriched data

### Testing DeepSeek Integration
```bash
python deepseek_enrichment.py
```

## Project Structure
```
techcrunch-corporate-etl/
├── main.py                      # Main ETL orchestration
├── deepseek_enrichment.py       # AI enhancement module
├── data/
│   ├── raw/                     # Original extracted data
│   │   ├── best_article.csv
│   │   ├── best_article.json
│   │   ├── corporate_phrase.csv
│   │   └── corporate_phrase.json
│   └── enriched/                # AI-enhanced data
│       ├── enriched_article.csv
│       └── enriched_article.json
├── examples/                    # Before/after demonstrations
│   └── vc_pitch_example.txt
├── requirements.txt
├── README.md
├── DEEPSEEK_USAGE.md
├── AI_USAGE.md
└── .gitignore
```

## Data Processing Pipeline

### Extract Phase
- Scrapes TechCrunch startup category for recent articles
- Identifies article with highest frequency of user keyword
- Calls Corporate BS API for business jargon phrase
- Implements rate limiting and error handling

### Transform Phase
- Uses pandas for data cleaning and standardization
- Removes excessive whitespace and normalizes text fields
- Adds derived metrics (word counts, character lengths)
- Structures data for AI processing

### Enrich Phase
- Sends article content and corporate phrase to DeepSeek AI
- AI generates investment pitch naturally incorporating jargon
- Processes and validates AI responses
- Creates enriched dataset with original + AI-generated content

### Load Phase
- Saves raw extraction data in CSV and JSON formats
- Saves AI-enriched data with additional columns
- Creates human-readable example file showing transformation
- Maintains complete audit trail of processing steps

## Error Handling & Robustness

### API Resilience
- Corporate BS API fallback phrases when service unavailable
- DeepSeek API timeout handling and error recovery
- Network request retries with exponential backoff

### Data Quality
- Input validation for malformed HTML content
- Graceful handling of missing article metadata
- Fallback processing when AI generation fails

### File System Operations
- Automatic directory creation with proper permissions
- Graceful degradation when file saving fails
- Cross-platform path handling

## Sample Output

### Before Enhancement (Raw Article)
```
Title: "AI Startup Raises $10M Series A"
Content: "TechCorp announced today they have raised $10 million..."
Keyword: "AI" (mentioned 8 times)
```

### After Enhancement (AI-Generated VC Pitch)
```
Corporate Phrase: "leveraging synergistic opportunities"
VC Pitch: "TechCorp is leveraging synergistic opportunities in the $50B AI market, positioning itself as the definitive solution for enterprise automation with validated product-market fit and a seasoned technical team ready for rapid scaling."
```

## Benefits and Applications

### For Venture Capital Analysis
- **Rapid Content Generation**: Convert news articles into investment summaries
- **Standardized Evaluation**: Consistent pitch format across all opportunities
- **Enhanced Communication**: Professional business language integration

### For Academic Research
- **AI Integration Study**: Demonstrates practical application of language models
- **ETL Pipeline Design**: Complete data processing workflow implementation
- **Creative AI Applications**: Novel combination of APIs for content enhancement

### Technical Achievements
- **Multi-API Orchestration**: Seamless integration of three different APIs
- **Natural Language Processing**: Contextual integration of disparate content
- **Data Pipeline Engineering**: Robust extract-transform-load implementation
