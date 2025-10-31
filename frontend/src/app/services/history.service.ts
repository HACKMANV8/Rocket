import { Injectable } from '@angular/core';

export interface ChatMessageRecord {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string; // ISO
  visualizations?: any;
  recommendations?: string[];
  audio?: any;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: string; // ISO
  updatedAt: string; // ISO
  language: string;
  messages: ChatMessageRecord[];
}

@Injectable({ providedIn: 'root' })
export class HistoryService {
  private STORAGE_KEY = 'mining_chat_sessions_v1';

  private readAll(): ChatSession[] {
    try {
      const raw = localStorage.getItem(this.STORAGE_KEY);
      return raw ? JSON.parse(raw) as ChatSession[] : [];
    } catch {
      return [];
    }
  }

  private writeAll(sessions: ChatSession[]): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessions));
  }

  list(): ChatSession[] {
    return this.readAll().sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  }

  create(title: string, language: string): ChatSession {
    const now = new Date().toISOString();
    const session: ChatSession = {
      id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2),
      title: title?.trim() || 'New chat',
      createdAt: now,
      updatedAt: now,
      language,
      messages: []
    };
    const sessions = this.readAll();
    sessions.unshift(session);
    this.writeAll(sessions);
    return session;
  }

  appendMessage(sessionId: string, message: ChatMessageRecord): void {
    const sessions = this.readAll();
    const idx = sessions.findIndex(s => s.id === sessionId);
    if (idx === -1) return;
    sessions[idx].messages.push(message);
    sessions[idx].updatedAt = new Date().toISOString();
    this.writeAll(sessions);
  }

  load(sessionId: string): ChatSession | null {
    return this.readAll().find(s => s.id === sessionId) || null;
  }

  rename(sessionId: string, title: string): void {
    const sessions = this.readAll();
    const idx = sessions.findIndex(s => s.id === sessionId);
    if (idx === -1) return;
    sessions[idx].title = title.trim() || sessions[idx].title;
    sessions[idx].updatedAt = new Date().toISOString();
    this.writeAll(sessions);
  }

  remove(sessionId: string): void {
    const sessions = this.readAll().filter(s => s.id !== sessionId);
    this.writeAll(sessions);
  }
}


