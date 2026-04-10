"use client";
/**
 * SportAI Suite — Grant Tracker
 * /app/grants/page.tsx
 * Sprint 2 · Level Playing Field Foundation
 * Tabs: Pipeline · Awards · Compliance · AI Narrative
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Award, ShieldCheck, Brain, RefreshCw, AlertTriangle } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const grantApi = {
  kpis:        () => fetch(`${API}/api/grants/kpis`).then(r => r.json()),
  funders:     () => fetch(`${API}/api/grants/funders`).then(r => r.json()),
  applications:(p?) => fetch(`${API}/api/grants/applications${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  compliance:  () => fetch(`${API}/api/grants/compliance`).then(r => r.json()),
  seed:        () => fetch(`${API}/api/grants/seed`, { method: "POST" }).then(r => r.json()),
  narrative:   (funder: string, amount: number, category: string) =>
    fetch(`${API}/api/grants/ai-narrative/${funder}?amount=${amount}&category=${category}`, { method: "POST" }).then(r => r.json()),
  pipelineBrief:() => fetch(`${API}/api/grants/ai-pipeline-brief`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const STATUS_COLORS: Record<string, string> = {
  drafting: "#6B7280", submitted: "#60A5FA", under_review: "#F97316",
  awarded: "#22C55E", declined: "#EF4444", waitlisted: GOLD, withdrawn: "#6B7280",
};
const FUNDER_COLORS: Record<string, string> = {
  irrrb: "#EF4444", mn_deed: "#F97316", lccmr: "#22C55E",
  gmrptc: "#60A5FA", northland_foundation: "#A855F7", duluth_community_foundation: GOLD,
};

type Application = { id: string; funder: string; title: string; category: string; amount_requested: number; amount_awarded?: number; status: string; submission_date?: string; decision_date?: string; deadline?: string; days_until_deadline?: number; is_deadline_urgent: boolean; lead_contact?: string; };
type KPIs = { total_applications: number; total_requested: number; total_awarded: number; in_pipeline: number; win_rate_pct: number; urgent_deadlines: number; awarded_count: number; declined_count: number; status_breakdown: Record<string, number>; funder_breakdown: Record<string, { applications: number; requested: number; awarded: number }>; };

function KPIStrip({ kpis }: { kpis: KPIs }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10, marginBottom: 24 }}>
      {[
        { l: "Total Applied",   v: fmt(kpis.total_requested),  c: "#60A5FA" },
        { l: "Total Awarded",   v: fmt(kpis.total_awarded),    c: "#22C55E" },
        { l: "In Pipeline",     v: fmt(kpis.in_pipeline),      c: GOLD },
        { l: "Win Rate",        v: `${kpis.win_rate_pct}%`,   c: kpis.win_rate_pct >= 50 ? "#22C55E" : "#F97316" },
        { l: "Applications",    v: kpis.total_applications,   c: "#F0F4FA" },
        { l: "Urgent Deadlines",v: kpis.urgent_deadlines,     c: kpis.urgent_deadlines > 0 ? "#EF4444" : "#22C55E" },
      ].map(s => (
        <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
          <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", color: "#4a6080", marginBottom: 4 }}>{s.l}</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
        </div>
      ))}
    </div>
  );
}

function AppCard({ app }: { app: Application }) {
  const sc = STATUS_COLORS[app.status] ?? "#6B7280";
  const fc = FUNDER_COLORS[app.funder] ?? GOLD;
  return (
    <div style={{ background: "#0f2744", border: `1px solid ${app.is_deadline_urgent ? "rgba(239,68,68,0.4)" : "rgba(201,168,76,0.12)"}`, borderRadius: 8, padding: "14px 16px", marginBottom: 10 }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 10 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", gap: 6, marginBottom: 5, flexWrap: "wrap" }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: fc, background: `${fc}15`, border: `1px solid ${fc}40`, borderRadius: 3, padding: "1px 7px" }}>{app.funder.toUpperCase().replace("_", " ")}</span>
            <span style={{ fontSize: 11, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(app.status)}</span>
            {app.is_deadline_urgent && <span style={{ fontSize: 11, fontWeight: 700, color: "#EF4444", background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 3, padding: "1px 7px" }}>⚠️ {app.days_until_deadline}d</span>}
          </div>
          <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA", marginBottom: 4, lineHeight: 1.4 }}>{app.title}</p>
          <p style={{ fontSize: 12, color: "#8aa0bb" }}>{lbl(app.category)}{app.lead_contact && ` · ${app.lead_contact}`}</p>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD }}>{fmt(app.amount_requested)}</p>
          {app.amount_awarded && <p style={{ fontSize: 12, color: "#22C55E" }}>Awarded: {fmt(app.amount_awarded)}</p>}
          {app.deadline && <p style={{ fontSize: 11, color: app.is_deadline_urgent ? "#EF4444" : "#8aa0bb" }}>Due: {app.deadline}</p>}
        </div>
      </div>
    </div>
  );
}

function PipelineTab({ onSeed }: { onSeed: () => void }) {
  const [statusFilter, setStatusFilter] = useState("");
  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  const { data: apps = [] } = useQuery<Application[]>({ queryKey: ["grant-apps", statusFilter], queryFn: () => grantApi.applications(params) });
  const STATUSES = ["drafting","submitted","under_review","waitlisted"];

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <button onClick={() => setStatusFilter("")} style={{ background: !statusFilter ? GOLD : "#0f2744", color: !statusFilter ? NAVY : "#8aa0bb", border: `1px solid ${!statusFilter ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>All Active</button>
        {STATUSES.map(s => (
          <button key={s} onClick={() => setStatusFilter(s)} style={{ background: statusFilter === s ? STATUS_COLORS[s] : "#0f2744", color: statusFilter === s ? "#071828" : "#8aa0bb", border: `1px solid ${statusFilter === s ? STATUS_COLORS[s] : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{lbl(s)}</button>
        ))}
      </div>
      {apps.length === 0 && (
        <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
          <FileText size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
          <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>No grant applications yet</p>
          <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Grant Pipeline</button>
        </div>
      )}
      {apps.map((a: Application) => <AppCard key={a.id} app={a} />)}
    </div>
  );
}

function AwardsTab() {
  const { data: awarded = [] } = useQuery<Application[]>({ queryKey: ["grant-awarded"], queryFn: () => grantApi.applications({ status: "awarded" }) });
  const total = (awarded as Application[]).reduce((s, a) => s + (a.amount_awarded ?? 0), 0);
  return (
    <div>
      <div style={{ background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.25)", borderRadius: 8, padding: "14px 18px", marginBottom: 20, display: "flex", gap: 24 }}>
        <div><p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em" }}>Total Awarded</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: "#22C55E" }}>{fmt(total)}</p></div>
        <div><p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em" }}>Grants Won</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: "#F0F4FA" }}>{(awarded as Application[]).length}</p></div>
      </div>
      {(awarded as Application[]).map((a: Application) => <AppCard key={a.id} app={a} />)}
    </div>
  );
}

function ComplianceTab() {
  const { data: comp } = useQuery({ queryKey: ["grant-compliance"], queryFn: grantApi.compliance });
  if (!comp) return <p style={{ color: "#8aa0bb", fontSize: 13 }}>Loading…</p>;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#EF4444", marginBottom: 12 }}>OVERDUE ({comp.summary.overdue_count})</p>
        {comp.overdue.length === 0 && <p style={{ fontSize: 13, color: "#22C55E" }}>✓ No overdue reports</p>}
        {comp.overdue.map((e: any) => (
          <div key={e.id} style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, padding: "12px 14px", marginBottom: 10 }}>
            <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA" }}>{lbl(e.event_type)}</p>
            {e.due_date && <p style={{ fontSize: 12, color: "#EF4444" }}>Was due: {e.due_date}</p>}
            {e.notes && <p style={{ fontSize: 12, color: "#8aa0bb", marginTop: 4 }}>{e.notes}</p>}
          </div>
        ))}
      </div>
      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD, marginBottom: 12 }}>DUE SOON ({comp.summary.due_soon_count})</p>
        {comp.due_soon.map((e: any) => (
          <div key={e.id} style={{ background: "rgba(201,168,76,0.08)", border: "1px solid rgba(201,168,76,0.25)", borderRadius: 8, padding: "12px 14px", marginBottom: 10 }}>
            <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA" }}>{lbl(e.event_type)}</p>
            <div style={{ display: "flex", gap: 16, fontSize: 12, color: "#8aa0bb", marginTop: 4 }}>
              <span>Due: {e.due_date}</span>
              {e.days_until_due !== undefined && <span style={{ color: e.days_until_due <= 14 ? "#F97316" : GOLD }}>{e.days_until_due} days</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AITab() {
  const FUNDERS = [
    { key: "irrrb",    label: "IRRRB",    color: "#EF4444" },
    { key: "mn_deed",  label: "MN DEED",  color: "#F97316" },
    { key: "lccmr",    label: "LCCMR",    color: "#22C55E" },
    { key: "gmrptc",   label: "GMRPTC",   color: "#60A5FA" },
    { key: "northland_foundation", label: "Northland", color: "#A855F7" },
    { key: "duluth_community_foundation", label: "Duluth CF", color: GOLD },
  ];
  const CATS = ["capital","programming","equipment","workforce","conservation","tourism","technology","general_operating"];

  const [selectedFunder, setSelectedFunder] = useState("irrrb");
  const [amount, setAmount] = useState(250000);
  const [category, setCategory] = useState("capital");
  const [narrative, setNarrative] = useState<any>(null);
  const [pipelineBrief, setPipelineBrief] = useState<string>("");
  const [loadingNarrative, setLoadingNarrative] = useState(false);
  const [loadingBrief, setLoadingBrief] = useState(false);

  const generateNarrative = async () => {
    setLoadingNarrative(true); setNarrative(null);
    const result = await grantApi.narrative(selectedFunder, amount, category);
    setNarrative(result); setLoadingNarrative(false);
  };

  const generateBrief = async () => {
    setLoadingBrief(true); setPipelineBrief("");
    const result = await grantApi.pipelineBrief();
    setPipelineBrief(result.brief); setLoadingBrief(false);
  };

  const fc = FUNDER_COLORS[selectedFunder] ?? GOLD;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 20 }}>
      <div>
        <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Narrative Generator</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 14 }}>
          {FUNDERS.map(f => (
            <div key={f.key} onClick={() => setSelectedFunder(f.key)} style={{ background: selectedFunder === f.key ? `${f.color}15` : "#0f2744", border: `1px solid ${selectedFunder === f.key ? f.color : "rgba(201,168,76,0.15)"}`, borderRadius: 7, padding: "10px 12px", cursor: "pointer" }}>
              <p style={{ fontSize: 13, fontWeight: 700, color: selectedFunder === f.key ? f.color : "#F0F4FA" }}>{f.label}</p>
            </div>
          ))}
        </div>
        <div style={{ marginBottom: 10 }}>
          <p style={{ fontSize: 11, color: "#4a6080", marginBottom: 4 }}>Amount Requested</p>
          <input type="number" value={amount} onChange={e => setAmount(Number(e.target.value))} style={{ width: "100%", background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "8px 12px", fontSize: 14, fontFamily: "'Barlow Condensed'" }} />
        </div>
        <div style={{ marginBottom: 14 }}>
          <p style={{ fontSize: 11, color: "#4a6080", marginBottom: 4 }}>Category</p>
          <select value={category} onChange={e => setCategory(e.target.value)} style={{ width: "100%", background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "8px 12px", fontSize: 13, fontFamily: "'Barlow Condensed'" }}>
            {CATS.map(c => <option key={c} value={c}>{lbl(c)}</option>)}
          </select>
        </div>
        <button onClick={generateNarrative} disabled={loadingNarrative} style={{ width: "100%", background: fc, color: "#071828", border: "none", borderRadius: 7, padding: "12px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
          {loadingNarrative ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={14} />Generate Narrative</>}
        </button>
        <button onClick={generateBrief} disabled={loadingBrief} style={{ width: "100%", background: "#0f2744", color: GOLD, border: `1px solid ${GOLD}`, borderRadius: 7, padding: "10px", fontWeight: 700, cursor: "pointer", fontSize: 13, marginTop: 8, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
          {loadingBrief ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Briefing…</> : "Pipeline Strategy Brief"}
        </button>
      </div>

      <div>
        {pipelineBrief && (
          <div style={{ background: "#0f2744", border: `1px solid rgba(201,168,76,0.3)`, borderRadius: 10, padding: "18px 20px", marginBottom: 16 }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Pipeline Strategy Brief</p>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{pipelineBrief}</p>
          </div>
        )}
        {narrative ? (
          <div style={{ background: "#0f2744", border: `1px solid ${fc}`, borderRadius: 10, padding: "20px 22px" }}>
            <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: fc, background: `${fc}15`, border: `1px solid ${fc}40`, borderRadius: 4, padding: "2px 8px" }}>{narrative.funder_name}</span>
              <span style={{ fontSize: 11, color: GOLD }}>Requesting: {fmt(narrative.amount_requested)}</span>
              <span style={{ fontSize: 11, color: "#8aa0bb" }}>{lbl(narrative.category)}</span>
            </div>
            <div style={{ maxHeight: "60vh", overflowY: "auto", paddingRight: 8 }}>
              <pre style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap", fontFamily: "'Barlow', sans-serif" }}>{narrative.narrative}</pre>
            </div>
          </div>
        ) : !pipelineBrief ? (
          <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
            <p style={{ fontSize: 14, color: "#8aa0bb" }}>Select a funder and generate a grant narrative</p>
            <p style={{ fontSize: 12, color: "#4a6080", marginTop: 4 }}>5-section narrative tuned to each funder's priorities</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

const TABS = [
  { id: "pipeline",   label: "Pipeline",   icon: <FileText size={14} /> },
  { id: "awards",     label: "Awards",     icon: <Award size={14} /> },
  { id: "compliance", label: "Compliance", icon: <ShieldCheck size={14} /> },
  { id: "ai",         label: "AI Narrative", icon: <Brain size={14} /> },
];

export default function GrantTrackerPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("pipeline");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery<KPIs>({ queryKey: ["grant-kpis"], queryFn: grantApi.kpis });

  const handleSeed = async () => {
    setSeeding(true);
    await grantApi.seed();
    qc.invalidateQueries({ queryKey: ["grant-kpis"] });
    qc.invalidateQueries({ queryKey: ["grant-apps"] });
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6 }}>
          {["LPF FOUNDATION","IRRRB · MN DEED · LCCMR · GMRPTC"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.15)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2, marginBottom: 12 }}>GRANT TRACKER</h1>
        <div style={{ display: "flex", gap: 0 }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{ background: "none", border: "none", cursor: "pointer", padding: "10px 18px", fontSize: 13, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", fontFamily: "'Barlow Condensed'", color: activeTab === t.id ? GOLD : "#8aa0bb", borderBottom: activeTab === t.id ? `2px solid ${GOLD}` : "2px solid transparent", display: "flex", alignItems: "center", gap: 6 }}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </div>
      <div style={{ padding: "24px 28px" }}>
        {kpis && <KPIStrip kpis={kpis} />}
        {activeTab === "pipeline"   && <PipelineTab onSeed={handleSeed} />}
        {activeTab === "awards"     && <AwardsTab />}
        {activeTab === "compliance" && <ComplianceTab />}
        {activeTab === "ai"         && <AITab />}
      </div>
    </div>
  );
}
