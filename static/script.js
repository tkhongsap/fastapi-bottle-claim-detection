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
    // Claim status bar (new summary section)
    const claimStatusBar = document.getElementById('claim-status-bar');
    const claimStatusLabel = document.getElementById('claim-status-label');

    
    // Result sections
    const dateResultSection = document.getElementById('date-result-section');
    const damageResultSection = document.getElementById('damage-result-section');

    // Date verification elements
    const dateVerificationBanner = document.getElementById('date-verification-banner');
    const dateVerificationMessage = document.getElementById('date-verification-message');
    
    // Loading and results divs
    const loadingIndicator = document.getElementById('loading');
    
    // Results content
    // const englishCaptionP = document.querySelector('#english-caption p');
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
    const INPUT_COST_USD_PER_MILLION_GPT_41 = 2;
    const OUTPUT_COST_USD_PER_MILLION_GPT_41 = 8;
    // Cost constants for o4-mini (per 1M tokens)
    const INPUT_COST_USD_PER_MILLION_O4_MINI = 1.1;
    const OUTPUT_COST_USD_PER_MILLION_O4_MINI = 4.4;

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
        resetClaimUI();
        resetResults();
    
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        loadingIndicator.querySelector('p').textContent = i18next.t('date_verification_loading');
    
        try {
            const dateVerificationResult = await verifyDate();
            console.log("📦 sending label file:", labelFileInput.files[0]);

            console.log("✅ calling updateDateVerificationUI with:", dateVerificationResult);
            updateDateVerificationUI(dateVerificationResult);
    
            const isDateEligible = dateVerificationResult.english.status === 'ELIGIBLE';
            let isDamageClaimable = false;
            const damageClaimInfo = document.getElementById('damage-claim-info');
            damageClaimInfo.textContent = '❌ ไม่เป็นความเสียหายที่สามารถเคลมได้'
    
            if (isDateEligible) {
                loadingIndicator.querySelector('p').textContent = i18next.t('loading');
                const damageResult = await analyzeDamage(dateVerificationResult);
    
                updateDamageResultUI(damageResult);
                isDamageClaimable = damageResult.claimable === true;
                damageClaimInfo.textContent = isDamageClaimable ? '✅ เป็นความเสียหายที่สามารถเคลมได้' : '❌ ไม่เป็นความเสียหายที่สามารถเคลมได้';
            }
    
            // ✅ สรุปการเคลมได้จริงหรือไม่
            // const claimStatusBar = document.getElementById('claim-status-bar');
            // const claimStatusLabel = document.getElementById('claim-status-label');
    
            // if (isDateEligible && isDamageClaimable) {
            //     claimStatusBar.classList.remove('red');
            //     claimStatusBar.classList.add('green');
            //     claimStatusLabel.textContent = i18next.t('claim');
            // } else {
            //     claimStatusBar.classList.add('red');
            //     claimStatusBar.classList.remove('green');
            //     claimStatusLabel.textContent = i18next.t('unclaim');
            // }

            // ✅ สรุปการเคลมได้จริงหรือไม่ — หลังประเมินครบ 2 ส่วน
            const claimStatusBar = document.getElementById('claim-status-bar');
            const claimStatusLabel = document.getElementById('claim-status-label');

            claimStatusBar.classList.remove('hidden'); // ✅ แสดงกล่อง

            if (isDateEligible && isDamageClaimable) {
                claimStatusBar.classList.remove('red');
                claimStatusBar.classList.add('green');
                claimStatusLabel.textContent = i18next.t('claim');
            } else {
                claimStatusBar.classList.add('red');
                claimStatusBar.classList.remove('green');
                claimStatusLabel.textContent = i18next.t('unclaim');
            }

    
            // Finish UI updates
            loadingIndicator.style.display = 'none';
            updateStepperUI('results');
            resultsAccordion.classList.add('open');
            
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            showError(error.message || 'An error occurred during analysis.');
        }
    }
    
    function formatDateToDDMMYYYY(dateObj) {
        const day = String(dateObj.getDate()).padStart(2, '0');
        const month = String(dateObj.getMonth() + 1).padStart(2, '0'); // month is 0-indexed
        const year = dateObj.getFullYear();
        return `${day}/${month}/${year}`;
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
        // englishCaptionP.textContent = '...';
        thaiCaptionP.textContent = '...';
        inputTokensSpan.textContent = '0';
        outputTokensSpan.textContent = '0';
        costUsdSpan.textContent = '$0.00';
        costThbSpan.textContent = '฿0.00';
    }

    function resetClaimUI() {
        // ซ่อนกล่องผลการตรวจสอบวันที่ผลิต
        document.getElementById('prod-date').textContent = '-';
        document.getElementById('exp-date').textContent = '-';
        document.getElementById('days-ago').textContent = '-';
        document.getElementById('claim-info').textContent = '-';
        
        // ซ่อนกล่องเคลมได้ / ไม่ได้
        const claimStatusBar = document.getElementById('claim-status-bar');
        const claimStatusLabel = document.getElementById('claim-status-label');
        claimStatusBar.classList.remove('green', 'red');
        claimStatusBar.classList.add('hidden'); // ✅ ซ่อนเคลม bar
        claimStatusLabel.textContent = '';
    
        // ซ่อน section ถ้ามีการเปิดไว้
        const dateResultCard = document.getElementById('date-result-card');
        if (dateResultCard) {
            dateResultCard.classList.add('hidden'); // ✅ ซ่อนกล่องวันที่
        }
        const damageResultSection = document.getElementById('damage-result-section');
        if (damageResultSection) {
            damageResultSection.classList.add('hidden');
        }

        
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
        
        
        const result = await response.json();
        console.log("🎯 API /verify-date/ response:", result);
        return result;

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
    function parseDDMMYYYYToISO(ddmmyyyy) {
        const [day, month, year] = ddmmyyyy.split('/');
        return `${year}-${month}-${day}`;
    }
    
    function updateDateVerificationUI(result) {

        document.getElementById('date-result-card').classList.remove('hidden');
        // document.getElementById('claim-status-bar').classList.remove('hidden');
        console.log("updateDateVerificationUI called");
        const status = result.english.status;
        const rawProdDate = result.english.production_date;
        const isoProdDate = parseDDMMYYYYToISO(rawProdDate);
        const prodDateObj = new Date(isoProdDate);
    
        const expDateObj = new Date(prodDateObj);
        expDateObj.setFullYear(expDateObj.getFullYear() + 1);
        const expDateFormatted = formatDateToDDMMYYYY(expDateObj);
    
        document.getElementById('prod-date').textContent = rawProdDate;
        document.getElementById('exp-date').textContent = expDateFormatted;
        document.getElementById('days-ago').textContent = result.english.days_elapsed;
        document.getElementById('claim-info').textContent = result.thai.message;
    
        const daysElapsed = parseInt(result.english.days_elapsed);
        console.log('Days elapsed:', daysElapsed); // <== ให้ลอง console.log ตรงนี้
        
    
        // เพิ่มบรรทัดสำหรับสถานะรับเคลม
        const claimInfo = document.getElementById('claim-info');
        claimInfo.textContent = daysElapsed <= 120
            ? '✅ อยู่ในระยะเวลารับเคลม'
            : '❌ ไม่อยู่ในระยะเวลารับเคลม';
    }
    
      
    
    
    
    
    // Update damage result UI
    function updateDamageResultUI(result) {
        damageResultSection.classList.remove('hidden');
        console.log(result)
        if (result.thai) {
            document.querySelector('#thai-caption p').textContent = result.thai;
        }
    
        if (result.total_input_tokens && result.total_output_tokens) {
            inputTokensSpan.textContent = result.total_input_tokens.toLocaleString();
            outputTokensSpan.textContent = result.total_output_tokens.toLocaleString();
        
            costUsdSpan.textContent = `$${result.total_cost_usd.toFixed(4)}`;
            costThbSpan.textContent = `฿${result.total_cost_thb.toFixed(2)}`;
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