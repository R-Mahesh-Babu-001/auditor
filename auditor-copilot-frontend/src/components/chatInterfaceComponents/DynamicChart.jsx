import React from "react";
import {
  ResponsiveContainer,
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  PieChart, Pie, Cell,
  ScatterChart, Scatter,
  ComposedChart,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';

const COLORS = [
  "#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#a4de6c",
  "#d0ed57", "#888888", "#ff4d4f", "#69c0ff", "#b37feb"
];

const DynamicChart = ({ chartData }) => {
  if (!chartData) return <div className="text-gray-500">No chart data provided.</div>;

  try {
    const { chartType, data, xKey, yKey, yKeys } = chartData;

    switch (chartType) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={yKey} fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case "line":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {yKeys?.map((key, index) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={COLORS[index % COLORS.length]}
                  dot={false}
                />
              ))}
              {!yKeys && yKey && (
                <Line type="monotone" dataKey={yKey} stroke="#8884d8" dot={false} />
              )}
            </LineChart>
          </ResponsiveContainer>
        );

      case "area":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {yKeys?.map((key, index) => (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={COLORS[index % COLORS.length]}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
              {!yKeys && yKey && (
                <Area
                  type="monotone"
                  dataKey={yKey}
                  stroke="#8884d8"
                  fill="#8884d8"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        );

      case "scatter":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart>
              <CartesianGrid />
              <XAxis
                type="number"
                dataKey={xKey}
                name="Price"
                unit="$"
              />
              <YAxis
                type="number"
                dataKey={yKey}
                name="Rating"
                unit=""
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                formatter={(value, name, props) => {
                  if (name === xKey) return [`$${value}`, "Price"];
                  if (name === yKey) return [value, "Rating"];
                  return value;
                }}
                labelFormatter={(label, payload) => {
                  const item = payload?.[0]?.payload;
                  return item?.product || '';
                }}
              />
              <Legend />
              <Scatter name="Scatter Data" data={data} fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case "composed":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {yKeys?.map((key, index) => (
                <Bar key={key} dataKey={key} fill={COLORS[index % COLORS.length]} />
              ))}
              {yKey && <Line type="monotone" dataKey={yKey} stroke="#ff7300" />}
            </ComposedChart>
          </ResponsiveContainer>
        );

      case "radar":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={data}>
              <PolarGrid />
              <PolarAngleAxis dataKey={xKey} />
              <PolarRadiusAxis />
              <Tooltip />
              <Legend />
              <Radar
                name="Radar Data"
                dataKey={yKey}
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.6}
              />
            </RadarChart>
          </ResponsiveContainer>
        );

      case "pie":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Tooltip />
              <Legend />
              <Pie
                data={data}
                dataKey={yKey}
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={120}
                label
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return (
          <div className="text-red-600">
            Unsupported chart type: <strong>{chartType}</strong>
          </div>
        );
    }
  } catch (error) {
    console.error("Chart rendering error:", error);
    return (
      <div className="text-red-500">
        Something went wrong while rendering the chart. Please check your chart configuration and try again.
      </div>
    );
  }
};

export default DynamicChart;
