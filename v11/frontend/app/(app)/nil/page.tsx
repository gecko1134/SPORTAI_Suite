"use client";

/**
 * SportAI Suite — NIL Program Dashboard
 * /app/nil/page.tsx
 * Sprint 1 · Level Playing Field Foundation
 *
 * 4 tabs: Athletes · Deals · Compliance · AI Briefs
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Users, FileText, ShieldCheck, Brain, Plus, RefreshCw,
  TrendingUp, DollarSign, AlertTriangle, CheckCircle, Clock, Star
} from "lucide-react";

// ── API layer ─────────────────────────────────────────────────────────────────

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const nilApi = {
  kpis:        ()         => fetch(`${API}/api/nil/kpis`).then(r => r.json()),
  athletes:    (params?)  => fetch(`${API}/api/nil/athletes${params ? "?" + new URLSearchParams(params) : ""}`).then(r => r.json()),
  athleteById: (id: string) => fetch(`${API}/api/nil/athletes/${id}`).then(r => r.json()),
  deals:       (params?)  => fetch(`${API}/api/nil/deals${params ? "?" + new URLSearchParams(params) : ""}`).then(r => r.json()),
  compliance:  ()         => fetch(`${API}/api/nil/compliance-alerts`).then(r => r.json()),
  seed:        ()         => fetch(`${API}/api/nil/seed`, { method: "POST" }).then(r => r.json()),
  athleteBrief:(id: string) => fetch(`${API}/api/nil/ai-brief/${id}`, { method: "POST" }).then(r => r.json()),
  programBrief:()         => fetch(`${API}/api/nil/ai-program-brief`, { method: "POST" }).then(r => r.json()),
};

// ── Types ─────────────────────────────────────────────────────────────────────

type Athlete = {
  id: string; full_name: string; school: string; grade: string;
  sport_primary: string; gpa: number; social_followers: number;
  active_deals: number; total_deal_value: number; compliance_status: string;
  deals?: Deal[]; compliance_events?: ComplianceEvent[];
};
type Deal = {
  id: string; athlete_id: string; brand_name: string; deal_type: string;
  deal_value: number; status: string; start_date: string; end_date?: string;
  completion_pct: number; is_expiring_soon: boolean;
  social_posts_required: number; social_posts_completed: number;
};
type ComplianceEvent = {
  id: string; athlete_id: string; event_type: string; status: string;
  due_date?: string; notes?: string; days_until_due?: number;
};
type KPIs = {
  active_athletes: number; active_deals: number; total_deal_value: number;
  avg_deal_per_athlete: number; avg_social_followers: number;
  compliance_violations: number; deals_expiring_soon: number;
  sports_breakdown: Record<string, number>;
};

// ── Helpers ───────────────────────────────────────────────────────────────────

const GOLD    = "#C9A84C";
const NAVY    = "#0A2240";
const fmt     = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const fmtK    = (n: number) => n >= 1000 ? `${(n / 1000).toFixed(1)}K` : n.toString();
const sportLabel  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
const gradeLabel  = (g: string) => `${g} Grade`;
const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(" ");

const COMPLIANCE_COLORS: Record<string, string> = {
  compliant:      "#22C55E",
  pending_review: GOLD,
  warning:        "#F97316",
  violation:      "#EF4444",
};

const STATUS_COLORS: Record<string, string> = {
  active:    "#22C55E",
  pending:   GOLD,
  completed: "#60A5FA",
  expired:   "#6B7280",
  cancelled: "#EF4444",
};

// ── Sub-components ────────────────────────────────────────────────────────────

function KPIStrip({ kpis }: { kpis: KPIs }) {
  const items = [
    { label: "Active Athletes",  value: kpis.active_athletes,                        icon: <Users size={14} />,        color: GOLD },
    { label: "Active Deals",     value: kpis.active_deals,                           icon: <FileText size={14} />,     color: "#60A5FA" },
    { label: "Total Deal Value", value: fmt(kpis.total_deal_value),                  icon: <DollarSign size={14} />,   color: "#22C55E" },
    { label: "Avg per Athlete",  value: fmt(kpis.avg_deal_per_athlete),              icon: <TrendingUp size={14} />,   color: GOLD },
    { label: "Avg Followers",    value: fmtK(kpis.avg_social_followers),             icon: <Star size={14} />,         color: "#A855F7" },
    { label: "Expiring ≤30d",   value: kpis.deals_expiring_soon,                    icon: <Clock size={14} />,        color: "#F97316" },
    { label: "Violations",       value: kpis.compliance_violations,                  icon: <AlertTriangle size={14} />,color: "#EF4444" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
      {items.map(item => (
        <div key={item.label} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 5, color: item.color, marginBottom: 4 }}>
            {item.icon}
            <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>{item.label}</span>
          </div>
          <p style={{ fontSize: 22, fontFamily: "'Bebas Neue'", letterSpacing: 1, color: "#F0F4FA" }}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}

function AthleteCard({ athlete, onClick, selected }: { athlete: Athlete; onClick: () => void; selected: boolean }) {
  const cc = COMPLIANCE_COLORS[athlete.compliance_status] ?? GOLD;
  return (
    <div onClick={onClick} style={{
      background: selected ? "#152f52" : "#0f2744",
      border: `1px solid ${selected ? GOLD : "rgba(201,168,76,0.15)"}`,
      borderRadius: 8, padding: "14px 16px", cursor: "pointer", transition: "all 0.2s",
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 6 }}>
        <div>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 17, letterSpacing: 0.5, color: "#F0F4FA" }}>{athlete.full_name}</p>
          <p style={{ fontSize: 12, color: "#8aa0bb" }}>{athlete.school} · {athlete.grade}</p>
        </div>
        <span style={{ fontSize: 10, fontWeight: 700, background: `${cc}20`, border: `1px solid ${cc}50`, color: cc, borderRadius: 4, padding: "2px 7px" }}>
          {athlete.compliance_status.replace("_", " ").toUpperCase()}
        </span>
      </div>
      <div style={{ display: "flex", gap: 14, fontSize: 12, color: "#8aa0bb" }}>
        <span>🏅 {sportLabel(athlete.sport_primary)}</span>
        <span>📱 {fmtK(athlete.social_followers)}</span>
        <span style={{ color: GOLD, fontWeight: 700 }}>{fmt(athlete.total_deal_value)}</span>
      </div>
      <div style={{ marginTop: 6, fontSize: 11, color: "#4a6080" }}>
        {athlete.active_deals} active deal{athlete.active_deals !== 1 ? "s" : ""} · GPA {athlete.gpa ?? "N/A"}
      </div>
    </div>
  );
}

function DealRow({ deal, athleteName }: { deal: Deal; athleteName?: string }) {
  const sc = STATUS_COLORS[deal.status] ?? "#6B7280";
  const pct = deal.completion_pct;
  return (
    <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 8, padding: "12px 16px", marginBottom: 10 }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 6 }}>
        <div>
          <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA" }}>{deal.brand_name}</p>
          {athleteName && <p style={{ fontSize: 11, color: "#8aa0bb" }}>{athleteName}</p>}
          <p style={{ fontSize: 12, color: "#8aa0bb" }}>{sportLabel(deal.deal_type)}</p>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{fmt(deal.deal_value)}</p>
          <span style={{ fontSize: 10, fontWeight: 700, background: `${sc}20`, border: `1px solid ${sc}50`, color: sc, borderRadius: 4, padding: "1px 6px" }}>
            {deal.status.toUpperCase()}
          </span>
        </div>
      </div>
      <div style={{ display: "flex", gap: 16, fontSize: 11, color: "#8aa0bb", marginBottom: 6 }}>
        <span>Start: {deal.start_date}</span>
        {deal.end_date && <span style={{ color: deal.is_expiring_soon ? "#F97316" : "#8aa0bb" }}>Ends: {deal.end_date}{deal.is_expiring_soon ? " ⚠️" : ""}</span>}
      </div>
      {pct > 0 && (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#8aa0bb", marginBottom: 3 }}>
            <span>Completion</span><span style={{ color: GOLD }}>{pct}%</span>
          </div>
          <div style={{ height: 4, background: "rgba(255,255,255,0.08)", borderRadius: 2 }}>
            <div style={{ height: "100%", width: `${pct}%`, background: `linear-gradient(90deg, #7a612e, ${GOLD})`, borderRadius: 2 }} />
          </div>
        </div>
      )}
    </div>
  );
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

function AthletesTab() {
  const qc = useQueryClient();
  const [selected, setSelected] = useState<Athlete | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);

  const { data: athletes = [], isLoading } = useQuery({ queryKey: ["nil-athletes"], queryFn: () => nilApi.athletes() });

  const handleSelect = async (a: Athlete) => {
    if (selected?.id === a.id) { setSelected(null); return; }
    setDetailLoading(true);
    const detail = await nilApi.athleteById(a.id);
    setSelected(detail);
    setDetailLoading(false);
  };

  const handleSeed = async () => {
    setSeeding(true);
    await nilApi.seed();
    qc.invalidateQueries({ queryKey: ["nil-athletes"] });
    qc.invalidateQueries({ queryKey: ["nil-kpis"] });
    setSeeding(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: selected ? "1fr 380px" : "1fr", gap: 20 }}>
      <div>
        {athletes.length === 0 && !isLoading && (
          <div style={{ textAlign: "center", padding: "48px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
            <Users size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
            <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 4 }}>No athletes enrolled yet</p>
            <p style={{ fontSize: 13, color: "#8aa0bb", marginBottom: 20 }}>Seed sample data to preview the NIL Program</p>
            <button onClick={handleSeed} disabled={seeding} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8, margin: "0 auto" }}>
              {seeding ? <><RefreshCw size={14} className="animate-spin" />Seeding…</> : <><Plus size={14} />Seed NIL Athletes</>}
            </button>
          </div>
        )}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 10 }}>
          {athletes.map((a: Athlete) => (
            <AthleteCard key={a.id} athlete={a} onClick={() => handleSelect(a)} selected={selected?.id === a.id} />
          ))}
        </div>
      </div>

      {selected && (
        <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px", position: "sticky", top: 20, maxHeight: "80vh", overflowY: "auto" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: "#F0F4FA", marginBottom: 2 }}>{selected.full_name}</p>
          <p style={{ fontSize: 13, color: "#8aa0bb", marginBottom: 16 }}>{selected.school} · {selected.grade} · {sportLabel(selected.sport_primary)}</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
            {[
              { l: "Deal Value", v: fmt(selected.total_deal_value), c: GOLD },
              { l: "Followers", v: fmtK(selected.social_followers), c: "#A855F7" },
              { l: "GPA", v: selected.gpa ?? "N/A", c: "#22C55E" },
              { l: "Active Deals", v: selected.active_deals, c: "#60A5FA" },
            ].map(s => (
              <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "8px 12px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 2, textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.l}</p>
                <p style={{ fontSize: 18, fontFamily: "'Bebas Neue'", color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
          {selected.deals && selected.deals.length > 0 && (
            <div>
              <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>Deals</p>
              {selected.deals.map(d => <DealRow key={d.id} deal={d} />)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function DealsTab() {
  const { data: deals = [] } = useQuery({ queryKey: ["nil-deals"], queryFn: () => nilApi.deals() });
  const { data: athletes = [] } = useQuery({ queryKey: ["nil-athletes"], queryFn: () => nilApi.athletes() });
  const athleteMap = Object.fromEntries((athletes as Athlete[]).map((a: Athlete) => [a.id, a.full_name]));
  const expiring = (deals as Deal[]).filter((d: Deal) => d.is_expiring_soon);

  return (
    <div>
      {expiring.length > 0 && (
        <div style={{ background: "rgba(249,115,22,0.1)", border: "1px solid rgba(249,115,22,0.3)", borderRadius: 8, padding: "12px 16px", marginBottom: 20, display: "flex", alignItems: "center", gap: 10 }}>
          <Clock size={16} style={{ color: "#F97316", flexShrink: 0 }} />
          <p style={{ fontSize: 13, color: "#F97316" }}><strong>{expiring.length} deal{expiring.length > 1 ? "s" : ""}</strong> expiring within 30 days — review and renew</p>
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 0 }}>
        {(deals as Deal[]).map((d: Deal) => <DealRow key={d.id} deal={d} athleteName={athleteMap[d.athlete_id]} />)}
      </div>
    </div>
  );
}

function ComplianceTab() {
  const { data: comp, isLoading } = useQuery({ queryKey: ["nil-compliance"], queryFn: nilApi.compliance });

  if (isLoading) return <p style={{ color: "#8aa0bb", fontSize: 13 }}>Loading compliance data…</p>;

  const openIssues: ComplianceEvent[] = comp?.open_issues ?? [];
  const deadlines: ComplianceEvent[]  = comp?.upcoming_deadlines ?? [];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>OPEN ISSUES ({openIssues.length})</p>
        {openIssues.length === 0 && <p style={{ fontSize: 13, color: "#22C55E" }}>✓ No open compliance issues</p>}
        {openIssues.map((e: ComplianceEvent) => {
          const cc = COMPLIANCE_COLORS[e.status] ?? GOLD;
          return (
            <div key={e.id} style={{ background: "#0f2744", border: `1px solid ${cc}40`, borderRadius: 8, padding: "12px 14px", marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <p style={{ fontWeight: 600, fontSize: 13, color: "#F0F4FA" }}>{e.event_type.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</p>
                <span style={{ fontSize: 10, fontWeight: 700, color: cc, background: `${cc}20`, border: `1px solid ${cc}40`, borderRadius: 4, padding: "2px 6px" }}>{e.status.toUpperCase()}</span>
              </div>
              {e.notes && <p style={{ fontSize: 12, color: "#8aa0bb" }}>{e.notes}</p>}
              {e.due_date && <p style={{ fontSize: 11, color: "#4a6080", marginTop: 4 }}>Due: {e.due_date}</p>}
            </div>
          );
        })}
      </div>
      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>UPCOMING DEADLINES ({deadlines.length})</p>
        {deadlines.map((e: ComplianceEvent) => (
          <div key={e.id} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px", marginBottom: 10 }}>
            <p style={{ fontWeight: 600, fontSize: 13, color: "#F0F4FA", marginBottom: 4 }}>{e.event_type.replace(/_/g, " ")}</p>
            <div style={{ display: "flex", gap: 16, fontSize: 12, color: "#8aa0bb" }}>
              <span>Due: {e.due_date}</span>
              {e.days_until_due !== undefined && <span style={{ color: e.days_until_due <= 14 ? "#F97316" : GOLD }}>{e.days_until_due} days</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AIBriefTab() {
  const { data: athletes = [] } = useQuery({ queryKey: ["nil-athletes"], queryFn: () => nilApi.athletes() });
  const [selectedId, setSelectedId] = useState<string>("program");
  const [brief, setBrief] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    setBrief("");
    const result = selectedId === "program"
      ? await nilApi.programBrief()
      : await nilApi.athleteBrief(selectedId);
    setBrief(result.brief);
    setLoading(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 20 }}>
      <div>
        <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>Select Scope</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div onClick={() => setSelectedId("program")} style={{ background: selectedId === "program" ? "rgba(201,168,76,0.1)" : "#0f2744", border: `1px solid ${selectedId === "program" ? GOLD : "rgba(201,168,76,0.15)"}`, borderRadius: 7, padding: "10px 12px", cursor: "pointer" }}>
            <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA" }}>Full Program Brief</p>
            <p style={{ fontSize: 11, color: "#8aa0bb" }}>All athletes · Portfolio view</p>
          </div>
          {(athletes as Athlete[]).map((a: Athlete) => (
            <div key={a.id} onClick={() => setSelectedId(a.id)} style={{ background: selectedId === a.id ? "rgba(201,168,76,0.1)" : "#0f2744", border: `1px solid ${selectedId === a.id ? GOLD : "rgba(201,168,76,0.15)"}`, borderRadius: 7, padding: "10px 12px", cursor: "pointer" }}>
              <p style={{ fontSize: 13, fontWeight: 600, color: "#F0F4FA" }}>{a.full_name}</p>
              <p style={{ fontSize: 11, color: "#8aa0bb" }}>{sportLabel(a.sport_primary)} · {a.school}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <button onClick={generate} disabled={loading} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "11px 24px", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer", fontSize: 14, display: "flex", alignItems: "center", gap: 8, marginBottom: 16, opacity: loading ? 0.7 : 1 }}>
          {loading ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={14} />Generate AI Brief</>}
        </button>
        {brief && (
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 22px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12 }}>
              <Brain size={14} style={{ color: GOLD }} />
              <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, letterSpacing: "0.08em", textTransform: "uppercase" }}>AI Strategic Brief</p>
            </div>
            <p style={{ fontSize: 14, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{brief}</p>
          </div>
        )}
        {!brief && !loading && (
          <div style={{ textAlign: "center", padding: "48px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Select a scope and generate an AI brief</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

const TABS = [
  { id: "athletes",   label: "Athletes",   icon: <Users size={14} /> },
  { id: "deals",      label: "Deals",      icon: <FileText size={14} /> },
  { id: "compliance", label: "Compliance", icon: <ShieldCheck size={14} /> },
  { id: "ai",         label: "AI Briefs",  icon: <Brain size={14} /> },
];

export default function NILProgramPage() {
  const [activeTab, setActiveTab] = useState("athletes");
  const { data: kpis } = useQuery<KPIs>({ queryKey: ["nil-kpis"], queryFn: nilApi.kpis });

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      

      {/* Header */}
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ background: GOLD, borderRadius: 3, padding: "1px 8px" }}>
            <span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: NAVY, letterSpacing: 2 }}>LPF FOUNDATION</span>
          </div>
        </div>
        <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2, marginBottom: 12 }}>NIL PROGRAM DASHBOARD</h1>
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
        {activeTab === "athletes"   && <AthletesTab />}
        {activeTab === "deals"      && <DealsTab />}
        {activeTab === "compliance" && <ComplianceTab />}
        {activeTab === "ai"         && <AIBriefTab />}
      </div>
    </div>
  );
}
