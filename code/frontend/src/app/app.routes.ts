import { Routes } from '@angular/router';
import { Main } from './components/main/main';
import { Form } from './components/form/form';
import { Test } from './components/test/test';

export const routes: Routes = [
    { path: '', redirectTo: '/home', pathMatch: 'full' },
    {
      path: '',
      component: Main,
      children: [
        {
          path: 'home',
          component: Form,
        },
        {
          path: 'test',
          component: Test,
        },
      ]
    }
  ];
  
