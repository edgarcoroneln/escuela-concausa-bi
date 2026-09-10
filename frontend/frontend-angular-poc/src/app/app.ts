import { Component } from '@angular/core';
import { NgxChartsModule, Color, ScaleType } from '@swimlane/ngx-charts';

// Mismos datos que las otras 3 variantes (Recharts / D3 a mano / Observable Plot)
// para que la comparación sea justa — combo #4: Angular + ngx-charts + D3.
const matriculaPorCiclo = [
  { name: '2022-2023', value: 6512340 },
  { name: '2023-2024', value: 6598110 },
  { name: '2024-2025', value: 6704229 },
];

const colorScheme: Color = {
  name: 'faro',
  selectable: true,
  group: ScaleType.Ordinal,
  domain: ['#2b5aa8'],
};

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [NgxChartsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  readonly data = matriculaPorCiclo;
  readonly colorScheme = colorScheme;
  readonly view: [number, number] = [420, 300];
}
