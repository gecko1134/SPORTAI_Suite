"use client";
/**
 * SportAI Suite — Facility Layout Optimizer
 * /app/layout-ai/page.tsx · Sprint 7
 * Tabs: Heatmap · Scenarios · Revenue/sqft · AI Recommendations
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Map, Layers, BarChart2, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const layoutApi = {
  zones:     (p?) => fetch(`${API}/api/layout-ai/zones${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  heatmap:   () => fetch(`${API}/api/layout-ai/utilization-heatmap`).then(r => r.json()),
  revSqft:   () => fetch(`${API}/api/layout-ai/revenue-per-sqft`).then(r => r.json()),
  scenarios: () => fetch(`${API}/api/layout-ai/scenarios`).then(r => r.json()),
  seed:      () => fetch(`${API}/api/layout-ai/seed`, { method: "POST" }).then(r => r.json()),
  aiOptimize:() => fetch(`${API}/api/layout-ai/ai-optimize`, { method: "POST" }).then(r => r.json()),
  aiCompare: (a: string, b: string) => fetch(`${API}/api/layout-ai/ai-scenario-compare?scenario_a_id=${a}&scenario_b_id=${b}`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const AREA_COLORS: Record<string, string> = {
  large_dome: "#60A5FA", small_dome: "#A855F7", health_center: "#22C55E",
  rink: "#60A5FA", outdoor: "#4ade80", hotel: GOLD, campground: "#F97316", parking: "#6B7280",
};
const UTIL_COLOR = (u: number) => u >= 75 ? "#22C55E" : u >= 50 ? GOLD : u >= 30 ? "#F97316" : "#EF4444";

function HeatmapTab({ onSeed }: { onSeed: () => void }) {
  const { data: heatmap } = useQuery({ queryKey: ["layout-heatmap"], queryFn: layoutApi.heatmap });
  const [selectedArea, setSelectedArea] = useState<string | null>(null);

  if (!heatmap) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Map size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Layout Optimizer not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Facility Zones</button>
    </div>
  );

  const hours = Array.from({ length: 17 }, (_, i) => `${i + 6}:00`);
  const zones = Object.entries(heatmap.heatmap);
  const filteredZones = selectedArea ? zones.filter(([, v]: [string, any]) => v.area === selectedArea) : zones;

  const areas = [...new Set(zones.map(([, v]: [string, any]) => (v as any).area))];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Area summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        {Object.entries(heatmap.area_summary).map(([area, data]: [string, any]) => {
          const ac = AREA_COLORS[area] ?? GOLD;
          return (
            <div key={area} onClick={() => setSelectedArea(selectedArea === area ? null : area)}
              style={{ background: selectedArea === area ? `${ac}15` : "#0f2744", border: `1px solid ${selectedArea === area ? ac : "rgba(201,168,76,0.12)"}`, borderRadius: 8, padding: "12px 14px", cursor: "pointer", transition: "all 0.15s" }}>
              <p style={{ fontSize: 12, color: ac, fontWeight: 700, marginBottom: 6 }}>{lbl(area)}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: UTIL_COLOR(data.avg_utilization_pct) }}>{data.avg_utilization_pct}%</p>
              <p style={{ fontSize: 11, color: "#8aa0bb" }}>${data.avg_revenue_per_sqft}/sqft</p>
              <p style={{ fontSize: 10, color: "#4a6080" }}>{data.total_sqft.toLocaleString()} sqft</p>
            </div>
          );
        })}
      </div>

      {/* Heatmap grid */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px", overflowX: "auto" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>
          UTILIZATION HEATMAP{selectedArea ? ` — ${lbl(selectedArea)}` : " — ALL ZONES"}
        </p>
        <div style={{ minWidth: 700 }}>
          {/* Hour labels */}
          <div style={{ display: "grid", gridTemplateColumns: `160px repeat(17, 1fr)`, gap: 2, marginBottom: 4 }}>
            <div />
            {hours.map(h => <div key={h} style={{ fontSize: 9, color: "#4a6080", textAlign: "center" }}>{h}</div>)}
          </div>
          {/* Zone rows */}
          {(filteredZones as [string, any][]).slice(0, 14).map(([zoneId, zoneData]) => (
            <div key={zoneId} style={{ display: "grid", gridTemplateColumns: `160px repeat(17, 1fr)`, gap: 2, marginBottom: 2 }}>
              <div style={{ fontSize: 11, color: "#8aa0bb", display: "flex", alignItems: "center", paddingRight: 8, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {zoneData.name.replace("Large Dome — ", "").replace("Small Dome — ", "SD: ").replace("Health Center — ", "HC: ")}
              </div>
              {(zoneData.utilization as number[]).map((u: number, hi: number) => {
                const intensity = u / 100;
                const bg = u >= 70 ? `rgba(34,197,94,${0.3 + intensity * 0.5})`
                         : u >= 45 ? `rgba(201,168,76,${0.3 + intensity * 0.4})`
                         : `rgba(239,68,68,${0.1 + intensity * 0.2})`;
                return (
                  <div key={hi} style={{ height: 22, background: bg, borderRadius: 2 }} title={`${zoneData.name} ${hours[hi]}: ${u}%`} />
                );
              })}
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 12, marginTop: 12, fontSize: 11 }}>
          {[["#22C55E30","High (70%+)"],["rgba(201,168,76,0.4)","Mid (45–70%)"],["rgba(239,68,68,0.2)","Low (<45%)"]].map(([color, label]) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 18, height: 14, background: color, borderRadius: 2 }} />
              <span style={{ color: "#8aa0bb" }}>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ScenariosTab() {
  const { data: scenarios = [] } = useQuery({ queryKey: ["layout-scenarios"], queryFn: layoutApi.scenarios });
  const [selectedA, setSelectedA] = useState<string>("");
  const [selectedB, setSelectedB] = useState<string>("");
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runCompare = async () => {
    if (!selectedA || !selectedB) return;
    setLoading(true); setComparison(null);
    setComparison(await layoutApi.aiCompare(selectedA, selectedB));
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 14 }}>
        {(scenarios as any[]).map((s: any) => {
          const isRecommended = s.status === "recommended";
          const roi = s.implementation_cost > 0 ? Math.round(s.projected_revenue_change / s.implementation_cost * 100) : 0;
          return (
            <div key={s.id} style={{ background: isRecommended ? "rgba(201,168,76,0.06)" : "#0f2744", border: `1px solid ${isRecommended ? GOLD : "rgba(201,168,76,0.12)"}`, borderRadius: 10, padding: "16px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                <div style={{ flex: 1 }}>
                  {isRecommended && <span style={{ fontSize: 10, fontWeight: 700, color: GOLD, background: "rgba(201,168,76,0.15)", border: "1px solid rgba(201,168,76,0.3)", borderRadius: 3, padding: "1px 7px", marginBottom: 6, display: "inline-block" }}>★ RECOMMENDED</span>}
                  <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 4 }}>{s.name}</p>
                  <p style={{ fontSize: 12, color: "#8aa0bb", marginBottom: 8 }}>{s.description}</p>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 10 }}>
                <div style={{ background: "#152f52", borderRadius: 5, padding: "6px 10px" }}>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>Revenue Gain</p>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#22C55E" }}>{fmt(s.projected_revenue_change)}</p>
                </div>
                <div style={{ background: "#152f52", borderRadius: 5, padding: "6px 10px" }}>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>Cost</p>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#F97316" }}>{fmt(s.implementation_cost)}</p>
                </div>
                <div style={{ background: "#152f52", borderRadius: 5, padding: "6px 10px" }}>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>Payback</p>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{s.payback_months}mo</p>
                </div>
              </div>
              <div style={{ fontSize: 11, color: "#22C55E", marginBottom: 3 }}>✓ {s.pros}</div>
              <div style={{ fontSize: 11, color: "#F97316", marginBottom: 8 }}>✗ {s.cons}</div>
              <div style={{ display: "flex", gap: 6 }}>
                <button onClick={() => setSelectedA(s.id)} style={{ flex: 1, background: selectedA === s.id ? "#60A5FA" : "#152f52", color: selectedA === s.id ? "#071828" : "#8aa0bb", border: "none", borderRadius: 5, padding: "5px", fontSize: 11, cursor: "pointer", fontWeight: 700 }}>Compare A</button>
                <button onClick={() => setSelectedB(s.id)} style={{ flex: 1, background: selectedB === s.id ? "#22C55E" : "#152f52", color: selectedB === s.id ? "#071828" : "#8aa0bb", border: "none", borderRadius: 5, padding: "5px", fontSize: 11, cursor: "pointer", fontWeight: 700 }}>Compare B</button>
              </div>
            </div>
          );
        })}
      </div>

      {selectedA && selectedB && (
        <div>
          <button onClick={runCompare} disabled={loading || selectedA === selectedB} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Comparing…</> : <><Brain size={14} />Run AI Comparison</>}
          </button>
          {comparison && (
            <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
              <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>AI SCENARIO COMPARISON</p>
              <p style={{ fontSize: 12, color: "#22C55E", marginBottom: 10 }}>Winner by ROI: <strong>{comparison.winner_by_roi}</strong></p>
              <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{comparison.comparison}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function RevSqftTab() {
  const { data: rev } = useQuery({ queryKey: ["layout-rev-sqft"], queryFn: layoutApi.revSqft });
  if (!rev) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  const maxRev = Math.max(...(rev.zone_rankings as any[]).map((z: any) => z.revenue_per_sqft), 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        {[
          { l: "Avg Revenue/sqft", v: `$${rev.avg_revenue_per_sqft_annual}/yr`, c: GOLD },
          { l: "Total Est. Revenue", v: fmt(rev.total_estimated_annual_revenue), c: "#22C55E" },
          { l: "Zones Tracked", v: (rev.zone_rankings as any[]).length, c: "#60A5FA" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "14px 16px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 26, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {[
          { label: "TOP PERFORMERS ($/sqft)", zones: rev.top_performers, color: "#22C55E" },
          { label: "UNDER PERFORMERS ($/sqft)", zones: rev.under_performers, color: "#EF4444" },
        ].map(panel => (
          <div key={panel.label} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 18px" }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, letterSpacing: 1, color: panel.color, marginBottom: 12 }}>{panel.label}</p>
            {panel.zones.map((z: any) => (
              <div key={z.zone_id} style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#F0F4FA", marginBottom: 3 }}>
                  <span>{z.name.replace("Large Dome — ", "LD: ").replace("Small Dome — ", "SD: ").replace("Health Center — ", "HC: ")}</span>
                  <span style={{ color: panel.color, fontWeight: 700 }}>${z.revenue_per_sqft}/sqft</span>
                </div>
                <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                  <div style={{ height: "100%", width: `${Math.min((z.revenue_per_sqft / maxRev) * 100, 100)}%`, background: panel.color, borderRadius: 2 }} />
                </div>
                <p style={{ fontSize: 10, color: "#4a6080", marginTop: 2 }}>{z.sqft.toLocaleString()} sqft · {z.utilization_pct}% utilized · {fmt(z.annual_revenue_est || (z.sqft * z.revenue_per_sqft))} est/yr</p>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Full rankings */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 20px", overflowX: "auto" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>ALL ZONES — REVENUE EFFICIENCY RANKING</p>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["#","Zone","Area","sqft","Rev/sqft","Utilization"].map(h => (
                <th key={h} style={{ padding: "6px 10px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(rev.zone_rankings as any[]).map((z: any, i: number) => {
              const ac = AREA_COLORS[z.area] ?? GOLD;
              return (
                <tr key={z.zone_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "7px 10px", fontSize: 12, color: "#4a6080", fontWeight: 700 }}>#{i + 1}</td>
                  <td style={{ padding: "7px 10px", fontSize: 12, color: "#F0F4FA" }}>{z.name.replace("Large Dome — ", "LD: ").replace("Small Dome — ", "SD: ").replace("Health Center — ", "HC: ")}</td>
                  <td style={{ padding: "7px 10px" }}><span style={{ fontSize: 10, color: ac, background: `${ac}15`, borderRadius: 3, padding: "1px 6px" }}>{lbl(z.area)}</span></td>
                  <td style={{ padding: "7px 10px", fontSize: 12, color: "#8aa0bb" }}>{z.sqft.toLocaleString()}</td>
                  <td style={{ padding: "7px 10px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>${z.revenue_per_sqft}</td>
                  <td style={{ padding: "7px 10px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <div style={{ width: 50, height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                        <div style={{ height: "100%", width: `${z.utilization_pct}%`, background: UTIL_COLOR(z.utilization_pct), borderRadius: 2 }} />
                      </div>
                      <span style={{ fontSize: 11, color: UTIL_COLOR(z.utilization_pct) }}>{z.utilization_pct}%</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AIRecommendationsTab() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button onClick={async () => { setLoading(true); setResult(await layoutApi.aiOptimize()); setLoading(false); }} disabled={loading}
          style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Optimizing…</> : <><Brain size={14} />Generate Layout Optimization</>}
        </button>
      </div>
      {result ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>AI FACILITY OPTIMIZATION</p>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{result.optimization}</p>
          </div>
          {result.top_scenario && (
            <div style={{ background: "rgba(201,168,76,0.06)", border: "1px solid rgba(201,168,76,0.25)", borderRadius: 8, padding: "14px 18px" }}>
              <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>TOP RECOMMENDED SCENARIO</p>
              <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA" }}>{result.top_scenario.name}</p>
              <p style={{ fontSize: 12, color: "#8aa0bb", margin: "4px 0" }}>{result.top_scenario.description}</p>
              <div style={{ display: "flex", gap: 16, fontSize: 12 }}>
                <span style={{ color: "#22C55E" }}>+{fmt(result.top_scenario.projected_revenue_change)}/yr</span>
                <span style={{ color: "#F97316" }}>Cost: {fmt(result.top_scenario.implementation_cost)}</span>
                <span style={{ color: GOLD }}>Payback: {result.top_scenario.payback_months}mo</span>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
          <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ fontSize: 14, color: "#8aa0bb" }}>Generate AI layout optimization across all campus zones</p>
          <p style={{ fontSize: 12, color: "#4a6080", marginTop: 4 }}>Dark zone analysis · Revenue/sqft gaps · Configuration sequencing</p>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id: "heatmap",    label: "Heatmap",      icon: <Map size={14} /> },
  { id: "scenarios",  label: "Scenarios",    icon: <Layers size={14} /> },
  { id: "revsqft",    label: "Revenue/sqft", icon: <BarChart2 size={14} /> },
  { id: "ai",         label: "AI Optimize",  icon: <Brain size={14} /> },
];

export default function LayoutAIPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("heatmap");
  const [seeding, setSeeding] = useState(false);
  const { data: rev } = useQuery({ queryKey: ["layout-rev-sqft"], queryFn: layoutApi.revSqft });

  const handleSeed = async () => {
    setSeeding(true);
    await layoutApi.seed();
    ["layout-heatmap","layout-scenarios","layout-rev-sqft"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["223,500 INDOOR SQFT","19 ZONES MAPPED","4 SCENARIOS","REVENUE/SQFT RANKING"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>FACILITY LAYOUT OPTIMIZER</h1>
          {rev && <span style={{ fontSize: 13, color: "#8aa0bb", marginBottom: 6 }}>Avg: <strong style={{ color: GOLD }}>${rev.avg_revenue_per_sqft_annual}/sqft</strong> · Est: <strong style={{ color: "#22C55E" }}>{fmt(rev.total_estimated_annual_revenue)}/yr</strong></span>}
        </div>
        <div style={{ display: "flex", gap: 0 }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{ background: "none", border: "none", cursor: "pointer", padding: "10px 18px", fontSize: 13, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", fontFamily: "'Barlow Condensed'", color: activeTab === t.id ? GOLD : "#8aa0bb", borderBottom: activeTab === t.id ? `2px solid ${GOLD}` : "2px solid transparent", display: "flex", alignItems: "center", gap: 6 }}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </div>
      <div style={{ padding: "24px 28px" }}>
        {activeTab === "heatmap"   && <HeatmapTab onSeed={handleSeed} />}
        {activeTab === "scenarios" && <ScenariosTab />}
        {activeTab === "revsqft"   && <RevSqftTab />}
        {activeTab === "ai"        && <AIRecommendationsTab />}
      </div>
    </div>
  );
}
