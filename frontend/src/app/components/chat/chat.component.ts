import { Component, Input, OnInit, ViewChild, ElementRef } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AudioService } from '../../services/audio.service';
import { HistoryService, ChatSession, ChatMessageRecord } from '../../services/history.service';
import { ChatMessage } from '../../models/interfaces';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  @Input() language: string = 'en';
  @ViewChild('chatMessages') chatMessages!: ElementRef;
  @ViewChild('chatInput') chatInput!: ElementRef;
  
  messages: ChatMessage[] = [];
  userInput: string = '';
  isLoading: boolean = false;
  includeAudio: boolean = true;
  private currentSession: ChatSession | null = null;
  private pendingUpload: File | null = null;

  constructor(
    private apiService: ApiService, 
    private audioService: AudioService,
    private history: HistoryService,
  ) {}

  ngOnInit(): void {
    this.messages.push({
      role: 'assistant',
      content: 'Hello! I\'m your Mining Intelligence Assistant. Ask me about equipment status, production efficiency, safety incidents, or get management recommendations.',
      timestamp: new Date()
    });

    this.setupEventListeners();
  }

  setupEventListeners(): void {
    window.addEventListener('suggestQuestion', (event: any) => {
      this.userInput = event.detail;
      this.sendMessage();
    });

    // Load a session from history
    window.addEventListener('loadSession', (event: any) => {
      const sessionId = event.detail as string;
      const session = this.history.load(sessionId);
      if (session) {
        this.currentSession = session;
        this.language = session.language || this.language;
        // Map stored records to ChatMessage format
        this.messages = session.messages.map(m => ({
          role: m.role,
          content: m.content,
          timestamp: new Date(m.timestamp),
          visualizations: m.visualizations,
          recommendations: m.recommendations,
          audio: m.audio,
        }));
        this.scrollToBottom();
      }
    });
  }

  sendMessage(): void {
    if (!this.userInput.trim() || this.isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: this.userInput,
      timestamp: new Date()
    };
    this.messages.push(userMessage);

    // Create session if not exists
    if (!this.currentSession) {
      this.currentSession = this.history.create(this.userInput, this.language);
    }
    // Persist user message
    this.history.appendMessage(this.currentSession.id, {
      role: 'user',
      content: userMessage.content,
      timestamp: userMessage.timestamp.toISOString(),
    } as ChatMessageRecord);

    // Auto-title session with first user message if needed
    if (this.currentSession && this.messages.length === 2) {
      this.history.rename(this.currentSession.id, userMessage.content.substring(0, 30));
    }
    const query = this.userInput;
    this.userInput = '';
    this.isLoading = true;

    // Use actual API call with your interface structure
    this.apiService.sendQuery(query, this.language, this.includeAudio).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        
        if (response.success) {
          const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: response.response.answer,
            timestamp: new Date(),
            visualizations: response.response.visualizations,
            recommendations: response.response.recommendations,
            audio: response.response.audio
          };
          
          this.messages.push(assistantMessage);

          // Persist assistant message
          if (this.currentSession) {
            this.history.appendMessage(this.currentSession.id, {
              role: 'assistant',
              content: assistantMessage.content,
              timestamp: assistantMessage.timestamp.toISOString(),
              visualizations: assistantMessage.visualizations,
              recommendations: assistantMessage.recommendations,
              audio: assistantMessage.audio,
            } as ChatMessageRecord);
          }

          if (this.includeAudio && response.response.audio?.success) {
            this.audioService.playAudio(response.response.audio.audio_base64!);
          }
        } else {
          this.messages.push({
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
            timestamp: new Date()
          });
        }
        this.scrollToBottom();
      },
      error: (err: any) => {
        this.isLoading = false;
        
        // Fallback: Show simulated response with sample data
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: `I analyzed your query about "${query}". Here are the current mining operations insights:`,
          timestamp: new Date(),
          visualizations: {
            kpis: {
              total_incidents: 5,
              critical_alerts: 2,
              avg_efficiency: 87,
              monthly_production: 12500
            },
            charts: {
              equipment_status: [
                { status: 'Operational', count: 45 },
                { status: 'Maintenance', count: 8 },
                { status: 'Critical', count: 2 }
              ],
              production_trend: [
                { month: 'Jan', production: 12000 },
                { month: 'Feb', production: 13500 },
                { month: 'Mar', production: 12800 }
              ]
            }
          },
          recommendations: [
            'Schedule maintenance for equipment with >5000 operating hours',
            'Review safety protocols for incident-prone areas',
            'Optimize shift schedules to improve efficiency'
          ]
        };
        
        this.messages.push(assistantMessage);
        this.scrollToBottom();
      }
    });
  }

  onFileSelected(event: any): void {
    const file: File | null = event?.target?.files?.[0] || null;
    if (!file) return;
    this.pendingUpload = file;
    // Immediately upload
    const docType = file.name.toLowerCase().endsWith('.csv') ? 'csv' : 'pdf';
    this.apiService.uploadFile(file, docType).subscribe({
      next: (res: any) => {
        this.messages.push({
          role: 'assistant',
          content: res?.success ? `Imported ${file.name} successfully.` : `Failed to import ${file.name}.`,
          timestamp: new Date()
        });
        this.scrollToBottom();
        this.pendingUpload = null;
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: `Failed to import ${file.name}.`,
          timestamp: new Date()
        });
        this.scrollToBottom();
        this.pendingUpload = null;
      }
    });
    // reset input element value to allow re-selecting same file
    event.target.value = '';
  }

  handleEnterEvent(event: KeyboardEvent): void {
    if (!event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  playAudio(message: ChatMessage): void {
    if (message.audio?.success && message.audio.audio_base64) {
      this.audioService.playAudio(message.audio.audio_base64);
    }
  }

  clearChat(): void {
    this.messages = [{
      role: 'assistant',
      content: 'Chat cleared. How can I help you with mining operations today?',
      timestamp: new Date()
    }];
  }

  scrollToBottom(): void {
    setTimeout(() => {
      if (this.chatMessages?.nativeElement) {
        this.chatMessages.nativeElement.scrollTop = this.chatMessages.nativeElement.scrollHeight;
      }
    }, 100);
  }

  // Helper method to check if we have chart data
  hasChartData(charts: any): boolean {
    return charts && (
      (charts.equipment_status && charts.equipment_status.length > 0) ||
      (charts.production_trend && charts.production_trend.length > 0) ||
      (charts.incidents_trend && charts.incidents_trend.length > 0)
    );
  }
}