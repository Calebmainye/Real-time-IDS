// Prediction JavaScript for CyberShield IDS
// Handles both file upload and manual prediction

document.addEventListener('DOMContentLoaded', function() {
    // File Upload Page Logic
    if (document.querySelector('.file-upload-container')) {
        // Elements
        const dropZone = document.querySelector('.drop-zone');
        const fileInput = document.getElementById('file-input');
        const fileInfo = document.getElementById('file-info');
        const fileName = document.querySelector('.file-name');
        const fileSize = document.querySelector('.file-size');
        const removeFile = document.getElementById('remove-file');
        const analyzeBtn = document.getElementById('analyze-btn');
        const uploadForm = document.getElementById('upload-form');
        const resultsCard = document.getElementById('results-card');
        
        // Drop zone functionality
        if (dropZone) {
            dropZone.addEventListener('click', () => fileInput.click());
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drop-zone--over');
            });
            
            ['dragleave', 'dragend'].forEach(type => {
                dropZone.addEventListener(type, () => {
                    dropZone.classList.remove('drop-zone--over');
                });
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drop-zone--over');
                
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    updateFileInfo();
                }
            });
        }
        
        // File input change
        if (fileInput) {
            fileInput.addEventListener('change', updateFileInfo);
        }
        
        // Remove file button
        if (removeFile) {
            removeFile.addEventListener('click', () => {
                fileInput.value = '';
                fileInfo.classList.add('d-none');
                analyzeBtn.disabled = true;
            });
        }
        
        // Update file info
        function updateFileInfo() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                // Check if file is CSV
                if (!file.name.endsWith('.csv')) {
                    alert('Please upload a CSV file');
                    fileInput.value = '';
                    return;
                }
                
                fileInfo.classList.remove('d-none');
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                analyzeBtn.disabled = false;
            } else {
                fileInfo.classList.add('d-none');
                analyzeBtn.disabled = true;
            }
        }
        
        // Format file size
        function formatFileSize(bytes) {
            if (bytes < 1024) return bytes + ' bytes';
            else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
            else return (bytes / 1048576).toFixed(1) + ' MB';
        }
        
        // Form submission
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                if (!fileInput.files.length) {
                    return;
                }
                
                // Set button to loading state
                analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
                analyzeBtn.disabled = true;
                
                // Create form data
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                // Submit form
                fetch('/predict-file', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.error || 'Error analyzing file');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    // Reset button
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Traffic';
                    analyzeBtn.disabled = false;
                    
                    // Display results
                    displayResults(data);
                })
                .catch(error => {
                    // Reset button
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Traffic';
                    analyzeBtn.disabled = false;
                    
                    // Show error
                    alert('Error: ' + error.message);
                });
            });
        }
        
        // Display results
        function displayResults(data) {
            // Update summary counts
            document.getElementById('total-packets').textContent = data.total;
            document.getElementById('safe-packets').textContent = data.safe;
            document.getElementById('intrusion-packets').textContent = data.intrusions;
            
            // Update message
            const messageTitle = document.getElementById('message-title');
            const messageContent = document.getElementById('message-content');
            const messageDiv = document.getElementById('analysis-message');
            
            if (data.intrusions > 0) {
                messageTitle.textContent = 'Security Alert';
                messageContent.textContent = `Detected ${data.intrusions} potential intrusions in the uploaded traffic data. Review the details below.`;
                messageDiv.className = 'alert alert-danger';
            } else {
                messageTitle.textContent = 'All Clear';
                messageContent.textContent = 'No intrusions detected in the uploaded traffic data.';
                messageDiv.className = 'alert alert-success';
            }
            
            // Create chart
            const ctx = document.getElementById('results-chart').getContext('2d');
            
            // Destroy existing chart if it exists
            if (window.resultsChart) {
                window.resultsChart.destroy();
            }
            
            window.resultsChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Safe Traffic', 'Intrusions'],
                    datasets: [{
                        data: [data.safe, data.intrusions],
                        backgroundColor: ['#28a745', '#dc3545'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Fill intrusion table
            const intrusionTable = document.getElementById('intrusion-table').querySelector('tbody');
            intrusionTable.innerHTML = '';
            
            if (data.intrusions > 0) {
                data.results.forEach((result, index) => {
                    if (result.is_intrusion) {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${index + 1}</td>
                            <td>
                                <div class="progress">
                                    <div class="progress-bar bg-danger" role="progressbar" 
                                         style="width: ${result.confidence * 100}%">
                                        ${(result.confidence * 100).toFixed(2)}%
                                    </div>
                                </div>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary view-packet" data-index="${index}">
                                    <i class="fas fa-eye"></i> View Details
                                </button>
                            </td>
                        `;
                        intrusionTable.appendChild(tr);
                    }
                });
                
                // Add event listeners to view packet buttons
                document.querySelectorAll('.view-packet').forEach(button => {
                    button.addEventListener('click', function() {
                        const index = this.getAttribute('data-index');
                        // In a real app, you would fetch the packet details
                        // For demo, just show a mock modal
                        alert(`Viewing details for packet ${parseInt(index) + 1}`);
                    });
                });
            } else {
                intrusionTable.innerHTML = '<tr><td colspan="3" class="text-center">No intrusions detected</td></tr>';
            }
            
            // Show results card
            resultsCard.classList.remove('d-none');
            resultsCard.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Manual Input Page Logic
    if (document.querySelector('.manual-input-container')) {
        // Elements
        const manualForm = document.getElementById('manual-input-form');
        const randomBtn = document.getElementById('random-values');
        const clearBtn = document.getElementById('clear-form');
        const resultsCard = document.getElementById('manual-results-card');
        const analyzeAnother = document.getElementById('analyze-another');
        const viewAllFeatures = document.getElementById('view-all-features');
        
        // Generate random values
        if (randomBtn) {
            randomBtn.addEventListener('click', () => {
                document.querySelectorAll('#manual-input-form input').forEach(input => {
                    // Generate appropriate random values based on feature name
                    let value;
                    const name = input.name;
                    
                    if (name.includes('duration')) {
                        // Duration in microseconds (0 to 2s)
                        value = Math.floor(Math.random() * 2000000);
                    } else if (name.includes('packet_length')) {
                        // Packet length in bytes (20 to 1500)
                        value = Math.floor(Math.random() * 1480) + 20;
                    } else if (name.includes('port')) {
                        // Port number (1 to 65535)
                        value = Math.floor(Math.random() * 65535) + 1;
                    } else if (name.includes('flag')) {
                        // Flag count (0 to 5)
                        value = Math.floor(Math.random() * 6);
                    } else if (name.includes('packets/s')) {
                        // Packets per second (1 to 1000)
                        value = Math.floor(Math.random() * 1000) + 1;
                    } else if (name.includes('iat')) {
                        // Inter-arrival time in microseconds (0 to 1s)
                        value = Math.floor(Math.random() * 1000000);
                    } else if (name.includes('ratio')) {
                        // Ratio (0 to 10)
                        value = (Math.random() * 10).toFixed(4);
                    } else if (name.includes('win')) {
                        // Window size (0 to 65535)
                        value = Math.floor(Math.random() * 65536);
                    } else {
                        // Default random value (0 to 1000)
                        value = Math.floor(Math.random() * 1000);
                    }
                    
                    input.value = value;
                });
            });
        }
        
        // Clear form
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                manualForm.reset();
            });
        }
        
        // Form submission
        if (manualForm) {
            manualForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                // Convert form to FormData
                const formData = new FormData(manualForm);
                
                // Convert FormData to URL encoded string
                const urlEncodedData = new URLSearchParams(formData).toString();
                
                // Submit form
                fetch('/predict-manual', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: urlEncodedData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.error || 'Error analyzing data');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    // Display results
                    displayManualResults(data, formData);
                })
                .catch(error => {
                    // Show error
                    alert('Error: ' + error.message);
                });
            });
        }
        
        // Analyze another button
        if (analyzeAnother) {
            analyzeAnother.addEventListener('click', () => {
                resultsCard.classList.add('d-none');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
        
        // View all features button
        if (viewAllFeatures) {
            viewAllFeatures.addEventListener('click', () => {
                const modal = new bootstrap.Modal(document.getElementById('all-features-modal'));
                modal.show();
            });
        }
        
        // Display manual prediction results
        function displayManualResults(data, formData) {
            // Show appropriate result icon
            document.getElementById('result-icon-safe').classList.add('d-none');
            document.getElementById('result-icon-danger').classList.add('d-none');
            
            if (data.is_intrusion) {
                document.getElementById('result-icon-danger').classList.remove('d-none');
                document.getElementById('result-title').textContent = 'Intrusion Detected';
                document.getElementById('result-title').className = 'text-danger';
                document.getElementById('result-description').textContent = 'This network packet has been classified as potentially malicious.';
            } else {
                document.getElementById('result-icon-safe').classList.remove('d-none');
                document.getElementById('result-title').textContent = 'Normal Traffic';
                document.getElementById('result-title').className = 'text-success';
                document.getElementById('result-description').textContent = 'This network packet appears to be legitimate traffic.';
            }
            
            // Update confidence bar
            const confidenceBar = document.getElementById('confidence-bar');
            const confidencePercent = data.confidence * 100;
            confidenceBar.style.width = confidencePercent + '%';
            confidenceBar.textContent = confidencePercent.toFixed(2) + '%';
            
            if (data.is_intrusion) {
                confidenceBar.className = 'progress-bar bg-danger';
            } else {
                confidenceBar.className = 'progress-bar bg-success';
            }
            
            // Update threshold value
            document.getElementById('threshold-value').textContent = data.threshold.toFixed(4);
            
            // Generate mock feature importance (in a real app, this would come from the backend)
            const featureImportanceRow = document.getElementById('feature-importance-row');
            featureImportanceRow.innerHTML = '';
            
            // Get all form values
            const features = {};
            for (const [key, value] of formData.entries()) {
                features[key] = parseFloat(value);
            }
            
            // Sort features by "importance" (mock for demo)
            const sortedFeatures = Object.entries(features)
                .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                .slice(0, 6);
            
            // Create feature importance cards
            sortedFeatures.forEach(([feature, value]) => {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-3';
                
                let icon = 'fas fa-info-circle';
                let colorClass = 'text-primary';
                
                if (feature.includes('flag') || feature.includes('port')) {
                    icon = 'fas fa-exclamation-triangle';
                    colorClass = 'text-danger';
                } else if (feature.includes('length') || feature.includes('duration')) {
                    icon = 'fas fa-ruler';
                    colorClass = 'text-warning';
                } else if (feature.includes('packets') || feature.includes('iat')) {
                    icon = 'fas fa-tachometer-alt';
                    colorClass = 'text-info';
                }
                
                col.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title ${colorClass}">
                                <i class="${icon}"></i> ${feature}
                            </h5>
                            <p class="card-text">
                                <strong>Value:</strong> ${value}
                            </p>
                        </div>
                    </div>
                `;
                
                featureImportanceRow.appendChild(col);
            });
            
            // Populate all features modal
            const allFeaturesTable = document.getElementById('all-features-table').querySelector('tbody');
            allFeaturesTable.innerHTML = '';
            
            Object.entries(features).forEach(([feature, value]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${feature}</strong></td>
                    <td>${value}</td>
                `;
                allFeaturesTable.appendChild(tr);
            });
            
            // Show results card
            resultsCard.classList.remove('d-none');
            resultsCard.scrollIntoView({ behavior: 'smooth' });
        }
    }
});