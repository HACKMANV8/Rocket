import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // Health check
  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/health`);
  }

  // Main query endpoint
  sendQuery(query: string, language: string = 'en', includeAudio: boolean = true): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/query`, {
      question: query,
      language: language,
      includeAudio: includeAudio
    });
  }

  // System status
  getSystemStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/system-status`);
  }

  // Quick actions for sidebar
  getQuickActions(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/quick-actions`);
  }

  // Get supported languages
  getLanguages(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/languages`);
  }

  // Get recent incidents
  getRecentIncidents(limit: number = 5): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/incidents?limit=${limit}`);
  }

  // Get maintenance alerts
  getEquipmentAlerts(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/maintenance-alerts`);
  }

  // Get KPIs
  getKPIs(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/kpis`);
  }

  // Test endpoint
  testRAG(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/test`);
  }

  // Upload CSV/PDF for ingestion
  uploadFile(file: File, docType: string = 'document'): Observable<any> {
    const form = new FormData();
    form.append('file', file);
    form.append('docType', docType);
    return this.http.post(`${this.apiUrl}/api/upload`, form);
  }
}