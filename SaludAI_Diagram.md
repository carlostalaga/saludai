# SaludAI Process Flow Diagram

```
+--------------------------------+
|          URL or Text           |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 0: Input Verification    |
|  - Check if URL or raw text    |
|  - Extract text from URL       |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 1: TRANSLATION           |
|  - Split text into chunks      |
|  - Translate English to Spanish|
|  - Handle technical terms      |
|  - Remove reference markers    |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 2: MODERATION            |
|  - Check for inappropriate     |
|    content                     |
|  - Filter or flag content      |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 3: FACT-CHECK            |
|  - Compare with original text  |
|  - Ensure factual accuracy     |
|  - Prevent fabrication         |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 4: SEO OPTIMIZATION      |
|  - Generate excerpt            |
|  - Assign category             |
|  - Map category to WordPress ID|
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 4.5: FORMAT CONTENT      |
|  - Extract article title       |
|  - Format content as HTML      |
|  - Structure for WordPress     |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 5: THUMBNAIL GENERATION  |
|  - Generate image using DALL-E |
|  - Download generated image    |
+--------------------------------+
               |
               v
+--------------------------------+
|  STEP 6: WORDPRESS PUBLISHING  |
|  - Upload thumbnail            |
|  - Publish article with title  |
|  - Attach excerpt & category   |
+--------------------------------+
```

## Component Interactions

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  translation  │     │   moderation  │     │  fact_check   │
│    module     │────▶│     module    │────▶│    module     │
└───────────────┘     └───────────────┘     └───────────────┘
        │                                            │
        │                                            │
        v                                            v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│      seo      │     │   formatting  │◀────│    config     │
│    module     │────▶│     module    │     │    module     │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        │                     │                     │
        v                     v                     v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   thumbnail   │────▶│   wordpress   │◀────│      env      │
│    module     │     │     module    │     │   variables   │
└───────────────┘     └───────────────┘     └───────────────┘
```

## Technical Stack

- **OpenAI Integration**:
  - GPT-4 (translation, moderation, fact-check)
  - GPT-3.5-Turbo (formatting, SEO)
  - DALL-E (thumbnail generation)

- **Web Technologies**:
  - WordPress API (publishing)
  - Beautiful Soup (content extraction)
  - Requests (HTTP operations)

- **Environment**:
  - Python
  - dotenv for configuration
  - Environment variables for API keys

## Data Flow

1. **Input**: URL or raw text
2. **Text Extraction**: If URL, uses Beautiful Soup to extract content
3. **Translation**: Content is split into chunks and translated from English to Spanish
4. **Moderation**: Content is checked for appropriateness
5. **Fact Checking**: Translated content is verified against original
6. **SEO Processing**: Excerpt generated and category assigned
7. **Formatting**: Content formatted as HTML with title extraction
8. **Image Generation**: Thumbnail created using DALL-E
9. **Publishing**: Content published to WordPress with metadata and thumbnail

## Implementation Details

- **Error Handling**: Each module includes try/except blocks and detailed logging
- **API Integration**: OpenAI and WordPress APIs configured via environment variables
- **Chunking**: Long text is split into manageable chunks for API processing
- **Technical Term Handling**: Special handling for technical terms and acronyms in translation 

## Installation Instructions

### System Requirements
- Python 3.8 or higher
- Internet connection for API access
- WordPress site with REST API enabled

### Step 1: Clone the Repository
```bash
git clone https://github.com/username/saludai.git
cd saludai
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the root directory with the following variables:
```
# OpenAI API key
OPENAI_API_KEY=your_openai_api_key

# WordPress credentials
WP_URL=https://your-wordpress-site.com/wp-json/wp/v2/posts
MEDIA_URL=https://your-wordpress-site.com/wp-json/wp/v2/media
WP_USER=your_wordpress_username
WP_APP_PASSWORD=your_wordpress_app_password
```

## Usage Instructions

### Processing a URL
To translate and publish content from a web page:
```bash
python main.py https://example.com/article-to-translate
```

### Processing Raw Text
To translate and publish raw text content:
```bash
python main.py "Your English text to translate and publish"
```

### Debug Mode
Debug mode is enabled by default in `main.py`. To disable verbose output:
1. Open `main.py`
2. Change `DEBUG = True` to `DEBUG = False`

### Example Commands
```bash
# Process a medical article
python main.py https://www.healthnews.com/some-medical-article

# Process scientific research
python main.py https://www.sciencedaily.com/some-research-article

# Process raw text
python main.py "The latest research in artificial intelligence shows promising results for medical diagnosis. Researchers at Stanford University have developed a new algorithm that can detect early signs of cancer with 95% accuracy."
``` 