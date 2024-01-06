import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { TestComponent } from './test/test.component';

const routes: Routes = [
  { path : '' , component: HomeComponent},
  { path : 'about', component: AboutComponent},
  { path : 'test', component: TestComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
