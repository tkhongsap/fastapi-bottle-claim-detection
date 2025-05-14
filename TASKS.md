# Media Analysis Story Generator Prototype - Tasks

Based on the PRD (Product Requirements Document) for the PoC.

## Completed Tasks
- [x] Initialize project structure (directories, `.gitignore`)
- [x] Set up `requirements.txt`
- [x] Create `.env` placeholder
- [x] Create basic HTML structure (`static/index.html`)
- [x] Implement basic frontend JavaScript (`static/script.js`) for form handling and API call
- [x] Add basic CSS (`static/style.css`)
- [x] Create initial `TASKS.md`
- [x] Implement FastAPI backend (`main.py`)
    - [x] Load environment variables (`python-dotenv`)
    - [x] Initialize FastAPI app and CORS
    - [x] Implement OpenAI client setup and API key validation
    - [x] Define API endpoint (`/analyze/`) to accept file uploads and optional prompt (using `Form`)
    - [x] Implement logic to identify input type (single image, multiple images, video)
    - [x] Implement Base64 encoding for images
    - [x] Implement function to call OpenAI for single/multiple images (translate `generateStoryFromImage`/`generateStoryFromMultipleImages`)
    - [x] Implement basic video handling (save temp file, get metadata - filename, size, type)
    - [x] Implement function to call OpenAI for video metadata (translate `generateStoryFromVideo` - without thumbnail for PoC)
    - [x] Integrate optional text prompt into OpenAI calls
    - [x] Implement response parsing and JSON formatting (`{"english": "...", "thai": "..."}`)
    - [x] Add error handling for API calls and file processing
    - [x] Add root endpoint (`/`) to serve the `index.html` file
    - [x] Mount the `static` directory
- [x] Add token usage tracking and display
    - [x] Update backend to capture input and output token counts from OpenAI API
    - [x] Update response structure to include token information
    - [x] Add UI elements to display token usage information
    - [x] Style token usage display section
- [x] Add basic logging to the backend
    - [x] Configure logging at appropriate levels (INFO, ERROR)
    - [x] Add log statements for API calls, errors, and application lifecycle
    - [x] Include error details in logging for debugging purposes
- [x] Enhance error handling and messages 
    - [x] Improve user-facing error messages on frontend
    - [x] Add more specific error types for different failure scenarios
    - [x] Handle OpenAI API rate limiting and quotas
    - [x] Add retry functionality with user-friendly error messages
- [x] Add file type and size validation
    - [x] Implement server-side validation for allowed file types (JPG, PNG, MP4)
    - [x] Add file size limits to prevent overly large uploads
    - [x] Provide clear error messages for invalid files
    - [x] Add frontend validation to prevent invalid uploads
- [x] Implement Production Date Verification feature
    - [x] Create date extraction module using OpenAI Vision
    - [x] Create date verification module to check 120-day eligibility
    - [x] Add /verify-date/ endpoint to API
    - [x] Integrate date verification with bottle damage assessment flow
    - [x] Add bilingual (English/Thai) responses for date verification
- [x] Update frontend to include production date verification step
    - [x] Add UI for date label upload
    - [x] Display date verification results to users
    - [x] Implement client-side validation for date images
    - [x] Create step-by-step wizard UI with stepper component
    - [x] Add help modal for date verification instructions
    - [x] Create date verification banner for displaying eligibility status
    - [x] Persist date verification data to damage assessment step
- [x] Implement frontend redesign with side-by-side layout
    - [x] Create side-by-side upload grid layout for label and damage media
    - [x] Update stepper to simplified two-step process
    - [x] Implement single "Analyse Both" button for sequential processing
    - [x] Create collapsible accordion for results display
    - [x] Add status badges for date eligibility and claim status
    - [x] Update translation keys and localization files

## In Progress Tasks
- [ ] Test backend endpoints thoroughly
    - [x] Test single image upload analysis
    - [x] Test multiple image upload analysis
    - [x] Test video upload analysis
    - [x] Test with various prompt variations
    - [x] Test error handling scenarios
    - [ ] Test production date verification with sample bottle labels
    - [ ] Test dual-stage UI workflow end-to-end
    - [ ] Test side-by-side layout with various device sizes

## Upcoming Tasks
- [ ] Improve video processing capabilities
    - [ ] Add thumbnail generation for videos
    - [ ] Extract and analyze multiple frames for better video understanding
    - [ ] Process video audio track if present (optional)
- [ ] Optimize performance
    - [ ] Implement proper file cleanup after processing
    - [ ] Add caching for frequent requests if applicable
    - [ ] Optimize image resizing before sending to API
- [ ] Create documentation
    - [ ] Create README.md with setup and usage instructions
    - [ ] Document API endpoints and parameters
    - [ ] Add example requests and responses
    - [ ] Add documentation for production date verification feature
- [ ] Deploy application (if applicable)
    - [ ] Prepare for production deployment
    - [ ] Configure environment for production

# Portfolio/Weekend Project Tasks

A track of tasks related to adding additional examples of bottle assessment to the user manual.

## Completed Tasks
- [x] Created initial analysis of ClaimBottle AI application functionality
- [x] Identified need for more detailed examples in user manual
- [x] Implemented additional examples in the user manual to show both claimable and unclaimable scenarios
- [x] Added a more nuanced unclaimable example showing partial damage patterns
- [x] Added example of partially damaged but unclaimable bottle to manual.html
- [x] Updated translations in both Thai and English locale files
- [x] Implemented dual-stage UI with production date verification as first step
- [x] Added stepper navigation to guide users through the claim assessment process
- [x] Created help modal for production date verification
- [x] Redesigned UI with side-by-side layout for improved user experience
- [x] Created accordion component for results display
- [x] Updated workflow to use single "Analyse Both" button for sequential processing

## In Progress Tasks
- [ ] Review the updated manual for consistency and clarity
- [ ] Add documentation for the production date verification process
- [ ] Test the new side-by-side UI on various devices

## Upcoming Tasks
- [ ] Create examples of production date verification in the user manual
- [ ] Test the manual with actual users to ensure examples are clear and helpful
- [ ] Add more visual aids or diagrams to illustrate damage patterns
- [ ] Explore possibility of adding animation or interactive elements to better explain the assessment criteria 