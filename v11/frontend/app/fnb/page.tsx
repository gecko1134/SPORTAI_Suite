"use client";
/**
 * SportAI Suite — F&B Restaurant Module
 * /app/fnb/page.tsx · Sprint 5 · NXS National Complex
 * Tabs: Venues · Events · Food Trucks · Revenue · AI Forecast
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, CalendarDays, Truck, BarChart2, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const fnbApi = {
  venues:    () => fetch(`${API}/api/fnb/venues`).then(r => r.json()),
  events:    (p?) => fetch(`${API}/api/fnb/events${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  trucks:    () => fetch(`${API}/api/fnb/food-truck-schedule?days_ahead=30`).then(r => r.json()),
  summary:   () => fetch(`${API}/api/fnb/revenue-summary`).then(r => r.json()),
  seed:      () => fetch(`${API}/api/fnb/seed`, { method: "POST" }).then(r => r.json()),
  aiForecast:() => fetch(`${API}/api/fnb/ai-revenue-forecast`, { method: "POST" }).then(r => r.json()),
  aiEvent:   (type: string, att: number) => fetch(`${API}/api/fnb/ai-event-day-plan?event_type=${type}&expected_attendees=${att}`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const VENUE_COLORS: Record<string, string> = {
  main_restaurant: GOLD, concession_stand: "#22C55E",
  food_truck_plaza: "#F97316", catering_kitchen: "#A855F7", bar_lounge: "#60A5FA",
};
const EVENT_COLORS: Record<string, string> = {
  tournament: "#EF4444", league_night: "#60A5FA", open_event: "#22C55E",
  corporate: GOLD, private_event: "#A855F7", camp_day: "#F97316", open_play: "#6B7280",
};

function VenuesTab({ onSeed }: { onSeed: () => void }) {
  const { data: venues = [] } = useQuery({ queryKey: ["fnb-venues"], queryFn: fnbApi.venues });

  if (!venues.length) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Building2 size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>F&B not seeded yet</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed F&B Module</button>
    </div>
  );

  const phase1 = (venues as any[]).filter((v: any) => v.phase_open === 1);
  const phase2 = (venues as any[]).filter((v: any) => v.phase_open === 2);
  const totalBuildout = (venues as any[]).reduce((s: number, v: any) => s + (v.buildout_cost || 0), 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        {[
          { l: "Phase 1 (Operational)", v: phase1.length, c: "#22C55E" },
          { l: "Phase 2 (Pending)",     v: phase2.length, c: "#F97316" },
          { l: "Total Buildout",        v: fmt(totalBuildout), c: GOLD },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 16px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 26, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      {[{ label: "PHASE 1 — OPERATIONAL", venues: phase1, borderColor: "#22C55E" },
        { label: "PHASE 2 — PENDING BUILDOUT", venues: phase2, borderColor: "#F97316" }].map(group => (
        <div key={group.label}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, letterSpacing: 1, color: "#F0F4FA", marginBottom: 10 }}>{group.label}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 12 }}>
            {group.venues.map((v: any) => {
              const tc = VENUE_COLORS[v.venue_type] ?? GOLD;
              return (
                <div key={v.id} style={{ background: `${tc}08`, border: `1px solid ${tc}30`, borderRadius: 10, padding: "16px 18px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA" }}>{v.name}</p>
                    <span style={{ fontSize: 11, fontWeight: 700, color: v.is_operational ? "#22C55E" : "#F97316", background: v.is_operational ? "rgba(34,197,94,0.15)" : "rgba(249,115,22,0.15)", border: `1px solid ${v.is_operational ? "rgba(34,197,94,0.3)" : "rgba(249,115,22,0.3)"}`, borderRadius: 3, padding: "1px 6px" }}>
                      {v.is_operational ? "OPEN" : "PHASE 2"}
                    </span>
                  </div>
                  <span style={{ fontSize: 11, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "2px 8px" }}>{lbl(v.venue_type)}</span>
                  {v.capacity > 0 && <p style={{ fontSize: 12, color: "#8aa0bb", marginTop: 6 }}>Capacity: {v.capacity}</p>}
                  {v.buildout_cost && <p style={{ fontSize: 13, color: GOLD, fontFamily: "'Bebas Neue'", marginTop: 4 }}>{fmt(v.buildout_cost)} buildout</p>}
                  {v.description && <p style={{ fontSize: 11, color: "#4a6080", marginTop: 4 }}>{v.description}</p>}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function EventsTab() {
  const [typeFilter, setTypeFilter] = useState("");
  const params: Record<string, string> = {};
  if (typeFilter) params.event_type = typeFilter;
  const { data: events = [] } = useQuery({ queryKey: ["fnb-events", typeFilter], queryFn: () => fnbApi.events(params) });
  const EVENT_TYPES = ["tournament","league_night","open_event","corporate","camp_day"];

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        <button onClick={() => setTypeFilter("")} style={{ background: !typeFilter ? GOLD : "#0f2744", color: !typeFilter ? NAVY : "#8aa0bb", border: `1px solid ${!typeFilter ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>All</button>
        {EVENT_TYPES.map(t => {
          const tc = EVENT_COLORS[t] ?? GOLD;
          return <button key={t} onClick={() => setTypeFilter(t)} style={{ background: typeFilter === t ? tc : "#0f2744", color: typeFilter === t ? "#071828" : "#8aa0bb", border: `1px solid ${typeFilter === t ? tc : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{lbl(t)}</button>;
        })}
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Date","Event","Type","Attendees","Per Cap","Gross","Net","Food Trucks","Total"].map(h => (
                <th key={h} style={{ padding: "8px 10px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(events as any[]).slice(0, 40).map((e: any) => {
              const tc = EVENT_COLORS[e.event_type] ?? GOLD;
              return (
                <tr key={e.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#8aa0bb" }}>{e.event_date}</td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#F0F4FA", fontWeight: 600 }}>{e.title}</td>
                  <td style={{ padding: "8px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(e.event_type)}</span></td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#F0F4FA" }}>{e.attendees.toLocaleString()}</td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#8aa0bb" }}>${e.per_cap_spend}</td>
                  <td style={{ padding: "8px 10px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(e.gross_revenue)}</td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#22C55E" }}>{fmt(e.net_revenue)}</td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#F97316" }}>{e.food_truck_revenue > 0 ? fmt(e.food_truck_revenue) : "—"}</td>
                  <td style={{ padding: "8px 10px", fontFamily: "'Bebas Neue'", fontSize: 16, color: "#F0F4FA" }}>{fmt(e.total_event_revenue)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FoodTrucksTab() {
  const { data: trucks = [] } = useQuery({ queryKey: ["fnb-trucks"], queryFn: fnbApi.trucks });
  const byDate = (trucks as any[]).reduce((acc: Record<string, any[]>, t: any) => {
    acc[t.event_date] = [...(acc[t.event_date] || []), t];
    return acc;
  }, {});
  const CUISINE_EMOJIS: Record<string, string> = { "BBQ / Comfort": "🔥", "Mexican / Fusion": "🌮", "Seafood / Walleye": "🐟", "Wood-fired Pizza": "🍕", "Desserts / Coffee": "☕", "Burgers / Fries": "🍔" };

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
        {[
          { l: "Trucks Scheduled (30d)", v: (trucks as any[]).length, c: "#F97316" },
          { l: "Plaza Spots",            v: "6 available",             c: GOLD },
          { l: "Daily Plaza Fee",        v: "$150/spot",               c: "#22C55E" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 16px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>
      {Object.entries(byDate).map(([dateStr, dayTrucks]) => {
        const d = new Date(dateStr + "T12:00:00");
        const label = d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
        return (
          <div key={dateStr} style={{ marginBottom: 14 }}>
            <p style={{ fontSize: 12, fontWeight: 700, color: "#8aa0bb", marginBottom: 6 }}>{label}</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 8 }}>
              {(dayTrucks as any[]).map((t: any) => (
                <div key={t.id} style={{ background: "rgba(249,115,22,0.08)", border: "1px solid rgba(249,115,22,0.25)", borderRadius: 7, padding: "10px 12px" }}>
                  <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4 }}>
                    <span style={{ fontSize: 18 }}>{(CUISINE_EMOJIS as any)[t.cuisine_type] || "🚚"}</span>
                    <div>
                      <p style={{ fontWeight: 700, fontSize: 12, color: "#F0F4FA" }}>{t.truck_name}</p>
                      <p style={{ fontSize: 10, color: "#8aa0bb" }}>{t.cuisine_type}</p>
                    </div>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11 }}>
                    <span style={{ color: "#4a6080" }}>Spot #{t.spot_number}</span>
                    <span style={{ color: "#F97316" }}>Fee: ${t.plaza_fee}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function RevenueTab() {
  const { data: summary } = useQuery({ queryKey: ["fnb-summary"], queryFn: fnbApi.summary });
  if (!summary) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  const maxLedgerRev = Math.max(...(summary.monthly_ledger || []).map((l: any) => l.total_revenue), 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {[
          { label: "Trailing 30 Days", data: summary.trailing_30 },
          { label: "Trailing 90 Days", data: summary.trailing_90 },
        ].map(period => (
          <div key={period.label} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 18px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>{period.label}</p>
            {[
              { l: "Gross Revenue",       v: fmt(period.data.gross_revenue),    c: GOLD },
              { l: "Net Revenue",         v: fmt(period.data.net_revenue),      c: "#22C55E" },
              { l: "Food Truck Revenue",  v: fmt(period.data.food_truck_revenue), c: "#F97316" },
              { l: "Catering",           v: fmt(period.data.catering_revenue),  c: "#A855F7" },
              { l: "Events",             v: period.data.events,                 c: "#F0F4FA" },
              { l: "Avg Per Cap",        v: `$${period.data.avg_per_cap}`,      c: period.data.avg_per_cap >= 12 ? "#22C55E" : "#F97316" },
            ].map(s => (
              <div key={s.l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 12, color: "#8aa0bb" }}>{s.l}</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: s.c as string }}>{s.v}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Per-cap targets */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>PER-CAP TARGETS BY EVENT TYPE</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
          {Object.entries(summary.per_cap_targets).map(([type, target]: [string, any]) => {
            const actual = summary.event_type_breakdown[type]?.avg_per_cap || 0;
            const color = actual >= target ? "#22C55E" : "#F97316";
            return (
              <div key={type} style={{ background: "#152f52", borderRadius: 6, padding: "10px 12px" }}>
                <p style={{ fontSize: 11, color: EVENT_COLORS[type] ?? GOLD, fontWeight: 700, marginBottom: 4 }}>{lbl(type)}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color }}>
                  ${actual > 0 ? actual.toFixed(0) : "—"}
                  <span style={{ fontSize: 11, color: "#4a6080" }}>/ ${target}</span>
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Monthly bar chart */}
      {summary.monthly_ledger?.length > 0 && (
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>MONTHLY REVENUE TREND</p>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 16, height: 90 }}>
            {summary.monthly_ledger.map((l: any) => {
              const h = Math.round((l.total_revenue / maxLedgerRev) * 80);
              return (
                <div key={l.month} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                  <span style={{ fontSize: 10, color: GOLD }}>{fmt(l.total_revenue)}</span>
                  <div style={{ width: "60%", background: `linear-gradient(180deg, ${GOLD}, #7a612e)`, borderRadius: "3px 3px 0 0", height: `${h}%`, minHeight: 4 }} />
                  <span style={{ fontSize: 10, color: "#8aa0bb" }}>{l.month.slice(5)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function AIForecastTab() {
  const [forecast, setForecast] = useState<any>(null);
  const [eventPlan, setEventPlan] = useState<any>(null);
  const [eventType, setEventType] = useState("tournament");
  const [attendees, setAttendees] = useState(250);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [loadingEvent, setLoadingEvent] = useState(false);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 17, letterSpacing: 1, color: "#F0F4FA" }}>REVENUE FORECAST</p>
          <button onClick={async () => { setLoadingForecast(true); setForecast(await fnbApi.aiForecast()); setLoadingForecast(false); }} disabled={loadingForecast}
            style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 6 }}>
            {loadingForecast ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={12} />Generate</>}
          </button>
        </div>
        {forecast ? (
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px" }}>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{forecast.forecast}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "60px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Generate Phase 2 revenue forecast</p>
          </div>
        )}
      </div>

      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 17, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>EVENT-DAY ACTIVATION PLAN</p>
        <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
          <select value={eventType} onChange={e => setEventType(e.target.value)} style={{ flex: 1, background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "8px 10px", fontSize: 13, fontFamily: "'Barlow Condensed'" }}>
            {["tournament","league_night","open_event","corporate","camp_day"].map(t => <option key={t} value={t}>{lbl(t)}</option>)}
          </select>
          <input type="number" value={attendees} onChange={e => setAttendees(Number(e.target.value))} placeholder="Attendees" style={{ width: 100, background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "8px 10px", fontSize: 13 }} />
          <button onClick={async () => { setLoadingEvent(true); setEventPlan(await fnbApi.aiEvent(eventType, attendees)); setLoadingEvent(false); }} disabled={loadingEvent}
            style={{ background: "#0f2744", color: GOLD, border: `1px solid ${GOLD}`, borderRadius: 6, padding: "8px 14px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 5 }}>
            {loadingEvent ? <RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} /> : <Brain size={12} />}
          </button>
        </div>
        {eventPlan ? (
          <div style={{ background: "#0f2744", border: `1px solid rgba(201,168,76,0.3)`, borderRadius: 10, padding: "18px 20px" }}>
            <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
              <div><p style={{ fontSize: 10, color: "#4a6080" }}>TARGET</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD }}>{fmt(eventPlan.target_revenue)}</p></div>
              <div><p style={{ fontSize: 10, color: "#4a6080" }}>ATTENDEES</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F0F4FA" }}>{eventPlan.expected_attendees}</p></div>
            </div>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{eventPlan.plan}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "60px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Truck size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Select event type and generate activation plan</p>
          </div>
        )}
      </div>
    </div>
  );
}

const TABS = [
  { id: "venues",  label: "Venues",      icon: <Building2 size={14} /> },
  { id: "events",  label: "Events",      icon: <CalendarDays size={14} /> },
  { id: "trucks",  label: "Food Trucks", icon: <Truck size={14} /> },
  { id: "revenue", label: "Revenue",     icon: <BarChart2 size={14} /> },
  { id: "ai",      label: "AI Forecast", icon: <Brain size={14} /> },
];

export default function FnBPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("venues");
  const [seeding, setSeeding] = useState(false);
  const { data: summary } = useQuery({ queryKey: ["fnb-summary"], queryFn: fnbApi.summary });

  const handleSeed = async () => {
    setSeeding(true);
    await fnbApi.seed();
    ["fnb-venues","fnb-events","fnb-trucks","fnb-summary"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NXS NATIONAL COMPLEX","$720K PHASE 2 BUILDOUT","6 FOOD TRUCK SPOTS"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>F&B RESTAURANT MODULE</h1>
          {summary && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>30d Revenue: <strong style={{ color: GOLD }}>{fmt(summary.trailing_30.gross_revenue)}</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Per Cap: <strong style={{ color: summary.trailing_30.avg_per_cap >= 12 ? "#22C55E" : "#F97316" }}>${summary.trailing_30.avg_per_cap}</strong></span>
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
        {activeTab === "venues"  && <VenuesTab onSeed={handleSeed} />}
        {activeTab === "events"  && <EventsTab />}
        {activeTab === "trucks"  && <FoodTrucksTab />}
        {activeTab === "revenue" && <RevenueTab />}
        {activeTab === "ai"      && <AIForecastTab />}
      </div>
    </div>
  );
}
