import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private audio: HTMLAudioElement | null = null;

  constructor() { }

  playAudio(base64Audio: string): void {
    if (this.audio) {
      this.audio.pause();
    }

    const audioData = `data:audio/mp3;base64,${base64Audio}`;
    this.audio = new Audio(audioData);
    this.audio.play().catch(error => {
      console.error('Error playing audio:', error);
    });
  }

  stopAudio(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio = null;
    }
  }

  isPlaying(): boolean {
    return this.audio !== null && !this.audio.paused;
  }
}