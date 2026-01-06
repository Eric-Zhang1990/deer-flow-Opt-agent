/*
 * @Author: caixuefei caixuefei@enn.cn
 * @Date: 2025-07-25 19:18:13
 * @LastEditors: caixuefei caixuefei@enn.cn
 * @LastEditTime: 2025-07-25 19:30:26
 * @FilePath: /deer-flow/web/src/components/deer-flow/echarts-view.tsx
 */
import React, { useEffect, useRef } from "react";
import ReactECharts from "echarts-for-react";

export function EChartsView({ option }: { option: any }) {
  const chartRef = useRef<ReactECharts>(null);

  useEffect(() => {
    const handleResize = () => {
      chartRef.current?.getEchartsInstance().resize();
    };

    // 监听窗口大小变化
    window.addEventListener("resize", handleResize);
    
    // 组件卸载时移除事件监听
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  useEffect(() => {
    // 当 option 更新时，调用 resize
    chartRef.current?.getEchartsInstance().resize();
  }, [option]);

  if (!option) return null;
  return (
    <div style={{ width: "100%", minHeight: 320, margin: "24px 0" }}>
      <ReactECharts ref={chartRef} option={option} style={{ height: 320, width: "100%" }} />
    </div>
  );
} 