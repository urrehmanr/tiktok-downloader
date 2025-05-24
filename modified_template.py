import os
import shutil

def setup_templates():
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create components directory inside templates
    os.makedirs('templates/components', exist_ok=True)
    
    # Copy index.html to templates directory if it exists in the root
    if os.path.exists('index.html'):
        # Read content
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Write to templates directory
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Modify index.html to use external JS if needed
    if os.path.exists('templates/index.html'):
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add external JS link if needed
        if '<script src="/static/js/app.js"></script>' not in content:
            content = content.replace('</body>', '<script src="/static/js/app.js"></script>\n</body>')
            
            with open('templates/index.html', 'w', encoding='utf-8') as f:
                f.write(content)
        
    return True

if __name__ == "__main__":
    setup_templates() 