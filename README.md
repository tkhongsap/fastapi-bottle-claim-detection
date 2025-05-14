# FastAPI Bottle Claim Detection

A specialized media analysis application for **bottle claim detection** and damage assessment, using OpenAI's vision models to evaluate claim eligibility for Chang beer bottles and similar use cases.

## Project Overview

FastAPI Bottle Claim Detection is a web application built to analyze Chang beer bottles and determine if they qualify for claims based on their condition. The application processes uploaded images or videos and generates detailed assessment reports that evaluate the bottle's structural integrity across multiple components (cap, neck, body, bottom). Assessment results are provided in both English and Thai languages.

## Features

- Upload and analyze images (JPG, PNG) or videos (MP4) of bottles
- Support for single or multiple image analysis
- Video frame extraction and detailed analysis
- Proprietary assessment criteria for claim eligibility determination
- Component-based evaluation with individual part scoring
- Percentage-based condition scoring with 80% threshold for claim eligibility
- Detailed visual characteristic identification
- Dual language output (English and Thai)
- Token usage tracking for API consumption monitoring
- User-friendly web interface
- Robust error handling for file type, size, and API errors

## Assessment Process

The application follows a structured evaluation process:
1. **Brand Verification**: Confirms the bottle is Chang brand (bottles of other brands are automatically rejected)
2. **Detailed Component Analysis**:
   - **Cap**: Checks presence and seal integrity
   - **Neck**: Evaluates structural condition and damage
   - **Body**: Assesses completeness and crack patterns
   - **Bottom**: Examines base integrity and separation
3. **Characteristic Matching**: Compares against known patterns of claimable/unclaimable bottles
4. **Score Calculation**: Assigns percentage scores to each component and overall condition
5. **Decision**: Determines claim eligibility based on 80% threshold
6. **Report Generation**: Creates detailed assessment with checkmarks (✅/❌) for passing/failing conditions

## Prerequisites

- Python 3.8+
- OpenAI API key with access to Vision models
- FFmpeg (for video processing)
- OpenCV and NumPy

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-imgstory.git
   cd fastapi-imgstory
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   # OPENAI_ORG_ID=your_org_id  # Optional: Uncomment if using organization ID
   ```
   **Note:** The `.env` file is required. The application will not start without a valid `OPENAI_API_KEY`.

## Usage

1. Start the server (recommended):
   ```
   uvicorn main:app --reload
   ```
   For Windows users, you can use the provided PowerShell script:
   ```
   .\restart-server.ps1
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. Upload bottle images or videos and receive a detailed assessment report with claim eligibility determination.

## API Endpoints

- `GET /` — Serves the web interface (`static/index.html`)
- `GET /document` — Serves the documentation page (`static/docs.html`)
- `GET /manual` — Serves the user manual page (`static/manual.html`)
- `POST /analyze/` — Processes uploaded media files for bottle assessment

### POST /analyze/

**Request:**
- `files`: List of files (JPG, PNG, MP4)
- `prompt` (optional): Text to guide the analysis (currently not used; system uses predefined prompts)

**Response:**
```json
{
  "english": "Detailed assessment in English with claim/unclaim decision and component scores",
  "thai": "Thai language translation of the assessment",
  "token_usage": {
    "input_tokens": 123,
    "output_tokens": 456,
    "total_tokens": 579
  }
}
```

**Error Handling:**
- Returns clear error messages for unsupported file types, file size limits (10MB per image, 50MB per video), and API errors.
- Only JPG, PNG images and MP4 videos are supported. Uploading other file types or exceeding size limits will result in a descriptive error.

## Key Assessment Criteria

The application evaluates bottles using a comprehensive set of characteristics including:

**For Claimable Bottles:**
- Breakage at specific structural weak points
- Specific fragmentation and crack patterns
- Detached neck with sealed cap integrity
- Main body remaining largely intact
- Visible but contained damage patterns

**For Unclaimable Bottles:**
- Catastrophic fragmentation
- Extensive crack propagation
- Significant structural instability
- Multiple sharp edges and dangerous fragments
- Severe compromise of bottle integrity

The final determination includes both a percentage score and a binary claim/unclaim decision.

## Project Structure

```
fastapi-imgstory/
├── .env                  # Environment variables
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── restart-server.ps1    # Server restart script for Windows
├── TASKS.md              # Project tasks and progress tracking
├── static/               # Static files (HTML, CSS, JavaScript, locales)
│   ├── index.html        # Web interface
│   ├── script.js         # Frontend JavaScript
│   ├── style.css         # CSS styles
│   ├── docs.html         # Documentation page
│   ├── manual.html       # User manual
│   └── locales/          # Localization files (e.g., en.json, th.json)
├── uploads/              # Temporary upload storage
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── media_analysis.py # Media analysis logic
│   ├── media_processing.py # Image processing
│   ├── media_validation.py # File validation
│   ├── openai_client.py  # OpenAI API client
│   ├── prompts.py        # Assessment criteria and prompt templates
│   ├── story_generation.py # Assessment generation functions
│   └── video_processing.py # Video processing
└── attached_assets/      # (Optional) Additional assets
```

## Upcoming Improvements

- Enhanced video processing with multiple frame analysis
- Integration of machine learning for preliminary damage assessment
- Performance optimizations and response caching
- Support for additional bottle brands and types
- Advanced reporting with visual annotations identifying damage points
- Batch processing for multiple bottles

---

**Note:** This project does not currently include a LICENSE file. If you intend to open source or distribute this project, please add an appropriate license. 