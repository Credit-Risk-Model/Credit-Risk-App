import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from '../header/header';
import { Footer } from '../footer/footer';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [
    Header, 
    Footer, 
    RouterOutlet,
    CommonModule
  ],
  templateUrl: './main.html',
  styleUrl: './main.css'
})
export class Main {

}
