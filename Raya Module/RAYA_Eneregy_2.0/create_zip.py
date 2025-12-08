"""
Script to create complete project ZIP
"""

import zipfile
import os
import shutil
from datetime import datetime

def create_project_zip():
    """Create complete project ZIP file"""
    
    # Files to include
    files = [
        'app.py',
        'requirements.txt',
        '.env.sample',
        'run_local.sh',
        'README.md',
        'setup.sh',
        'create_model.py'
    ]
    
    # Directories to include
    directories = [
        'modules',
        'utils',
        'static',
        'templates',
        'data',
        'tests'
    ]
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'raya-energy-ai-complete-{timestamp}.zip'
    
    print(f"Creating {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for file in files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  Added: {file}")
            else:
                print(f"  Warning: {file} not found")
        
        # Add directories
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        # Skip __pycache__ and .pyc files
                        if '__pycache__' in root or file.endswith('.pyc'):
                            continue
                        
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start='.')
                        zipf.write(file_path, arcname)
                        print(f"  Added: {arcname}")
            else:
                print(f"  Warning: {directory} directory not found")
    
    print(f"\n✅ ZIP created: {zip_filename}")
    print(f"📁 Size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    
    return zip_filename

if __name__ == '__main__':
    create_project_zip()