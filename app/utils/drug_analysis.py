import spacy
from typing import Dict, Any, List
import re
from app.models.database import get_drug_interactions, get_drug_contraindications

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def analyze_prescription(text: str) -> Dict[str, Any]:
    """
    Analyze prescription content for potential issues using NLP
    """
    if not text:
        return {
            'status': 'error',
            'message': 'No prescription text provided'
        }
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract medications and dosages
    medications = extract_medications(doc)
    
    # Analyze for potential issues
    analysis = {
        'medications': medications,
        'warnings': [],
        'interactions': [],
        'contraindications': [],
        'risk_level': 'low'
    }
    
    # Check for drug interactions
    if len(medications) > 1:
        interactions = check_drug_interactions(medications)
        if interactions:
            analysis['interactions'] = interactions
            analysis['risk_level'] = 'high'
    
    # Check for contraindications
    contraindications = check_contraindications(medications)
    if contraindications:
        analysis['contraindications'] = contraindications
        analysis['risk_level'] = 'high'
    
    # Check for unusual dosages
    unusual_dosages = check_unusual_dosages(medications)
    if unusual_dosages:
        analysis['warnings'].extend(unusual_dosages)
        analysis['risk_level'] = 'medium'
    
    # Check for missing information
    missing_info = check_missing_information(doc)
    if missing_info:
        analysis['warnings'].extend(missing_info)
        if analysis['risk_level'] == 'low':
            analysis['risk_level'] = 'medium'
    
    return analysis

def extract_medications(doc) -> List[Dict[str, Any]]:
    """Extract medications and their dosages from the prescription text"""
    medications = []
    
    # Common medication patterns
    patterns = [
        r'(\d+)\s*(mg|g|ml|tablet|capsule)s?\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(\d+)\s*(mg|g|ml|tablet|capsule)s?',
        r'Rx:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(\d+)\s*(mg|g|ml|tablet|capsule)s?'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, doc.text)
        for match in matches:
            if len(match.groups()) == 3:
                if pattern.startswith('Rx:'):
                    name, amount, unit = match.groups()
                else:
                    amount, unit, name = match.groups()
                
                medications.append({
                    'name': name.strip(),
                    'dosage': {
                        'amount': int(amount),
                        'unit': unit
                    }
                })
    
    return medications

def check_drug_interactions(medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for potential drug interactions"""
    interactions = []
    
    for i, med1 in enumerate(medications):
        for med2 in medications[i+1:]:
            interaction = get_drug_interactions(med1['name'], med2['name'])
            if interaction:
                interactions.append({
                    'medication1': med1['name'],
                    'medication2': med2['name'],
                    'severity': interaction['severity'],
                    'description': interaction['description']
                })
            else:
                # Add a warning for unknown interactions
                interactions.append({
                    'medication1': med1['name'],
                    'medication2': med2['name'],
                    'severity': 'unknown',
                    'description': 'Interaction data not available in database'
                })
    
    return interactions

def check_contraindications(medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for contraindications"""
    contraindications = []
    
    for medication in medications:
        contraindication = get_drug_contraindications(medication['name'])
        if contraindication:
            contraindications.append({
                'medication': medication['name'],
                'conditions': contraindication['conditions'],
                'severity': contraindication['severity']
            })
        else:
            # Add a warning for unknown contraindications
            contraindications.append({
                'medication': medication['name'],
                'conditions': ['Unknown'],
                'severity': 'unknown',
                'description': 'Contraindication data not available in database'
            })
    
    return contraindications

def check_unusual_dosages(medications: List[Dict[str, Any]]) -> List[str]:
    """Check for unusual medication dosages"""
    warnings = []
    
    for medication in medications:
        # Example thresholds (should be replaced with actual medical guidelines)
        if medication['dosage']['unit'] == 'mg':
            if medication['dosage']['amount'] > 1000:
                warnings.append(f"High dosage detected for {medication['name']}: {medication['dosage']['amount']}mg")
        elif medication['dosage']['unit'] == 'g':
            if medication['dosage']['amount'] > 2:
                warnings.append(f"High dosage detected for {medication['name']}: {medication['dosage']['amount']}g")
    
    return warnings

def check_missing_information(doc) -> List[str]:
    """Check for missing important information in the prescription"""
    missing_info = []
    
    # Check for common required fields
    required_fields = {
        'patient': r'patient|name',
        'date': r'date|prescribed',
        'doctor': r'dr\.|doctor|physician',
        'instructions': r'take|use|apply|dosage|frequency'
    }
    
    for field, pattern in required_fields.items():
        if not re.search(pattern, doc.text.lower()):
            missing_info.append(f"Missing {field} information")
    
    return missing_info 