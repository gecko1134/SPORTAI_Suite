"use client";
/**
 * SportAI Suite — PuttView AR Analytics
 * /app/puttview/page.tsx · Sprint 4 · NGP Development
 * EXCLUSIVE within 200 miles · $280K · $153K/yr · 137% ROI
 * Tabs: Sessions · ROI Dashboard · Exclusivity · AI Optimization
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Crosshair, TrendingUp, Shield, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const pvApi = {
  kpis:         () => fetch(`${API}/api/puttview/kpis`).then(r => r.json()),
  sessions:     (p?) => fetch(`${API}/api/puttview/sessions${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  ledger:       () => fetch(`${API}/api/puttview/revenue-ledger`).then(r => r.json()),
  roi:          () => fetch(`${API}/api/puttview/roi-dashboard`).then(r => r.json()),
  exclusivity:  () => fetch(`${API}/api/puttview/exclusivity-radius`).then(r => r.json()),
  seed:         () => fetch(`${API}/api/puttview/seed`, { method: "POST" }).then(r => r.json()),
  aiOptimize:   () => fetch(`${API}/api/puttview/ai-optimization`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const MODE_COLORS: Record<string, string> = {
  open_play: "#60A5FA", lesson: GOLD, league: "#A855F7",
  corporate: "#F97316", event: "#22C55E", tournament: "#EF4444",
};

function ROIGauge({ current, target }: { current: number; target: number }) {
  const clamped = Math.min(Math.max(current, -50), 200);
  const pct = (clamped + 50) / 250;
  const r = 64; const circ = 2 * Math.PI * r;
  const color = current >= target ? "#22C55E" : current >= 0 ? GOLD : "#EF4444";
  return (
    <div style={{ textAlign: "center" }}>
      <svg width={160} height={160} viewBox="0 0 160 160">
        <circle cx={80} cy={80} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={14} />
        <circle cx={80} cy={80} r={r} fill="none" stroke="#22C55E30" strokeWidth={14}
          strokeDasharray={circ} strokeDashoffset={circ - (target / 200) * circ}
          transform="rotate(-90 80 80)" />
        <circle cx={80} cy={80} r={r} fill="none" stroke={color} strokeWidth={14}
          strokeDasharray={circ} strokeDashoffset={circ - pct * circ}
          strokeLinecap="round" transform="rotate(-90 80 80)" style={{ transition: "stroke-dashoffset 0.8s" }} />
        <text x={80} y={74} textAnchor="middle" fill="#F0F4FA" fontSize={26} fontFamily="'Bebas Neue'" letterSpacing={1}>{current}%</text>
        <text x={80} y={92} textAnchor="middle" fill={color} fontSize={11} fontFamily="'Barlow Condensed'" fontWeight={700}>CURRENT ROI</text>
        <text x={80} y={105} textAnchor="middle" fill="#4a6080" fontSize={10} fontFamily="'Barlow Condensed'">TARGET: {target}%</text>
      </svg>
    </div>
  );
}

function SessionsTab({ onSeed }: { onSeed: () => void }) {
  const [modeFilter, setModeFilter] = useState("");
  const params: Record<string, string> = { days_back: "90" };
  if (modeFilter) params.session_mode = modeFilter;
  const { data: sessions = [] } = useQuery({ queryKey: ["pv-sessions", modeFilter], queryFn: () => pvApi.sessions(params) });
  const MODES = ["open_play","lesson","league","corporate","event","tournament"];

  if (!sessions.length && !modeFilter) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Crosshair size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>PuttView AR not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed PuttView Data</button>
    </div>
  );

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        <button onClick={() => setModeFilter("")} style={{ background: !modeFilter ? GOLD : "#0f2744", color: !modeFilter ? NAVY : "#8aa0bb", border: `1px solid ${!modeFilter ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>All</button>
        {MODES.map(m => {
          const tc = MODE_COLORS[m] ?? GOLD;
          return (
            <button key={m} onClick={() => setModeFilter(m)} style={{ background: modeFilter === m ? tc : "#0f2744", color: modeFilter === m ? "#071828" : "#8aa0bb", border: `1px solid ${modeFilter === m ? tc : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{lbl(m)}</button>
          );
        })}
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Bay","Mode","Guest","Date","Duration","Guests","Revenue","Make %"].map(h => (
                <th key={h} style={{ padding: "8px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(sessions as any[]).slice(0, 50).map((s: any) => {
              const mc = MODE_COLORS[s.session_mode] ?? GOLD;
              return (
                <tr key={s.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "8px 12px", fontSize: 13, color: "#F0F4FA", fontWeight: 700 }}>#{s.bay_number}</td>
                  <td style={{ padding: "8px 12px" }}><span style={{ fontSize: 10, fontWeight: 700, color: mc, background: `${mc}15`, border: `1px solid ${mc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.session_mode)}</span></td>
                  <td style={{ padding: "8px 12px", fontSize: 12, color: "#F0F4FA" }}>{s.guest_name}</td>
                  <td style={{ padding: "8px 12px", fontSize: 12, color: "#8aa0bb" }}>{s.session_date}</td>
                  <td style={{ padding: "8px 12px", fontSize: 12, color: "#8aa0bb" }}>{s.duration_minutes}min</td>
                  <td style={{ padding: "8px 12px", fontSize: 12, color: "#F0F4FA" }}>{s.guest_count}</td>
                  <td style={{ padding: "8px 12px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>${s.revenue}</td>
                  <td style={{ padding: "8px 12px", fontSize: 12, color: s.make_pct ? "#22C55E" : "#4a6080" }}>{s.make_pct ? `${s.make_pct}%` : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ROIDashboardTab() {
  const { data: roi } = useQuery({ queryKey: ["pv-roi"], queryFn: pvApi.roi });
  const { data: ledger = [] } = useQuery({ queryKey: ["pv-ledger"], queryFn: pvApi.ledger });

  if (!roi) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;
  const maxRev = Math.max(...(ledger as any[]).map((l: any) => l.revenue), 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ background: "#0f2744", border: `1px solid ${GOLD}40`, borderRadius: 10, padding: "24px 28px", display: "grid", gridTemplateColumns: "auto 1fr", gap: 24, alignItems: "start" }}>
        <ROIGauge current={roi.current_roi_pct} target={137} />
        <div>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 13, color: "#4a6080", letterSpacing: 2, marginBottom: 8 }}>INVESTMENT: $280K · TARGET ROI: 137%</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              { l: "Total Revenue",       v: fmt(roi.total_revenue),        c: GOLD },
              { l: "Annualized",          v: fmt(roi.annualized_revenue),   c: "#22C55E" },
              { l: "Annual Target",       v: fmt(roi.annual_revenue_target), c: "#4a6080" },
              { l: "Pacing",             v: `${roi.annual_pacing_pct}%`,   c: roi.annual_pacing_pct >= 80 ? "#22C55E" : "#F97316" },
              { l: "Sessions/Day",        v: roi.sessions_per_day,          c: "#60A5FA" },
              { l: "Avg Rev/Session",     v: `$${roi.avg_revenue_per_session}`, c: GOLD },
              { l: "Net Return",          v: fmt(roi.net_return),            c: roi.net_return >= 0 ? "#22C55E" : "#EF4444" },
              { l: "On Track",            v: roi.on_track_for_target ? "✓ YES" : "⚠ NEEDS ↑", c: roi.on_track_for_target ? "#22C55E" : "#F97316" },
            ].map(s => (
              <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "8px 12px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Session mode breakdown */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>SESSION MIX BREAKDOWN</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10 }}>
          {Object.entries(roi.mode_breakdown).map(([mode, data]: [string, any]) => {
            const tc = MODE_COLORS[mode] ?? GOLD;
            return (
              <div key={mode} style={{ background: `${tc}08`, border: `1px solid ${tc}30`, borderRadius: 7, padding: "10px 12px" }}>
                <p style={{ fontSize: 11, color: tc, fontWeight: 700, marginBottom: 4 }}>{lbl(mode)}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F0F4FA" }}>{data.sessions}</p>
                <p style={{ fontSize: 12, color: GOLD }}>{fmt(data.revenue)}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Monthly ledger bars */}
      {(ledger as any[]).length > 0 && (
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>MONTHLY REVENUE VS TARGET</p>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 16, height: 100 }}>
            {(ledger as any[]).map((l: any) => {
              const barH = Math.round((l.revenue / maxRev) * 85);
              const tgtH = Math.round((l.target_monthly / maxRev) * 85);
              const color = l.revenue >= l.target_monthly ? "#22C55E" : GOLD;
              return (
                <div key={l.month} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                  <div style={{ width: "100%", position: "relative", height: 85 }}>
                    <div style={{ position: "absolute", bottom: 0, left: "15%", right: "15%", background: "rgba(201,168,76,0.15)", borderRadius: "2px 2px 0 0", height: `${tgtH}%` }} title="Target" />
                    <div style={{ position: "absolute", bottom: 0, left: "30%", right: "30%", background: color, borderRadius: "2px 2px 0 0", height: `${barH}%`, transition: "height 0.4s" }} title={`$${l.revenue}`} />
                  </div>
                  <p style={{ fontSize: 10, color: "#8aa0bb", transform: "rotate(-30deg)", whiteSpace: "nowrap" }}>{l.month.slice(5)}/{l.month.slice(2,4)}</p>
                  <p style={{ fontSize: 10, color: color }}>{l.pacing_pct}%</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function ExclusivityTab() {
  const { data: excl } = useQuery({ queryKey: ["pv-exclusivity"], queryFn: pvApi.exclusivity });
  if (!excl) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 10, padding: "20px 24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <Shield size={20} style={{ color: "#22C55E" }} />
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, letterSpacing: 1, color: "#22C55E" }}>EXCLUSIVITY STATUS: {excl.exclusivity_status}</p>
        </div>
        <p style={{ fontSize: 14, color: "#d0dce8", lineHeight: 1.6 }}>{excl.zone_summary}</p>
        <div style={{ display: "flex", gap: 20, marginTop: 12 }}>
          {[
            { l: "Exclusivity Radius", v: `${excl.exclusivity_radius_miles} miles`, c: "#22C55E" },
            { l: "Competitors in Zone", v: excl.competitors_within_zone.length, c: "#F97316" },
            { l: "Zone AR Competitors", v: 0, c: "#22C55E" },
            { l: "Closest AR (outside)", v: `${excl.closest_ar_competitor_miles} mi`, c: GOLD },
            { l: "Threat Level",        v: excl.zone_threat_level, c: "#22C55E" },
          ].map(s => (
            <div key={s.l}>
              <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>{s.l}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>COMPETITOR MAP — {excl.exclusivity_radius_miles}-MILE ZONE</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {/* NXS anchor */}
          <div style={{ background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 7, padding: "10px 14px", display: "flex", justifyContent: "space-between" }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span style={{ fontSize: 16 }}>🏆</span>
              <div>
                <p style={{ fontWeight: 700, fontSize: 13, color: "#22C55E" }}>NXS National Complex — PuttView AR</p>
                <p style={{ fontSize: 11, color: "#8aa0bb" }}>Proctor, MN · EXCLUSIVE within 200 miles</p>
              </div>
            </div>
            <span style={{ fontSize: 11, fontWeight: 700, color: "#22C55E", background: "rgba(34,197,94,0.15)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 3, padding: "2px 8px", height: "fit-content" }}>HOME</span>
          </div>

          {excl.competitors_within_zone.map((c: any) => (
            <div key={c.name} style={{ background: "#0f2744", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 7, padding: "10px 14px", display: "flex", justifyContent: "space-between" }}>
              <div>
                <p style={{ fontWeight: 600, fontSize: 13, color: "#F0F4FA" }}>{c.name}</p>
                <p style={{ fontSize: 11, color: "#8aa0bb" }}>{c.city}, {c.state} · {c.distance_miles} miles</p>
              </div>
              <span style={{ fontSize: 10, fontWeight: 700, color: "#22C55E", background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 3, padding: "1px 6px", height: "fit-content" }}>NO AR</span>
            </div>
          ))}

          {excl.competitors_outside_zone.map((c: any) => (
            <div key={c.name} style={{ background: "#0f2744", border: "1px solid rgba(255,255,255,0.04)", borderRadius: 7, padding: "10px 14px", display: "flex", justifyContent: "space-between", opacity: 0.6 }}>
              <div>
                <p style={{ fontWeight: 600, fontSize: 12, color: "#F0F4FA" }}>{c.name}</p>
                <p style={{ fontSize: 11, color: "#8aa0bb" }}>{c.city}, {c.state} · {c.distance_miles} mi · outside zone</p>
              </div>
              {c.has_ar && <span style={{ fontSize: 10, color: GOLD }}>HAS AR</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AIOptimizationTab() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true); setResult(null);
    setResult(await pvApi.aiOptimize());
    setLoading(false);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button onClick={generate} disabled={loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={14} />Generate Optimization Brief</>}
        </button>
      </div>
      {result ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>AI REVENUE OPTIMIZATION</p>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{result.optimization}</p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10 }}>
            {[
              { l: "Current ROI",       v: `${result.roi_snapshot.current_roi_pct}%`,    c: result.roi_snapshot.current_roi_pct >= 137 ? "#22C55E" : GOLD },
              { l: "Projected ROI",     v: `${result.roi_snapshot.projected_annual_roi_pct}%`, c: GOLD },
              { l: "Sessions/Day",      v: result.roi_snapshot.sessions_per_day,          c: "#60A5FA" },
              { l: "Avg Rev/Session",   v: `$${result.roi_snapshot.avg_revenue_per_session}`, c: "#F0F4FA" },
            ].map(s => (
              <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 7, padding: "10px 14px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
          <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ fontSize: 14, color: "#8aa0bb" }}>Generate AI revenue optimization for PuttView AR</p>
          <p style={{ fontSize: 12, color: "#4a6080", marginTop: 4 }}>ROI trajectory · Session mix · Exclusivity monetization</p>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id: "sessions",     label: "Sessions",      icon: <Crosshair size={14} /> },
  { id: "roi",          label: "ROI Dashboard", icon: <TrendingUp size={14} /> },
  { id: "exclusivity",  label: "Exclusivity",   icon: <Shield size={14} /> },
  { id: "ai",           label: "AI Optimize",   icon: <Brain size={14} /> },
];

export default function PuttViewPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("roi");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery({ queryKey: ["pv-kpis"], queryFn: pvApi.kpis });

  const handleSeed = async () => {
    setSeeding(true);
    await pvApi.seed();
    ["pv-kpis","pv-sessions","pv-roi","pv-ledger"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NGP DEVELOPMENT","EXCLUSIVE — 200 MILES","$280K INVESTMENT","137% ROI TARGET"].map((l, i) => (
            <div key={l} style={{ background: i === 1 ? "rgba(34,197,94,0.15)" : "rgba(201,168,76,0.12)", border: i === 1 ? "1px solid rgba(34,197,94,0.3)" : "none", borderRadius: 3, padding: "1px 8px" }}>
              <span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: i === 1 ? "#22C55E" : GOLD, letterSpacing: 2 }}>{l}</span>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>PUTTVIEW AR ANALYTICS</h1>
          {kpis && (
            <div style={{ display: "flex", gap: 16, marginBottom: 6, alignItems: "center", flexWrap: "wrap" }}>
              <span style={{ fontSize: 13, color: "#8aa0bb" }}>ROI: <strong style={{ color: kpis.current_roi_pct >= 137 ? "#22C55E" : GOLD }}>{kpis.current_roi_pct}%</strong></span>
              <span style={{ fontSize: 13, color: "#8aa0bb" }}>Pacing: <strong style={{ color: GOLD }}>{kpis.annual_pacing_pct}%</strong></span>
              <span style={{ fontSize: 13, color: "#8aa0bb" }}>Zone: <strong style={{ color: "#22C55E" }}>{kpis.exclusivity_status}</strong></span>
            </div>
          )}
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
        {activeTab === "sessions"    && <SessionsTab onSeed={handleSeed} />}
        {activeTab === "roi"         && <ROIDashboardTab />}
        {activeTab === "exclusivity" && <ExclusivityTab />}
        {activeTab === "ai"          && <AIOptimizationTab />}
      </div>
    </div>
  );
}
