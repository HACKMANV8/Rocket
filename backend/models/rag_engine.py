from utils.langchain_setup import langchain_setup
from utils.chromadb_manager import ChromaDBManager
from database.db_config import get_mysql_connection
from models.mistral_client import MistralService
from models.tts_service import MultilingualTTS
from config import Config
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.chroma_manager = ChromaDBManager()
        self.mistral = MistralService()
        self.tts = MultilingualTTS()
        # ✅ ADDED: Initialize LangChain prompt and components
        self.prompt = langchain_setup.create_custom_prompt()
        self.known_sites = {"mine a", "mine b", "mine c", "xi mine", "alpha mine", "beta mine"}
        
    def query(self, question, language='en'):
        """
        Returns structured response for chat interface
        """
        try:
            # Normalize input once
            q_lower = question.strip().lower()

            # Handle simple greetings with a concise friendly response, NO KPIs/Charts/Recs
            if q_lower in {"hi", "hii", "hello", "hlo", "hey", "hola"}:
                answer_text = "Hello! Ask about equipment status, production efficiency, safety incidents, or maintenance."
                audio_result = self.tts.text_to_speech(answer_text, language)
                result = {
                    "answer": answer_text,
                    "type": "greeting",
                    "visualizations": {},
                    "recommendations": [],
                    "sources": [],
                    "language": language,
                }
                if audio_result.get("success"):
                    result["audio"] = audio_result
                return result

            # If the query doesn't look mining/domain related, reply briefly without charts/recs
            domain_keywords = [
                "equipment", "production", "incident", "safety", "maintenance",
                "efficiency", "mine", "vector", "chromadb", "alerts", "kpi"
            ]
            if len(q_lower.split()) < 3 and not any(k in q_lower for k in domain_keywords):
                return {
                    "answer": "Please ask a mining-related question (e.g., equipment status, production metrics, safety incidents).",
                    "type": "info",
                    "visualizations": {},
                    "recommendations": [],
                    "sources": [],
                    "language": language,
                }

            # 1. Vector Search + SQL Context + AI Answer (existing code)
            relevant_docs = self.chroma_manager.similarity_search(question, k=Config.TOP_K_RESULTS)
            sql_context = self.get_sql_context(question)
            vector_context = "\n\n".join([doc.page_content for doc in relevant_docs])
            full_context = f"{vector_context}\n\nDatabase Records:\n{sql_context}"
            answer = self.mistral.generate_response(full_context, question)
            
            # 2. Get Enhanced Visualization Data (dynamic based on query)
            viz_data = self.get_enhanced_visualization_data(question)
            
            # 3. Generate Manager Recommendations with LLM using current data
            recommendations = self.mistral.generate_recommendations(
                question=question,
                answer_summary=answer,
                kpis=viz_data.get("kpis", {}),
                charts=viz_data.get("charts", {}),
                max_recs=4,
            ) or self.generate_recommendations(question, answer, viz_data)
            
            # 4. Generate Audio (TTS)
            audio_result = self.tts.text_to_speech(answer, language)
            
            result = {
                "answer": answer,
                "type": "ai_response",  # ✅ Identify response type
                "visualizations": {
                    "kpis": viz_data["kpis"],
                    "charts": self.filter_relevant_charts(question, viz_data["charts"]),
                    "tables": self.extract_data_tables(question, sql_context)
                },
                "recommendations": recommendations,
                "sources": [doc.metadata for doc in relevant_docs],
                "language": language
            }
            if audio_result.get("success"):
                result["audio"] = audio_result
            
            return result
        except Exception as e:
            logger.error(f"❌ RAG query error: {e}")
            error_text = f"Error processing query: {str(e)}"
            error_result = {
                "answer": error_text,
                "type": "error",
                "visualizations": {},
                "recommendations": [],
                "sources": [],
                "language": language
            }
            # Try to generate audio for error message too
            try:
                audio_result = self.tts.text_to_speech(error_text, language)
                if audio_result.get("success"):
                    error_result["audio"] = audio_result
            except:
                pass  # Audio not critical for errors
            return error_result

    def generate_recommendations(self, question, answer, viz_data):
        """Generate actionable recommendations for managers"""
        recommendations = []
        
        # Analyze question context for specific recommendations
        query_lower = question.lower()
        
        if any(word in query_lower for word in ['equipment', 'machine', 'status']):
            critical_count = viz_data["kpis"].get("critical_alerts", 0)
            if critical_count > 0:
                recommendations.append(f"🚨 Immediate attention needed for {critical_count} critical equipment")
                recommendations.append("Schedule maintenance for equipment with efficiency below 70%")
                recommendations.append("Review equipment alerts in the maintenance dashboard")
        
        if any(word in query_lower for word in ['production', 'output', 'efficiency']):
            efficiency = viz_data["kpis"].get("avg_efficiency", 0)
            if efficiency < 80:
                recommendations.append(f"📊 Production efficiency ({efficiency}%) below target - investigate bottlenecks")
                recommendations.append("Optimize shift schedules to improve equipment utilization")
            else:
                recommendations.append(f"✅ Good production efficiency ({efficiency}%) - maintain current processes")
        
        if any(word in query_lower for word in ['safety', 'incident', 'accident']):
            incidents = viz_data["kpis"].get("total_incidents", 0)
            if incidents > 0:
                recommendations.append(f"⚠️ {incidents} safety incidents reported - review safety protocols")
                recommendations.append("Conduct safety audit in high-risk areas")
            else:
                recommendations.append("✅ No recent safety incidents - continue current safety measures")
        
        # Always add general recommendations
        if not recommendations:
            recommendations = [
                "Review weekly equipment maintenance schedules",
                "Monitor production targets vs actual performance", 
                "Check safety compliance reports regularly",
                "Optimize fuel consumption across all sites"
            ]
        
        return recommendations[:4]  # Return top 4 recommendations

    def filter_relevant_charts(self, question, charts_data):
        """Return only charts relevant to the question"""
        query_lower = question.lower()
        relevant_charts = {}
        
        if any(word in query_lower for word in ['trend', 'history', 'over time']):
            if "incidents_trend" in charts_data:
                relevant_charts["incidents_trend"] = charts_data["incidents_trend"]
            if "production_metrics" in charts_data:
                relevant_charts["production_trend"] = charts_data["production_metrics"]
        
        if any(word in query_lower for word in ['equipment', 'machine', 'status']):
            if "equipment_status" in charts_data:
                relevant_charts["equipment_status"] = charts_data["equipment_status"]
        
        if any(word in query_lower for word in ['production', 'output', 'efficiency']):
            if "production_metrics" in charts_data:
                relevant_charts["production_trend"] = charts_data["production_metrics"]
        
        return relevant_charts

    def extract_data_tables(self, question, sql_context):
        """Extract structured data tables from SQL context"""
        # This would parse the SQL response into table format
        # For now, return simplified version
        return {
            "summary": f"Data from {len(sql_context.splitlines())} records",
            "preview": sql_context[:200] + "..." if len(sql_context) > 200 else sql_context
        }

    def get_enhanced_visualization_data(self, query):
        """Get dynamic visualization data based on user query intent"""
        try:
            conn = get_mysql_connection()
            question = query.lower()
            charts = {}

            if "efficiency" in question:
                charts["efficiency_trend"] = self.get_efficiency_trend(conn)
            if "incident" in question or "alerts" in question:
                charts["incidents_trend"] = self.get_incidents_trend(conn)
            if "production" in question:
                charts["production_metrics"] = self.get_production_trend(conn)
            if "equipment" in question or "status" in question:
                charts["equipment_status"] = self.get_equipment_status(conn)

            # If no keywords matched, return all charts
            if not charts:
                charts = {
                    "incidents_trend": self.get_incidents_trend(conn),
                    "equipment_status": self.get_equipment_status(conn),
                    "production_metrics": self.get_production_trend(conn),
                    "efficiency_trend": self.get_efficiency_trend(conn)
                }
            viz_data = {
                "kpis": self.get_kpis(conn),
                "charts": charts
            }
            conn.close()
            return viz_data
        except Exception as e:
            logger.error(f"❌ Enhanced visualization data error: {e}")
            return {"kpis": {}, "charts": {}}

    def get_efficiency_trend(self, conn):
        """Get efficiency trend data"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(metric_date, '%Y-%m') as month,
                    AVG(efficiency_percentage) as avg_efficiency
                FROM production_metrics
                WHERE metric_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY month
                ORDER BY month DESC
            """
            return pd.read_sql(query, conn).to_dict(orient='records')
        except Exception as e:
            logger.error(f"❌ Efficiency trend error: {e}")
            return []

    def get_sql_context(self, query):
        """Fetch relevant MySQL data with enhanced query routing"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_lower = query.lower()
        # Heuristic extraction of site and timeframe
        site_filter = None
        for token in query_lower.replace("?", " ").split():
            # capture patterns like 'mine' followed by a word/letter
            pass
        for site in self.known_sites:
            if site in query_lower:
                site_filter = site
                break
        # Timeframe: last month / this month / last 30 days
        timeframe = None
        if "last month" in query_lower:
            timeframe = "last_month"
        elif "this month" in query_lower or "current month" in query_lower:
            timeframe = "this_month"
        elif "last 30 days" in query_lower or "past 30 days" in query_lower:
            timeframe = "last_30_days"
        
        try:
            # Enhanced query routing with multiple conditions
            if any(word in query_lower for word in ['incident', 'accident', 'safety', 'casualt', 'injur']):
                cursor.execute("""
                    SELECT 
                        incident_date, 
                        mine_name, 
                        incident_type, 
                        severity, 
                        description, 
                        casualties,
                        injuries,
                        cost_impact,
                        response_time_minutes
                    FROM mining_incidents 
                    WHERE incident_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                    ORDER BY 
                        CASE severity 
                            WHEN 'Critical' THEN 4
                            WHEN 'High' THEN 3
                            WHEN 'Medium' THEN 2
                            ELSE 1 
                        END DESC,
                        incident_date DESC 
                    LIMIT 8
                """)
                
            elif any(word in query_lower for word in ['equipment', 'machine', 'maintenance', 'repair', 'breakdown']):
                # Check if query is about maintenance history or current status
                if any(word in query_lower for word in ['history', 'past', 'last', 'previous']):
                    cursor.execute("""
                        SELECT 
                            mr.equipment_id,
                            mr.maintenance_type,
                            mr.start_date,
                            mr.end_date,
                            mr.cost,
                            mr.downtime_hours,
                            em.equipment_type
                        FROM maintenance_repairs mr
                        LEFT JOIN equipment_monitoring em ON mr.equipment_id = em.equipment_id
                        ORDER BY mr.start_date DESC 
                        LIMIT 6
                    """)
                else:
                    cursor.execute("""
                        SELECT 
                            equipment_id, 
                            equipment_type, 
                            status, 
                            efficiency_score, 
                            alerts,
                            temperature_celsius,
                            vibration_level,
                            last_maintenance,
                            next_maintenance
                        FROM equipment_monitoring 
                        WHERE status != 'Operational' OR efficiency_score < 80
                        ORDER BY 
                            CASE status 
                                WHEN 'Critical' THEN 4
                                WHEN 'Maintenance' THEN 3
                                WHEN 'Offline' THEN 2
                                ELSE 1 
                            END DESC,
                            efficiency_score ASC 
                        LIMIT 8
                    """)
                    
            elif any(word in query_lower for word in ['production', 'output', 'tons', 'efficiency', 'downtime']):
                where_clauses = []
                params = []
                if timeframe == 'last_month':
                    where_clauses.append("MONTH(metric_date) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND YEAR(metric_date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))")
                elif timeframe == 'this_month':
                    where_clauses.append("MONTH(metric_date) = MONTH(CURDATE()) AND YEAR(metric_date) = YEAR(CURDATE())")
                elif timeframe == 'last_30_days':
                    where_clauses.append("metric_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
                else:
                    where_clauses.append("metric_date >= DATE_SUB(CURDATE(), INTERVAL 180 DAY)")
                if site_filter:
                    where_clauses.append("LOWER(site_name) = %s")
                    params.append(site_filter)
                where_sql = " AND ".join(where_clauses)
                cursor.execute(f"""
                    SELECT 
                        metric_date, 
                        site_name, 
                        material_type, 
                        quantity_tons, 
                        efficiency_percentage,
                        downtime_hours,
                        target_tons,
                        cost_per_ton
                    FROM production_metrics 
                    WHERE {where_sql}
                    ORDER BY metric_date DESC, quantity_tons DESC 
                    LIMIT 50
                """, tuple(params))
                
            elif any(word in query_lower for word in ['fuel', 'energy', 'consumption', 'power']):
                cursor.execute("""
                    SELECT 
                        equipment_id,
                        reading_date,
                        fuel_liters,
                        energy_kwh,
                        shift
                    FROM fuel_energy 
                    WHERE reading_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    ORDER BY reading_date DESC, energy_kwh DESC 
                    LIMIT 6
                """)
                
            elif any(word in query_lower for word in ['quality', 'defect', 'grade', 'inspection']):
                cursor.execute("""
                    SELECT 
                        site_name,
                        metric_date,
                        material_type,
                        quality_grade,
                        defects_found
                    FROM quality_metrics 
                    WHERE metric_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    ORDER BY metric_date DESC, defects_found DESC 
                    LIMIT 6
                """)
                
            elif any(word in query_lower for word in ['safety', 'compliance', 'audit', 'violation']):
                cursor.execute("""
                    SELECT 
                        audit_date,
                        site_name,
                        compliance_score,
                        violations,
                        auditor_name,
                        recommendations
                    FROM safety_compliance 
                    ORDER BY audit_date DESC 
                    LIMIT 5
                """)
                
            else:
                # Default: mixed context from multiple tables
                cursor.execute("""
                    (SELECT 
                        'incident' as source_type,
                        incident_date as date,
                        mine_name as name,
                        severity as metric,
                        description as details
                    FROM mining_incidents 
                    ORDER BY incident_date DESC 
                    LIMIT 2)
                    
                    UNION ALL
                    
                    (SELECT 
                        'equipment' as source_type,
                        updated_at as date,
                        equipment_id as name,
                        status as metric,
                        alerts as details
                    FROM equipment_monitoring 
                    WHERE status != 'Operational'
                    ORDER BY updated_at DESC 
                    LIMIT 2)
                    
                    UNION ALL
                    
                    (SELECT 
                        'production' as source_type,
                        metric_date as date,
                        site_name as name,
                        efficiency_percentage as metric,
                        CONCAT('Production: ', quantity_tons, ' tons') as details
                    FROM production_metrics 
                    ORDER BY metric_date DESC 
                    LIMIT 2)
                    
                    ORDER BY date DESC
                """)
            
            results = cursor.fetchall()
            
            # Format results for better readability and grounding
            if results:
                df = pd.DataFrame(results)
                # Build a concise textual summary with top-level stats
                summary_lines = [f"Retrieved {len(results)} records from database."]
                if 'site_name' in df.columns:
                    sites = ", ".join(sorted(set(df['site_name'].dropna().astype(str)))[0:5])
                    if sites:
                        summary_lines.append(f"Sites: {sites}")
                if {'quantity_tons','efficiency_percentage','downtime_hours'}.issubset(df.columns):
                    try:
                        total_qty = float(df['quantity_tons'].fillna(0).sum())
                        avg_eff = float(df['efficiency_percentage'].dropna().astype(float).mean()) if not df['efficiency_percentage'].dropna().empty else 0.0
                        total_down = float(df['downtime_hours'].fillna(0).sum())
                        summary_lines.append(f"Total production: {total_qty:.0f} tons; Avg efficiency: {avg_eff:.1f}%; Downtime: {total_down:.1f} hrs")
                    except Exception:
                        pass
                summary = "\n".join(summary_lines) + "\n\n"
                return summary + df.head(10).to_string(index=False, max_colwidth=50)
            else:
                return "No relevant data found in database for this query."
                
        except Exception as e:
            logger.error(f"❌ SQL context error: {e}")
            return f"Database query error: {str(e)}"
        
        finally:
            cursor.close()
            conn.close()
    
    def get_visualization_data(self, query):
        """Get data for charts and KPIs"""
        try:
            conn = get_mysql_connection()
            
            viz_data = {
                "kpis": self.get_kpis(conn),
                "charts": {
                    "incidents_trend": self.get_incidents_trend(conn),
                    "equipment_status": self.get_equipment_status(conn),
                    "production_metrics": self.get_production_trend(conn)
                }
            }
            
            conn.close()
            return viz_data
        except Exception as e:
            logger.error(f"❌ Visualization data error: {e}")
            return {"kpis": {}, "charts": {}}
    
    def get_kpis(self, conn):
        """Calculate KPIs"""
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Total incidents
            cursor.execute("SELECT COUNT(*) as total_incidents FROM mining_incidents")
            total_incidents = cursor.fetchone()['total_incidents']
            
            # Critical alerts
            cursor.execute("SELECT COUNT(*) as critical_alerts FROM equipment_monitoring WHERE status='Critical'")
            critical_alerts = cursor.fetchone()['critical_alerts']
            
            # Average efficiency (ignore NULL/0)
            cursor.execute("SELECT AVG(NULLIF(efficiency_percentage, 0)) as avg_efficiency FROM production_metrics")
            avg_efficiency = cursor.fetchone()['avg_efficiency'] or 0
            
            # Monthly production (current month) to match UI label
            cursor.execute("SELECT SUM(quantity_tons) as monthly_production FROM production_metrics WHERE MONTH(metric_date)=MONTH(CURDATE()) AND YEAR(metric_date)=YEAR(CURDATE())")
            monthly_production = cursor.fetchone()['monthly_production'] or 0
            
            # Also compute total production (not shown in UI but useful)
            cursor.execute("SELECT SUM(quantity_tons) as total_production FROM production_metrics")
            total_production = cursor.fetchone()['total_production'] or 0
            
            cursor.close()
            
            return {
                "total_incidents": total_incidents,
                "critical_alerts": critical_alerts,
                "avg_efficiency": round(float(avg_efficiency), 1),
                "monthly_production": float(monthly_production),
                "total_production": float(total_production)
            }
        except Exception as e:
            logger.error(f"❌ KPI calculation error: {e}")
            return {
                "total_incidents": 0,
                "critical_alerts": 0,
                "avg_efficiency": 0,
                "monthly_production": 0
            }
    
    def get_incidents_trend(self, conn):
        """Get incident trend data"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(incident_date, '%Y-%m') as month,
                    severity,
                    COUNT(*) as count
                FROM mining_incidents
                GROUP BY month, severity
                ORDER BY month DESC
            """
            return pd.read_sql(query, conn).to_dict(orient='records')
        except Exception as e:
            logger.error(f"❌ Incidents trend error: {e}")
            return []
    
    def get_equipment_status(self, conn):
        """Get equipment status distribution, with a robust output for chart"""
        try:
            query = """
                SELECT status, COUNT(*) as count
                FROM equipment_monitoring
                GROUP BY status
            """
            rows = pd.read_sql(query, conn).to_dict(orient='records')
            # Ensure all expected statuses are represented, even if count is zero
            expected_statuses = ["Critical", "Operational", "Maintenance"]
            result = []
            for status in expected_statuses:
                match = next((r for r in rows if r['status'] == status), None)
                result.append({
                    "status": status,
                    "count": int(match["count"]) if match else 0
                })
            return result
        except Exception as e:
            logger.error(f"❌ Equipment status error: {e}")
            return [
                {"status": "Critical", "count": 0},
                {"status": "Operational", "count": 0},
                {"status": "Maintenance", "count": 0}
            ]
    
    def get_production_trend(self, conn):
        """Get production trend"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(metric_date, '%Y-%m') as month,
                    SUM(quantity_tons) as production,
                    AVG(NULLIF(efficiency_percentage,0)) as efficiency
                FROM production_metrics
                GROUP BY month
                ORDER BY month DESC
            """
            return pd.read_sql(query, conn).to_dict(orient='records')
        except Exception as e:
            logger.error(f"❌ Production trend error: {e}")
            return []