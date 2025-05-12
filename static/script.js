document.addEventListener('DOMContentLoaded', function() {
    // Main elements
    const labelFileInput = document.getElementById('label-files');
    const damageFileInput = document.getElementById('damage-files');
    const analyzeBothBtn = document.getElementById('analyze-both-btn');
    const resultsAccordion = document.getElementById('results-accordion');
    const accordionToggle = document.querySelector('.accordion-toggle');
    const accordionHeader = document.querySelector('.accordion-header');
    
    // Badge elements
    const dateBadge = document.getElementById('date-badge');
    const claimBadge = document.getElementById('claim-badge');
    
    // Result sections
    const dateResultSection = document.getElementById('date-result-section');
    const damageResultSection = document.getElementById('damage-result-section');
    
    // Date verification elements
    const dateVerificationBanner = document.getElementById('date-verification-banner');
    const dateVerificationMessage = document.getElementById('date-verification-message');
    
    // Loading and results divs
    const loadingIndicator = document.getElementById('loading');
    
    // Results content
    const englishCaptionP = document.querySelector('#english-caption p');
    const thaiCaptionP = document.querySelector('#thai-caption p');
    const inputTokensSpan = document.querySelector('#input-tokens');
    const outputTokensSpan = document.querySelector('#output-tokens');
    const costUsdSpan = document.querySelector('#cost-usd');
    const costThbSpan = document.querySelector('#cost-thb');
    
    // Error elements
    const errorDiv = document.getElementById('error-message');
    const errorP = document.querySelector('#error-message p');
    const retryButton = document.getElementById('retry-button');
    
    // Preview elements
    const labelPreviewContent = document.getElementById('label-preview-content');
    const damagePreviewContent = document.getElementById('damage-preview-content');
    
    // Help modal
    const helpModal = document.getElementById('help-modal');
    const helpModalButton = document.getElementById('date-help-button');
    const helpModalClose = document.querySelector('.help-modal-close');
    
    // Stepper elements
    const stepperSteps = document.querySelectorAll('.stepper-step');

    // Cost constants for gpt-4.1-mini (per 1M tokens)
    const INPUT_COST_USD_PER_MILLION = 0.40;
    const OUTPUT_COST_USD_PER_MILLION = 1.60;
    const USD_TO_THB_RATE = 35.0;
    
    // Files containers to keep track of selected files
    let selectedLabelFiles = new DataTransfer();
    let selectedDamageFiles = new DataTransfer();
    
    // Date verification result
    let dateVerificationData = null;
    
    // Helper function to update the active step in the stepper UI
    function updateStepperUI(step) {
        stepperSteps.forEach(stepEl => {
            const stepName = stepEl.getAttribute('data-step');
            stepEl.classList.remove('active', 'completed');
            
            if (stepName === step) {
                stepEl.classList.add('active');
            } else if (
                (step === 'results' && stepName === 'upload')
            ) {
                stepEl.classList.add('completed');
            }
        });
    }
    
    // Initialize event listeners for navigation and modals
    function initUIInteractions() {
        // Accordion toggle
        accordionHeader.addEventListener('click', function(e) {
            if (!e.target.closest('.badge')) {
                resultsAccordion.classList.toggle('open');
            }
        });
        
        // Analyze both button
        analyzeBothBtn.addEventListener('click', analyzeFiles);
        
        // Help modal
        helpModalButton.addEventListener('click', function() {
            helpModal.classList.add('active');
        });
        
        helpModalClose.addEventListener('click', function() {
            helpModal.classList.remove('active');
        });
        
        // Close modal when clicking outside
        helpModal.addEventListener('click', function(e) {
            if (e.target === helpModal) {
                helpModal.classList.remove('active');
            }
        });
        
        // Set up file input listeners
        labelFileInput.addEventListener('change', function() {
            const files = this.files;
            if (validateFiles(files, true)) {
                updateSelectedFiles(files, true);
                updateFileInputUI(true);
                generatePreviews(true);
                checkEnableAnalyzeButton();
            }
        });
        
        damageFileInput.addEventListener('change', function() {
            const files = this.files;
            if (validateFiles(files, false)) {
                updateSelectedFiles(files, false);
                updateFileInputUI(false);
                generatePreviews(false);
                checkEnableAnalyzeButton();
            }
        });
        
        // Error retry button
        retryButton.addEventListener('click', function() {
            errorDiv.style.display = 'none';
        });
    }
    
    // Check if analyze button should be enabled
    function checkEnableAnalyzeButton() {
        analyzeBothBtn.disabled = !(selectedLabelFiles.files.length > 0 && selectedDamageFiles.files.length > 0);
    }
    
    // Main analysis function
    async function analyzeFiles() {
        // Reset previous results
        resetResults();
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        loadingIndicator.querySelector('p').textContent = i18next.t('date_verification_loading');
        
        try {
            // Step 1: Verify date
            const dateVerificationResult = await verifyDate();
            
            // Update UI with date verification result
            updateDateVerificationUI(dateVerificationResult);
            
            // If date is eligible, proceed to damage assessment
            if (dateVerificationResult.english.status === 'ELIGIBLE') {
                // Update loading message
                loadingIndicator.querySelector('p').textContent = i18next.t('loading');
                
                // Step 2: Analyze damage
                const damageResult = await analyzeDamage(dateVerificationResult);
                
                // Update UI with damage assessment result
                updateDamageResultUI(damageResult);
            }
            
            // Hide loading indicator, update stepper, and show results
            loadingIndicator.style.display = 'none';
            updateStepperUI('results');
            resultsAccordion.classList.add('open');
            
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            showError(error.message || 'An error occurred during analysis.');
        }
    }
    
    // Reset all result data
    function resetResults() {
        // Hide all result sections
        dateResultSection.classList.add('hidden');
        damageResultSection.classList.add('hidden');
        
        // Reset badges
        dateBadge.classList.add('hidden');
        claimBadge.classList.add('hidden');
        
        // Clear text content
        englishCaptionP.textContent = '...';
        thaiCaptionP.textContent = '...';
        inputTokensSpan.textContent = '0';
        outputTokensSpan.textContent = '0';
        costUsdSpan.textContent = '$0.00';
        costThbSpan.textContent = '฿0.00';
    }
    
    // Verify date API call
    async function verifyDate() {
        const formData = new FormData();
        formData.append('file', labelFileInput.files[0]); // Send only the first image for date verification
        
        const response = await fetch('/verify-date/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.english?.message || 'An error occurred during date verification.');
        }
        
        return await response.json();
    }
    
    // Analyze damage API call
    async function analyzeDamage(dateVerificationResult) {
        const formData = new FormData();
        
        // Append each damage file
        for (let i = 0; i < damageFileInput.files.length; i++) {
            formData.append('files', damageFileInput.files[i]);
        }
        
        // Append date verification data
        formData.append('date_verification', JSON.stringify(dateVerificationResult));
        
        const response = await fetch('/claimability/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'An error occurred during damage assessment.');
        }
        
        return await response.json();
    }
    
    // Update date verification UI
    function updateDateVerificationUI(result) {
        // Show date result section
        dateResultSection.classList.remove('hidden');
        
        // Update date badge
        dateBadge.classList.remove('hidden');
        dateBadge.className = 'badge'; // Reset class
        
        const status = result.english.status;
        
        if (status === 'ELIGIBLE') {
            dateBadge.classList.add('green');
            dateBadge.querySelector('span').textContent = i18next.t('eligible');
            dateVerificationBanner.classList.add('eligible');
            dateVerificationBanner.classList.remove('ineligible');
            dateVerificationBanner.querySelector('i').className = 'fas fa-check-circle';
        } else {
            dateBadge.classList.add('red');
            dateBadge.querySelector('span').textContent = i18next.t('ineligible');
            dateVerificationBanner.classList.add('ineligible');
            dateVerificationBanner.classList.remove('eligible');
            dateVerificationBanner.querySelector('i').className = 'fas fa-times-circle';
        }
        
        // Format the message with the days value
        const translationKey = status === 'ELIGIBLE' ? 'date_banner_eligible' : 'date_banner_ineligible';
        const message = i18next.t(translationKey, { days: result.english.days_elapsed });
        dateVerificationMessage.textContent = message;
    }
    
    // Update damage result UI
    function updateDamageResultUI(result) {
        // Show damage result section
        damageResultSection.classList.remove('hidden');
        
        // Update claim badge
        claimBadge.classList.remove('hidden');
        claimBadge.className = 'badge'; // Reset class
        
        // Determine if claimable (this is an assumption, adjust based on your actual API response)
        const isClaimable = result.claimable === true;
        
        if (isClaimable) {
            claimBadge.classList.add('green');
            claimBadge.querySelector('span').textContent = i18next.t('claim');
        } else {
            claimBadge.classList.add('red');
            claimBadge.querySelector('span').textContent = i18next.t('unclaim');
        }
        
        // Update text content
        if (result.english && result.thai) {
            englishCaptionP.textContent = result.english;
            thaiCaptionP.textContent = result.thai;
        }
        
        // Update token usage if available
        if (result.token_usage) {
            inputTokensSpan.textContent = result.token_usage.input_tokens.toLocaleString();
            outputTokensSpan.textContent = result.token_usage.output_tokens.toLocaleString();
            
            // Calculate costs
            const inputCost = (result.token_usage.input_tokens / 1000000) * INPUT_COST_USD_PER_MILLION;
            const outputCost = (result.token_usage.output_tokens / 1000000) * OUTPUT_COST_USD_PER_MILLION;
            const totalCostUSD = inputCost + outputCost;
            const totalCostTHB = totalCostUSD * USD_TO_THB_RATE;
            
            costUsdSpan.textContent = `$${totalCostUSD.toFixed(4)}`;
            costThbSpan.textContent = `฿${totalCostTHB.toFixed(2)}`;
        }
    }
    
    // Drag and drop functionality for both upload areas
    function setupDragAndDrop() {
        const uploadAreas = [
            { element: document.querySelector('.label-upload-area'), input: labelFileInput, filesList: selectedLabelFiles },
            { element: document.querySelector('.upload-area'), input: damageFileInput, filesList: selectedDamageFiles }
        ];
        
        uploadAreas.forEach(area => {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                area.element.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                area.element.addEventListener(eventName, function() {
                    area.element.classList.add('highlight');
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                area.element.addEventListener(eventName, function() {
                    area.element.classList.remove('highlight');
                }, false);
            });
            
            area.element.addEventListener('drop', function(e) {
                const dt = e.dataTransfer;
                const droppedFiles = dt.files;
                
                if (validateFiles(droppedFiles, area.input === labelFileInput)) {
                    updateSelectedFiles(droppedFiles, area.input === labelFileInput);
                    updateFileInputUI(area.input === labelFileInput);
                    generatePreviews(area.input === labelFileInput);
                    checkEnableAnalyzeButton();
                }
            }, false);
        });
    }
    
    // Function to validate file uploads
    function validateFiles(files, isLabelUpload) {
        if (!files || files.length === 0) {
            return false;
        }
        
        let hasErrors = false;
        let errorMessage = '';
        
        if (isLabelUpload) {
            // Label validation: only images, max 3, each ≤ 5MB
            const maxLabelSize = 5 * 1024 * 1024; // 5MB
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            
            // Check if we're adding too many files
            if (files.length + selectedLabelFiles.files.length > 3) {
                errorMessage = 'You can upload a maximum of 3 label images.';
                hasErrors = true;
            } else {
                // Check file types
                const invalidFiles = Array.from(files).filter(file => !allowedTypes.includes(file.type));
                if (invalidFiles.length > 0) {
                    const fileNames = invalidFiles.map(f => f.name).join(', ');
                    errorMessage = `Unsupported file type(s): ${fileNames}. Only JPG and PNG images are supported.`;
                    hasErrors = true;
                } else {
                    // Check file sizes
                    const oversizedFiles = Array.from(files).filter(file => file.size > maxLabelSize);
                    if (oversizedFiles.length > 0) {
                        const fileNames = oversizedFiles.map(f => f.name).join(', ');
                        errorMessage = `File(s) too large: ${fileNames}. Maximum size per image is 5MB.`;
                        hasErrors = true;
                    }
                }
            }
        } else {
            // Damage media validation
            const maxImageSize = 10 * 1024 * 1024; // 10MB
            const maxVideoSize = 50 * 1024 * 1024; // 50MB
            const allowedImageTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            const allowedVideoTypes = ['video/mp4'];
            
            // Check if we have a video or images
            const hasVideo = Array.from(files).some(file => allowedVideoTypes.includes(file.type));
            const hasExistingVideo = Array.from(selectedDamageFiles.files).some(file => allowedVideoTypes.includes(file.type));
            
            // If we already have images and trying to add a video, or vice versa
            if (hasVideo && selectedDamageFiles.files.length > 0 && !hasExistingVideo) {
                errorMessage = 'Cannot mix videos and images. Please clear your selection first.';
                hasErrors = true;
            } else if (hasExistingVideo && !hasVideo && selectedDamageFiles.files.length > 0) {
                errorMessage = 'Cannot mix videos and images. Please clear your selection first.';
                hasErrors = true;
            }
            // Make sure we don't have both video and images in new selection
            else if (hasVideo && files.length > 1) {
                errorMessage = 'Please upload either a single video or multiple images, not both.';
                hasErrors = true;
            } else if (hasVideo) {
                // Check video size
                const videoFile = Array.from(files).find(file => allowedVideoTypes.includes(file.type));
                if (videoFile.size > maxVideoSize) {
                    errorMessage = `Video file '${videoFile.name}' is too large. Maximum size is 50MB.`;
                    hasErrors = true;
                }
            } else {
                // Check image types and sizes
                const invalidFiles = Array.from(files).filter(file => !allowedImageTypes.includes(file.type));
                if (invalidFiles.length > 0) {
                    const fileNames = invalidFiles.map(f => f.name).join(', ');
                    errorMessage = `Unsupported file type(s): ${fileNames}. Only JPG and PNG images are supported.`;
                    hasErrors = true;
                } else {
                    // Check image sizes
                    const oversizedFiles = Array.from(files).filter(file => file.size > maxImageSize);
                    if (oversizedFiles.length > 0) {
                        const fileNames = oversizedFiles.map(f => f.name).join(', ');
                        errorMessage = `File(s) too large: ${fileNames}. Maximum size per image is 10MB.`;
                        hasErrors = true;
                    }
                }
            }
        }
        
        if (hasErrors) {
            // Show error
            showError(errorMessage);
            return false;
        }
        
        return true;
    }
    
    // Function to update the selected files
    function updateSelectedFiles(newFiles, isLabelUpload) {
        const fileList = isLabelUpload ? selectedLabelFiles : selectedDamageFiles;
        
        // For damage files, handle video uploads specially
        if (!isLabelUpload) {
            // Clear the DataTransfer object if we're uploading a video
            // (since we only allow either multiple images OR one video)
            if (newFiles.length === 1 && newFiles[0].type.startsWith('video/')) {
                selectedDamageFiles = new DataTransfer();
            }
        }
        
        // Add each file to our DataTransfer object
        for (let i = 0; i < newFiles.length; i++) {
            // Only add the file if it's not already in the list
            const file = newFiles[i];
            let isDuplicate = false;
            
            for (let j = 0; j < fileList.files.length; j++) {
                if (fileList.files[j].name === file.name && 
                    fileList.files[j].size === file.size && 
                    fileList.files[j].type === file.type) {
                    isDuplicate = true;
                    break;
                }
            }
            
            if (!isDuplicate) {
                fileList.items.add(file);
            }
        }
        
        // Update the file input with our managed files
        if (isLabelUpload) {
            labelFileInput.files = fileList.files;
        } else {
            damageFileInput.files = fileList.files;
        }
    }
    
    // Function to update the file input UI
    function updateFileInputUI(isLabelUpload) {
        const fileList = isLabelUpload ? selectedLabelFiles.files : selectedDamageFiles.files;
        const uploadArea = isLabelUpload ? 
            document.querySelector('.label-upload-area') : 
            document.querySelector('.upload-area');
        const fileNote = uploadArea.querySelector('.file-note');
        const placeholderDiv = uploadArea.querySelector('.file-input-placeholder');
        
        if (fileList.length > 0) {
            // Update visual state of upload area
            uploadArea.classList.add('has-files');
            
            // Check if we have a video (only applies to damage files)
            if (!isLabelUpload) {
                const hasVideo = Array.from(fileList).some(file => file.type.startsWith('video/'));
                if (hasVideo) {
                    uploadArea.classList.add('has-video');
                } else {
                    uploadArea.classList.remove('has-video');
                }
            }
            
            // Hide placeholder, show thumbnails
            placeholderDiv.style.display = 'none';
            
            // Update file note with file names or count
            if (fileList.length <= 3) {
                const fileNames = Array.from(fileList).map(file => file.name).join(', ');
                fileNote.innerHTML = `<i class="fas fa-check-circle" style="color: var(--success-color);"></i> ${fileNames}`;
            } else {
                fileNote.innerHTML = `<i class="fas fa-check-circle" style="color: var(--success-color);"></i> ${fileList.length} files selected`;
            }
        } else {
            // Reset upload area
            uploadArea.classList.remove('has-files', 'has-video');
            placeholderDiv.style.display = 'flex';
            
            // Reset file note
            if (isLabelUpload) {
                fileNote.innerHTML = `<i class="fas fa-info-circle"></i> <span data-i18n="label_file_limits">${i18next.t('label_file_limits')}</span>`;
            } else {
                fileNote.innerHTML = `<i class="fas fa-info-circle"></i> <span data-i18n="file_note">${i18next.t('file_note')}</span>`;
            }
        }
    }
    
    // Function to show error messages
    function showError(message) {
        errorP.textContent = message;
        errorDiv.style.display = 'block';
    }
    
    // Function to prevent defaults on events
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Function to generate previews
    function generatePreviews(isLabelUpload) {
        const files = isLabelUpload ? labelFileInput.files : damageFileInput.files;
        const previewContainer = isLabelUpload ? labelPreviewContent : damagePreviewContent;
        
        // Clear existing previews
        previewContainer.innerHTML = '';
        
        // Check if we have files to preview
        if (files.length === 0) {
            return;
        }
        
        // Add preview items
        Array.from(files).forEach(file => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            
            const removeButton = document.createElement('button');
            removeButton.className = 'remove-item';
            removeButton.setAttribute('data-filename', file.name);
            removeButton.innerHTML = '<i class="fas fa-times"></i>';
            removeButton.addEventListener('click', function() {
                removeFile(file.name, isLabelUpload);
            });
            
            // Create thumbnail based on file type
            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.file = file;
                previewItem.appendChild(img);
                previewItem.appendChild(removeButton);
                
                const reader = new FileReader();
                reader.onload = (function(aImg) { 
                    return function(e) { 
                        aImg.src = e.target.result; 
                    }; 
                })(img);
                reader.readAsDataURL(file);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.controls = true;
                video.muted = true;
                
                const source = document.createElement('source');
                source.file = file;
                video.appendChild(source);
                previewItem.appendChild(video);
                previewItem.appendChild(removeButton);
                
                // Add a 'video' class to the container if we have a video
                previewContainer.classList.add('single-video');
                
                const reader = new FileReader();
                reader.onload = (function(aSource) { 
                    return function(e) { 
                        aSource.src = e.target.result; 
                    }; 
                })(source);
                reader.readAsDataURL(file);
            }
            
            // Add file info element
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
            previewItem.appendChild(fileInfo);
            
            // Add to preview container
            previewContainer.appendChild(previewItem);
        });
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    // Function to remove a file
    function removeFile(fileName, isLabelUpload) {
        const filesList = isLabelUpload ? selectedLabelFiles : selectedDamageFiles;
        const fileInput = isLabelUpload ? labelFileInput : damageFileInput;
        const previewContent = isLabelUpload ? labelPreviewContent : damagePreviewContent;
        const fileNote = isLabelUpload ? 
            document.querySelector('.label-upload-area .file-note') :
            document.querySelector('.upload-area .file-note');
        
        // Find the preview item to animate
        const itemToRemove = Array.from(previewContent.querySelectorAll('.preview-item')).find(
            item => item.querySelector('.remove-item').getAttribute('data-filename') === fileName
        );
        
        // Get the current file count for immediate UI feedback
        const currentCount = filesList.files.length;
        const newCount = currentCount - 1;
        
        // Update file count immediately for responsive UI
        if (newCount > 0) {
            if (newCount <= 3) {
                // Will be updated with actual names in the full refresh
                const tempNames = Array.from(filesList.files)
                    .filter(file => file.name !== fileName)
                    .map(file => file.name)
                    .join(', ');
                fileNote.innerHTML = `<i class="fas fa-check-circle" style="color: var(--success-color);"></i> ${tempNames}`;
            } else {
                fileNote.innerHTML = `<i class="fas fa-check-circle" style="color: var(--success-color);"></i> ${newCount} files selected`;
            }
        }
        
        if (itemToRemove) {
            // Apply the removal animation
            itemToRemove.classList.add('removing');
            
            // Wait for animation to complete before removing from DOM
            setTimeout(() => {
                const newFiles = new DataTransfer();
                
                // Add all files except the one to remove
                for (let i = 0; i < filesList.files.length; i++) {
                    const file = filesList.files[i];
                    if (file.name !== fileName) {
                        newFiles.items.add(file);
                    }
                }
                
                // Update our file list
                if (isLabelUpload) {
                    selectedLabelFiles = newFiles;
                    labelFileInput.files = selectedLabelFiles.files;
                } else {
                    selectedDamageFiles = newFiles;
                    damageFileInput.files = selectedDamageFiles.files;
                }
                
                // Update UI
                updateFileInputUI(isLabelUpload);
                
                // Regenerate previews
                generatePreviews(isLabelUpload);
                
                // Remove single-video class if we removed a video
                if (!isLabelUpload && newFiles.files.length === 0) {
                    previewContent.classList.remove('single-video');
                }
                
                // Check if the analyze button should be enabled/disabled
                checkEnableAnalyzeButton();
            }, 300); // Match this to the CSS animation duration
        }
    }
    
    // Initialize the app
    initUIInteractions();
    setupDragAndDrop();
}); 