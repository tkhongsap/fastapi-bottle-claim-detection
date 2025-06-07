# Product Requirements Document (PRD): Production Date Verification Feature

## 1. Introduction

This document outlines the requirements for a new "Production Date Verification" feature for the ClaimBottle AI application. This feature will enhance the bottle claim eligibility assessment by first verifying that the bottle's production date falls within the required 120-day window before proceeding with the standard damage assessment.

## 2. Feature Overview

The Production Date Verification feature will:
1. Request users to upload a clear image of the bottle label showing the production date
2. Extract and interpret the production date from the label image using AI vision 
3. Calculate if the bottle is within the 120-day eligibility window
4. Only proceed with damage assessment if the date requirement is met
5. Provide clear feedback to users regarding date verification results

## 3. Business Requirements

### 3.1 Business Need
- Chang beer bottles are only eligible for claims if they were produced within the last 120 days
- Manual verification of production dates is time-consuming and error-prone
- Automating date verification will improve assessment accuracy and reduce processing time

### 3.2 Success Metrics
- 90%+ accuracy in production date extraction
- 50% reduction in time spent on date verification
- 30% reduction in ineligible claim submissions
- Improved user satisfaction scores

## 4. User Experience

### 4.1 User Flow
1. User initiates bottle claim assessment process
2. System prompts user to upload a clear image of the bottle label showing the production date
3. System analyzes the image and extracts the production date
4. System calculates if the bottle is within the 120-day eligibility window
   - If eligible: System proceeds with the standard damage assessment flow
   - If ineligible: System informs the user that the bottle is not eligible due to age
5. User receives comprehensive assessment results including date verification status

### 4.2 UI Requirements

#### 4.2.1 Production Date Upload Screen
- Header: "Upload Production Date Label"
- Instruction text: "Please upload a clear photo of the bottle label showing the production date. The date must be clearly visible."
- Upload area with drag-and-drop functionality
- Preview of uploaded image
- Progress indicator during processing
- Link to help content showing where to find production dates on Chang bottles

#### 4.2.2 Date Verification Results Display
- Clear indication of production date extracted (e.g., "Production Date: DD/MM/YYYY")
- Elapsed days calculation (e.g., "Days since production: XX")
- Visual indicator of eligibility status:
  - Green checkmark ✅ if within 120 days
  - Red X ❌ if beyond 120 days
- Translated results in both English and Thai

#### 4.2.3 Integration with Existing UI
- The date verification step should be presented before the damage assessment step
- Maintain consistent styling with the existing application
- Mobile-responsive design
- Appropriate error states for unclear images or unrecognizable dates

## 5. Technical Requirements

### 5.1 API Endpoint

Add a new endpoint `/verify-date/` that:
- Accepts POST requests with image file uploads
- Validates files (format, size)
- Processes the image to extract production date
- Returns verification results in a structured format

**Request:**
```
POST /verify-date/
Content-Type: multipart/form-data

file: [Image file of bottle label]
```

**Response:**
```json
{
  "english": {
    "status": "ELIGIBLE|INELIGIBLE",
    "production_date": "YYYY-MM-DD",
    "days_elapsed": 85,
    "max_allowed_days": 120,
    "message": "This bottle was produced on [DATE], which is [X] days ago. It is eligible for claim assessment."
  },
  "thai": {
    "status": "มีสิทธิ์|ไม่มีสิทธิ์",
    "production_date": "YYYY-MM-DD",
    "days_elapsed": 85,
    "max_allowed_days": 120,
    "message": "[Thai translation of the message]"
  },
  "token_usage": {
    "input_tokens": 123,
    "output_tokens": 456,
    "total_tokens": 579
  }
}
```

### 5.2 Backend Components

#### 5.2.1 Date Extraction Module
Create a new module `utils/date_extraction.py` that:
- Takes an image as input
- Uses OpenAI's vision model to locate and extract the production date
- Handles various date formats that might appear on Chang bottles
- Returns structured date information

#### 5.2.2 Date Verification Module
Create a new module `utils/date_verification.py` that:
- Takes extracted date as input
- Calculates the number of days between production date and current date
- Determines eligibility based on the 120-day rule
- Handles edge cases (unclear dates, missing information)

#### 5.2.3 Extensions to Existing Code

Modify `main.py` to:
- Add the new endpoint `/verify-date/`
- Update the existing `/analyze/` endpoint to accept an optional date verification result
- Add logic to skip damage assessment if date verification fails

Modify `media_analysis.py` to:
- Add a date verification check before proceeding with damage assessment
- Update result format to include date verification details

### 5.3 AI Prompt Enhancement

Update `utils/prompts.py` to add a new prompt for date extraction:
- Specific instructions to identify production date formats on Chang bottles
- Guidelines for handling partially visible or unclear dates
- Format standardization instructions (YYYY-MM-DD)

### 5.4 Frontend Updates

Update `static/index.html` and related files to:
- Add a new step in the upload process for date verification
- Create new UI components to display date verification results
- Update validation logic for the new file upload requirements
- Enhance error handling for date-related issues

### 5.5 User Manual Updates

Update `static/manual.html` to:
- Add information about the new date verification requirement
- Include visual examples of where to find production dates on Chang bottles
- Provide troubleshooting tips for date verification issues
- Update FAQs to address common date-related questions

## 6. Internationalization

- All new user-facing text should be added to both English and Thai locale files
- Error messages and status indicators should be translated
- Date formats should be displayed according to locale standards

## 7. Testing Requirements

### 7.1 Unit Tests
- Test date extraction accuracy with various label images
- Test date calculation logic with edge cases
- Test eligibility determination for different scenarios

### 7.2 Integration Tests
- Test the entire flow from date verification to damage assessment
- Test API responses for different input scenarios
- Test error handling and fallback mechanisms

### 7.3 User Acceptance Testing
- Test with real Chang bottle labels of various production dates
- Test with intentionally unclear or obscured date labels
- Test with different image qualities and lighting conditions

## 8. Dependencies and Constraints

### 8.1 Dependencies
- OpenAI Vision API for date extraction
- Date/time libraries for calculation
- Existing file upload and validation mechanisms

### 8.2 Constraints
- Maintain performance requirements (response time under 5 seconds)
- Maintain file size limits (10MB for images)
- Ensure backward compatibility with existing clients

## 9. Deployment and Release Plan

### 9.1 Development Phases
1. Backend Development (2 weeks)
   - Implement date extraction and verification modules
   - Create new API endpoint
   - Develop integration with existing assessment flow
   
2. Frontend Development (1.5 weeks)
   - Implement UI updates for date verification
   - Create new UI components
   - Implement client-side validation

3. Testing (1 week)
   - Unit and integration testing
   - Performance testing
   - User acceptance testing

4. Deployment (0.5 weeks)
   - Deploy to staging environment
   - Final validation
   - Production deployment

### 9.2 Dependencies
- Completion of existing bottle assessment feature
- Access to sample Chang bottles with various production dates for testing

## 10. Future Considerations

- Adding batch processing capabilities for multiple bottles
- Implementing a caching mechanism for repeated date verifications
- Developing an offline mode for date verification
- Creating a database to store verification results for analytics
- Building a reporting feature for date verification statistics

## Appendices

### Appendix A: Chang Bottle Date Format Examples
- Include examples of how production dates appear on different Chang bottle types
- Provide sample images with production dates highlighted
- Document known date format variations

### Appendix B: Eligibility Calculation Reference
- Detailed explanation of how the 120-day window is calculated
- Edge case handling (leap years, time zones, etc.)
- Example calculations for reference