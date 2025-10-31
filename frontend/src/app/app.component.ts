import { Component, OnInit } from '@angular/core';
import { ApiService } from './services/api.service';

interface SystemStatus {
  database: boolean;
  chromadb: boolean;
  mistral_ai: boolean;
  services_ready: boolean;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'Mining Intelligence System';
  isHealthy = false;
  selectedLanguage = 'en';
  languages: any = {};
  systemStatus: SystemStatus | null = null;
  showHistory = false;
  sessions: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.checkHealth();
    this.loadLanguages();
    this.loadSystemStatus();
    this.refreshSessions();
  }

  checkHealth(): void {
    this.apiService.healthCheck().subscribe({
      next: (response) => {
        this.isHealthy = response.status === 'healthy';
      },
      error: (error) => {
        this.isHealthy = false;
      }
    });
  }

  loadSystemStatus(): void {
    this.apiService.getSystemStatus().subscribe({
      next: (response) => {
        if (response.success) {
          this.systemStatus = response.status;
        }
      },
      error: (error) => {
        console.error('Error loading system status:', error);
      }
    });
  }

  loadLanguages(): void {
    this.apiService.getLanguages().subscribe({
      next: (response) => {
        if (response.success) {
          this.languages = response.languages;
        } else {
          // Fallback languages
          this.languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'hi': 'Hindi'
          };
        }
      },
      error: (error) => {
        // Fallback if API fails
        this.languages = {
          'en': 'English',
          'es': 'Spanish',
          'fr': 'French',
          'hi': 'Hindi'
        };
      }
    });
  }

  onLanguageChange(event: any): void {
    this.selectedLanguage = event.target.value;
  }

  suggestQuestion(question: string): void {
    // This will be handled by the chat component
    const chatComponent = document.querySelector('app-chat');
    if (chatComponent) {
      // We'll use a custom event to pass the suggestion to chat component
      const event = new CustomEvent('suggestQuestion', { detail: question });
      chatComponent.dispatchEvent(event);
    }
  }

  toggleHistory(): void {
    this.showHistory = !this.showHistory;
    if (this.showHistory) {
      this.refreshSessions();
    }
  }

  refreshSessions(): void {
    try {
      const raw = localStorage.getItem('mining_chat_sessions_v1');
      this.sessions = raw ? JSON.parse(raw) : [];
    } catch {
      this.sessions = [];
    }
  }

  openSession(sessionId: string): void {
    const chatComponent = document.querySelector('app-chat');
    if (chatComponent) {
      const event = new CustomEvent('loadSession', { detail: sessionId });
      chatComponent.dispatchEvent(event);
    }
    this.showHistory = false;
  }
}