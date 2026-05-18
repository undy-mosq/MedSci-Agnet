/** [2026-05-18] 注册 DataZoom 组件以支持图表缩放。 */
import { BarChart, PieChart } from 'echarts/charts';
import {
  DataZoomComponent,
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
  DataZoomComponent,
]);

const app = createApp(App);
app.component('VChart', ECharts);
app.mount('#app');
