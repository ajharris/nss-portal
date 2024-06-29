import os

# Define the new CSS content to be placed in the separate CSS file
css_content = """
body.light-mode {
    background-color: #ffffff;
    color: #000000;
}
body.dark-mode {
    background-color: #333333;
    color: #ffffff;
}
.navbar-inverse.light-mode {
    background-color: #f8f9fa;
    color: #333333; /* Changed to a darker shade */
}
.navbar-inverse.dark-mode {
    background-color: #333333;
    color: #ffffff;
}
.navbar-inverse.light-mode .navbar-nav > li > a {
    color: #333333; /* Changed to a darker shade */
}
.navbar-inverse.dark-mode .navbar-nav > li > a {
    color: #cccccc;
}
.theme-switch-wrapper, .view-switch-wrapper {
    display: flex;
    align-items: center;
    padding: 15px 10px;
}
.theme-switch, .view-switch {
    position: relative;
    display: inline-block;
    width: 34px;
    height: 20px;
}
.theme-switch input, .view-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}
.slider, .view-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 20px;
}
.slider:before, .view-slider:before {
    position: absolute;
    content: "";
    height: 12px;
    width: 12px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}
input:checked + .slider, input:checked + .view-slider {
    background-color: #2196F3;
}
input:checked + .slider:before, input:checked + .view-slider:before {
    transform: translateX(14px);
}
.toggle-label {
    margin-left: 10px;
    font-weight: normal; /* Ensure the font weight is the same as the rest of the menu */
    color: inherit; /* Ensure the color follows the theme */
}
"""

# Path to the CSS file
css_directory_path = os.path.join('app', 'static', 'css')
css_file_path = os.path.join(css_directory_path, 'styles.css')

# Create the directory if it doesn't exist
os.makedirs(css_directory_path, exist_ok=True)

# Write the CSS content to the file
with open(css_file_path, 'w') as file:
    file.write(css_content)

print(f"CSS file created at: {css_file_path}")
