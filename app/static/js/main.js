document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseButton = document.getElementById('browseButton');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');

    // Drag and drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    // Handle file drop
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle file selection through browse button
    browseButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        if (!isValidFileType(file)) {
            showError('Please upload a PDF or image file (JPG, PNG)');
            return;
        }

        uploadFile(file);
    }

    function isValidFileType(file) {
        const validTypes = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff',
            'image/webp'
        ];
        return validTypes.includes(file.type);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show loading state
        loading.classList.remove('hidden');
        results.classList.add('hidden');

        fetch('/api/verify', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || data.details || 'An error occurred while processing the file');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                if (data.installation_guide) {
                    showInstallationGuide(data.error, data.installation_guide);
                } else {
                    showError(data.error);
                }
                return;
            }
            displayResults(data.data);
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            loading.classList.add('hidden');
        });
    }

    function showInstallationGuide(error, guide) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full';
        modal.innerHTML = `
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3 text-center">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">${error}</h3>
                    <div class="mt-2 px-7 py-3">
                        <p class="text-sm text-gray-500 text-left whitespace-pre-line">${guide}</p>
                    </div>
                    <div class="items-center px-4 py-3">
                        <button id="closeModal" class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md shadow-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('closeModal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }

    function displayResults(data) {
        results.classList.remove('hidden');

        // Display doctor verification results
        const doctorVerification = document.getElementById('doctorVerification');
        doctorVerification.innerHTML = createDoctorVerificationHTML(data.doctor_verification);

        // Display document analysis results
        const documentAnalysis = document.getElementById('documentAnalysis');
        documentAnalysis.innerHTML = createDocumentAnalysisHTML(data.tampering_detection);

        // Display medication analysis results
        const medicationAnalysis = document.getElementById('medicationAnalysis');
        medicationAnalysis.innerHTML = createMedicationAnalysisHTML(data.drug_analysis);
    }

    function createDoctorVerificationHTML(verification) {
        const statusClass = verification.is_valid ? 'text-green-600' : 'text-red-600';
        const statusIcon = verification.is_valid ? '✓' : '✗';
        
        return `
            <div class="space-y-4">
                <div class="flex items-center space-x-2">
                    <span class="text-2xl ${statusClass}">${statusIcon}</span>
                    <span class="font-medium ${statusClass}">${verification.is_valid ? 'Valid' : 'Invalid'} License</span>
                </div>
                ${verification.is_valid ? `
                    <div class="bg-gray-50 p-4 rounded-md">
                        <p class="text-gray-700"><span class="font-medium">Doctor:</span> ${verification.doctor_info.name}</p>
                        <p class="text-gray-700"><span class="font-medium">Specialty:</span> ${verification.doctor_info.specialty}</p>
                        <p class="text-gray-700"><span class="font-medium">License Status:</span> ${verification.doctor_info.license_status}</p>
                    </div>
                ` : `
                    <p class="text-red-600">${verification.message}</p>
                `}
            </div>
        `;
    }

    function createDocumentAnalysisHTML(analysis) {
        const statusClass = analysis.is_tampered ? 'text-red-600' : 'text-green-600';
        const statusIcon = analysis.is_tampered ? '✗' : '✓';
        
        return `
            <div class="space-y-4">
                <div class="flex items-center space-x-2">
                    <span class="text-2xl ${statusClass}">${statusIcon}</span>
                    <span class="font-medium ${statusClass}">${analysis.is_tampered ? 'Potential Tampering Detected' : 'No Tampering Detected'}</span>
                </div>
                ${analysis.detected_issues.length > 0 ? `
                    <div class="bg-gray-50 p-4 rounded-md">
                        <p class="font-medium text-gray-700 mb-2">Detected Issues:</p>
                        <ul class="list-disc list-inside space-y-1">
                            ${analysis.detected_issues.map(issue => `
                                <li class="text-gray-600">${issue}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                <p class="text-sm text-gray-500">Confidence: ${Math.round(analysis.confidence * 100)}%</p>
            </div>
        `;
    }

    function createMedicationAnalysisHTML(analysis) {
        return `
            <div class="space-y-4">
                <div class="flex items-center space-x-2">
                    <span class="text-2xl ${getRiskLevelClass(analysis.risk_level)}">${getRiskLevelIcon(analysis.risk_level)}</span>
                    <span class="font-medium ${getRiskLevelClass(analysis.risk_level)}">${getRiskLevelText(analysis.risk_level)}</span>
                </div>
                
                ${analysis.medications.length > 0 ? `
                    <div class="bg-gray-50 p-4 rounded-md">
                        <p class="font-medium text-gray-700 mb-2">Prescribed Medications:</p>
                        <ul class="space-y-2">
                            ${analysis.medications.map(med => `
                                <li class="text-gray-600">
                                    ${med.name} - ${med.dosage.amount} ${med.dosage.unit}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${analysis.warnings.length > 0 ? `
                    <div class="bg-yellow-50 p-4 rounded-md">
                        <p class="font-medium text-yellow-700 mb-2">Warnings:</p>
                        <ul class="list-disc list-inside space-y-1">
                            ${analysis.warnings.map(warning => `
                                <li class="text-yellow-600">${warning}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${analysis.interactions.length > 0 ? `
                    <div class="bg-red-50 p-4 rounded-md">
                        <p class="font-medium text-red-700 mb-2">Drug Interactions:</p>
                        <ul class="space-y-2">
                            ${analysis.interactions.map(interaction => `
                                <li class="text-red-600">
                                    <p class="font-medium">${interaction.medication1} + ${interaction.medication2}</p>
                                    <p class="text-sm">${interaction.description}</p>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${analysis.contraindications.length > 0 ? `
                    <div class="bg-red-50 p-4 rounded-md">
                        <p class="font-medium text-red-700 mb-2">Contraindications:</p>
                        <ul class="space-y-2">
                            ${analysis.contraindications.map(contraindication => `
                                <li class="text-red-600">
                                    <p class="font-medium">${contraindication.medication}</p>
                                    <p class="text-sm">Conditions: ${contraindication.conditions.join(', ')}</p>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    function getRiskLevelClass(level) {
        switch (level) {
            case 'high': return 'text-red-600';
            case 'medium': return 'text-yellow-600';
            default: return 'text-green-600';
        }
    }

    function getRiskLevelIcon(level) {
        switch (level) {
            case 'high': return '⚠';
            case 'medium': return '⚡';
            default: return '✓';
        }
    }

    function getRiskLevelText(level) {
        switch (level) {
            case 'high': return 'High Risk';
            case 'medium': return 'Medium Risk';
            default: return 'Low Risk';
        }
    }

    function showError(message) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full';
        modal.innerHTML = `
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3 text-center">
                    <h3 class="text-lg leading-6 font-medium text-red-600 mb-4">Error</h3>
                    <div class="mt-2 px-7 py-3">
                        <p class="text-sm text-gray-500">${message}</p>
                    </div>
                    <div class="items-center px-4 py-3">
                        <button id="closeModal" class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md shadow-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('closeModal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }
}); 