"use client";
/**
 * SportAI Suite — Foundation Card CRM
 * /app/foundation-card/page.tsx
 * Sprint 2 · Level Playing Field Foundation
 * Tabs: Members · Revenue · Pipeline · AI Strategy
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CreditCard, TrendingUp, Users, Brain, Plus, RefreshCw, AlertTriangle, CheckCircle } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const fcApi = {
  kpis:         () => fetch(`${API}/api/foundation-card/kpis`).then(r => r.json()),
  members:      (p?) => fetch(`${API}/api/foundation-card/members${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  pacing:       () => fetch(`${API}/api/foundation-card/revenue-pacing`).then(r => r.json()),
  tierBenefits: () => fetch(`${API}/api/foundation-card/tier-benefits`).then(r => r.json()),
  seed:         () => fetch(`${API}/api/foundation-card/seed`, { method: "POST" }).then(r => r.json()),
  riskBrief:    () => fetch(`${API}/api/foundation-card/ai-renewal-risk`, { method: "POST" }).then(r => r.json()),
  growthBrief:  () => fetch(`${API}/api/foundation-card/ai-growth-brief`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const TIER_COLORS: Record<string, string> = { individual: "#60A5FA", family: "#22C55E", corporate: "#F97316", charter: GOLD };
const RISK_COLORS: Record<string, string> = { low: "#22C55E", medium: GOLD, high: "#F97316", critical: "#EF4444" };
const STATUS_COLORS: Record<string, string> = { active: "#22C55E", expired: "#EF4444", cancelled: "#6B7280", trial: "#A855F7", pending: GOLD };

type Member = { id: string; full_name: string; email: string; tier: string; status: string; annual_fee: number; member_since: string; expiry_date: string; days_until_expiry: number; is_expiring_soon: boolean; renewal_risk: string; engagement_score: number; visits_ytd: number; redemptions_ytd: number; company_name?: string; family_size: number; };
type KPIs = { active_members: number; target_members: number; member_pacing_pct: number; annual_revenue: number; target_revenue: number; revenue_pacing_pct: number; monthly_revenue: number; at_risk_members: number; expiring_60d: number; avg_engagement_score: number; total_value_redeemed: number; tier_breakdown: Record<string, { members: number; revenue: number }>; };

function GaugeMeter({ value, label, color }: { value: number; label: string; color: string }) {
  const r = 36; const circ = 2 * Math.PI * r;
  const offset = circ - (value / 100) * circ;
  return (
    <div style={{ textAlign: "center" }}>
      <svg width={90} height={90} viewBox="0 0 90 90">
        <circle cx={45} cy={45} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={8} />
        <circle cx={45} cy={45} r={r} fill="none" stroke={color} strokeWidth={8}
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 45 45)" style={{ transition: "stroke-dashoffset 0.5s" }} />
        <text x={45} y={49} textAnchor="middle" fill="#F0F4FA" fontSize={14} fontFamily="'Bebas Neue'" letterSpacing={0.5}>{value}%</text>
      </svg>
      <p style={{ fontSize: 11, color: "#8aa0bb", marginTop: 2 }}>{label}</p>
    </div>
  );
}

function MembersTab({ onSeed }: { onSeed: () => void }) {
  const [filter, setFilter] = useState("all");
  const filterMap: Record<string, Record<string, string>> = {
    all: {}, active: { status: "active" }, at_risk: { renewal_risk: "high" },
    expiring: { expiring_soon: "true" }, corporate: { tier: "corporate" },
  };
  const { data: members = [] } = useQuery<Member[]>({ queryKey: ["fc-members", filter], queryFn: () => fcApi.members(filterMap[filter]) });

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {[["all","All"], ["active","Active"], ["at_risk","At Risk"], ["expiring","Expiring Soon"], ["corporate","Corporate"]].map(([k, l]) => (
          <button key={k} onClick={() => setFilter(k)} style={{ background: filter === k ? GOLD : "#0f2744", color: filter === k ? NAVY : "#8aa0bb", border: `1px solid ${filter === k ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>
            {l}
          </button>
        ))}
      </div>

      {members.length === 0 && (
        <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
          <CreditCard size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>No members yet</p>
          <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Foundation Card Members</button>
        </div>
      )}

      <div style={{ overflowX: "auto" }}>
        {members.length > 0 && (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
                {["Member","Tier","Status","Annual Fee","Engagement","Expires","Risk"].map(h => (
                  <th key={h} style={{ padding: "8px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {members.map((m: Member) => {
                const tc = TIER_COLORS[m.tier] ?? GOLD;
                const sc = STATUS_COLORS[m.status] ?? "#6B7280";
                const rc = RISK_COLORS[m.renewal_risk] ?? "#22C55E";
                return (
                  <tr key={m.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                    <td style={{ padding: "10px 12px" }}>
                      <p style={{ fontWeight: 600, fontSize: 13, color: "#F0F4FA" }}>{m.full_name}</p>
                      <p style={{ fontSize: 11, color: "#4a6080" }}>{m.company_name || m.email}</p>
                    </td>
                    <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "2px 8px" }}>{lbl(m.tier)}</span></td>
                    <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "2px 8px" }}>{m.status.toUpperCase()}</span></td>
                    <td style={{ padding: "10px 12px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(m.annual_fee)}</td>
                    <td style={{ padding: "10px 12px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <div style={{ width: 60, height: 4, background: "rgba(255,255,255,0.08)", borderRadius: 2 }}>
                          <div style={{ height: "100%", width: `${m.engagement_score}%`, background: m.engagement_score >= 60 ? "#22C55E" : m.engagement_score >= 30 ? GOLD : "#EF4444", borderRadius: 2 }} />
                        </div>
                        <span style={{ fontSize: 11, color: "#8aa0bb" }}>{m.engagement_score}</span>
                      </div>
                    </td>
                    <td style={{ padding: "10px 12px", fontSize: 12, color: m.is_expiring_soon ? "#F97316" : "#8aa0bb" }}>{m.expiry_date}{m.is_expiring_soon && " ⚠️"}</td>
                    <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: rc }}>{m.renewal_risk.toUpperCase()}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function RevenueTab() {
  const { data: kpis } = useQuery<KPIs>({ queryKey: ["fc-kpis"], queryFn: fcApi.kpis });
  const { data: pacing } = useQuery({ queryKey: ["fc-pacing"], queryFn: fcApi.pacing });
  const { data: benefits } = useQuery({ queryKey: ["fc-benefits"], queryFn: fcApi.tierBenefits });

  if (!kpis || !pacing) return <p style={{ color: "#8aa0bb", fontSize: 13 }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Revenue pacing */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 10, padding: "20px 24px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, letterSpacing: 1, color: "#F0F4FA", marginBottom: 16 }}>REVENUE PACING — $416K/YR TARGET</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12, marginBottom: 20 }}>
          {[
            { l: "Annual Actual",  v: fmt(kpis.annual_revenue),  c: GOLD },
            { l: "Annual Target",  v: fmt(416000),               c: "#4a6080" },
            { l: "Annual Gap",     v: fmt(pacing.annual_gap),    c: "#EF4444" },
            { l: "Monthly Actual", v: fmt(kpis.monthly_revenue), c: "#60A5FA" },
            { l: "Monthly Target", v: fmt(pacing.monthly_target),c: "#4a6080" },
            { l: "Members Needed", v: pacing.projection_to_hit_target?.new_members_needed, c: "#F97316" },
          ].map(s => (
            <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "10px 14px" }}>
              <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.l}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 32, justifyContent: "center" }}>
          <GaugeMeter value={kpis.revenue_pacing_pct} label="Revenue Pacing" color={kpis.revenue_pacing_pct >= 80 ? "#22C55E" : GOLD} />
          <GaugeMeter value={kpis.member_pacing_pct} label="Member Pacing" color={kpis.member_pacing_pct >= 80 ? "#22C55E" : "#60A5FA"} />
          <GaugeMeter value={Math.min(100, kpis.avg_engagement_score)} label="Avg Engagement" color="#A855F7" />
        </div>
      </div>

      {/* Tier breakdown */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
        {Object.entries(kpis.tier_breakdown).map(([tier, data]) => {
          const tc = TIER_COLORS[tier] ?? GOLD;
          return (
            <div key={tier} style={{ background: `${tc}08`, border: `1px solid ${tc}30`, borderRadius: 8, padding: "16px 18px" }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: tc, marginBottom: 8 }}>{lbl(tier)}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: "#F0F4FA" }}>{data.members}</p>
              <p style={{ fontSize: 12, color: "#8aa0bb" }}>members</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD, marginTop: 6 }}>{fmt(data.revenue)}</p>
              <p style={{ fontSize: 11, color: "#4a6080" }}>annual revenue</p>
            </div>
          );
        })}
      </div>

      {/* Tier benefits */}
      {benefits && (
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "20px 24px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>TIER BENEFIT MATRIX</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 14 }}>
            {Object.entries(benefits).map(([tier, info]: [string, any]) => {
              const tc = TIER_COLORS[tier] ?? GOLD;
              return (
                <div key={tier} style={{ border: `1px solid ${tc}40`, borderRadius: 8, padding: "14px 16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                    <p style={{ fontWeight: 700, color: tc, fontSize: 14 }}>{lbl(tier)}</p>
                    <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{fmt(info.price)}/yr</p>
                  </div>
                  {info.benefits.map((b: string, i: number) => (
                    <div key={i} style={{ display: "flex", gap: 6, marginBottom: 4 }}>
                      <span style={{ color: tc, flexShrink: 0, fontSize: 12 }}>✓</span>
                      <span style={{ fontSize: 12, color: "#8aa0bb" }}>{b}</span>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function AIStrategyTab() {
  const [riskResult, setRiskResult] = useState<any>(null);
  const [growthResult, setGrowthResult] = useState<any>(null);
  const [loadingRisk, setLoadingRisk] = useState(false);
  const [loadingGrowth, setLoadingGrowth] = useState(false);

  const runRisk = async () => { setLoadingRisk(true); setRiskResult(await fcApi.riskBrief()); setLoadingRisk(false); };
  const runGrowth = async () => { setLoadingGrowth(true); setGrowthResult(await fcApi.growthBrief()); setLoadingGrowth(false); };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      {[
        { title: "RENEWAL RISK & WIN-BACK", btn: "Generate Risk Brief", loading: loadingRisk, run: runRisk, result: riskResult,
          extra: riskResult && <p style={{ fontSize: 13, color: "#EF4444", fontWeight: 700, marginTop: 10 }}>Revenue at risk: {fmt(riskResult.revenue_at_risk)}</p> },
        { title: "GROWTH & PIPELINE STRATEGY", btn: "Generate Growth Brief", loading: loadingGrowth, run: runGrowth, result: growthResult, extra: null },
      ].map(panel => (
        <div key={panel.title}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA" }}>{panel.title}</p>
            <button onClick={panel.run} disabled={panel.loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 6 }}>
              {panel.loading ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={12} />{panel.btn}</>}
            </button>
          </div>
          {panel.result ? (
            <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px" }}>
              <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{panel.result.brief}</p>
              {panel.extra}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "48px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
              <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
              <p style={{ fontSize: 13, color: "#8aa0bb" }}>Click generate to get AI strategy</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

const TABS = [
  { id: "members", label: "Members",     icon: <Users size={14} /> },
  { id: "revenue", label: "Revenue",     icon: <TrendingUp size={14} /> },
  { id: "ai",      label: "AI Strategy", icon: <Brain size={14} /> },
];

export default function FoundationCardPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("members");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery<KPIs>({ queryKey: ["fc-kpis"], queryFn: fcApi.kpis });

  const handleSeed = async () => {
    setSeeding(true);
    await fcApi.seed();
    qc.invalidateQueries({ queryKey: ["fc-kpis"] });
    qc.invalidateQueries({ queryKey: ["fc-members"] });
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6 }}>
          <div style={{ background: GOLD, borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: NAVY, letterSpacing: 2 }}>LPF FOUNDATION</span></div>
          <div style={{ background: "rgba(201,168,76,0.15)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>$416K/YR TARGET</span></div>
        </div>
        <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2, marginBottom: 8 }}>FOUNDATION CARD CRM</h1>
        {kpis && (
          <div style={{ display: "flex", gap: 16, marginBottom: 12, flexWrap: "wrap" }}>
            {[
              { l: "Members", v: `${kpis.active_members} / ${kpis.target_members}`, c: "#60A5FA" },
              { l: "Revenue", v: fmt(kpis.annual_revenue), c: GOLD },
              { l: "Pacing",  v: `${kpis.revenue_pacing_pct}%`, c: kpis.revenue_pacing_pct >= 80 ? "#22C55E" : "#F97316" },
              { l: "At Risk", v: kpis.at_risk_members, c: "#EF4444" },
              { l: "Expiring ≤60d", v: kpis.expiring_60d, c: "#F97316" },
            ].map(s => (
              <span key={s.l} style={{ fontSize: 13, color: "#8aa0bb" }}>{s.l}: <strong style={{ color: s.c as string }}>{s.v}</strong></span>
            ))}
          </div>
        )}
        <div style={{ display: "flex", gap: 0 }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{ background: "none", border: "none", cursor: "pointer", padding: "10px 18px", fontSize: 13, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", fontFamily: "'Barlow Condensed'", color: activeTab === t.id ? GOLD : "#8aa0bb", borderBottom: activeTab === t.id ? `2px solid ${GOLD}` : "2px solid transparent", display: "flex", alignItems: "center", gap: 6 }}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </div>
      <div style={{ padding: "24px 28px" }}>
        {activeTab === "members" && <MembersTab onSeed={handleSeed} />}
        {activeTab === "revenue" && <RevenueTab />}
        {activeTab === "ai"      && <AIStrategyTab />}
      </div>
    </div>
  );
}
