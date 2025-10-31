import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from models.rag_engine import RAGEngine
from utils.langchain_setup import langchain_setup
from database.db_config import init_database, get_mysql_connection
from config import Config
import logging
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global RAG engine instance
rag_engine = None

def initialize_services():
    """Initialize all services on startup"""
    global rag_engine
    
    try:
        # Initialize LangChain components
        embedding_info = langchain_setup.get_embedding_model_info()
        logger.info(f"🚀 LangChain initialized with: {embedding_info.get('model_name', 'Unknown')}")
        
        # Initialize database connection
        if init_database():
            logger.info("✅ Database connection established")
        else:
            logger.error("❌ Database connection failed")
        
        # Initialize RAG engine
        rag_engine = RAGEngine()
        logger.info("✅ RAG Engine initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        return False

# File upload and ingestion
ALLOWED_EXTENSIONS = {"csv", "pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
        file = request.files['file']
        doc_type = request.form.get('docType', '').strip().lower() or 'document'
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Unsupported file type"}), 400

        filename = secure_filename(file.filename)
        upload_dir = os.path.join('/app', 'data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        saved_path = os.path.join(upload_dir, filename)
        file.save(saved_path)

        # Ingest into Chroma via rag_engine
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'csv':
            success = rag_engine.chroma_manager.add_csv_data(saved_path, doc_type)
        else:
            # PDF: extract text
            try:
                reader = PdfReader(saved_path)
                pages_text = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ''
                    if text.strip():
                        pages_text.append(text)
                # Build documents
                from langchain_core.documents import Document
                docs = [Document(page_content=t, metadata={"source": filename, "type": doc_type, "page": idx+1}) for idx, t in enumerate(pages_text)]
                success = rag_engine.chroma_manager.add_documents(docs)
            except Exception as e:
                logger.error(f"❌ PDF ingestion error: {e}")
                success = False

        if not success:
            return jsonify({"success": False, "error": "Ingestion failed (embeddings offline or parsing error)"}), 500

        return jsonify({"success": True, "message": "File ingested successfully"})
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "rag_engine_ready": rag_engine is not None
    })

@app.route('/api/query', methods=['POST'])
def handle_query():
    """Main query endpoint - UPDATED for structured response"""
    try:
        if rag_engine is None:
            return jsonify({
                "success": False,
                "error": "RAG engine not initialized",
                "response": {
                    "answer": "System is still initializing, please try again shortly.",
                    "type": "error",
                    "visualizations": {},
                    "recommendations": []
                }
            }), 503
        
        data = request.get_json()
        question = data.get('question', '')
        language = data.get('language', 'en')
        
        if not question:
            return jsonify({
                "success": False,
                "error": "No question provided",
                "response": {
                    "answer": "Please provide a question.",
                    "type": "error", 
                    "visualizations": {},
                    "recommendations": []
                }
            }), 400
        
        # Process the query - now returns structured data
        result = rag_engine.query(question, language)
        
        return jsonify({
            "success": True,
            "response": result  # Contains answer + visualizations + recommendations
        })
        
    except Exception as e:
        logger.error(f"❌ Query processing error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": {
                "answer": "An error occurred while processing your query.",
                "type": "error",
                "visualizations": {},
                "recommendations": []
            }
        }), 500

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    """Get overall system status for dashboard"""
    try:
        status = {
            "database": False,
            "chromadb": False,
            "mistral_ai": False,
            "services_ready": rag_engine is not None
        }
        
        # Check database
        try:
            conn = get_mysql_connection()
            if conn:
                status["database"] = True
                conn.close()
        except:
            status["database"] = False
            
        # Check ChromaDB (through RAG engine)
        if rag_engine and rag_engine.chroma_manager and rag_engine.chroma_manager.client:
            status["chromadb"] = True
            
        # Check Mistral (through RAG engine)  
        if rag_engine and rag_engine.mistral:
            status["mistral_ai"] = True
            
        return jsonify({
            "success": True,
            "status": status,
            "timestamp": "2024-01-15T10:30:00Z"
        })
        
    except Exception as e:
        logger.error(f"❌ System status error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/quick-actions', methods=['GET'])
def get_quick_actions():
    """Get quick actions and suggestions for sidebar"""
    try:
        return jsonify({
            "success": True,
            "quick_actions": [
                {
                    "icon": "🚨", 
                    "text": "Check Critical Alerts", 
                    "suggestion": "Show me equipment with critical status"
                },
                {
                    "icon": "📊", 
                    "text": "Production Efficiency", 
                    "suggestion": "What is our current production efficiency?"
                },
                {
                    "icon": "🛡️", 
                    "text": "Safety Overview", 
                    "suggestion": "Recent safety incidents and trends"
                },
                {
                    "icon": "🔧", 
                    "text": "Maintenance Status", 
                    "suggestion": "Which equipment needs maintenance?"
                },
                {
                    "icon": "⚡", 
                    "text": "Fuel Consumption", 
                    "suggestion": "How is our fuel consumption across sites?"
                }
            ],
            "recent_activity": [
                "Equipment status checked",
                "Production report generated", 
                "Safety audit completed"
            ]
        })
    except Exception as e:
        logger.error(f"❌ Quick actions error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages for TTS"""
    try:
        return jsonify({
            "success": True,
            "languages": Config.SUPPORTED_LANGUAGES
        })
    except Exception as e:
        logger.error(f"❌ Languages endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "languages": {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French', 
                'hi': 'Hindi'
            }
        }), 500

# ✅ ADDED: MySQL Data Endpoints (for sidebar)
@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get recent safety incidents"""
    try:
        limit = request.args.get('limit', 5, type=int)
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT incident_date, mine_name, incident_type, severity, description
            FROM mining_incidents 
            ORDER BY incident_date DESC 
            LIMIT %s
        """, (limit,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "incidents": rows
        })
        
    except Exception as e:
        logger.error(f"❌ Incidents endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "incidents": []
        }), 500

@app.route('/api/maintenance-alerts', methods=['GET'])
def get_maintenance_alerts():
    """Get maintenance alerts"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT equipment_id, equipment_type, status, alerts, efficiency_score
            FROM equipment_monitoring 
            WHERE status != 'Operational' OR efficiency_score < 80
            ORDER BY 
                CASE status 
                    WHEN 'Critical' THEN 1
                    WHEN 'Maintenance' THEN 2  
                    ELSE 3
                END,
                efficiency_score ASC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "alerts": rows
        })
        
    except Exception as e:
        logger.error(f"❌ Maintenance alerts error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "alerts": []
        }), 500

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    """Get current KPIs"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total incidents (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as total_incidents 
            FROM mining_incidents 
            WHERE incident_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """)
        total_incidents = cursor.fetchone()['total_incidents']
        
        # Critical equipment alerts
        cursor.execute("""
            SELECT COUNT(*) as critical_alerts 
            FROM equipment_monitoring 
            WHERE status = 'Critical'
        """)
        critical_alerts = cursor.fetchone()['critical_alerts']
        
        # Average efficiency (use all available data)
        cursor.execute("""
            SELECT AVG(efficiency_percentage) as avg_efficiency 
            FROM production_metrics
        """)
        avg_efficiency = cursor.fetchone()['avg_efficiency'] or 0
        
        # Total production (use all available data)
        cursor.execute("""
            SELECT SUM(quantity_tons) as monthly_production 
            FROM production_metrics
        """)
        monthly_production = cursor.fetchone()['monthly_production'] or 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "kpis": {
                "total_incidents": total_incidents,
                "critical_alerts": critical_alerts,
                "avg_efficiency": round(float(avg_efficiency), 2),
                "monthly_production": float(monthly_production)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ KPIs endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "kpis": {
                "total_incidents": 0,
                "critical_alerts": 0,
                "avg_efficiency": 0,
                "monthly_production": 0
            }
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify RAG functionality"""
    try:
        if rag_engine is None:
            return jsonify({
                "success": False,
                "error": "RAG engine not ready"
            }), 503
        
        test_question = "What is the current equipment status?"
        result = rag_engine.query(test_question)
        
        return jsonify({
            "success": True,
            "test_question": test_question,
            "response": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Initialize services
    if initialize_services():
        logger.info("🎉 All services initialized successfully!")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        logger.error("💥 Failed to initialize services, exiting...")
        sys.exit(1)