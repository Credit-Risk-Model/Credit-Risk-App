import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-card-footer',
  imports: [CommonModule],
  templateUrl: './card-footer.html',
  styleUrl: './card-footer.css'
})
export class CardFooter {  
@Input() modelResults: any[] = [];

getAlertClass(value: string): string {
  if (value == "Rejected") return 'alert-danger';   // Red
  return 'alert-success';                           // Green
}
}
