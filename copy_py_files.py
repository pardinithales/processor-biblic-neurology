import os
import pyperclip

def copy_py_files_content():
    # Get the current directory
    current_dir = os.getcwd()
    all_content = []
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(current_dir):
        # Filter .py and .env files
        target_files = [f for f in files if f.endswith('.py') or f.endswith('.env')]
        
        for file in target_files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    all_content.append(f"\n# File: {file}\n{content}")
            except Exception as e:
                print(f"Error reading {file}: {str(e)}")
    
    # Join all content with separators
    final_content = "\n" + "="*80 + "\n".join(all_content)
    
    # Copy to clipboard
    try:
        pyperclip.copy(final_content)
        print(f"Successfully copied {len(all_content)} files to clipboard!")
    except Exception as e:
        print(f"Error copying to clipboard: {str(e)}")

if __name__ == "__main__":
    copy_py_files_content()