import { Component, ViewChild, ElementRef } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  @ViewChild('contactSection') contactSection!: ElementRef;

  scrollToContact() {
    if (this.contactSection) {
      this.contactSection.nativeElement.scrollIntoView({ behavior: 'smooth' });
    }
  }
}
