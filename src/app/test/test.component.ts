import { Component, OnInit, ViewChild,ElementRef } from '@angular/core';

import * as cv from 'opencv-ts';
@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrl: './test.component.css'
})
export class TestComponent implements OnInit {
  @ViewChild('video') videoElement!: ElementRef;
  videoWidth = 640;
  videoHeight = 480;

  videoFeedUrl !: string;

  constructor() { }

  ngOnInit(): void {
    this.startCamera();
  }

  async startCamera() {
    const video = this.videoElement.nativeElement;

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;

        video.width = this.videoWidth;
        video.height = this.videoHeight;

        video.onloadedmetadata = () => {
          video.play();

        };
      } catch (error) {
        console.error('Error accessing the camera:', error);
      }
    }
  }


}
