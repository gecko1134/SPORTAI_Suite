"use client";
/**
 * SportAI Suite — Skill Shot Academy
 * /app/skill-shot/page.tsx · Sprint 4 · NGP Development Phase 2
 * Tabs: Overview · Bays · Sessions · Capital Stack · AI Briefs
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Target, Grid3x3, CalendarDays, DollarSign, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const ssApi = {
  overview:    () => fetch(`${API}/api/skill-shot/overview`).then(r => r.json()),
  bays:        () => fetch(`${API}/api/skill-shot/bays`).then(r => r.json()),
  sessions:    (p?) => fetch(`${API}/api/skill-shot/sessions${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  milestones:  (p?) => fetch(`${API}/api/skill-shot/milestones${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  capital:     () => fetch(`${API}/api/skill-shot/capital-stack`).then(r => r.json()),
  seed:        () => fetch(`${API}/api/skill-shot/seed`, { method: "POST" }).then(r => r.json()),
  launchBrief: () => fetch(`${API}/api/skill-shot/ai-launch-brief`, { method: "POST" }).then(r => r.json()),
  investorBrief:() => fetch(`${API}/api/skill-shot/ai-investor-brief`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const pct  = (n: number) => `${n.toFixed(1)}%`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const BAY_STATUS_COLORS: Record<string, string> = {
  planned: "#6B7280", installation: "#60A5FA", calibration: "#F97316",
  operational: "#22C55E", maintenance: "#EF4444",
};
const MILESTONE_STATUS_COLORS: Record<string, string> = {
  not_started: "#6B7280", in_progress: "#60A5FA", completed: "#22C55E",
  at_risk: "#F97316", blocked: "#EF4444",
};
const CAPITAL_SOURCE_COLORS: Record<string, string> = {
  sba_504: "#60A5FA", naming_rights: GOLD, state_grants: "#22C55E", crowdfunding: "#F97316",
};

function ReadinessGauge({ score }: { score: number }) {
  const r = 60; const circ = 2 * Math.PI * r;
  const color = score >= 75 ? "#22C55E" : score >= 50 ? GOLD : "#F97316";
  return (
    <div style={{ textAlign: "center" }}>
      <svg width={150} height={150} viewBox="0 0 150 150">
        <circle cx={75} cy={75} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={14} />
        <circle cx={75} cy={75} r={r} fill="none" stroke={color} strokeWidth={14}
          strokeDasharray={circ} strokeDashoffset={circ - (score / 100) * circ}
          strokeLinecap="round" transform="rotate(-90 75 75)" style={{ transition: "stroke-dashoffset 0.8s ease" }} />
        <text x={75} y={70} textAnchor="middle" fill="#F0F4FA" fontSize={28} fontFamily="'Bebas Neue'" letterSpacing={1}>{score}</text>
        <text x={75} y={88} textAnchor="middle" fill={color} fontSize={11} fontFamily="'Barlow Condensed'" fontWeight={700}>READINESS</text>
      </svg>
      <p style={{ fontSize: 12, color: "#8aa0bb", marginTop: 2 }}>Launch Readiness Score</p>
    </div>
  );
}

function OverviewTab({ onSeed }: { onSeed: () => void }) {
  const { data: ov } = useQuery({ queryKey: ["ss-overview"], queryFn: ssApi.overview });
  const { data: milestones = [] } = useQuery({ queryKey: ["ss-milestones"], queryFn: () => ssApi.milestones() });

  if (!ov) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Target size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Skill Shot Academy not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Skill Shot Academy</button>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 24, background: "#0f2744", border: `1px solid ${GOLD}40`, borderRadius: 10, padding: "24px 28px", alignItems: "start" }}>
        <ReadinessGauge score={ov.launch_readiness_score} />
        <div>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 13, color: "#4a6080", letterSpacing: 2, marginBottom: 4 }}>NGP DEVELOPMENT — PHASE 2 FLAGSHIP</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            {[
              { l: "Bays Operational", v: `${ov.bays_operational} / ${ov.bays_total}`, c: "#22C55E" },
              { l: "In Progress",      v: ov.bays_in_progress,   c: "#60A5FA" },
              { l: "Revenue",          v: fmt(ov.total_revenue),  c: GOLD },
              { l: "Year 1 Target",    v: fmt(ov.year1_revenue_target), c: "#4a6080" },
              { l: "Capital Committed",v: `${ov.capital_committed_pct}%`, c: ov.capital_committed_pct >= 80 ? "#22C55E" : "#F97316" },
              { l: "Capital Gap",      v: fmt(ov.capital_gap),   c: "#EF4444" },
            ].map(s => (
              <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "8px 12px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
          <div style={{ background: "#152f52", borderRadius: 6, padding: "8px 14px" }}>
            <p style={{ fontSize: 11, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>Revenue Pacing vs $3.8M Target</p>
            <div style={{ height: 6, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
              <div style={{ height: "100%", width: `${Math.min(ov.revenue_pacing_pct, 100)}%`, background: `linear-gradient(90deg, #7a612e, ${GOLD})`, borderRadius: 3 }} />
            </div>
            <p style={{ fontSize: 11, color: GOLD, marginTop: 4 }}>{ov.revenue_pacing_pct.toFixed(2)}% of target</p>
          </div>
        </div>
      </div>

      {/* Milestone phases */}
      {[1, 2, 3].map(phase => {
        const phaseMs = (milestones as any[]).filter((m: any) => m.phase === phase);
        const completed = phaseMs.filter((m: any) => m.status === "completed").length;
        const phaseLabels = ["Planning & Capital", "Build & Install", "Launch & Revenue"];
        return (
          <div key={phase} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 10, padding: "16px 20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 17, letterSpacing: 1, color: "#F0F4FA" }}>PHASE {phase} — {phaseLabels[phase - 1]}</p>
              <span style={{ fontSize: 12, color: GOLD, fontWeight: 700 }}>{completed}/{phaseMs.length} complete</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {phaseMs.map((m: any) => {
                const sc = MILESTONE_STATUS_COLORS[m.status] ?? "#6B7280";
                return (
                  <div key={m.id} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 10, height: 10, borderRadius: "50%", background: sc, flexShrink: 0 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                        <p style={{ fontSize: 12, color: "#F0F4FA" }}>{m.title}</p>
                        <span style={{ fontSize: 10, color: sc, fontWeight: 700, whiteSpace: "nowrap" }}>{lbl(m.status)}</span>
                      </div>
                      {m.progress_pct > 0 && m.progress_pct < 100 && (
                        <div style={{ height: 3, background: "rgba(255,255,255,0.06)", borderRadius: 2, marginTop: 3 }}>
                          <div style={{ height: "100%", width: `${m.progress_pct}%`, background: sc, borderRadius: 2 }} />
                        </div>
                      )}
                      {m.blockers && <p style={{ fontSize: 11, color: "#F97316", marginTop: 2 }}>⚠️ {m.blockers}</p>}
                    </div>
                    <span style={{ fontSize: 11, color: "#4a6080", whiteSpace: "nowrap" }}>{m.target_date}</span>
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

function BaysTab() {
  const { data: bays = [] } = useQuery({ queryKey: ["ss-bays"], queryFn: ssApi.bays });
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
      {(bays as any[]).map((b: any) => {
        const sc = BAY_STATUS_COLORS[b.status] ?? "#6B7280";
        return (
          <div key={b.id} style={{ background: `${sc}08`, border: `1px solid ${sc}35`, borderRadius: 10, padding: "16px 18px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 32, color: "#F0F4FA", lineHeight: 1 }}>#{b.bay_number}</p>
              <span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}20`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "2px 7px" }}>{lbl(b.status)}</span>
            </div>
            {b.trackman_serial && <p style={{ fontSize: 11, color: "#4a6080", marginBottom: 6 }}>TrackMan {b.trackman_serial}</p>}
            {b.installation_date && <p style={{ fontSize: 11, color: "#8aa0bb" }}>Installed: {b.installation_date}</p>}
            {b.operational_date && <p style={{ fontSize: 11, color: "#22C55E" }}>Operational: {b.operational_date}</p>}
            {b.status === "operational" && (
              <div style={{ marginTop: 10, borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: 10 }}>
                <p style={{ fontSize: 12, color: "#8aa0bb" }}>{b.sessions_total} sessions</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD }}>{fmt(b.revenue_total)}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function SessionsTab() {
  const { data: sessions = [] } = useQuery({ queryKey: ["ss-sessions"], queryFn: () => ssApi.sessions({ days_back: "60" }) });
  const TYPE_COLORS: Record<string, string> = { individual: "#60A5FA", group: "#22C55E", lesson: GOLD, league: "#A855F7", corporate: "#F97316", simulator: "#6B7280" };
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
            {["Guest","Type","Bay","Date","Duration","Guests","Rate/hr","Revenue"].map(h => (
              <th key={h} style={{ padding: "8px 12px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(sessions as any[]).map((s: any) => {
            const tc = TYPE_COLORS[s.session_type] ?? GOLD;
            return (
              <tr key={s.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <td style={{ padding: "10px 12px", fontWeight: 600, fontSize: 13, color: "#F0F4FA" }}>{s.guest_name}</td>
                <td style={{ padding: "10px 12px" }}><span style={{ fontSize: 11, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(s.session_type)}</span></td>
                <td style={{ padding: "10px 12px", fontSize: 13, color: "#8aa0bb" }}>Bay {s.bay_id?.slice(-4)}</td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "#8aa0bb" }}>{s.session_date}</td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "#F0F4FA" }}>{s.duration_hours}hr</td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "#F0F4FA" }}>{s.guest_count}</td>
                <td style={{ padding: "10px 12px", fontSize: 13, color: "#8aa0bb" }}>${s.rate_per_hour}</td>
                <td style={{ padding: "10px 12px", fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{fmt(s.revenue)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function CapitalTab() {
  const { data: cap } = useQuery({ queryKey: ["ss-capital"], queryFn: ssApi.capital });
  if (!cap) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10 }}>
        {[
          { l: "Total Investment", v: fmt(cap.total_investment), c: "#F0F4FA" },
          { l: "Committed",        v: `${cap.committed_pct}%`,  c: cap.committed_pct >= 80 ? "#22C55E" : GOLD },
          { l: "Received",         v: `${cap.received_pct}%`,   c: "#60A5FA" },
          { l: "Deployed",         v: `${cap.deployed_pct}%`,   c: "#A855F7" },
          { l: "Gap to Close",     v: fmt(cap.gap_to_close),   c: "#EF4444" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {cap.sources.map((s: any) => {
          const sc = CAPITAL_SOURCE_COLORS[s.source] ?? GOLD;
          return (
            <div key={s.id} style={{ background: `${sc}08`, border: `1px solid ${sc}30`, borderRadius: 10, padding: "16px 20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 0.5, color: "#F0F4FA" }}>{s.label}</p>
                  <span style={{ fontSize: 11, fontWeight: 700, color: sc, background: `${sc}20`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(s.status)}</span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: GOLD }}>{fmt(s.committed_amount)}</p>
                  <p style={{ fontSize: 11, color: "#4a6080" }}>of {fmt(s.target_amount)}</p>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 10 }}>
                {[["Committed", s.committed_amount, sc], ["Received", s.received_amount, "#60A5FA"], ["Deployed", s.deployed_amount, "#A855F7"]].map(([label, val, color]) => (
                  <div key={label as string} style={{ background: "rgba(0,0,0,0.2)", borderRadius: 5, padding: "8px 10px" }}>
                    <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 2 }}>{label}</p>
                    <p style={{ fontSize: 15, fontFamily: "'Bebas Neue'", color: color as string }}>{fmt(val as number)}</p>
                  </div>
                ))}
              </div>
              <div style={{ height: 6, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
                <div style={{ height: "100%", width: `${s.committed_pct}%`, background: sc, borderRadius: 3, transition: "width 0.4s" }} />
              </div>
              {s.notes && <p style={{ fontSize: 11, color: "#F97316", marginTop: 6 }}>⚠️ {s.notes}</p>}
              {s.gap > 0 && <p style={{ fontSize: 11, color: "#4a6080", marginTop: 4 }}>Gap: {fmt(s.gap)}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AIBriefTab() {
  const [launchResult, setLaunchResult] = useState<any>(null);
  const [investorResult, setInvestorResult] = useState<any>(null);
  const [loadingLaunch, setLoadingLaunch] = useState(false);
  const [loadingInvestor, setLoadingInvestor] = useState(false);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      {[
        { title: "LAUNCH READINESS BRIEF", btn: "Generate Launch Brief", loading: loadingLaunch, result: launchResult, field: "brief",
          run: async () => { setLoadingLaunch(true); setLaunchResult(await ssApi.launchBrief()); setLoadingLaunch(false); },
          extra: (r: any) => <div style={{ marginTop: 10, background: "rgba(201,168,76,0.08)", borderRadius: 6, padding: "8px 12px" }}><p style={{ fontSize: 11, color: "#4a6080" }}>Readiness Score</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: GOLD }}>{r.readiness_score}/100</p></div> },
        { title: "INVESTOR NARRATIVE", btn: "Generate Investor Brief", loading: loadingInvestor, result: investorResult, field: "narrative",
          run: async () => { setLoadingInvestor(true); setInvestorResult(await ssApi.investorBrief()); setLoadingInvestor(false); },
          extra: null },
      ].map(panel => (
        <div key={panel.title}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 17, letterSpacing: 1, color: "#F0F4FA" }}>{panel.title}</p>
            <button onClick={panel.run} disabled={panel.loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 6 }}>
              {panel.loading ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={12} />{panel.btn}</>}
            </button>
          </div>
          {panel.result ? (
            <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px" }}>
              <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{panel.result[panel.field]}</p>
              {panel.extra && panel.extra(panel.result)}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "60px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
              <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
              <p style={{ fontSize: 13, color: "#8aa0bb" }}>{panel.btn}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

const TABS = [
  { id: "overview",  label: "Overview",      icon: <Target size={14} /> },
  { id: "bays",      label: "Bays",          icon: <Grid3x3 size={14} /> },
  { id: "sessions",  label: "Sessions",      icon: <CalendarDays size={14} /> },
  { id: "capital",   label: "Capital Stack", icon: <DollarSign size={14} /> },
  { id: "ai",        label: "AI Briefs",     icon: <Brain size={14} /> },
];

export default function SkillShotPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("overview");
  const [seeding, setSeeding] = useState(false);
  const { data: ov } = useQuery({ queryKey: ["ss-overview"], queryFn: ssApi.overview });

  const handleSeed = async () => {
    setSeeding(true);
    await ssApi.seed();
    ["ss-overview","ss-bays","ss-sessions","ss-milestones","ss-capital"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NGP DEVELOPMENT","PHASE 2","$4.65M INVESTMENT","10 TRACKMAN BAYS"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>SKILL SHOT ACADEMY</h1>
          {ov && <div style={{ display: "flex", gap: 16, marginBottom: 6, alignItems: "center" }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Readiness: <strong style={{ color: ov.launch_readiness_score >= 75 ? "#22C55E" : GOLD }}>{ov.launch_readiness_score}/100</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Capital: <strong style={{ color: GOLD }}>{ov.capital_committed_pct}%</strong></span>
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
        {activeTab === "overview" && <OverviewTab onSeed={handleSeed} />}
        {activeTab === "bays"     && <BaysTab />}
        {activeTab === "sessions" && <SessionsTab />}
        {activeTab === "capital"  && <CapitalTab />}
        {activeTab === "ai"       && <AIBriefTab />}
      </div>
    </div>
  );
}
