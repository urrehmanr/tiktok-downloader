import os
import shutil

def setup_static_directory():
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('static/img', exist_ok=True)
    
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Move index.html to templates directory if it exists in the root
    if os.path.exists('index.html'):
        shutil.move('index.html', 'templates/index.html')
    
    return True

if __name__ == "__main__":
    setup_static_directory() 