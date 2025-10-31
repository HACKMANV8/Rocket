export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audio?: AudioData;
  // ✅ UPDATED: Embedded visualizations
  visualizations?: {
    kpis: {
      total_incidents: number;
      critical_alerts: number;
      avg_efficiency: number;
      monthly_production: number;
    };
    charts: {
      equipment_status?: any[];
      production_trend?: any[];
      incidents_trend?: any[];
      efficiency_trend?: any[];
    };
    tables?: {
      summary: string;
      preview: string;
    };
  };
  // ✅ ADDED: Embedded recommendations
  recommendations?: string[];
}

export interface AudioData {
  success: boolean;
  audio_base64?: string;
  language?: string;
  format?: string;
  error?: string;
}

// ✅ UPDATED: Response structure
export interface ChatResponse {
  success: boolean;
  response: {
    answer: string;
    type: 'ai_response' | 'error';
    visualizations: {
      kpis: any;
      charts: any;
      tables: any;
    };
    recommendations: string[];
    sources: any[];
    language: string;
    audio?: AudioData;
  };
}

export interface KPIsResponse {
  success: boolean;
  kpis: {
    total_incidents: number;
    critical_alerts: number;
    avg_efficiency: number;
    monthly_production: number;
  };
}

// ✅ ADDED: System status interface
export interface SystemStatus {
  database: boolean;
  chromadb: boolean;
  mistral_ai: boolean;
  services_ready: boolean;
}

// ✅ ADDED: Quick actions interface
export interface QuickAction {
  icon: string;
  text: string;
  suggestion: string;
  action?: string;
}