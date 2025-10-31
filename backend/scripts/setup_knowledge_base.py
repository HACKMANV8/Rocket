import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chromadb_manager import ChromaDBManager
from utils.langchain_setup import langchain_setup  # ✅ ADDED
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_complete_knowledge_base():
    """Setup ChromaDB with all CSV data"""
    
    # ✅ ADDED: Initialize and log LangChain setup
    embedding_info = langchain_setup.get_embedding_model_info()
    print(f"🔧 LangChain initialized with: {embedding_info.get('model_name', 'Unknown')}")
    
    # Initialize ChromaDB manager
    chroma = ChromaDBManager()
    
    # Path to your CSV folder
    csv_folder = r"C:\Users\pavit\OneDrive\Desktop\mit\thanucheck\bhooom\mysql\kaggle_data"
    
    # Map CSV files to document types
    csv_mapping = {
        "equipment_monitoring.csv": "equipment",
        "mining_incidents.csv": "incidents", 
        "production_metrics.csv": "production",
        "safety_compliance.csv": "safety",
        "maintenance_repairs.csv": "maintenance",
        "fuel_energy.csv": "fuel",
        "quality_metrics.csv": "quality"
    }
    
    success_count = 0
    total_files = len(csv_mapping)
    
    print("🚀 Starting ChromaDB Knowledge Base Setup...")
    print("=" * 50)
    
    for csv_file, doc_type in csv_mapping.items():
        csv_path = os.path.join(csv_folder, csv_file)
        
        if os.path.exists(csv_path):
            print(f"📁 Loading {csv_file} as {doc_type}...")
            if chroma.add_csv_data(csv_path, doc_type):
                success_count += 1
                print(f"✅ Successfully loaded {csv_file}")
            else:
                print(f"❌ Failed to load {csv_file}")
        else:
            print(f"⚠️ File not found: {csv_file}")
    
    print("=" * 50)
    print(f"🎉 Setup complete! {success_count}/{total_files} files loaded successfully")
    
    # Show collection info
    collection_info = chroma.get_collection_info()
    print(f"📊 {collection_info}")
    
    # Test the search
    if success_count > 0:
        print("\n🔍 Testing search functionality...")
        test_queries = [
            "equipment efficiency",
            "safety incidents", 
            "production metrics"
        ]
        
        for query in test_queries:
            results = chroma.similarity_search(query, k=1)
            print(f"Query: '{query}' → Found {len(results)} documents")

if __name__ == "__main__":
    setup_complete_knowledge_base()