import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

project_dir = ""  # Replace with the path to your Android project
output_file = "strings.xml"

def find_strings_files(root_dir):
    """Find all strings.xml files in the given root directory."""
    strings_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file == "strings.xml":
                strings_files.append(os.path.join(subdir, file))
    return strings_files

def add_comment(element, text):
    """Add a comment to the XML element."""
    comment = ET.Comment(text)
    element.append(comment)

def get_module_name(file_path, root_dir):
    """Extract the module name from the file path."""
    relative_path = os.path.relpath(file_path, root_dir)
    parts = relative_path.split(os.sep)
    if 'src' in parts:
        src_index = parts.index('src')
        if src_index > 0:
            return ':'.join(parts[:src_index])
    return "unknown"

def print_duplicates(combined_root):
    strings_values = {}
    for string in combined_root.findall("string"):
        value = string.text
        if value in strings_values:
            strings_values[value].append(string)
        else:
            strings_values[value] = [string]

    for value, strings in strings_values.items():
        if len(strings) > 1:
            print(f"String value '{value}' is duplicated in the following strings:")
            for string in strings:
                print(f"  - {string.attrib['name']}")
            print()

def combine_strings_files(strings_files, output_file, root_dir):
    """Combine all strings.xml files into a single XML file."""
    combined_root = ET.Element("resources")

    for file in strings_files:
        module_name = get_module_name(file, root_dir)
        add_comment(combined_root, f"From module: {module_name}")

        tree = ET.parse(file)
        root = tree.getroot()
        for string in root.findall("string"):
            combined_root.append(string)
    
    combined_tree = ET.ElementTree(combined_root)

    # print all strings values that are duplicated
    print_duplicates(combined_root)
    
    with open(output_file, "wb") as f:
        combined_tree.write(f, encoding="utf-8", xml_declaration=True)

    # Format the outputted XML
    formatted_xml = xml.dom.minidom.parseString(ET.tostring(combined_root)).toprettyxml(indent="")
    formatted_xml = "\n".join([line for line in formatted_xml.split("\n") if line.strip()])

    # On each line except for the <resources> tag the resources closing tag
    formatted_xml = "\n".join([f"\t{line}" if line.strip() and not line.startswith("<resources>") and not line.startswith("</resources>") else line for line in formatted_xml.split("\n")])

    # Remove tab in front of the first line if this first line is not "<resources>"
    if formatted_xml.startswith("\t") and not formatted_xml.startswith("\t<resources>"):
        formatted_xml = formatted_xml[1:]
    

    with open(output_file, "w") as f:
        f.write(formatted_xml)

def main(): 
    strings_files = find_strings_files(project_dir)
    print(f"Found {len(strings_files)} strings.xml files.")
    
    combine_strings_files(strings_files, output_file, project_dir)
    print(f"Combined strings.xml files have been written to {output_file}.")

if __name__ == "__main__":
    main()

    
