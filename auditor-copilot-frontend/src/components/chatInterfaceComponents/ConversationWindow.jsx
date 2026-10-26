import React, { useEffect, useRef } from "react"
import { cn } from "../../lib/utils"
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Loader2, FileText, FileSpreadsheet, FileImage, File } from "lucide-react"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"

// Recharts for chart rendering
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ComposedChart,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Cell,
} from "recharts";

const ConversationWindow = ({ messages, setMessages }) => {
  const messagesEndRef = useRef(null)

  console.log("Messages: ", messages)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return <FileImage className="h-4 w-4" />;
    if (['xls', 'xlsx', 'csv'].includes(ext)) return <FileSpreadsheet className="h-4 w-4" />;
    if (['pdf', 'txt', 'doc', 'docx'].includes(ext)) return <FileText className="h-4 w-4" />;
    return <File className="h-4 w-4" />;
  };

  return (
    <div>
      {messages?.map((message, index) => (
        <div
          key={index}
          className={cn(
            "flex my-3 transition-opacity duration-300 animate-in fade-in",
            message.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          <Card
            className={cn(
              "max-w-[80%] overflow-x-auto shadow-sm border-0",
              message.role === "user"
                ? "bg-gradient-to-br from-primary to-blue-600 text-white rounded-2xl rounded-tr-sm"
                : "bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border border-border/50 rounded-2xl rounded-tl-sm text-foreground"
            )}
          >
            <CardContent className="px-4 py-2 text-sm leading-relaxed">
              {message.attachments && message.attachments.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {message.attachments.map((att, i) => (
                    <div key={i} className={cn(
                        "flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium backdrop-blur-sm transition-colors shadow-sm",
                        message.role === "user" 
                          ? "bg-white/20 text-white hover:bg-white/30 border border-white/20" 
                          : "bg-muted/50 text-foreground border border-border/50"
                    )}>
                        {getFileIcon(att.name)}
                        <span className="truncate max-w-[200px]">{att.name}</span>
                    </div>
                  ))}
                </div>
              )}

              {message.isLoading && !message.content ? (
                // Loading state before first chunk
                <div className="flex items-center gap-2 py-1">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <span className="text-muted-foreground animate-pulse font-medium">
                    Thinking...
                  </span>
                </div>
              ) : (
                <div>
                  {/* Try to parse message content as chart JSON */}
                  {(() => {
                    try {
                      const parsed = typeof message.content === "string" ? JSON.parse(message.content) : message.content;
                      const isChart = parsed && parsed.chartType && Array.isArray(parsed.data) && parsed.data.length > 0;
                      if (isChart) {
                        const chart = parsed;
                        const firstItem = chart.data[0] || {};
                        const xKey = chart.xKey || (chart.nameKey) || Object.keys(firstItem)[0] || "name";
                        const yKeys = chart.yKeys || (chart.yKey ? [chart.yKey] : Object.keys(firstItem).filter(k => k !== xKey));
                        // Ensure at least one yKey for charts that need it
                        const primaryYKey = chart.yKey || yKeys[0] || "value";
                        
                        const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"];

                        let ChartComponent;
                        if (chart.chartType === 'bar') {
                          ChartComponent = (
                            <BarChart data={chart.data}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey={xKey} />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              {yKeys.map((k, i) => (
                                <Bar key={k} dataKey={k} fill={colors[i % colors.length]} />
                              ))}
                            </BarChart>
                          );
                        } else if (chart.chartType === 'area') {
                          ChartComponent = (
                            <AreaChart data={chart.data}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey={xKey} />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              {yKeys.map((k, i) => (
                                <Area key={k} type="monotone" dataKey={k} fill={colors[i % colors.length]} stroke={colors[i % colors.length]} fillOpacity={0.3} />
                              ))}
                            </AreaChart>
                          );
                        } else if (chart.chartType === 'pie') {
                          ChartComponent = (
                            <PieChart>
                              <Pie
                                data={chart.data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey={primaryYKey}
                                nameKey={chart.nameKey || xKey}
                              >
                                {chart.data.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                              </Pie>
                              <Tooltip />
                              <Legend />
                            </PieChart>
                          );
                        } else if (chart.chartType === 'scatter') {
                          ChartComponent = (
                            <ScatterChart>
                              <CartesianGrid />
                              <XAxis type="number" dataKey={xKey} name={xKey} />
                              <YAxis type="number" dataKey={primaryYKey} name={primaryYKey} />
                              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                              <Legend />
                              <Scatter name={chart.title || "Data"} data={chart.data} fill="#8884d8" />
                            </ScatterChart>
                          );
                        } else if (chart.chartType === 'radar') {
                          ChartComponent = (
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chart.data}>
                              <PolarGrid />
                              <PolarAngleAxis dataKey={xKey} />
                              <PolarRadiusAxis />
                              {yKeys.map((k, i) => (
                                <Radar key={k} name={k} dataKey={k} stroke={colors[i % colors.length]} fill={colors[i % colors.length]} fillOpacity={0.6} />
                              ))}
                              <Legend />
                              <Tooltip />
                            </RadarChart>
                          );
                        } else if (chart.chartType === 'composed') {
                          ChartComponent = (
                            <ComposedChart data={chart.data}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey={xKey} />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              {yKeys.map((k, i) => (
                                <Bar key={k} dataKey={k} fill={colors[i % colors.length]} barSize={20} />
                              ))}
                              {chart.yKey && (
                                <Line type="monotone" dataKey={chart.yKey} stroke="#ff7300" strokeWidth={2} />
                              )}
                            </ComposedChart>
                          );
                        } else {
                          // Default to line chart
                          ChartComponent = (
                            <LineChart data={chart.data}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey={xKey} />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              {yKeys.map((k, i) => (
                                <Line key={k} type="monotone" dataKey={k} stroke={colors[i % colors.length]} strokeWidth={2} dot={{ r: 2 }} />
                              ))}
                            </LineChart>
                          );
                        }

                        return (
                          <div className="space-y-3">
                            {chart.title && <div className="font-semibold text-sm mb-1">{chart.title}</div>}
                            {chart.description && <div className="text-xs text-muted-foreground mb-2">{chart.description}</div>}
                            <div style={{ width: '100%', height: 260 }}>
                              <ResponsiveContainer>
                                {ChartComponent}
                              </ResponsiveContainer>
                            </div>
                            {/* provider/model metadata */}
                            {message.role === "assistant" && (message.model || message.provider) && (
                              <div className="mt-2 pt-2 border-t border-border/40 flex gap-2 items-center opacity-70">
                                {message.provider && (
                                  <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                                    {message.provider === "azure openai" ? "Azure OpenAI" : 
                                     message.provider === "awsbedrock" ? "AWS Bedrock" : 
                                     message.provider}
                                  </span>
                                )}
                                {message.model && (
                                  <Badge variant="outline" className="text-[10px] h-4 px-1.5 py-0 font-normal border-border/60 bg-background/50 text-muted-foreground shadow-none">
                                      {message.model}
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      }
                    } catch (e) {
                      // not JSON or not a chart, fall through to markdown
                    }

                    return (
                      <div>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm, remarkMath]}
                          rehypePlugins={[rehypeKatex]}
                          components={{
                            // Paragraph spacing
                            p: ({ children }) => (
                              <p className="mb-3 last:mb-0">{children}</p>
                            ),

                            // Code blocks
                            code: ({ inline, className, children }) => {
                              if (inline) {
                                return (
                                  <code className={cn(
                                    "px-1.5 py-0.5 rounded text-xs font-mono",
                                    message.role === "user" ? "bg-white/20 text-white" : "bg-muted text-foreground"
                                  )}>
                                    {children}
                                  </code>
                                )
                              }
                              return (
                                <pre className="bg-slate-950 text-slate-50 p-4 rounded-xl overflow-x-auto text-xs my-3 shadow-inner">
                                  <code>{children}</code>
                                </pre>
                              )
                            },

                            // Tables
                            table: ({ children }) => (
                              <div className="overflow-hidden my-3 rounded-lg border border-border/50">
                                <table className="w-full border-collapse text-xs">
                                  {children}
                                </table>
                              </div>
                            ),
                            th: ({ children }) => (
                              <th className="border-b border-r last:border-r-0 border-border/50 px-3 py-2 bg-muted/50 font-semibold text-left">
                                {children}
                              </th>
                            ),
                            td: ({ children }) => (
                              <td className="border-b last:border-b-0 border-r last:border-r-0 border-border/50 px-3 py-2 bg-card/30">{children}</td>
                            ),

                            // Lists
                            li: ({ children }) => (
                              <li className="ml-4 list-disc marker:text-muted-foreground">{children}</li>
                            ),
                          }}
                        >
                          {message.content || ""}
                        </ReactMarkdown>
                        {message.role === "assistant" && (message.model || message.provider) && (
                          <div className="mt-2 pt-2 border-t border-border/40 flex gap-2 items-center opacity-70">
                            {message.provider && (
                              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                                {message.provider === "azure openai" ? "Azure OpenAI" : 
                                 message.provider === "awsbedrock" ? "AWS Bedrock" : 
                                 message.provider}
                              </span>
                            )}
                            {message.model && (
                              <Badge variant="outline" className="text-[10px] h-4 px-1.5 py-0 font-normal border-border/60 bg-background/50 text-muted-foreground shadow-none">
                                  {message.model}
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                    )
                  })()}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      ))}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default ConversationWindow