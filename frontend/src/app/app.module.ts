import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';  // <-- ADD THIS

import { AppComponent } from './app.component';
//import { KpisComponent } from './components/kpis/kpis.component';
import { ChatComponent } from './components/chat/chat.component';
import { ChartsComponent } from './components/charts/charts.component';
//import { GuidanceComponent } from './components/guidance/guidance.component';
//import { DashboardComponent } from './components/dashboard/dashboard.component';

@NgModule({
  declarations: [
    AppComponent,
  //  KpisComponent,
    ChatComponent,
    ChartsComponent,
    //GuidanceComponent,
    //ashboardComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule, // <-- ADD THIS
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
