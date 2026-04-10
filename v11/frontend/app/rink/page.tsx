"use client";
/**
 * SportAI Suite — Ice Rink Module
 * /app/rink/page.tsx · Sprint 5 · NXS National Complex
 * Tabs: Schedule · Leagues · Revenue · AI Optimizer
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, Users, TrendingUp, Brain, RefreshCw, Snowflake, Grid3x3 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const rinkApi = {
  schedule:     (p?) => fetch(`${API}/api/rink/schedule${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  leagues:      () => fetch(`${API}/api/rink/leagues`).then(r => r.json()),
  utilization:  () => fetch(`${API}/api/rink/utilization`).then(r => r.json()),
  conversions:  () => fetch(`${API}/api/rink/conversion-log`).then(r => r.json()),
  seed:         () => fetch(`${API}/api/rink/seed`, { method: "POST" }).then(r => r.json()),
  aiOptimizer:  () => fetch(`${API}/api/rink/ai-optimizer`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const CAT_COLORS: Record<string, string> = {
  hockey_prime: "#60A5FA", hockey_off: "#3b82f680", figure_skating: "#A855F7",
  open_skate: "#22C55E", learn_to_skate: "#4ade80", league_block: GOLD,
  tournament: "#EF4444", turf_prime: "#F97316", turf_off: "#f9731660", maintenance: "#6B7280", dark: "#374151",
};

const SURFACE_ICON = { ice: "🧊", turf: "🟩" };

function ScheduleTab({ onSeed }: { onSeed: () => void }) {
  const today = new Date().toISOString().split("T")[0];
  const futureDate = new Date(Date.now() + 14 * 86400000).toISOString().split("T")[0];
  const { data: sessions = [] } = useQuery({
    queryKey: ["rink-schedule"], queryFn: () => rinkApi.schedule({ from_date: today, to_date: futureDate })
  });

  const grouped = (sessions as any[]).reduce((acc: Record<string, any[]>, s: any) => {
    acc[s.session_date] = [...(acc[s.session_date] || []), s];
    return acc;
  }, {});

  if (!sessions.length) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Snowflake size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Rink not seeded yet</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Ice Rink</button>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {Object.entries(grouped).map(([dateStr, daySessions]) => {
        const d = new Date(dateStr + "T12:00:00");
        const label = d.toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });
        const dayRev = (daySessions as any[]).reduce((s: number, ses: any) => s + ses.revenue, 0);
        return (
          <div key={dateStr} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 10, overflow: "hidden" }}>
            <div style={{ background: "#152f52", padding: "10px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, letterSpacing: 1, color: "#F0F4FA" }}>{label}</p>
              <span style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{fmt(dayRev)}</span>
            </div>
            <div style={{ padding: "8px 12px", display: "flex", flexDirection: "column", gap: 6 }}>
              {(daySessions as any[]).sort((a: any, b: any) => a.start_time.localeCompare(b.start_time)).map((s: any) => {
                const cc = CAT_COLORS[s.category] ?? GOLD;
                return (
                  <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", background: `${cc}10`, borderRadius: 6, borderLeft: `3px solid ${cc}` }}>
                    <span style={{ fontSize: 14 }}>{(SURFACE_ICON as any)[s.surface]}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA" }}>{s.title}</p>
                        <p style={{ fontSize: 13, fontFamily: "'Bebas Neue'", color: GOLD }}>{fmt(s.revenue)}</p>
                      </div>
                      <div style={{ display: "flex", gap: 12, fontSize: 11, color: "#8aa0bb" }}>
                        <span>{s.start_time}–{s.end_time}</span>
                        <span style={{ color: cc }}>{lbl(s.category)}</span>
                        {s.attendees && <span>👥 {s.attendees}</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function LeaguesTab() {
  const { data: leagues = [] } = useQuery({ queryKey: ["rink-leagues"], queryFn: rinkApi.leagues });
  const total_annual = (leagues as any[]).reduce((s: number, l: any) => s + l.annual_value, 0);
  const total_participants = (leagues as any[]).reduce((s: number, l: any) => s + l.total_participants, 0);

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { l: "Active Leagues", v: (leagues as any[]).length, c: "#60A5FA" },
          { l: "Total Participants", v: total_participants, c: "#22C55E" },
          { l: "Annual League Value", v: fmt(total_annual), c: GOLD },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "14px 16px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 26, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {(leagues as any[]).map((l: any) => (
          <div key={l.id} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 8, padding: "14px 18px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
              <div>
                <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 2 }}>{l.league_name}</p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 11, color: "#22C55E", background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 3, padding: "1px 7px" }}>{(SURFACE_ICON as any)[l.surface]} {lbl(l.surface)}</span>
                  <span style={{ fontSize: 11, color: "#8aa0bb" }}>{l.day_of_week} · {l.start_time}–{l.end_time}</span>
                  <span style={{ fontSize: 11, color: "#8aa0bb" }}>{l.teams} teams · {l.total_participants} players</span>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD }}>{fmt(l.weekly_rate)}<span style={{ fontSize: 12, color: "#4a6080" }}>/wk</span></p>
                <p style={{ fontSize: 12, color: "#22C55E" }}>Season: {fmt(l.annual_value)}</p>
              </div>
            </div>
            <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
              <div style={{ height: "100%", width: "100%", background: `linear-gradient(90deg, #7a612e, ${GOLD})`, borderRadius: 2 }} />
            </div>
            <div style={{ display: "flex", gap: 16, fontSize: 11, color: "#4a6080", marginTop: 6 }}>
              <span>Season: {l.season_start} → {l.season_end}</span>
              {l.contact_name && <span>Contact: {l.contact_name}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RevenueTab() {
  const { data: util } = useQuery({ queryKey: ["rink-util"], queryFn: rinkApi.utilization });
  const { data: conversions = [] } = useQuery({ queryKey: ["rink-conversions"], queryFn: rinkApi.conversions });
  if (!util) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Period comparison */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {[
          { label: "Trailing 30 Days", data: util.trailing_30 },
          { label: "Trailing 90 Days", data: util.trailing_90 },
        ].map(period => (
          <div key={period.label} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 18px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>{period.label}</p>
            {[
              { l: "Revenue",           v: fmt(period.data.revenue),         c: GOLD },
              { l: "Hours Booked",      v: `${period.data.hours_booked}h`,  c: "#60A5FA" },
              { l: "Utilization",       v: `${period.data.utilization_pct}%`, c: period.data.utilization_pct >= 70 ? "#22C55E" : "#F97316" },
              { l: "Avg $/hr",          v: `$${period.data.avg_revenue_per_hour}`, c: "#22C55E" },
              { l: "Attendees",         v: period.data.total_attendees.toLocaleString(), c: "#F0F4FA" },
            ].map(s => (
              <div key={s.l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 12, color: "#8aa0bb" }}>{s.l}</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: s.c as string }}>{s.v}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Category breakdown */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>REVENUE BY CATEGORY (30d)</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10 }}>
          {Object.entries(util.category_breakdown_30d).map(([cat, data]: [string, any]) => {
            const cc = CAT_COLORS[cat] ?? GOLD;
            return (
              <div key={cat} style={{ background: `${cc}08`, border: `1px solid ${cc}30`, borderRadius: 7, padding: "10px 12px" }}>
                <span style={{ fontSize: 14 }}>{(SURFACE_ICON as any)[cat.includes("turf") ? "turf" : "ice"]}</span>
                <p style={{ fontSize: 11, color: cc, fontWeight: 700, margin: "4px 0" }}>{lbl(cat)}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#F0F4FA" }}>{fmt(data.revenue)}</p>
                <p style={{ fontSize: 11, color: "#4a6080" }}>{data.sessions} sessions</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* League value + conversion costs */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 18px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, letterSpacing: 1, color: GOLD, marginBottom: 8 }}>ANNUAL LEAGUE VALUE</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 32, color: "#F0F4FA" }}>{fmt(util.league_annual_value)}</p>
          <p style={{ fontSize: 12, color: "#8aa0bb", marginTop: 4 }}>Guaranteed recurring revenue from all active league blocks</p>
        </div>
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 18px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, letterSpacing: 1, color: "#F97316", marginBottom: 8 }}>CONVERSION LOG</p>
          {(conversions as any[]).map((c: any) => (
            <div key={c.id} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#8aa0bb", marginBottom: 5 }}>
              <span>{c.direction === "turf_to_ice" ? "🧊 Turf→Ice" : "🟩 Ice→Turf"}</span>
              <span>{c.conversion_date}</span>
              <span style={{ color: "#F97316" }}>${c.cost.toLocaleString()}</span>
              <span style={{ color: c.completed ? "#22C55E" : GOLD }}>{c.completed ? "Done" : "Pending"}</span>
            </div>
          ))}
          <p style={{ fontSize: 11, color: "#4a6080", marginTop: 8 }}>Total conversion cost: {fmt(util.conversion_stats.total_cost)} ({util.conversion_stats.total_conversions} conversions)</p>
        </div>
      </div>
    </div>
  );
}

function AIOptimizerTab() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button onClick={async () => { setLoading(true); setResult(await rinkApi.aiOptimizer()); setLoading(false); }} disabled={loading}
          style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Optimizing…</> : <><Brain size={14} />Generate Optimization Brief</>}
        </button>
      </div>
      {result ? (
        <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
          <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>AI RINK REVENUE OPTIMIZATION</p>
          <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{result.optimization}</p>
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
          <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ fontSize: 14, color: "#8aa0bb" }}>AI scheduling + dark ice analysis + conversion strategy</p>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id: "schedule", label: "Schedule",    icon: <CalendarDays size={14} /> },
  { id: "leagues",  label: "Leagues",     icon: <Users size={14} /> },
  { id: "revenue",  label: "Revenue",     icon: <TrendingUp size={14} /> },
  { id: "ai",       label: "AI Optimizer",icon: <Brain size={14} /> },
];

export default function RinkPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("schedule");
  const [seeding, setSeeding] = useState(false);
  const { data: util } = useQuery({ queryKey: ["rink-util"], queryFn: rinkApi.utilization });

  const handleSeed = async () => {
    setSeeding(true);
    await rinkApi.seed();
    ["rink-schedule","rink-leagues","rink-util","rink-conversions"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NXS NATIONAL COMPLEX","200×85 FT NHL-SPEC","ICE ↔ TURF CONVERTIBLE"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>ICE RINK MODULE</h1>
          {util && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>30d Revenue: <strong style={{ color: GOLD }}>{fmt(util.trailing_30.revenue)}</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Utilization: <strong style={{ color: util.trailing_30.utilization_pct >= 70 ? "#22C55E" : "#F97316" }}>{util.trailing_30.utilization_pct}%</strong></span>
          </div>}
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
        {activeTab === "schedule" && <ScheduleTab onSeed={handleSeed} />}
        {activeTab === "leagues"  && <LeaguesTab />}
        {activeTab === "revenue"  && <RevenueTab />}
        {activeTab === "ai"       && <AIOptimizerTab />}
      </div>
    </div>
  );
}
