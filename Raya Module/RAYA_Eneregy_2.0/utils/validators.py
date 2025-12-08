"""
Input validation utilities
"""

def validate_prediction_input(data):
    """Validate prediction API input"""
    errors = []
    
    # Check required fields
    required_fields = ['city', 'temperature', 'humidity', 'hour']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return {'valid': False, 'error': '; '.join(errors)}
    
    # Validate city
    valid_cities = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore']
    if data['city'] not in valid_cities:
        errors.append(f"Invalid city. Must be one of: {', '.join(valid_cities)}")
    
    # Validate temperature
    try:
        temp = float(data['temperature'])
        if not -10 <= temp <= 50:
            errors.append("Temperature must be between -10°C and 50°C")
    except ValueError:
        errors.append("Temperature must be a number")
    
    # Validate humidity
    try:
        humidity = float(data['humidity'])
        if not 0 <= humidity <= 100:
            errors.append("Humidity must be between 0% and 100%")
    except ValueError:
        errors.append("Humidity must be a number")
    
    # Validate hour
    try:
        hour = int(data['hour'])
        if not 0 <= hour <= 23:
            errors.append("Hour must be between 0 and 23")
    except ValueError:
        errors.append("Hour must be an integer")
    
    # Validate is_weekend (optional)
    if 'is_weekend' in data and not isinstance(data['is_weekend'], bool):
        errors.append("is_weekend must be true or false")
    
    if errors:
        return {'valid': False, 'error': '; '.join(errors)}
    
    return {'valid': True, 'error': None}