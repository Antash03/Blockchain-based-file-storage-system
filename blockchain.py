import hashlib

import ipywidgets as widgets
from IPython.display import display, Javascript
import time
import json
import os

# Define the blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(proof=100, previous_hash=None)  # Create the genesis block

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, file_hash):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'file_hash': file_hash,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

# Create a blockchain instance
blockchain = Blockchain()

# List to keep track of uploaded file names
uploaded_files_list = []

# Function to handle file upload
def handle_file_upload(change):
    global uploaded_file, uploaded_files_list
    uploaded_file = change['new']
    if uploaded_file:
        file_contents = uploaded_file[list(uploaded_file.keys())[0]]['content']
        file_hash = hashlib.sha256(file_contents).hexdigest()
        blockchain.new_transaction('User', 'Colab', file_hash)
        blockchain.new_block(proof=100)  # Placeholder proof value for simplicity
        file_name = uploaded_file[list(uploaded_file.keys())[0]]['metadata']['name']
        uploaded_files_list.append(file_name)
        print(f"File '{file_name}' uploaded and added to the blockchain.")
        # Update the uploaded files list after the upload
        display_uploaded_files()

# Function to handle file download
def handle_download_button_click(b):
    selected_file = selected_file_dropdown.value
    if selected_file and selected_file in uploaded_files_list:
        file_hash = hashlib.sha256(uploaded_file[list(uploaded_file.keys())[0]]['content']).hexdigest()
        download_file_from_blockchain(blockchain, file_hash, selected_file)
    else:
        print("Please select a valid file to download.")

# Function to view blockchain transactions
def handle_view_transactions_button_click(b):
    display_transactions(blockchain)

# Function to download file from blockchain using its hash
def download_file_from_blockchain(blockchain, file_hash, file_name):
    for block in blockchain.chain:
        for transaction in block['transactions']:
            if transaction['file_hash'] == file_hash:
                with open(file_name, 'wb') as file:
                    file.write(uploaded_file[list(uploaded_file.keys())[0]]['content'])
                print(f"File downloaded: {file_name}")
                return
    print("File not found in the blockchain.")

# Function to display blockchain transactions
def display_transactions(blockchain):
    if not blockchain.chain:
        print("Blockchain is empty.")
    else:
        for block in blockchain.chain:
            print(f"Block: {block['index']}")
            for transaction in block['transactions']:
                print(f"  Sender: {transaction['sender']}")
                print(f"  Recipient: {transaction['recipient']}")
                print(f"  File Hash: {transaction['file_hash']}")
                print("-" * 30)

# Function to display the list of uploaded files in Colab
def display_uploaded_files():
    selected_file_dropdown.options = uploaded_files_list
    print("Uploaded files:")
    for file_name in uploaded_files_list:
        print(f"- {file_name}")

# Create widgets for file upload, download, view transactions, and file selection
upload_button = widgets.FileUpload(description="Choose File")
download_button = widgets.Button(description="Download Selected File")
view_transactions_button = widgets.Button(description="View Transactions")
selected_file_dropdown = widgets.Dropdown(description="Select File")

# Attach event handlers to buttons
uploaded_file = None
upload_button.observe(handle_file_upload, names='value')
download_button.on_click(handle_download_button_click)
view_transactions_button.on_click(handle_view_transactions_button_click)

# Display widgets
display(upload_button)
display(selected_file_dropdown)
display(download_button)
display(view_transactions_button)
