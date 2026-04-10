"use client";

/**
 * SportAI Suite — Equipment Exchange Dashboard
 * /app/equipment/page.tsx
 * Sprint 1 · Level Playing Field Foundation
 *
 * 5 tabs: Inventory · Drop Boxes · Transactions · Sports · AI Insights
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Package, MapPin, ArrowLeftRight, BarChart2, Brain, Plus, RefreshCw, AlertTriangle, Truck } from "lucide-react";

// ── API ───────────────────────────────────────────────────────────────────────

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const eqApi = {
  kpis:         () => fetch(`${API}/api/equipment/kpis`).then(r => r.json()),
  inventory:    (p?) => fetch(`${API}/api/equipment/inventory${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  dropboxes:    () => fetch(`${API}/api/equipment/dropboxes`).then(r => r.json()),
  transactions: (p?) => fetch(`${API}/api/equipment/transactions${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  utilization:  () => fetch(`${API}/api/equipment/utilization`).then(r => r.json()),
  seed:         () => fetch(`${API}/api/equipment/seed`, { method: "POST" }).then(r => r.json()),
  aiInsights:   () => fetch(`${API}/api/equipment/ai-insights`, { method: "POST" }).then(r => r.json()),
  aiRoute:      () => fetch(`${API}/api/equipment/ai-dropbox-route`, { method: "POST" }).then(r => r.json()),
};

// ── Types ─────────────────────────────────────────────────────────────────────

type Item = { id: string; name: string; sport: string; tier: string; condition: string; status: string; size?: string; brand?: string; retail_value: number; rental_rate: number; received_date: string; };
type DropBox = { id: string; name: string; address: string; city: string; state: string; status: string; capacity: number; current_items: number; fill_pct: number; sports_accepted: string; last_pickup_date?: string; next_pickup_date?: string; items_collected_ytd: number; };
type Transaction = { id: string; item_id: string; transaction_type: string; recipient_name?: string; recipient_age?: number; recipient_school?: string; donor_name?: string; rental_revenue: number; transaction_date: string; };
type Util = { sport: string; total_items: number; checked_out: number; utilization_pct: number; };
type KPIs = { total_items: number; available_items: number; checked_out_items: number; utilization_rate: number; active_drop_boxes: number; full_drop_boxes: number; total_exchanges_ytd: number; rental_revenue_total: number; sports_breakdown: Record<string, number>; tier_breakdown: Record<string, number>; };

// ── Helpers ───────────────────────────────────────────────────────────────────

const GOLD = "#C9A84C";
const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const TIER_COLORS: Record<string, string> = {
  manufacturer: "#22C55E",
  consignment:  "#60A5FA",
  rental:       "#A855F7",
};
const CONDITION_COLORS: Record<string, string> = {
  new:       "#22C55E",
  excellent: "#4ade80",
  good:      GOLD,
  fair:      "#F97316",
  poor:      "#EF4444",
};
const STATUS_COLORS: Record<string, string> = {
  available:    "#22C55E",
  checked_out:  "#F97316",
  reserved:     GOLD,
  maintenance:  "#60A5FA",
  retired:      "#6B7280",
};

// ── KPI Strip ─────────────────────────────────────────────────────────────────

function KPIStrip({ kpis }: { kpis: KPIs }) {
  const items = [
    { label: "Total Items",     value: kpis.total_items },
    { label: "Available",       value: kpis.available_items,       color: "#22C55E" },
    { label: "Checked Out",     value: kpis.checked_out_items,     color: "#F97316" },
    { label: "Utilization",     value: `${kpis.utilization_rate}%`, color: GOLD },
    { label: "Drop Boxes",      value: kpis.active_drop_boxes },
    { label: "Youth Served",    value: kpis.total_exchanges_ytd,   color: "#60A5FA" },
    { label: "Rental Revenue",  value: fmt(kpis.rental_revenue_total), color: "#A855F7" },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 10, marginBottom: 24 }}>
      {items.map(item => (
        <div key={item.label} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
          <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", color: "#4a6080", marginBottom: 4 }}>{item.label}</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 24, color: (item.color as string) ?? "#F0F4FA" }}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}

// ── Inventory Tab ─────────────────────────────────────────────────────────────

function InventoryTab({ onSeed }: { onSeed: () => void }) {
  const [tierFilter, setTierFilter] = useState<string>("");
  const [sportFilter, setSportFilter] = useState<string>("");

  const params: Record<string, string> = {};
  if (tierFilter)  params.tier = tierFilter;
  if (sportFilter) params.sport = sportFilter;

  const { data: items = [] } = useQuery<Item[]>({ queryKey: ["equipment-items", tierFilter, sportFilter], queryFn: () => eqApi.inventory(params) });
  const SPORTS = ["flag_football","soccer","lacrosse","volleyball","softball","basketball","pickleball","robotics"];
  const TIERS  = ["manufacturer","consignment","rental"];

  return (
    <div>
      <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
        <select value={tierFilter} onChange={e => setTierFilter(e.target.value)} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "7px 12px", fontSize: 13, fontFamily: "'Barlow Condensed'" }}>
          <option value="">All Tiers</option>
          {TIERS.map(t => <option key={t} value={t}>{lbl(t)}</option>)}
        </select>
        <select value={sportFilter} onChange={e => setSportFilter(e.target.value)} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "7px 12px", fontSize: 13, fontFamily: "'Barlow Condensed'" }}>
          <option value="">All Sports</option>
          {SPORTS.map(s => <option key={s} value={s}>{lbl(s)}</option>)}
        </select>
      </div>

      {items.length === 0 && (
        <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
          <Package size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>No inventory yet</p>
          <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Equipment Inventory</button>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: 10 }}>
        {items.map((item: Item) => {
          const tc = TIER_COLORS[item.tier] ?? GOLD;
          const cc = CONDITION_COLORS[item.condition] ?? GOLD;
          const sc = STATUS_COLORS[item.status] ?? "#6B7280";
          return (
            <div key={item.id} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 8, padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA", flex: 1 }}>{item.name}</p>
                <span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}20`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 6px", marginLeft: 8, flexShrink: 0 }}>
                  {item.status.replace("_", " ").toUpperCase()}
                </span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 8 }}>
                <span style={{ fontSize: 11, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "2px 7px" }}>{lbl(item.tier)}</span>
                <span style={{ fontSize: 11, color: cc, background: `${cc}15`, border: `1px solid ${cc}40`, borderRadius: 3, padding: "2px 7px" }}>{lbl(item.condition)}</span>
              </div>
              <div style={{ fontSize: 12, color: "#8aa0bb" }}>
                <span>{lbl(item.sport)}</span>
                {item.size && <span> · {item.size}</span>}
                {item.brand && <span> · {item.brand}</span>}
              </div>
              {item.retail_value > 0 && <p style={{ fontSize: 12, color: GOLD, marginTop: 4 }}>Value: {fmt(item.retail_value)}</p>}
              {item.rental_rate > 0 && <p style={{ fontSize: 12, color: "#A855F7" }}>Rental: ${item.rental_rate}/session</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Drop Boxes Tab ────────────────────────────────────────────────────────────

function DropBoxesTab() {
  const { data: boxes = [] } = useQuery<DropBox[]>({ queryKey: ["equipment-dropboxes"], queryFn: eqApi.dropboxes });
  const highPriority = (boxes as DropBox[]).filter(b => b.fill_pct >= 60);

  return (
    <div>
      {highPriority.length > 0 && (
        <div style={{ background: "rgba(249,115,22,0.1)", border: "1px solid rgba(249,115,22,0.3)", borderRadius: 8, padding: "12px 16px", marginBottom: 20, display: "flex", gap: 10, alignItems: "center" }}>
          <Truck size={16} style={{ color: "#F97316", flexShrink: 0 }} />
          <p style={{ fontSize: 13, color: "#F97316" }}><strong>{highPriority.length} box{highPriority.length > 1 ? "es" : ""}</strong> at 60%+ capacity — schedule pickup</p>
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
        {(boxes as DropBox[]).map((box: DropBox) => {
          const fillColor = box.fill_pct >= 80 ? "#EF4444" : box.fill_pct >= 60 ? "#F97316" : "#22C55E";
          return (
            <div key={box.id} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 8, padding: "14px 16px" }}>
              <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA", marginBottom: 2 }}>{box.name}</p>
              <p style={{ fontSize: 11, color: "#8aa0bb", marginBottom: 10 }}>{box.address} · {box.city}, {box.state}</p>
              <div style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#8aa0bb", marginBottom: 3 }}>
                  <span>Fill level</span>
                  <span style={{ color: fillColor, fontWeight: 700 }}>{box.fill_pct}% ({box.current_items}/{box.capacity})</span>
                </div>
                <div style={{ height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 3 }}>
                  <div style={{ height: "100%", width: `${Math.min(box.fill_pct, 100)}%`, background: fillColor, borderRadius: 3, transition: "width 0.3s" }} />
                </div>
              </div>
              <div style={{ fontSize: 11, color: "#4a6080" }}>
                {box.last_pickup_date && <span>Last pickup: {box.last_pickup_date}</span>}
                {box.next_pickup_date && <span style={{ display: "block" }}>Next pickup: <span style={{ color: GOLD }}>{box.next_pickup_date}</span></span>}
                <span style={{ display: "block", marginTop: 2 }}>YTD collected: <strong style={{ color: "#F0F4FA" }}>{box.items_collected_ytd}</strong> items</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Transactions Tab ──────────────────────────────────────────────────────────

function TransactionsTab() {
  const { data: txns = [] } = useQuery<Transaction[]>({ queryKey: ["equipment-txns"], queryFn: () => eqApi.transactions() });
  const TXN_COLORS: Record<string, string> = { donation: "#22C55E", exchange: GOLD, rental: "#A855F7", return: "#60A5FA", consignment: "#F97316" };

  return (
    <div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Type","Item","Recipient/Donor","School","Revenue","Date"].map(h => (
                <th key={h} style={{ padding: "8px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(txns as Transaction[]).map((t: Transaction) => {
              const tc = TXN_COLORS[t.transaction_type] ?? GOLD;
              return (
                <tr key={t.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "2px 8px" }}>{t.transaction_type.toUpperCase()}</span></td>
                  <td style={{ padding: "10px 12px", fontSize: 13, color: "#F0F4FA" }}>{t.item_id.slice(0, 8)}…</td>
                  <td style={{ padding: "10px 12px", fontSize: 13, color: "#F0F4FA" }}>{t.recipient_name || t.donor_name || "—"}</td>
                  <td style={{ padding: "10px 12px", fontSize: 12, color: "#8aa0bb" }}>{t.recipient_school || "—"}</td>
                  <td style={{ padding: "10px 12px", fontSize: 13, color: t.rental_revenue > 0 ? "#A855F7" : "#4a6080" }}>{t.rental_revenue > 0 ? fmt(t.rental_revenue) : "—"}</td>
                  <td style={{ padding: "10px 12px", fontSize: 12, color: "#8aa0bb" }}>{t.transaction_date}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Sports Tab ────────────────────────────────────────────────────────────────

function SportsTab() {
  const { data: util = [] } = useQuery<Util[]>({ queryKey: ["equipment-util"], queryFn: eqApi.utilization });
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
      {(util as Util[]).map((u: Util) => {
        const barColor = u.utilization_pct >= 80 ? "#EF4444" : u.utilization_pct >= 50 ? GOLD : "#22C55E";
        return (
          <div key={u.sport} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 8, padding: "16px 18px" }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 6 }}>{lbl(u.sport)}</p>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#8aa0bb", marginBottom: 6 }}>
              <span>{u.checked_out} out / {u.total_items} total</span>
              <span style={{ color: barColor, fontWeight: 700 }}>{u.utilization_pct}%</span>
            </div>
            <div style={{ height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 3 }}>
              <div style={{ height: "100%", width: `${u.utilization_pct}%`, background: barColor, borderRadius: 3 }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── AI Insights Tab ───────────────────────────────────────────────────────────

function AIInsightsTab() {
  const [insights, setInsights] = useState<any>(null);
  const [route, setRoute] = useState<any>(null);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [loadingRoute, setLoadingRoute] = useState(false);

  const generateInsights = async () => {
    setLoadingInsights(true);
    const result = await eqApi.aiInsights();
    setInsights(result);
    setLoadingInsights(false);
  };

  const generateRoute = async () => {
    setLoadingRoute(true);
    const result = await eqApi.aiRoute();
    setRoute(result);
    setLoadingRoute(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA" }}>INVENTORY INSIGHTS</p>
          <button onClick={generateInsights} disabled={loadingInsights} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 13, display: "flex", alignItems: "center", gap: 6 }}>
            {loadingInsights ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={12} />Generate</>}
          </button>
        </div>
        {insights ? (
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px" }}>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap", marginBottom: 16 }}>{insights.insights}</p>
            {insights.boxes_needing_pickup?.length > 0 && (
              <div>
                <p style={{ fontSize: 11, fontWeight: 700, color: "#F97316", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>⚠️ Boxes Needing Pickup</p>
                {insights.boxes_needing_pickup.map((b: any) => (
                  <div key={b.name} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#8aa0bb", marginBottom: 4 }}>
                    <span>{b.name}</span><span style={{ color: "#F97316" }}>{b.fill_pct}% full</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "48px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Click Generate to get AI insights on inventory health</p>
          </div>
        )}
      </div>

      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA" }}>PICKUP ROUTE OPTIMIZER</p>
          <button onClick={generateRoute} disabled={loadingRoute} style={{ background: "#0f2744", color: GOLD, border: `1px solid ${GOLD}`, borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 13, display: "flex", alignItems: "center", gap: 6 }}>
            {loadingRoute ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Routing…</> : <><Truck size={12} />Optimize Route</>}
          </button>
        </div>
        {route ? (
          <div style={{ background: "#0f2744", border: `1px solid rgba(201,168,76,0.3)`, borderRadius: 10, padding: "18px 20px" }}>
            <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
              <div style={{ background: "rgba(201,168,76,0.1)", borderRadius: 6, padding: "8px 12px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 2 }}>HIGH PRIORITY BOXES</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD }}>{route.high_priority_boxes}</p>
              </div>
            </div>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{route.route_recommendation}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "48px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Truck size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Optimize drop box pickup routing from NXS hub</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

const TABS = [
  { id: "inventory",    label: "Inventory",   icon: <Package size={14} /> },
  { id: "dropboxes",   label: "Drop Boxes",  icon: <MapPin size={14} /> },
  { id: "transactions",label: "Transactions",icon: <ArrowLeftRight size={14} /> },
  { id: "sports",      label: "Sports",      icon: <BarChart2 size={14} /> },
  { id: "ai",          label: "AI Insights", icon: <Brain size={14} /> },
];

export default function EquipmentExchangePage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("inventory");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery<KPIs>({ queryKey: ["equipment-kpis"], queryFn: eqApi.kpis });

  const handleSeed = async () => {
    setSeeding(true);
    await eqApi.seed();
    qc.invalidateQueries({ queryKey: ["equipment-kpis"] });
    qc.invalidateQueries({ queryKey: ["equipment-items"] });
    qc.invalidateQueries({ queryKey: ["equipment-dropboxes"] });
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>

      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ background: "#22C55E", borderRadius: 3, padding: "1px 8px" }}>
            <span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: "#071828", letterSpacing: 2 }}>LPF FOUNDATION</span>
          </div>
          <div style={{ background: "rgba(201,168,76,0.15)", borderRadius: 3, padding: "1px 8px" }}>
            <span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>100+ DROP BOXES</span>
          </div>
        </div>
        <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2, marginBottom: 12 }}>EQUIPMENT EXCHANGE</h1>
        <div style={{ display: "flex", gap: 0 }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
              background: "none", border: "none", cursor: "pointer",
              padding: "10px 18px", fontSize: 13, fontWeight: 600, letterSpacing: "0.05em",
              textTransform: "uppercase", fontFamily: "'Barlow Condensed', sans-serif",
              color: activeTab === t.id ? GOLD : "#8aa0bb",
              borderBottom: activeTab === t.id ? `2px solid ${GOLD}` : "2px solid transparent",
              display: "flex", alignItems: "center", gap: 6,
            }}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ padding: "24px 28px" }}>
        {kpis && <KPIStrip kpis={kpis} />}
        {activeTab === "inventory"    && <InventoryTab onSeed={handleSeed} />}
        {activeTab === "dropboxes"    && <DropBoxesTab />}
        {activeTab === "transactions" && <TransactionsTab />}
        {activeTab === "sports"       && <SportsTab />}
        {activeTab === "ai"           && <AIInsightsTab />}
      </div>
    </div>
  );
}
