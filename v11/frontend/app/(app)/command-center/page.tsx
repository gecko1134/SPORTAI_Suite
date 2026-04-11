"use client";
/**
 * SportAI Suite — Cross-Entity Command Center
 * /app/command-center/page.tsx · Sprint 9 · Final Integration Capstone
 * Tabs: Overview · Entity Health · Anomalies · AI Summaries · Entity Deep-Dive
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { LayoutDashboard, Activity, AlertTriangle, Brain, Building2, RefreshCw, CheckCircle } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const ccApi = {
  kpis:          () => fetch(`${API}/api/command-center/v11-kpi-dashboard`).then(r => r.json()),
  health:        () => fetch(`${API}/api/command-center/entity-health-scores`).then(r => r.json()),
  anomalies:     (p?) => fetch(`${API}/api/command-center/anomaly-alerts${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  summaries:     () => fetch(`${API}/api/command-center/executive-summaries`).then(r => r.json()),
  seed:          () => fetch(`${API}/api/command-center/seed`, { method: "POST" }).then(r => r.json()),
  execSummary:   (period: string) => fetch(`${API}/api/command-center/executive-summary?period=${period}`, { method: "POST" }).then(r => r.json()),
  entityBrief:   (entity: string) => fetch(`${API}/api/command-center/entity-brief/${entity}`, { method: "POST" }).then(r => r.json()),
  resolveAlert:  (id: string) => fetch(`${API}/api/command-center/anomaly-alerts/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resolved: true }) }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const pct  = (n: number, d = 1) => `${n.toFixed(d)}%`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const ENTITY_CONFIG = {
  nexus_domes:          { label: "Nexus Domes Inc.",   color: GOLD,      bg: "rgba(201,168,76,0.08)",   border: "rgba(201,168,76,0.25)",   icon: "🏢" },
  nxs_national_complex: { label: "NXS National Complex", color: "#60A5FA", bg: "rgba(96,165,250,0.08)",   border: "rgba(96,165,250,0.25)",   icon: "🏟️" },
  lpf_foundation:       { label: "LPF Foundation",     color: "#22C55E", bg: "rgba(34,197,94,0.08)",    border: "rgba(34,197,94,0.25)",    icon: "🎯" },
  ngp_development:      { label: "NGP Development",    color: "#F97316", bg: "rgba(249,115,22,0.08)",   border: "rgba(249,115,22,0.25)",   icon: "🏗️" },
};

const ANOMALY_COLORS = { critical: "#EF4444", warning: "#F97316", info: GOLD };

function EntityHealthGauge({ entity, score, subScores }: { entity: string; score: number; subScores: any }) {
  const cfg = (ENTITY_CONFIG as any)[entity];
  const r = 44; const circ = 2 * Math.PI * r;
  const color = score >= 80 ? "#22C55E" : score >= 65 ? GOLD : "#F97316";

  return (
    <div style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, borderRadius: 10, padding: "16px 18px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
        <span style={{ fontSize: 22 }}>{cfg.icon}</span>
        <p style={{ fontWeight: 700, fontSize: 14, color: cfg.color }}>{cfg.label}</p>
      </div>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <svg width={105} height={105} viewBox="0 0 105 105">
          <circle cx={52.5} cy={52.5} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={10} />
          <circle cx={52.5} cy={52.5} r={r} fill="none" stroke={color} strokeWidth={10}
            strokeDasharray={circ} strokeDashoffset={circ - (score / 100) * circ}
            strokeLinecap="round" transform="rotate(-90 52.5 52.5)" style={{ transition: "stroke-dashoffset 0.7s" }} />
          <text x={52.5} y={48} textAnchor="middle" fill="#F0F4FA" fontSize={22} fontFamily="'Bebas Neue'">{score}</text>
          <text x={52.5} y={63} textAnchor="middle" fill={color} fontSize={9} fontFamily="'Barlow Condensed'" fontWeight={700}>HEALTH</text>
        </svg>
        <div style={{ flex: 1 }}>
          {[["Revenue", subScores.revenue_score], ["Ops", subScores.operations_score], ["Growth", subScores.growth_score], ["Compliance", subScores.compliance_score]].map(([l, v]) => {
            const c = (v as number) >= 80 ? "#22C55E" : (v as number) >= 60 ? GOLD : "#F97316";
            return (
              <div key={l} style={{ marginBottom: 5 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#8aa0bb", marginBottom: 2 }}>
                  <span>{l}</span><span style={{ color: c }}>{v}</span>
                </div>
                <div style={{ height: 3, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                  <div style={{ height: "100%", width: `${v}%`, background: c, borderRadius: 2 }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ kpis }: { kpis: any }) {
  if (!kpis) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  const cx = kpis.cross_entity;
  const nxs = kpis.nxs_complex;
  const nd = kpis.nexus_domes;
  const lpf = kpis.lpf_foundation;
  const ngp = kpis.ngp_development;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Platform pulse */}
      <div style={{ background: "#0f2744", border: `1px solid ${GOLD}40`, borderRadius: 10, padding: "20px 24px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 13, color: "#4a6080", letterSpacing: 2, marginBottom: 6 }}>ENTERPRISE PLATFORM PULSE</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10 }}>
          {[
            { l: "12mo Revenue Est.",   v: fmt(cx.total_platform_revenue_12mo_est), c: GOLD },
            { l: "Phase 1 Target",      v: fmt(cx.phase1_revenue_target),           c: "#4a6080" },
            { l: "Pacing",             v: pct(cx.phase1_pacing_pct),               c: cx.phase1_pacing_pct >= 80 ? "#22C55E" : "#F97316" },
            { l: "Active Modules",     v: `${cx.modules_active}`,                  c: "#F0F4FA" },
            { l: "Open Anomalies",     v: cx.open_anomalies,                        c: cx.open_anomalies > 3 ? "#F97316" : "#22C55E" },
            { l: "Critical Alerts",    v: cx.critical_anomalies,                   c: cx.critical_anomalies > 0 ? "#EF4444" : "#22C55E" },
          ].map(s => (
            <div key={s.l} style={{ background: "#152f52", borderRadius: 7, padding: "10px 12px" }}>
              <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Entity summaries */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* NXS Complex */}
        <div style={{ background: "rgba(96,165,250,0.06)", border: "1px solid rgba(96,165,250,0.2)", borderRadius: 10, padding: "16px 18px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: "#60A5FA", marginBottom: 12 }}>🏟️ NXS NATIONAL COMPLEX</p>
          {[
            ["Hotel Occupancy", `${nxs.hotel.occupancy_pct}%`, nxs.hotel.occupancy_pct >= 70 ? "#22C55E" : "#F97316"],
            ["ADR / RevPAR", `$${nxs.hotel.adr} / $${nxs.hotel.revpar}`, GOLD],
            ["Apt Occupancy", `${nxs.lodging.apartment_occupancy_pct}%`, "#22C55E"],
            ["Rent Roll/mo", fmt(nxs.lodging.monthly_rent_roll), GOLD],
            ["Rink Util.", `${nxs.rink.utilization_pct}%`, "#60A5FA"],
            ["F&B Per Cap", `$${nxs.fnb.avg_per_cap} / $${nxs.fnb.per_cap_target}`, nxs.fnb.avg_per_cap >= nxs.fnb.per_cap_target ? "#22C55E" : "#F97316"],
            ["Academic Rev", fmt(nxs.academic.annual_contract_revenue), GOLD],
          ].map(([l, v, c]) => (
            <div key={l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 5, fontSize: 12 }}>
              <span style={{ color: "#8aa0bb" }}>{l}</span>
              <span style={{ color: c as string, fontWeight: 700 }}>{v}</span>
            </div>
          ))}
        </div>

        {/* Nexus Domes */}
        <div style={{ background: "rgba(201,168,76,0.06)", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 10, padding: "16px 18px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD, marginBottom: 12 }}>🏢 NEXUS DOMES INC.</p>
          {[
            ["Members", `${nd.membership.total_members.toLocaleString()} / ${nd.membership.target_members.toLocaleString()}`, GOLD],
            ["Member Pacing", pct(nd.membership.member_pacing_pct), nd.membership.member_pacing_pct >= 60 ? "#22C55E" : "#F97316"],
            ["Foundation Card", `${pct(nd.foundation_card.pacing_pct)} of ${fmt(nd.foundation_card.revenue_target)}`, GOLD],
            ["At-Risk Members", nd.membership.at_risk_count, nd.membership.at_risk_count > 5 ? "#F97316" : "#22C55E"],
            ["Upgrade Candidates", nd.membership.upgrade_candidates, "#22C55E"],
            ["Upgrade Potential", fmt(nd.membership.upgrade_potential_annual), "#22C55E"],
            ["Sponsor Revenue", fmt(nd.sponsorship.total_sponsor_revenue), GOLD],
          ].map(([l, v, c]) => (
            <div key={l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 5, fontSize: 12 }}>
              <span style={{ color: "#8aa0bb" }}>{l}</span>
              <span style={{ color: c as string, fontWeight: 700 }}>{v}</span>
            </div>
          ))}
        </div>

        {/* LPF */}
        <div style={{ background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 10, padding: "16px 18px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: "#22C55E", marginBottom: 12 }}>🎯 LEVEL PLAYING FIELD FOUNDATION</p>
          {[
            ["Grants Awarded", fmt(lpf.grants.total_awarded), "#22C55E"],
            ["Grant Pipeline", fmt(lpf.grants.in_pipeline), GOLD],
            ["Win Rate", pct(lpf.grants.win_rate_pct), "#22C55E"],
            ["NIL Athletes", lpf.nil_program.active_athletes, "#60A5FA"],
            ["NIL Deals Expiring", lpf.nil_program.deals_expiring_30d, lpf.nil_program.deals_expiring_30d > 3 ? "#F97316" : "#22C55E"],
            ["Scholarship Util.", pct(lpf.scholarships.utilization_pct), lpf.scholarships.utilization_pct >= 60 ? "#22C55E" : "#F97316"],
            ["Drop Boxes", lpf.equipment_exchange.active_drop_boxes, "#22C55E"],
          ].map(([l, v, c]) => (
            <div key={l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 5, fontSize: 12 }}>
              <span style={{ color: "#8aa0bb" }}>{l}</span>
              <span style={{ color: c as string, fontWeight: 700 }}>{v}</span>
            </div>
          ))}
        </div>

        {/* NGP */}
        <div style={{ background: "rgba(249,115,22,0.06)", border: "1px solid rgba(249,115,22,0.2)", borderRadius: 10, padding: "16px 18px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: "#F97316", marginBottom: 12 }}>🏗️ NGP DEVELOPMENT</p>
          {[
            ["Capital Committed", pct(ngp.capital_stack.committed_pct), ngp.capital_stack.committed_pct >= 85 ? "#22C55E" : "#F97316"],
            ["Capital Gap", fmt(ngp.capital_stack.total_gap), "#EF4444"],
            ["Projected IRR", `${ngp.capital_stack.projected_irr}%`, ngp.capital_stack.projected_irr >= ngp.capital_stack.target_irr ? "#22C55E" : "#F97316"],
            ["Skill Shot Bays", `${ngp.skill_shot.bays_operational}/10`, "#60A5FA"],
            ["Launch Readiness", `${ngp.skill_shot.launch_readiness_score}/100`, ngp.skill_shot.launch_readiness_score >= 70 ? "#22C55E" : "#F97316"],
            ["PuttView ROI", `${ngp.puttview.current_roi_pct}%`, ngp.puttview.current_roi_pct >= ngp.puttview.target_roi_pct ? "#22C55E" : "#F97316"],
            ["TID Assessed (12mo)", fmt(ngp.tid.total_tid_assessed_12mo), GOLD],
          ].map(([l, v, c]) => (
            <div key={l} style={{ display: "flex", justifyContent: "space-between", marginBottom: 5, fontSize: 12 }}>
              <span style={{ color: "#8aa0bb" }}>{l}</span>
              <span style={{ color: c as string, fontWeight: 700 }}>{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function EntityHealthTab({ onSeed }: { onSeed: () => void }) {
  const { data: health = [] } = useQuery({ queryKey: ["cc-health"], queryFn: ccApi.health });

  if (!health.length || (health[0] as any)?.notes?.includes("Not seeded")) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Activity size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Command Center not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Command Center</button>
    </div>
  );

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
      {(health as any[]).map((h: any) => (
        <EntityHealthGauge key={h.entity} entity={h.entity} score={h.health_score} subScores={h} />
      ))}
    </div>
  );
}

function AnomaliesTab() {
  const qc = useQueryClient();
  const { data: anomalies } = useQuery({ queryKey: ["cc-anomalies"], queryFn: () => ccApi.anomalies() });
  const [resolving, setResolving] = useState<string | null>(null);

  const resolve = async (id: string) => {
    setResolving(id);
    await ccApi.resolveAlert(id);
    qc.invalidateQueries({ queryKey: ["cc-anomalies"] });
    setResolving(null);
  };

  if (!anomalies) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Summary bar */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        {[["critical","Critical",anomalies.critical],["warning","Warning",anomalies.warnings],["info","Info",anomalies.info]].map(([level,label,count]) => {
          const c = (ANOMALY_COLORS as any)[level];
          return (
            <div key={level} style={{ background: `${c}10`, border: `1px solid ${c}30`, borderRadius: 8, padding: "12px 16px", textAlign: "center" }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 36, color: c }}>{count}</p>
              <p style={{ fontSize: 11, color: "#8aa0bb" }}>{label} Alerts</p>
            </div>
          );
        })}
      </div>

      {/* Alerts by level */}
      {(["critical","warning","info"] as const).map(level => {
        const levelAlerts = anomalies.alerts[level];
        if (!levelAlerts?.length) return null;
        const c = ANOMALY_COLORS[level];
        return (
          <div key={level}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: c, marginBottom: 10 }}>
              {level.toUpperCase()} ({levelAlerts.length})
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {levelAlerts.map((a: any) => {
                const entityCfg = (ENTITY_CONFIG as any)[a.entity] || {};
                return (
                  <div key={a.id} style={{ background: `${c}08`, border: `1px solid ${c}30`, borderRadius: 8, padding: "14px 16px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10 }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", gap: 6, marginBottom: 5 }}>
                          <span style={{ fontSize: 10, fontWeight: 700, color: c, background: `${c}15`, border: `1px solid ${c}40`, borderRadius: 3, padding: "1px 6px" }}>{level.toUpperCase()}</span>
                          <span style={{ fontSize: 10, color: "#8aa0bb", background: "#152f52", borderRadius: 3, padding: "1px 6px" }}>{a.module}</span>
                          <span style={{ fontSize: 10, color: entityCfg.color, background: entityCfg.bg || "#152f52", borderRadius: 3, padding: "1px 6px" }}>{entityCfg.icon} {entityCfg.label}</span>
                        </div>
                        <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA", marginBottom: 4 }}>{a.title}</p>
                        <p style={{ fontSize: 12, color: "#8aa0bb", lineHeight: 1.5 }}>{a.description}</p>
                        <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: 11 }}>
                          <span style={{ color: "#4a6080" }}>Metric: {a.metric_name}</span>
                          <span style={{ color: c }}>Actual: {a.metric_value}</span>
                          <span style={{ color: "#22C55E" }}>Expected: {a.expected_value}</span>
                          <span style={{ color: c }}>Deviation: {a.deviation_pct > 0 ? "+" : ""}{a.deviation_pct}%</span>
                        </div>
                      </div>
                      <button onClick={() => resolve(a.id)} disabled={resolving === a.id}
                        style={{ background: "rgba(34,197,94,0.1)", color: "#22C55E", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 5, padding: "6px 12px", fontSize: 11, cursor: "pointer", display: "flex", alignItems: "center", gap: 4, flexShrink: 0 }}>
                        {resolving === a.id ? <RefreshCw size={11} style={{ animation: "spin 1s linear infinite" }} /> : <CheckCircle size={11} />}
                        Resolve
                      </button>
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

function AISummaryTab() {
  const [period, setPeriod] = useState<"weekly" | "monthly" | "annual">("weekly");
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { data: history = [] } = useQuery({ queryKey: ["cc-summaries"], queryFn: ccApi.summaries });

  const generate = async () => {
    setLoading(true); setSummary(null);
    setSummary(await ccApi.execSummary(period));
    setLoading(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 20 }}>
      <div>
        <div style={{ display: "flex", gap: 8, marginBottom: 14, alignItems: "center" }}>
          {(["weekly","monthly","annual"] as const).map(p => (
            <button key={p} onClick={() => setPeriod(p)} style={{ background: period === p ? GOLD : "#0f2744", color: period === p ? NAVY : "#8aa0bb", border: `1px solid ${period === p ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{lbl(p)}</button>
          ))}
          <button onClick={generate} disabled={loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 18px", fontWeight: 700, cursor: "pointer", fontSize: 13, display: "flex", alignItems: "center", gap: 6, marginLeft: "auto" }}>
            {loading ? <><RefreshCw size={13} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={13} />Generate {lbl(period)} Summary</>}
          </button>
        </div>

        {summary ? (
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
              <span style={{ fontFamily: "'Bebas Neue'", fontSize: 14, color: GOLD, letterSpacing: 1 }}>{summary.period_label.toUpperCase()}</span>
              {summary.entity_health && Object.entries(summary.entity_health).map(([e, score]: [string, any]) => {
                const cfg = (ENTITY_CONFIG as any)[e];
                return cfg ? <span key={e} style={{ fontSize: 11, color: cfg.color, background: cfg.bg, border: `1px solid ${cfg.border}`, borderRadius: 3, padding: "2px 8px" }}>{cfg.icon} {score}/100</span> : null;
              })}
            </div>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{summary.summary}</p>
            <div style={{ marginTop: 14, display: "flex", gap: 10, flexWrap: "wrap" }}>
              {[
                { l: "Platform Pacing", v: `${summary.platform_pacing_pct}%`, c: summary.platform_pacing_pct >= 80 ? "#22C55E" : "#F97316" },
                { l: "Critical Alerts", v: summary.critical_alerts, c: summary.critical_alerts > 0 ? "#EF4444" : "#22C55E" },
              ].map(s => (
                <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "8px 14px" }}>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>{s.l}</p>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={40} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 14px" }} />
            <p style={{ fontSize: 14, color: "#8aa0bb" }}>Generate {period} executive summary across all 4 entities</p>
          </div>
        )}
      </div>

      {/* Summary history */}
      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: "#F0F4FA", marginBottom: 10 }}>HISTORY</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {(history as any[]).map((s: any) => (
            <div key={s.id} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 7, padding: "10px 12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: GOLD }}>{lbl(s.period)}</span>
                <span style={{ fontSize: 10, color: "#4a6080" }}>{new Date(s.generated_at).toLocaleDateString()}</span>
              </div>
              <p style={{ fontSize: 11, color: "#8aa0bb" }}>{s.period_label}</p>
              <p style={{ fontSize: 11, color: "#4a6080", marginTop: 3 }}>{s.summary_preview}</p>
            </div>
          ))}
          {(history as any[]).length === 0 && <p style={{ fontSize: 12, color: "#4a6080" }}>No summaries generated yet</p>}
        </div>
      </div>
    </div>
  );
}

function EntityDeepDiveTab() {
  const [selectedEntity, setSelectedEntity] = useState<string>("nexus_domes");
  const [brief, setBrief] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true); setBrief(null);
    setBrief(await ccApi.entityBrief(selectedEntity));
    setLoading(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 20 }}>
      <div>
        <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Select Entity</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {Object.entries(ENTITY_CONFIG).map(([key, cfg]) => (
            <div key={key} onClick={() => { setSelectedEntity(key); setBrief(null); }}
              style={{ background: selectedEntity === key ? cfg.bg : "#0f2744", border: `1px solid ${selectedEntity === key ? cfg.color : "rgba(201,168,76,0.12)"}`, borderRadius: 8, padding: "12px 14px", cursor: "pointer", transition: "all 0.15s" }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span style={{ fontSize: 20 }}>{cfg.icon}</span>
                <p style={{ fontSize: 13, fontWeight: 700, color: selectedEntity === key ? cfg.color : "#F0F4FA" }}>{cfg.label}</p>
              </div>
            </div>
          ))}
        </div>
        <button onClick={generate} disabled={loading} style={{ width: "100%", background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px", fontWeight: 700, cursor: "pointer", fontSize: 13, marginTop: 12, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={13} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Building2 size={13} />Generate Entity Brief</>}
        </button>
      </div>

      <div>
        {brief ? (
          <div style={{ background: "#0f2744", border: `1px solid ${(ENTITY_CONFIG as any)[selectedEntity]?.color || GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <div style={{ display: "flex", gap: 10, marginBottom: 14, alignItems: "center" }}>
              <span style={{ fontSize: 24 }}>{(ENTITY_CONFIG as any)[selectedEntity]?.icon}</span>
              <div>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F0F4FA" }}>{(ENTITY_CONFIG as any)[selectedEntity]?.label}</p>
                <p style={{ fontSize: 12, color: "#8aa0bb" }}>Health Score: <span style={{ color: brief.health_score >= 80 ? "#22C55E" : GOLD, fontWeight: 700 }}>{brief.health_score}/100</span> · {brief.open_alerts} open alerts</p>
              </div>
            </div>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{brief.brief}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Building2 size={40} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 14px" }} />
            <p style={{ fontSize: 14, color: "#8aa0bb" }}>Select an entity and generate a focused brief</p>
          </div>
        )}
      </div>
    </div>
  );
}

const TABS = [
  { id: "overview",  label: "Overview",       icon: <LayoutDashboard size={14} /> },
  { id: "health",    label: "Entity Health",  icon: <Activity size={14} /> },
  { id: "anomalies", label: "Anomalies",      icon: <AlertTriangle size={14} /> },
  { id: "summaries", label: "AI Summaries",   icon: <Brain size={14} /> },
  { id: "deepdive",  label: "Entity Brief",   icon: <Building2 size={14} /> },
];

export default function CommandCenterPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("overview");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery({ queryKey: ["cc-kpis"], queryFn: ccApi.kpis });
  const { data: anomalies } = useQuery({ queryKey: ["cc-anomalies"], queryFn: () => ccApi.anomalies() });

  const handleSeed = async () => {
    setSeeding(true);
    await ccApi.seed();
    ["cc-health","cc-anomalies","cc-summaries"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  const criticalCount = anomalies?.critical || 0;

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["4 ENTITIES","15 MODULES","CEO-LEVEL DASHBOARD","ANOMALY DETECTION"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
          {criticalCount > 0 && <div style={{ background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: "#EF4444", letterSpacing: 2 }}>⚠️ {criticalCount} CRITICAL</span></div>}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>CROSS-ENTITY COMMAND CENTER</h1>
          {kpis && <span style={{ fontSize: 13, color: "#8aa0bb", marginBottom: 6 }}>Phase 1 Pacing: <strong style={{ color: kpis.cross_entity.phase1_pacing_pct >= 80 ? "#22C55E" : "#F97316" }}>{kpis.cross_entity.phase1_pacing_pct}%</strong> of {fmt(kpis.cross_entity.phase1_revenue_target)}</span>}
        </div>
        <div style={{ display: "flex", gap: 0 }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{ background: "none", border: "none", cursor: "pointer", padding: "10px 18px", fontSize: 13, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", fontFamily: "'Barlow Condensed'", color: activeTab === t.id ? GOLD : "#8aa0bb", borderBottom: activeTab === t.id ? `2px solid ${GOLD}` : "2px solid transparent", display: "flex", alignItems: "center", gap: 6 }}>
              {t.icon}{t.label}
              {t.id === "anomalies" && criticalCount > 0 && <span style={{ background: "#EF4444", color: "#fff", borderRadius: "50%", width: 16, height: 16, fontSize: 10, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>{criticalCount}</span>}
            </button>
          ))}
        </div>
      </div>
      <div style={{ padding: "24px 28px" }}>
        {activeTab === "overview"  && <OverviewTab kpis={kpis} />}
        {activeTab === "health"    && <EntityHealthTab onSeed={handleSeed} />}
        {activeTab === "anomalies" && <AnomaliesTab />}
        {activeTab === "summaries" && <AISummaryTab />}
        {activeTab === "deepdive"  && <EntityDeepDiveTab />}
      </div>
    </div>
  );
}
