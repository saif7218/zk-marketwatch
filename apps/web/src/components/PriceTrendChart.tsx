import React from 'react';
import { useTranslation } from 'react-i18next';
import { EChartsReact } from 'echarts-for-react';
import { PriceTrendData, UserPreferences } from '../types/price';
import { useUserPreferences } from '../hooks/useUserPreferences';
import { cn } from '../lib/utils';

interface PriceTrendChartProps {
  data: PriceTrendData[];
  className?: string;
}

const PriceTrendChart = ({ data, className }: PriceTrendChartProps) => {
  const { t, i18n } = useTranslation();
  const { preferences } = useUserPreferences();

  const getSeries = (item: PriceTrendData) => ({
    name: item.competitorId,
    type: 'line',
    data: item.data.map(d => [d.timestamp, d.price]),
    showSymbol: false,
    smooth: true,
    areaStyle: {
      opacity: 0.1,
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#83bff6' },
        { offset: 0.5, color: '#188df0' },
        { offset: 1, color: '#188df0' }
      ])
    },
    lineStyle: {
      width: 2
    }
  });

  const option = {
    title: {
      text: t('charts.priceTrend'),
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      formatter: (params: any) => {
        const date = new Date(params[0].axisValue);
        const formattedDate = date.toLocaleDateString(i18n.language, {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
        
        return `
          <div style="padding: 8px; background: rgba(255,255,255,0.9)">
            <div style="font-weight: bold; margin-bottom: 8px">${formattedDate}</div>
            ${params.map(param => `
              <div>
                <span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color}"></span>
                ${param.seriesName}: ${param.value[1].toLocaleString(i18n.language)}
              </div>
            `).join('')}
          </div>
        `;
      }
    },
    legend: {
      data: data.map(d => d.competitorId),
      right: '10%'
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLabel: {
        formatter: function (value: number) {
          return new Date(value).toLocaleDateString(i18n.language, {
            month: 'short',
            day: 'numeric'
          });
        }
      }
    },
    yAxis: {
      type: 'value',
      name: t('charts.price'),
      axisLabel: {
        formatter: function (value: number) {
          return value.toLocaleString(i18n.language);
        }
      }
    },
    series: data.map(getSeries)
  };

  return (
    <div className={cn('h-[600px] w-full', className)}>
      <EChartsReact
        option={option}
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      />
    </div>
  );
};

export default PriceTrendChart;
