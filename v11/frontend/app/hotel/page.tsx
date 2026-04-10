"use client";
/**
 * SportAI Suite — Hotel Revenue Module
 * /app/hotel/page.tsx · Sprint 3 · NXS National Complex
 * Tabs: Occupancy · Reservations · Revenue & TID · AI Forecast
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, CalendarDays, TrendingUp, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const hotelApi = {
  occupancy:      () => fetch(`${API}/api/hotel/occupancy`).then(r => r.json()),
  rooms:          (p?) => fetch(`${API}/api/hotel/rooms${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  reservations:   (p?) => fetch(`${API}/api/hotel/reservations${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  revpar:         () => fetch(`${API}/api/hotel/revpar`).then(r => r.json()),
  tidLedger:      () => fetch(`${API}/api/hotel/tid-ledger`).then(r => r.json()),
  rateCards:      () => fetch(`${API}/api/hotel/rate-cards`).then(r => r.json()),
  seed:           () => fetch(`${API}/api/hotel/seed`, { method: "POST" }).then(r => r.json()),
  aiRate:         () => fetch(`${API}/api/hotel/ai-rate-recommendation`, { method: "POST" }).then(r => r.json()),
  aiForecast:     () => fetch(`${API}/api/hotel/ai-revenue-forecast`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const fmt2 = (n: number) => `$${n.toFixed(2)}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const STRATEGY_COLORS: Record<string, string> = {
  standard: "#60A5FA", tournament: "#22C55E", peak: GOLD, rescue: "#F97316", group: "#A855F7",
};
const STATUS_COLORS: Record<string, string> = {
  confirmed: "#60A5FA", checked_in: "#22C55E", checked_out: "#6B7280", cancelled: "#EF4444", no_show: "#F97316",
};

type Occupancy = { date: string; total_rooms: number; occupied: number; available: number; occupancy_pct: number; adr: number; revpar: number; room_revenue_today: number; tid_today: number; booked_next_7_days: number; occupancy_band: string; };
type Reservation = { id: string; room_id: string; guest_name: string; check_in: string; check_out: string; nights: number; guests: number; rate_per_night: number; total_revenue: number; rate_strategy: string; status: string; source?: string; group_name?: string; tid_contribution: number; };
type TIDRow = { month: string; room_revenue: number; tid_assessment: number; rooms_sold: number; adr: number; occupancy_pct: number; revpar: number; };

function OccupancyGauge({ pct, band }: { pct: number; band: string }) {
  const color = band === "HIGH" ? "#22C55E" : band === "MID" ? GOLD : "#EF4444";
  const r = 52; const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  return (
    <div style={{ position: "relative", display: "inline-flex", flexDirection: "column", alignItems: "center" }}>
      <svg width={130} height={130} viewBox="0 0 130 130">
        <circle cx={65} cy={65} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={12} />
        <circle cx={65} cy={65} r={r} fill="none" stroke={color} strokeWidth={12}
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          transform="rotate(-90 65 65)" style={{ transition: "stroke-dashoffset 0.6s ease" }} />
        <text x={65} y={60} textAnchor="middle" fill="#F0F4FA" fontSize={22} fontFamily="'Bebas Neue'" letterSpacing={1}>{pct}%</text>
        <text x={65} y={78} textAnchor="middle" fill={color} fontSize={11} fontFamily="'Barlow Condensed'" fontWeight={700}>{band}</text>
      </svg>
    </div>
  );
}

function OccupancyTab({ onSeed }: { onSeed: () => void }) {
  const { data: occ } = useQuery<Occupancy>({ queryKey: ["hotel-occ"], queryFn: hotelApi.occupancy });
  const { data: rateCards = [] } = useQuery({ queryKey: ["hotel-rates"], queryFn: hotelApi.rateCards });

  if (!occ) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Building2 size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Hotel not seeded yet</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed 85-Unit Hotel</button>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Live snapshot */}
      <div style={{ background: "#0f2744", border: `1px solid ${GOLD}40`, borderRadius: 10, padding: "24px 28px" }}>
        <p style={{ fontSize: 11, color: "#4a6080", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>LIVE OCCUPANCY — {occ.date}</p>
        <div style={{ display: "flex", gap: 32, alignItems: "center", flexWrap: "wrap" }}>
          <OccupancyGauge pct={occ.occupancy_pct} band={occ.occupancy_band} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, flex: 1 }}>
            {[
              { l: "Occupied", v: `${occ.occupied} / ${occ.total_rooms}`, c: "#22C55E" },
              { l: "Available", v: occ.available, c: "#60A5FA" },
              { l: "ADR", v: fmt2(occ.adr), c: GOLD },
              { l: "RevPAR", v: fmt2(occ.revpar), c: GOLD },
              { l: "Room Revenue Today", v: fmt(occ.room_revenue_today), c: "#F0F4FA" },
              { l: "TID Today", v: fmt2(occ.tid_today), c: "#A855F7" },
              { l: "Booked Next 7d", v: occ.booked_next_7_days, c: "#F97316" },
            ].map(s => (
              <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "10px 14px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Room type breakdown */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        {[
          { label: "Standard Double", count: 40, rate: "$99", color: "#60A5FA" },
          { label: "Standard King",   count: 30, rate: "$109", color: "#22C55E" },
          { label: "Suite King",      count: 8,  rate: "$159", color: GOLD },
          { label: "Accessible",      count: 5,  rate: "$109", color: "#A855F7" },
          { label: "Tournament Block",count: 2,  rate: "$89", color: "#F97316" },
        ].map(rt => (
          <div key={rt.label} style={{ background: `${rt.color}08`, border: `1px solid ${rt.color}30`, borderRadius: 8, padding: "12px 14px" }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 26, color: rt.color }}>{rt.count}</p>
            <p style={{ fontSize: 12, fontWeight: 700, color: "#F0F4FA", marginBottom: 2 }}>{rt.label}</p>
            <p style={{ fontSize: 12, color: GOLD }}>{rt.rate}/night</p>
          </div>
        ))}
      </div>

      {/* Rate cards */}
      {(rateCards as any[]).length > 0 && (
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>ACTIVE RATE CARDS</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 10 }}>
            {(rateCards as any[]).map((rc: any) => {
              const sc = STRATEGY_COLORS[rc.strategy] ?? GOLD;
              return (
                <div key={rc.id} style={{ background: `${sc}10`, border: `1px solid ${sc}35`, borderRadius: 7, padding: "12px 14px" }}>
                  <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA", marginBottom: 4 }}>{rc.name}</p>
                  <div style={{ display: "flex", gap: 10, fontSize: 12, color: "#8aa0bb", marginBottom: 6 }}>
                    <span>{rc.start_date} → {rc.end_date}</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: sc, background: `${sc}20`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(rc.strategy)}</span>
                    <span style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{rc.multiplier}x</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function ReservationsTab() {
  const { data: reservations = [] } = useQuery<Reservation[]>({ queryKey: ["hotel-reservations"], queryFn: () => hotelApi.reservations() });
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
            {["Guest / Group","Check-In","Check-Out","Nights","Rate/Night","Total","Strategy","Status","TID"].map(h => (
              <th key={h} style={{ padding: "8px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left", whiteSpace: "nowrap" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(reservations as Reservation[]).map((r: Reservation) => {
            const sc = STRATEGY_COLORS[r.rate_strategy] ?? GOLD;
            const stc = STATUS_COLORS[r.status] ?? "#6B7280";
            return (
              <tr key={r.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <td style={{ padding: "10px 12px" }}>
                  <p style={{ fontWeight: 600, fontSize: 13, color: "#F0F4FA" }}>{r.guest_name}</p>
                  {r.group_name && <p style={{ fontSize: 11, color: "#8aa0bb" }}>{r.group_name}</p>}
                  {r.source && <p style={{ fontSize: 10, color: "#4a6080" }}>{r.source}</p>}
                </td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "#F0F4FA" }}>{r.check_in}</td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "#F0F4FA" }}>{r.check_out}</td>
                <td style={{ padding: "10px 12px", fontFamily: "'Bebas Neue'", fontSize: 16, color: "#F0F4FA" }}>{r.nights}</td>
                <td style={{ padding: "10px 12px", fontSize: 13, color: GOLD, fontWeight: 700 }}>{fmt2(r.rate_per_night)}</td>
                <td style={{ padding: "10px 12px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(r.total_revenue)}</td>
                <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(r.rate_strategy)}</span></td>
                <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: stc, background: `${stc}15`, border: `1px solid ${stc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(r.status)}</span></td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "#A855F7" }}>{fmt2(r.tid_contribution)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function RevenueTIDTab() {
  const { data: revpar } = useQuery({ queryKey: ["hotel-revpar"], queryFn: hotelApi.revpar });
  const { data: ledger = [] } = useQuery<TIDRow[]>({ queryKey: ["hotel-tid"], queryFn: hotelApi.tidLedger });

  if (!revpar) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  const maxRev = Math.max(...(ledger as TIDRow[]).map((l: TIDRow) => l.room_revenue), 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Period comparison */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
        {[
          { label: "Month-to-Date",   data: revpar.mtd },
          { label: "Trailing 30 Days",data: revpar.trailing_30 },
          { label: "Trailing 90 Days",data: revpar.trailing_90 },
        ].map(period => (
          <div key={period.label} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 18px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>{period.label}</p>
            {[
              { l: "Revenue",    v: fmt(period.data.revenue),          c: GOLD },
              { l: "Occupancy",  v: `${period.data.occupancy_pct}%`,  c: "#60A5FA" },
              { l: "ADR",        v: fmt2(period.data.adr),             c: "#22C55E" },
              { l: "RevPAR",     v: fmt2(period.data.revpar),          c: "#A855F7" },
              { l: "TID",        v: fmt(period.data.tid),              c: "#F97316" },
            ].map(s => (
              <div key={s.l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 12, color: "#8aa0bb" }}>{s.l}</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: s.c as string }}>{s.v}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* TID Ledger chart */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "20px 24px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, letterSpacing: 1, color: "#F0F4FA", marginBottom: 16 }}>MONTHLY TID LEDGER — 6-MONTH HISTORY</p>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 120 }}>
          {(ledger as TIDRow[]).map((l: TIDRow) => {
            const h = Math.round((l.room_revenue / maxRev) * 100);
            return (
              <div key={l.month} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <span style={{ fontSize: 10, color: GOLD }}>{fmt(l.tid_assessment)}</span>
                <div style={{ width: "100%", background: `linear-gradient(180deg, ${GOLD}, #7a612e)`, borderRadius: "3px 3px 0 0", height: `${h}%`, minHeight: 4, transition: "height 0.4s" }} title={`${l.month}: ${fmt(l.room_revenue)}`} />
                <span style={{ fontSize: 10, color: "#8aa0bb", transform: "rotate(-45deg)", transformOrigin: "center", whiteSpace: "nowrap" }}>{l.month.slice(5)}/{l.month.slice(2, 4)}</span>
              </div>
            );
          })}
        </div>
        <div style={{ marginTop: 16, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr>{["Month","Revenue","TID","Occ %","ADR","RevPAR"].map(h => (
                <th key={h} style={{ padding: "6px 10px", color: "#4a6080", textAlign: "left", fontWeight: 700, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {(ledger as TIDRow[]).map((l: TIDRow) => (
                <tr key={l.month} style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "6px 10px", color: "#F0F4FA", fontWeight: 600 }}>{l.month}</td>
                  <td style={{ padding: "6px 10px", color: GOLD }}>{fmt(l.room_revenue)}</td>
                  <td style={{ padding: "6px 10px", color: "#A855F7" }}>{fmt(l.tid_assessment)}</td>
                  <td style={{ padding: "6px 10px", color: "#60A5FA" }}>{l.occupancy_pct}%</td>
                  <td style={{ padding: "6px 10px", color: "#22C55E" }}>${l.adr}</td>
                  <td style={{ padding: "6px 10px", color: "#F0F4FA" }}>${l.revpar}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function AIForecastTab() {
  const [rateResult, setRateResult] = useState<any>(null);
  const [forecastResult, setForecastResult] = useState<any>(null);
  const [loadingRate, setLoadingRate] = useState(false);
  const [loadingForecast, setLoadingForecast] = useState(false);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      {[
        { title: "RATE RECOMMENDATION (14 DAYS)", loadFn: async () => { setLoadingRate(true); setRateResult(await hotelApi.aiRate()); setLoadingRate(false); }, loading: loadingRate, result: rateResult, field: "recommendation", btnLabel: "Generate Rate Rec" },
        { title: "90-DAY REVENUE FORECAST",       loadFn: async () => { setLoadingForecast(true); setForecastResult(await hotelApi.aiForecast()); setLoadingForecast(false); }, loading: loadingForecast, result: forecastResult, field: "forecast", btnLabel: "Generate Forecast" },
      ].map(panel => (
        <div key={panel.title}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 17, letterSpacing: 1, color: "#F0F4FA" }}>{panel.title}</p>
            <button onClick={panel.loadFn} disabled={panel.loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 6 }}>
              {panel.loading ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={12} />{panel.btnLabel}</>}
            </button>
          </div>
          {panel.result ? (
            <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px" }}>
              <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{panel.result[panel.field]}</p>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "60px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
              <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
              <p style={{ fontSize: 13, color: "#8aa0bb" }}>Generate AI {panel.btnLabel.includes("Rate") ? "rate strategy" : "revenue forecast"}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

const TABS = [
  { id: "occupancy",     label: "Occupancy",    icon: <Building2 size={14} /> },
  { id: "reservations",  label: "Reservations", icon: <CalendarDays size={14} /> },
  { id: "revenue",       label: "Revenue & TID",icon: <TrendingUp size={14} /> },
  { id: "ai",            label: "AI Forecast",  icon: <Brain size={14} /> },
];

export default function HotelPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("occupancy");
  const [seeding, setSeeding] = useState(false);
  const { data: occ } = useQuery<Occupancy>({ queryKey: ["hotel-occ"], queryFn: hotelApi.occupancy });

  const handleSeed = async () => {
    setSeeding(true);
    await hotelApi.seed();
    qc.invalidateQueries({ queryKey: ["hotel-occ"] });
    qc.invalidateQueries({ queryKey: ["hotel-reservations"] });
    qc.invalidateQueries({ queryKey: ["hotel-revpar"] });
    qc.invalidateQueries({ queryKey: ["hotel-tid"] });
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NXS NATIONAL COMPLEX", "85 UNITS", "TID ASSESSMENT"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>HOTEL REVENUE MODULE</h1>
          {occ && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            {[
              { l: "Occupancy", v: `${occ.occupancy_pct}%`, c: occ.occupancy_pct >= 75 ? "#22C55E" : GOLD },
              { l: "ADR", v: `$${occ.adr}`, c: GOLD },
              { l: "RevPAR", v: `$${occ.revpar}`, c: "#60A5FA" },
            ].map(s => <span key={s.l} style={{ fontSize: 13, color: "#8aa0bb" }}>{s.l}: <strong style={{ color: s.c as string }}>{s.v}</strong></span>)}
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
        {activeTab === "occupancy"    && <OccupancyTab onSeed={handleSeed} />}
        {activeTab === "reservations" && <ReservationsTab />}
        {activeTab === "revenue"      && <RevenueTIDTab />}
        {activeTab === "ai"           && <AIForecastTab />}
      </div>
    </div>
  );
}
