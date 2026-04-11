"use client";
/**
 * SportAI Suite — Membership Value Predictor
 * /app/membership-predictor/page.tsx · Sprint 8
 * Tabs: LTV Rankings · Churn Risk · Win-Back · Cohorts · AI Brief
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Star, AlertTriangle, Mail, Users, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const mpApi = {
  kpis:      () => fetch(`${API}/api/membership-predictor/kpis`).then(r => r.json()),
  ltv:       (p?) => fetch(`${API}/api/membership-predictor/ltv-scores${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  churn:     () => fetch(`${API}/api/membership-predictor/churn-risk`).then(r => r.json()),
  winback:   (p?) => fetch(`${API}/api/membership-predictor/win-back-sequences${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  cohorts:   () => fetch(`${API}/api/membership-predictor/cohort-analysis`).then(r => r.json()),
  seed:      () => fetch(`${API}/api/membership-predictor/seed`, { method: "POST" }).then(r => r.json()),
  aiBrief:   () => fetch(`${API}/api/membership-predictor/ai-brief`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
const pct  = (n: number) => `${(n * 100).toFixed(1)}%`;

const TIER_COLORS: Record<string, string> = { explorer: "#60A5FA", active: "#22C55E", elite: GOLD, charter: "#A855F7", corporate: "#F97316" };
const RISK_COLORS: Record<string, string>  = { safe: "#22C55E", watch: GOLD, at_risk: "#F97316", critical: "#EF4444" };
const UPGRADE_COLORS: Record<string, string> = { low: "#6B7280", medium: GOLD, high: "#F97316", very_high: "#22C55E" };

function LTVScoreBar({ score }: { score: number }) {
  const color = score >= 700 ? "#22C55E" : score >= 400 ? GOLD : "#F97316";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ width: 80, height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
        <div style={{ height: "100%", width: `${score / 10}%`, background: color, borderRadius: 3, transition: "width 0.3s" }} />
      </div>
      <span style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color }}>{score}</span>
    </div>
  );
}

function KPIStrip({ kpis }: { kpis: any }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10, marginBottom: 24 }}>
      {[
        { l: "Scored Members",      v: kpis.total_members_scored,      c: "#F0F4FA" },
        { l: "Avg LTV Score",       v: `${kpis.avg_ltv_score}/1000`,   c: GOLD },
        { l: "LTV 12mo",            v: fmt(kpis.total_predicted_ltv_12mo), c: "#22C55E" },
        { l: "Revenue at Risk",     v: fmt(kpis.revenue_at_risk_12mo),  c: "#EF4444" },
        { l: "Churn Rate 30d",      v: pct(kpis.overall_churn_rate_30d), c: kpis.overall_churn_rate_30d < 0.15 ? "#22C55E" : "#F97316" },
        { l: "Upgrade Candidates",  v: kpis.upgrade_candidates,         c: "#22C55E" },
        { l: "Upgrade Potential",   v: fmt(kpis.upgrade_annual_potential), c: GOLD },
        { l: "Pending Win-Back",    v: kpis.pending_win_back_sequences, c: "#F97316" },
      ].map(s => (
        <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "10px 12px" }}>
          <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
        </div>
      ))}
    </div>
  );
}

function LTVTab({ onSeed }: { onSeed: () => void }) {
  const [tierFilter, setTierFilter] = useState("");
  const [sortBy, setSortBy] = useState("ltv_score");
  const params: Record<string, string> = { sort_by: sortBy };
  if (tierFilter) params.tier = tierFilter;
  const { data: scores = [] } = useQuery({ queryKey: ["mp-ltv", tierFilter, sortBy], queryFn: () => mpApi.ltv(params) });

  if (!scores.length && !tierFilter) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Star size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Predictor not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed 40 Member Scores</button>
    </div>
  );

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {[["","All Tiers"],["explorer","Explorer"],["active","Active"],["elite","Elite"],["corporate","Corporate"]].map(([k,l]) => (
            <button key={k} onClick={() => setTierFilter(k)} style={{ background: tierFilter === k ? GOLD : "#0f2744", color: tierFilter === k ? NAVY : "#8aa0bb", border: `1px solid ${tierFilter === k ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 10px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>
          ))}
        </div>
        <select value={sortBy} onChange={e => setSortBy(e.target.value)} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "5px 10px", fontSize: 12, fontFamily: "'Barlow Condensed'", marginLeft: "auto" }}>
          <option value="ltv_score">Sort: LTV Score</option>
          <option value="churn_probability_30d">Sort: Churn Risk</option>
          <option value="predicted_ltv_12mo">Sort: 12mo Value</option>
        </select>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Member","Tier","LTV Score","Churn 30d","Risk","12mo Value","36mo Value","Upgrade"].map(h => (
                <th key={h} style={{ padding: "8px 10px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(scores as any[]).map((s: any) => {
              const tc = TIER_COLORS[s.tier] ?? GOLD;
              const rc = RISK_COLORS[s.churn_risk_band] ?? "#6B7280";
              const uc = UPGRADE_COLORS[s.upgrade_propensity] ?? "#6B7280";
              return (
                <tr key={s.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "9px 10px" }}>
                    <p style={{ fontWeight: 600, fontSize: 13, color: "#F0F4FA" }}>{s.member_name}</p>
                    <p style={{ fontSize: 10, color: "#4a6080" }}>{s.days_since_last_visit}d ago · {s.visits_last_30d} visits/mo</p>
                  </td>
                  <td style={{ padding: "9px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.tier)}</span></td>
                  <td style={{ padding: "9px 10px" }}><LTVScoreBar score={s.ltv_score} /></td>
                  <td style={{ padding: "9px 10px", fontSize: 13, fontWeight: 700, color: s.churn_probability_30d > 0.3 ? "#EF4444" : s.churn_probability_30d > 0.15 ? "#F97316" : "#22C55E" }}>{pct(s.churn_probability_30d)}</td>
                  <td style={{ padding: "9px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: rc, background: `${rc}15`, border: `1px solid ${rc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.churn_risk_band)}</span></td>
                  <td style={{ padding: "9px 10px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(s.predicted_ltv_12mo)}</td>
                  <td style={{ padding: "9px 10px", fontSize: 12, color: "#8aa0bb" }}>{fmt(s.predicted_ltv_36mo)}</td>
                  <td style={{ padding: "9px 10px" }}>
                    {s.upgrade_propensity !== "low" && (
                      <span style={{ fontSize: 10, fontWeight: 700, color: uc, background: `${uc}15`, border: `1px solid ${uc}40`, borderRadius: 3, padding: "1px 6px" }}>
                        {lbl(s.upgrade_propensity)} {s.upgrade_target_tier ? `→ ${lbl(s.upgrade_target_tier)}` : ""}
                      </span>
                    )}
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

function ChurnRiskTab() {
  const { data: churn } = useQuery({ queryKey: ["mp-churn"], queryFn: mpApi.churn });
  if (!churn) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: 8, padding: "14px 18px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p style={{ fontSize: 14, color: "#EF4444" }}>Total revenue at risk (at-risk + critical)</p>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: "#EF4444" }}>{fmt(churn.total_revenue_at_risk_12mo)}</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        {Object.entries(churn.bands).map(([band, data]: [string, any]) => {
          const rc = RISK_COLORS[band] ?? "#6B7280";
          return (
            <div key={band} style={{ background: `${rc}08`, border: `1px solid ${rc}30`, borderRadius: 10, padding: "14px 16px" }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: rc, marginBottom: 6 }}>{lbl(band)}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 36, color: "#F0F4FA" }}>{data.count}</p>
              <p style={{ fontSize: 12, color: "#8aa0bb", marginTop: 4 }}>{fmt(data.revenue_at_risk_12mo)} at risk</p>
              <p style={{ fontSize: 11, color: "#4a6080" }}>{pct(data.avg_churn_30d || 0)} avg churn</p>
              {data.members && data.members.slice(0, 3).map((m: any) => (
                <div key={m.member_name} style={{ marginTop: 6, padding: "4px 8px", background: "rgba(0,0,0,0.2)", borderRadius: 4, fontSize: 11 }}>
                  <p style={{ color: "#F0F4FA" }}>{m.member_name}</p>
                  <p style={{ color: "#4a6080" }}>{fmt(m.monthly_fee)}/mo · {m.days_since_visit}d ago</p>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WinBackTab() {
  const { data: sequences = [] } = useQuery({ queryKey: ["mp-winback"], queryFn: () => mpApi.winback({ status: "pending" }) });
  const totalAtRisk = (sequences as any[]).reduce((s: number, w: any) => s + w.revenue_at_risk, 0);

  return (
    <div>
      {(sequences as any[]).length > 0 && (
        <div style={{ background: "rgba(249,115,22,0.08)", border: "1px solid rgba(249,115,22,0.25)", borderRadius: 8, padding: "12px 16px", marginBottom: 16, display: "flex", justifyContent: "space-between" }}>
          <p style={{ fontSize: 13, color: "#F97316" }}><strong>{(sequences as any[]).length}</strong> win-back sequences pending</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F97316" }}>{fmt(totalAtRisk)} at risk</p>
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {(sequences as any[]).map((s: any) => {
          const rc = RISK_COLORS[s.churn_risk_band] ?? GOLD;
          const tc = TIER_COLORS[s.tier] ?? GOLD;
          return (
            <div key={s.id} style={{ background: "#0f2744", border: `1px solid ${rc}30`, borderRadius: 8, padding: "14px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                <div>
                  <div style={{ display: "flex", gap: 6, marginBottom: 5 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: rc, background: `${rc}15`, border: `1px solid ${rc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.churn_risk_band)}</span>
                    <span style={{ fontSize: 10, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.tier)}</span>
                  </div>
                  <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 3 }}>{s.member_name}</p>
                  <p style={{ fontSize: 12, color: GOLD, fontWeight: 700 }}>📧 {s.subject_line}</p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#EF4444" }}>{fmt(s.revenue_at_risk)}</p>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>at risk</p>
                  <p style={{ fontSize: 12, color: GOLD, marginTop: 4 }}>Offer: {lbl(s.offer_type)} (${s.offer_value})</p>
                </div>
              </div>
              {s.scheduled_send && <p style={{ fontSize: 11, color: "#4a6080" }}>📅 Scheduled: {s.scheduled_send}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CohortsTab() {
  const { data: cohorts = [] } = useQuery({ queryKey: ["mp-cohorts"], queryFn: mpApi.cohorts });
  const quarters = [...new Set((cohorts as any[]).map((c: any) => c.join_quarter))].sort();

  return (
    <div style={{ overflowX: "auto" }}>
      <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>COHORT RETENTION BY JOIN QUARTER + TIER</p>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
            {["Cohort","Tier","Members","Avg LTV","Churn 30d","Retention 90d","Monthly Rev"].map(h => (
              <th key={h} style={{ padding: "8px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(cohorts as any[]).map((c: any) => {
            const tc = TIER_COLORS[c.tier] ?? GOLD;
            const retColor = c.retention_rate_90d >= 0.85 ? "#22C55E" : c.retention_rate_90d >= 0.70 ? GOLD : "#F97316";
            return (
              <tr key={c.cohort_label} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <td style={{ padding: "9px 12px", fontSize: 12, color: "#8aa0bb", fontWeight: 600 }}>{c.join_quarter}</td>
                <td style={{ padding: "9px 12px" }}><span style={{ fontSize: 10, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(c.tier)}</span></td>
                <td style={{ padding: "9px 12px", fontSize: 13, color: "#F0F4FA" }}>{c.member_count}</td>
                <td style={{ padding: "9px 12px" }}><LTVScoreBar score={c.avg_ltv_score} /></td>
                <td style={{ padding: "9px 12px", fontSize: 12, color: c.avg_churn_30d > 0.2 ? "#F97316" : "#22C55E" }}>{pct(c.avg_churn_30d)}</td>
                <td style={{ padding: "9px 12px", fontSize: 13, fontWeight: 700, color: retColor }}>{Math.round(c.retention_rate_90d * 100)}%</td>
                <td style={{ padding: "9px 12px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(c.avg_monthly_revenue)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function AIBriefTab() {
  const [brief, setBrief] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button onClick={async () => { setLoading(true); setBrief(await mpApi.aiBrief()); setLoading(false); }} disabled={loading}
          style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={14} />Generate AI Retention Brief</>}
        </button>
      </div>
      {brief ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>AI MEMBERSHIP RETENTION BRIEF</p>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{brief.brief}</p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10 }}>
            {[
              { l: "Avg LTV Score",    v: `${brief.kpis.avg_ltv_score}/1000`, c: GOLD },
              { l: "Revenue at Risk",  v: fmt(brief.kpis.revenue_at_risk_12mo), c: "#EF4444" },
              { l: "Upgrade Potential",v: fmt(brief.kpis.upgrade_annual_potential), c: "#22C55E" },
              { l: "Churn Rate 30d",   v: pct(brief.kpis.overall_churn_rate_30d), c: "#F97316" },
            ].map(s => (
              <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 7, padding: "10px 12px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 3 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
          <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ fontSize: 14, color: "#8aa0bb" }}>Generate AI membership retention and upgrade strategy</p>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id: "ltv",     label: "LTV Rankings",  icon: <Star size={14} /> },
  { id: "churn",   label: "Churn Risk",    icon: <AlertTriangle size={14} /> },
  { id: "winback", label: "Win-Back",      icon: <Mail size={14} /> },
  { id: "cohorts", label: "Cohort Analysis",icon: <Users size={14} /> },
  { id: "ai",      label: "AI Brief",      icon: <Brain size={14} /> },
];

export default function MembershipPredictorPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("ltv");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery({ queryKey: ["mp-kpis"], queryFn: mpApi.kpis });

  const handleSeed = async () => {
    setSeeding(true);
    await mpApi.seed();
    ["mp-kpis","mp-ltv","mp-churn","mp-winback","mp-cohorts"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NEXUS DOMES INC.","CHURN PREDICTION","LTV SCORING","WIN-BACK ENGINE"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>MEMBERSHIP VALUE PREDICTOR</h1>
          {kpis && !kpis.error && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>At Risk: <strong style={{ color: "#EF4444" }}>{fmt(kpis.revenue_at_risk_12mo)}</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Upgrade: <strong style={{ color: "#22C55E" }}>{kpis.upgrade_candidates} candidates</strong></span>
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
        {kpis && !kpis.error && <KPIStrip kpis={kpis} />}
        {activeTab === "ltv"     && <LTVTab onSeed={handleSeed} />}
        {activeTab === "churn"   && <ChurnRiskTab />}
        {activeTab === "winback" && <WinBackTab />}
        {activeTab === "cohorts" && <CohortsTab />}
        {activeTab === "ai"      && <AIBriefTab />}
      </div>
    </div>
  );
}
