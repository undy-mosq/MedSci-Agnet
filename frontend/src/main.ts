import { BarChart, PieChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { createApp } from 'vue';
import ECharts from 'vue-echarts';

import App from './App.vue';
import './styles/main.scss';

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
]);

const app = createApp(App);
app.component('VChart', ECharts);
app.mount('#app');
