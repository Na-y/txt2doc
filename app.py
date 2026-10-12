import streamlit as st
import zipfile
import io
from docx import Document

def text_to_docx(text_content):
    """
    Helper function to convert a string of text into a Word Document.
    Returns the document as an in-memory bytes buffer.
    """
    # Create a new Word Document object
    doc = Document()
    
    # Add the plain text to the document
    doc.add_paragraph(text_content)
    
    # Create an in-memory buffer to save the document
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    
    # Reset the buffer's pointer to the beginning so it can be read later
    doc_buffer.seek(0)
    
    return doc_buffer

# --- App UI Configuration ---
st.set_page_config(page_title="TXT to DOCX Converter", page_icon="📝")
st.title("📝 TXT to DOCX Converter")
st.write("Upload individual `.txt` files or a `.zip` file containing text files. We will convert them to Word documents and provide a `.zip` file to download!")

# Create a file uploader that accepts multiple files
uploaded_files = st.file_uploader(
    "Choose .txt or .zip files", 
    type=['txt', 'zip'], 
    accept_multiple_files=True
)

if uploaded_files:
    # Create an in-memory buffer for our final output zip file
    output_zip_buffer = io.BytesIO()
    
    # Keep track of how many files we successfully convert
    converted_count = 0 
    
    # Open the output zip file in 'write' mode
    with zipfile.ZipFile(output_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as output_zip:
        
        # Loop through everything the user uploaded
        for uploaded_file in uploaded_files:
            
            # SCENARIO 1: The user uploaded a raw .txt file
            if uploaded_file.name.endswith('.txt'):
                # Read the text and decode it (assuming UTF-8)
                text_content = uploaded_file.read().decode('utf-8', errors='ignore')
                
                # Convert text to docx buffer
                docx_buffer = text_to_docx(text_content)
                
                # Create a new filename (change .txt to .docx)
                new_filename = uploaded_file.name.replace('.txt', '.docx')
                
                # Write the docx buffer into our output zip
                output_zip.writestr(new_filename, docx_buffer.read())
                converted_count += 1

            # SCENARIO 2: The user uploaded a .zip file
            elif uploaded_file.name.endswith('.zip'):
                # Read the uploaded zip file
                with zipfile.ZipFile(uploaded_file, 'r') as input_zip:
                    # Loop through all files inside the uploaded zip
                    for inner_filename in input_zip.namelist():
                        
                        # Check if the inner file is a text file
                        if inner_filename.endswith('.txt'):
                            # Open and read the inner text file
                            with input_zip.open(inner_filename) as inner_file:
                                text_content = inner_file.read().decode('utf-8', errors='ignore')
                                
                                # Convert to docx
                                docx_buffer = text_to_docx(text_content)
                                
                                # Create a new filename
                                new_filename = inner_filename.replace('.txt', '.docx')
                                
                                # Write to our output zip
                                output_zip.writestr(new_filename, docx_buffer.read())
                                converted_count += 1

    # Only show the download button if we actually converted something
    if converted_count > 0:
        st.success(f"Successfully converted {converted_count} files!")
        
        # Provide the final zip file for download
        st.download_button(
            label="⬇️ Download Converted Files (.zip)",
            data=output_zip_buffer.getvalue(),
            file_name="converted_docx_files.zip",
            mime="application/zip"
        )
    else:
        st.warning("No valid .txt files were found to convert.")
