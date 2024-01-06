import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class VideoService {

  constructor() { }

  getVideoFeedUrl(): string {
    // Ici, vous simuleriez une requête ou une logique pour obtenir l'URL réelle du flux vidéo
    // Par exemple, vous pourriez avoir une API ou une logique de génération d'URL
    // Pour cet exemple, retournons une URL statique
    return 'https://example.com/video_feed';
  }
}
