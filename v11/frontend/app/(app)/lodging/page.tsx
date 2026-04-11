"use client";
/**
 * SportAI Suite — Apartment & Campground Module
 * /app/lodging/page.tsx · Sprint 3 · NXS National Complex
 * Tabs: Apartments · Campground · Revenue Rollup · AI Insights
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Home, Tent, BarChart2, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const lodgingApi = {
  apartments: (p?) => fetch(`${API}/api/lodging/apartments${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  leases:     (p?) => fetch(`${API}/api/lodging/leases${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  rentRoll:   () => fetch(`${API}/api/lodging/rent-roll`).then(r => r.json()),
  campground: () => fetch(`${API}/api/lodging/campground`).then(r => r.json()),
  campRes:    () => fetch(`${API}/api/lodging/campground/reservations?days_ahead=30`).then(r => r.json()),
  campRates:  () => fetch(`${API}/api/lodging/campground/seasonal-rates`).then(r => r.json()),
  rollup:     () => fetch(`${API}/api/lodging/revenue-rollup`).then(r => r.json()),
  seed:       () => fetch(`${API}/api/lodging/seed`, { method: "POST" }).then(r => r.json()),
  aiInsights: () => fetch(`${API}/api/lodging/ai-insights`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const UNIT_COLORS: Record<string, string> = { studio: "#60A5FA", one_bedroom: "#22C55E", two_bedroom: GOLD, three_bedroom: "#F97316" };
const LEASE_COLORS: Record<string, string> = { active: "#22C55E", expiring: "#F97316", expired: "#EF4444", vacant: "#6B7280", maintenance: "#A855F7" };
const SITE_COLORS: Record<string, string>  = { tent: "#22C55E", rv_hookup: "#60A5FA", cabin: GOLD, group: "#F97316" };
const SEASON_COLORS: Record<string, string>= { summer: "#F97316", fall: GOLD, winter: "#60A5FA", spring: "#22C55E" };

type Unit = { id: string; unit_number: string; unit_type: string; floor: number; sqft: number; bedrooms: number; bathrooms: number; monthly_rent: number; status: string; };
type Lease = { id: string; unit_id: string; tenant_name: string; lease_start: string; lease_end: string; monthly_rent: number; days_until_expiry: number; is_expiring_soon: boolean; renewal_offered: boolean; };
type Site  = { id: string; site_number: string; site_type: string; max_guests: number; has_electric: boolean; has_water: boolean; has_sewer: boolean; rates: Record<string, number>; amenities: string; };
type CampRes = { id: string; site_id: string; guest_name: string; check_in: string; check_out: string; nights: number; guests: number; rate_per_night: number; total_revenue: number; season: string; trail_interest?: string; is_team_group: boolean; };

function ApartmentsTab({ onSeed }: { onSeed: () => void }) {
  const [filter, setFilter] = useState("all");
  const filterMap: Record<string, Record<string, string>> = { all: {}, vacant: { status: "vacant" }, expiring: { status: "expiring" }, active: { status: "active" } };
  const { data: units = [] } = useQuery<Unit[]>({ queryKey: ["apts", filter], queryFn: () => lodgingApi.apartments(filterMap[filter]) });
  const { data: rentRoll } = useQuery({ queryKey: ["rent-roll"], queryFn: lodgingApi.rentRoll });

  return (
    <div>
      {!units.length && (
        <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
          <Home size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>No units seeded yet</p>
          <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed 40 Apartments + Campground</button>
        </div>
      )}

      {rentRoll && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10, marginBottom: 20 }}>
          {[
            { l: "Occupied", v: `${rentRoll.occupied_units}/${rentRoll.total_units}`, c: "#22C55E" },
            { l: "Occupancy", v: `${rentRoll.occupancy_rate}%`, c: GOLD },
            { l: "Monthly Revenue", v: fmt(rentRoll.actual_monthly_revenue), c: GOLD },
            { l: "Annual Revenue", v: fmt(rentRoll.annual_actual), c: GOLD },
            { l: "Vacancy Loss/mo", v: fmt(rentRoll.vacancy_loss_monthly), c: "#EF4444" },
            { l: "Expiring ≤60d", v: rentRoll.leases_expiring_60d, c: "#F97316" },
          ].map(s => (
            <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "10px 12px" }}>
              <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        {[["all","All"],["active","Occupied"],["expiring","Expiring"],["vacant","Vacant"]].map(([k,l]) => (
          <button key={k} onClick={() => setFilter(k)} style={{ background: filter === k ? GOLD : "#0f2744", color: filter === k ? NAVY : "#8aa0bb", border: `1px solid ${filter === k ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10 }}>
        {(units as Unit[]).map((u: Unit) => {
          const tc = UNIT_COLORS[u.unit_type] ?? GOLD;
          const sc = LEASE_COLORS[u.status] ?? "#6B7280";
          return (
            <div key={u.id} style={{ background: "#0f2744", border: `1px solid ${sc}30`, borderRadius: 8, padding: "12px 14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#F0F4FA" }}>{u.unit_number}</span>
                <span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}20`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 6px" }}>{u.status.toUpperCase()}</span>
              </div>
              <p style={{ fontSize: 11, color: tc, fontWeight: 700, marginBottom: 4 }}>{lbl(u.unit_type)}</p>
              <p style={{ fontSize: 12, color: "#8aa0bb" }}>{u.bedrooms}BR / {u.bathrooms}BA · {u.sqft} sqft</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD, marginTop: 6 }}>{fmt(u.monthly_rent)}<span style={{ fontSize: 11, color: "#4a6080" }}>/mo</span></p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CampgroundTab() {
  const { data: sites = [] } = useQuery<Site[]>({ queryKey: ["camp-sites"], queryFn: lodgingApi.campground });
  const { data: reservations = [] } = useQuery<CampRes[]>({ queryKey: ["camp-res"], queryFn: lodgingApi.campRes });
  const { data: rates } = useQuery({ queryKey: ["camp-rates"], queryFn: lodgingApi.campRates });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Trail connections */}
      {rates?.trail_connections && (
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {rates.trail_connections.map((t: any) => (
            <div key={t.name} style={{ background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.25)", borderRadius: 6, padding: "8px 14px", display: "flex", gap: 10, alignItems: "center" }}>
              <span style={{ fontSize: 18 }}>🥾</span>
              <div>
                <p style={{ fontSize: 12, fontWeight: 700, color: "#22C55E" }}>{t.name}</p>
                <p style={{ fontSize: 11, color: "#8aa0bb" }}>{t.type} · {t.miles_to_trailhead} mi to trailhead</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Sites */}
      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>CAMPGROUND SITES ({(sites as Site[]).length})</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 }}>
          {(sites as Site[]).map((s: Site) => {
            const tc = SITE_COLORS[s.site_type] ?? GOLD;
            const hooks = [s.has_electric && "⚡", s.has_water && "💧", s.has_sewer && "🔌"].filter(Boolean);
            return (
              <div key={s.id} style={{ background: `${tc}08`, border: `1px solid ${tc}30`, borderRadius: 8, padding: "12px 14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#F0F4FA" }}>{s.site_number}</span>
                  <span style={{ fontSize: 11, fontWeight: 700, color: tc }}>{lbl(s.site_type).toUpperCase()}</span>
                </div>
                <p style={{ fontSize: 11, color: "#8aa0bb", marginBottom: 4 }}>{s.amenities}</p>
                <p style={{ fontSize: 11, color: "#4a6080", marginBottom: 6 }}>Max {s.max_guests} guests {hooks.join(" ")}</p>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {Object.entries(s.rates).map(([season, rate]) => (
                    <span key={season} style={{ fontSize: 10, color: SEASON_COLORS[season] ?? GOLD, background: `${SEASON_COLORS[season] ?? GOLD}15`, borderRadius: 3, padding: "1px 5px" }}>${rate}<span style={{ opacity: 0.7 }}>/{season.slice(0,3)}</span></span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Upcoming reservations */}
      {(reservations as CampRes[]).length > 0 && (
        <div>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>UPCOMING 30 DAYS</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 10 }}>
            {(reservations as CampRes[]).map((r: CampRes) => {
              const sc = SEASON_COLORS[r.season] ?? GOLD;
              return (
                <div key={r.id} style={{ background: "#0f2744", border: `1px solid ${r.is_team_group ? "rgba(249,115,22,0.3)" : "rgba(201,168,76,0.12)"}`, borderRadius: 8, padding: "12px 14px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA" }}>{r.guest_name}</p>
                    {r.is_team_group && <span style={{ fontSize: 10, color: "#F97316", background: "rgba(249,115,22,0.15)", border: "1px solid rgba(249,115,22,0.3)", borderRadius: 3, padding: "1px 6px", fontWeight: 700 }}>TEAM</span>}
                  </div>
                  <div style={{ fontSize: 12, color: "#8aa0bb", display: "flex", gap: 12, marginBottom: 6 }}>
                    <span>{r.check_in} → {r.check_out}</span>
                    <span>{r.nights}n · {r.guests} guests</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 11, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(r.season)}</span>
                    <span style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(r.total_revenue)}</span>
                  </div>
                  {r.trail_interest && <p style={{ fontSize: 11, color: "#22C55E", marginTop: 4 }}>🥾 {r.trail_interest}</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function RevenueRollupTab() {
  const { data: rollup } = useQuery({ queryKey: ["lodging-rollup"], queryFn: lodgingApi.rollup });
  if (!rollup) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
        {[
          { title: "APARTMENTS", data: rollup.apartments, color: "#60A5FA", items: [
              { l: "Monthly Revenue", v: fmt(rollup.apartments.monthly_revenue) },
              { l: "Annual Revenue",  v: fmt(rollup.apartments.annual_revenue) },
              { l: "Occupancy",       v: `${rollup.apartments.occupancy_rate}%` },
              { l: "Vacancy Loss/mo", v: fmt(rollup.apartments.vacancy_loss_monthly), warn: true },
              { l: "Leases Expiring ≤60d", v: rollup.apartments.leases_expiring_60d, warn: rollup.apartments.leases_expiring_60d > 3 },
          ]},
          { title: "CAMPGROUND", data: rollup.campground, color: "#22C55E", items: [
              { l: "All-Time Revenue", v: fmt(rollup.campground.total_revenue_all_time) },
              { l: "Upcoming Revenue", v: fmt(rollup.campground.upcoming_revenue) },
              { l: "Total Reservations", v: rollup.campground.total_reservations },
              { l: "Trail Connections", v: rollup.campground.trail_connections },
          ]},
          { title: "COMBINED LODGING", data: rollup.combined, color: GOLD, items: [
              { l: "Monthly Revenue", v: fmt(rollup.combined.monthly_lodging_revenue) },
              { l: "Annual Estimate", v: fmt(rollup.combined.annual_lodging_estimate) },
          ]},
        ].map(panel => (
          <div key={panel.title} style={{ background: `${panel.color}08`, border: `1px solid ${panel.color}30`, borderRadius: 10, padding: "18px 20px" }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: panel.color, marginBottom: 14 }}>{panel.title}</p>
            {panel.items.map((item: any) => (
              <div key={item.l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: "#8aa0bb" }}>{item.l}</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: item.warn ? "#F97316" : "#F0F4FA" }}>{item.v}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function AIInsightsTab() {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true); setInsights(null);
    const result = await lodgingApi.aiInsights();
    setInsights(result); setLoading(false);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button onClick={generate} disabled={loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={14} />Generate Lodging Insights</>}
        </button>
      </div>
      {insights ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>AI LODGING STRATEGY BRIEF</p>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{insights.insights}</p>
          </div>
          {insights.trail_connections && (
            <div style={{ background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 8, padding: "14px 18px" }}>
              <p style={{ fontSize: 11, fontWeight: 700, color: "#22C55E", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Trail-Connected Marketing Assets</p>
              {insights.trail_connections.map((t: any) => (
                <p key={t.name} style={{ fontSize: 12, color: "#8aa0bb", marginBottom: 4 }}>🥾 <strong style={{ color: "#F0F4FA" }}>{t.name}</strong> — {t.type} · {t.miles_to_trailhead} miles</p>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
          <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ fontSize: 14, color: "#8aa0bb" }}>Generate AI insights across apartments, campground, and trail connections</p>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id: "apartments",  label: "Apartments",     icon: <Home size={14} /> },
  { id: "campground",  label: "Campground",      icon: <Tent size={14} /> },
  { id: "rollup",      label: "Revenue Rollup",  icon: <BarChart2 size={14} /> },
  { id: "ai",          label: "AI Insights",     icon: <Brain size={14} /> },
];

export default function LodgingPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("apartments");
  const [seeding, setSeeding] = useState(false);
  const { data: rollup } = useQuery({ queryKey: ["lodging-rollup"], queryFn: lodgingApi.rollup });

  const handleSeed = async () => {
    setSeeding(true);
    await lodgingApi.seed();
    ["apts","rent-roll","camp-sites","camp-res","lodging-rollup"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NXS NATIONAL COMPLEX","40 APARTMENTS","30 CAMP SITES","3 TRAIL CONNECTIONS"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 10, flexWrap: "wrap" }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>APARTMENT & CAMPGROUND</h1>
          {rollup && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Monthly: <strong style={{ color: GOLD }}>{fmt(rollup.combined.monthly_lodging_revenue)}</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Annual Est: <strong style={{ color: GOLD }}>{fmt(rollup.combined.annual_lodging_estimate)}</strong></span>
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
        {activeTab === "apartments" && <ApartmentsTab onSeed={handleSeed} />}
        {activeTab === "campground" && <CampgroundTab />}
        {activeTab === "rollup"     && <RevenueRollupTab />}
        {activeTab === "ai"         && <AIInsightsTab />}
      </div>
    </div>
  );
}
