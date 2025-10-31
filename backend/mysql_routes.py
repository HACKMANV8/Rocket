from flask import jsonify
from database.db_config import get_mysql_connection  # ✅ FIXED: Use correct import
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

# ✅ UPDATED: Mock data that matches YOUR schema
IN_MEMORY_EQUIPMENT = [
    {
        "equipment_id": "EX-001", 
        "equipment_type": "Excavator", 
        "status": "Operational",
        "efficiency_score": 85.5,
        "alerts": "None",
        "location": "Pit A"
    },
]

def register_mysql_routes(app):

    @app.route('/api/mysql/status')
    def mysql_status():
        """Check MySQL connection status"""
        try:
            conn = get_mysql_connection()  # ✅ FIXED: Use correct function
            if conn:
                conn.close()
                return jsonify({"status": "connected", "database": True})
            return jsonify({"status": "disconnected", "database": False})
        except Exception as e:
            logger.error(f"MySQL status error: {e}")
            return jsonify({"status": "error", "database": False, "error": str(e)})

    @app.route('/api/equipment')
    def get_equipment():
        """Get equipment data - UPDATED for your schema"""
        try:
            conn = get_mysql_connection()
            if not conn:
                return jsonify(IN_MEMORY_EQUIPMENT)
            
            cur = conn.cursor(dictionary=True)
            # ✅ FIXED: Use your actual table name and columns
            cur.execute("""
                SELECT 
                    equipment_id, equipment_type, status, efficiency_score, 
                    alerts, location, last_maintenance, next_maintenance
                FROM equipment_monitoring 
                ORDER BY efficiency_score DESC 
                LIMIT 50
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(rows or IN_MEMORY_EQUIPMENT)
        except Exception as e:
            logger.error(f"Equipment endpoint error: {e}")
            return jsonify(IN_MEMORY_EQUIPMENT)

    @app.route('/api/production')
    def get_production():
        """Get production data - UPDATED for your schema"""
        try:
            conn = get_mysql_connection()
            if not conn:
                # ✅ FIXED: Mock data that matches your schema
                return jsonify([
                    {
                        "site_name": "Northern Mine",
                        "metric_date": datetime.now().date().isoformat(),
                        "quantity_tons": random.uniform(800,1500),
                        "efficiency_percentage": random.uniform(75,95)
                    }
                ])
            
            cur = conn.cursor(dictionary=True)
            # ✅ FIXED: Use your actual table and columns
            cur.execute("""
                SELECT 
                    site_name, metric_date, quantity_tons, efficiency_percentage,
                    material_type, downtime_hours
                FROM production_metrics 
                ORDER BY metric_date DESC 
                LIMIT 50
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(rows)
        except Exception as e:
            logger.error(f"Production endpoint error: {e}")
            return jsonify([
                {
                    "site_name": "Fallback Mine",
                    "metric_date": datetime.now().date().isoformat(),
                    "quantity_tons": 1000,
                    "efficiency_percentage": 85.0
                }
            ])

    @app.route('/api/maintenance-alerts')
    def get_maintenance_alerts():
        """Get maintenance alerts - UPDATED for your schema"""
        try:
            conn = get_mysql_connection()
            if not conn:
                # ✅ FIXED: Mock alerts that match your schema
                alerts = []
                for e in IN_MEMORY_EQUIPMENT:
                    if e.get("status") in ["Critical", "Maintenance"]:
                        alerts.append({
                            "equipment_id": e["equipment_id"],
                            "equipment_type": e["equipment_type"],
                            "status": e["status"],
                            "alerts": e.get("alerts", "Maintenance required")
                        })
                return jsonify(alerts)
            
            cur = conn.cursor(dictionary=True)
            # ✅ FIXED: Use your actual tables and logic
            cur.execute("""
                SELECT 
                    equipment_id, equipment_type, status, alerts,
                    efficiency_score, last_maintenance
                FROM equipment_monitoring 
                WHERE status != 'Operational' OR efficiency_score < 80
                ORDER BY 
                    CASE status 
                        WHEN 'Critical' THEN 1
                        WHEN 'Maintenance' THEN 2  
                        ELSE 3
                    END,
                    efficiency_score ASC
                LIMIT 20
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(rows)
        except Exception as e:
            logger.error(f"Maintenance alerts error: {e}")
            return jsonify([])

    @app.route('/api/incidents')
    def get_incidents():
        """✅ ADDED: Get recent safety incidents"""
        try:
            conn = get_mysql_connection()
            if not conn:
                return jsonify([])
            
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT 
                    incident_date, mine_name, incident_type, severity,
                    description, casualties, injuries
                FROM mining_incidents 
                ORDER BY incident_date DESC 
                LIMIT 20
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(rows)
        except Exception as e:
            logger.error(f"Incidents endpoint error: {e}")
            return jsonify([])

    @app.route('/api/kpis')
    def get_kpis():
        """✅ ADDED: Get current KPIs for dashboard"""
        try:
            conn = get_mysql_connection()
            if not conn:
                return jsonify({
                    "total_incidents": 0,
                    "critical_alerts": 0,
                    "avg_efficiency": 0,
                    "monthly_production": 0
                })
            
            cur = conn.cursor(dictionary=True)
            
            # Total incidents (last 30 days)
            cur.execute("""
                SELECT COUNT(*) as total_incidents 
                FROM mining_incidents 
                WHERE incident_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """)
            total_incidents = cur.fetchone()['total_incidents']
            
            # Critical equipment alerts
            cur.execute("""
                SELECT COUNT(*) as critical_alerts 
                FROM equipment_monitoring 
                WHERE status = 'Critical'
            """)
            critical_alerts = cur.fetchone()['critical_alerts']
            
            # Average efficiency (last 30 days)
            cur.execute("""
                SELECT AVG(efficiency_percentage) as avg_efficiency 
                FROM production_metrics 
                WHERE metric_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """)
            avg_efficiency = cur.fetchone()['avg_efficiency'] or 0
            
            # Monthly production
            cur.execute("""
                SELECT SUM(quantity_tons) as monthly_production 
                FROM production_metrics 
                WHERE MONTH(metric_date) = MONTH(CURDATE())
            """)
            monthly_production = cur.fetchone()['monthly_production'] or 0
            
            cur.close()
            conn.close()
            
            return jsonify({
                "total_incidents": total_incidents,
                "critical_alerts": critical_alerts,
                "avg_efficiency": round(float(avg_efficiency), 2),
                "monthly_production": float(monthly_production)
            })
        except Exception as e:
            logger.error(f"KPIs endpoint error: {e}")
            return jsonify({
                "total_incidents": 0,
                "critical_alerts": 0,
                "avg_efficiency": 0,
                "monthly_production": 0
            })


def gather_context():
    """UPDATED: Gather context for ML - matches your schema"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return {
                "equipment": IN_MEMORY_EQUIPMENT, 
                "production": [], 
                "alerts": []
            }

        cur = conn.cursor(dictionary=True)
        
        # ✅ FIXED: Use your actual equipment table
        cur.execute("""
            SELECT equipment_id, equipment_type, status, efficiency_score, alerts
            FROM equipment_monitoring 
            LIMIT 20
        """)
        equipment = cur.fetchall()

        # ✅ FIXED: Use your actual production table
        cur.execute("""
            SELECT metric_date as date, site_name, quantity_tons as ore_extracted_tons, efficiency_percentage
            FROM production_metrics 
            ORDER BY metric_date DESC 
            LIMIT 7
        """)
        production = cur.fetchall()

        # ✅ FIXED: Use your actual alerts logic
        cur.execute("""
            SELECT equipment_id, equipment_type, status, alerts
            FROM equipment_monitoring 
            WHERE status != 'Operational' OR efficiency_score < 80
        """)
        alerts = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "equipment": equipment or IN_MEMORY_EQUIPMENT,
            "production": production,
            "alerts": alerts or []
        }
    except Exception as e:
        logger.error(f"Gather context error: {e}")
        return {
            "equipment": IN_MEMORY_EQUIPMENT,
            "production": [],
            "alerts": []
        }