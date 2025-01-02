import os
import faiss
import numpy as np
from langchain.text_splitter import CharacterTextSplitter
from docx import Document
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def invoke_openai_embeddings(texts):
    """Invoke the OpenAI API to get embeddings for the given texts."""
    try:
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [embedding.embedding for embedding in response.data]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def load_docx_files(folder_path):
    """Load and extract text from all .docx files in the specified folder."""
    try:
        docs = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".docx"):
                file_path = os.path.join(folder_path, file_name)
                document = Document(file_path)
                full_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
                docs.append(full_text)
        return docs
    except Exception as e:
        print(f"Error loading documents: {e}")
        return None

def split_text(doc_texts):
    """Split the extracted text into smaller chunks for better processing."""
    try:
        text_splitter = CharacterTextSplitter(
            separator='\n',
            chunk_size=1000,
            chunk_overlap=200
        )
        return [chunk for text in doc_texts for chunk in text_splitter.split_text(text)]
    except Exception as e:
        print(f"Error splitting text: {e}")
        return None

def embed_in_DB(docs, index_file="faiss_index.bin", metadata_file="metadata.json"):
    """Embed text chunks into a FAISS index and save it to disk."""
    try:
        embedded_vectors = invoke_openai_embeddings(docs)
        if embedded_vectors is None:
            return None, None

        # Create FAISS index
        dimension = len(embedded_vectors[0])
        print("Dimension: ", dimension)
        index = faiss.IndexFlatL2(dimension)
        print("Index created")
        print(index)
        embedded_vectors = np.array(embedded_vectors, dtype='float32')
        index.add(embedded_vectors)
        print("Index added")

        # Save index to disk
        faiss.write_index(index, index_file)

        # Save metadata to disk
        metadata = {i: docs[i] for i in range(len(docs))}
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        return index, metadata
    except Exception as e:
        print(f"Error embedding in DB: {e}")
        return None, None

def main(folder_path):
    """Main function to load documents, split text, and create embeddings."""
    if folder_path and os.path.exists(folder_path):
        print("Loading documents and creating embeddings...")
        doc_texts = load_docx_files(folder_path)
        if doc_texts is None:
            return
        text_chunks = split_text(doc_texts)
        if text_chunks is None:
            return
        index, metadata = embed_in_DB(text_chunks)
        if index is None or metadata is None:
            return
        print("Documents loaded and embeddings created successfully!")
    else:
        print("Invalid folder path! Please provide a valid path.")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Load documents, split text, and create embeddings.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing .docx files")
    args = parser.parse_args()

    # Call the main function with the folder path argument
    main(args.folder_path)