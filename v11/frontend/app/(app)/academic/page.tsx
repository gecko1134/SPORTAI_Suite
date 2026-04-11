"use client";
/**
 * SportAI Suite — Academic Programs
 * /app/academic/page.tsx · Sprint 6 · NXS National Complex
 * Tabs: Partners · Scheduling · Scholarships · Recruiting · AI Briefs
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GraduationCap, CalendarDays, BookOpen, Trophy, Brain, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const acadApi = {
  kpis:          () => fetch(`${API}/api/academic/kpis`).then(r => r.json()),
  partners:      (p?) => fetch(`${API}/api/academic/partners${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  schedule:      (p?) => fetch(`${API}/api/academic/schedule${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  scholarships:  () => fetch(`${API}/api/academic/scholarship-hours`).then(r => r.json()),
  matches:       (p?) => fetch(`${API}/api/academic/recruiting-matches${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  compliance:    () => fetch(`${API}/api/academic/compliance`).then(r => r.json()),
  seed:          () => fetch(`${API}/api/academic/seed`, { method: "POST" }).then(r => r.json()),
  partnerBrief:  (id: string) => fetch(`${API}/api/academic/ai-partner-brief/${id}`, { method: "POST" }).then(r => r.json()),
  programBrief:  () => fetch(`${API}/api/academic/ai-program-brief`, { method: "POST" }).then(r => r.json()),
  recruitingBrief:(id: string) => fetch(`${API}/api/academic/ai-recruiting-brief?partner_id=${id}`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const LEVEL_COLORS: Record<string, string> = {
  high_school: "#22C55E", community_college: "#60A5FA",
  college: GOLD, university: "#EF4444", club_program: "#A855F7",
};
const STATUS_COLORS: Record<string, string> = {
  active: "#22C55E", renewal: "#F97316", negotiating: "#60A5FA",
  prospect: "#6B7280", lapsed: "#374151",
};
const MATCH_COLORS: Record<string, string> = {
  pending: "#6B7280", contacted: "#60A5FA", visited: GOLD,
  committed: "#22C55E", declined: "#EF4444",
};

type Partner = {
  id: string; institution_name: string; level: string; city: string; state: string;
  status: string; sports: string[]; student_athletes: number; annual_contract_value: number;
  partnership_end?: string; scholarship_hours_granted: number; scholarship_hours_used: number;
  scholarship_hours_remaining: number; scholarship_utilization_pct: number;
  days_until_expiry?: number; is_renewal_due: boolean; primary_contact: string;
};
type KPIs = {
  active_partners: number; renewal_partners: number; prospects: number;
  annual_contract_revenue: number; total_student_athletes: number;
  scholarship_hours_granted: number; scholarship_hours_used: number;
  scholarship_utilization_pct: number; scholarship_dollar_value: number;
  upcoming_blocks_14d: number; committed_recruiting_matches: number;
  level_breakdown: Record<string, number>;
};

function KPIStrip({ kpis }: { kpis: KPIs }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10, marginBottom: 24 }}>
      {[
        { l: "Active Partners",    v: kpis.active_partners,           c: "#22C55E" },
        { l: "Renewal Due",        v: kpis.renewal_partners,          c: "#F97316" },
        { l: "Prospects",          v: kpis.prospects,                 c: "#6B7280" },
        { l: "Contract Revenue",   v: fmt(kpis.annual_contract_revenue), c: GOLD },
        { l: "Student Athletes",   v: kpis.total_student_athletes.toLocaleString(), c: "#60A5FA" },
        { l: "Scholarship Hrs",    v: `${kpis.scholarship_hours_granted}h`, c: "#A855F7" },
        { l: "Sch Utilization",    v: `${kpis.scholarship_utilization_pct}%`, c: kpis.scholarship_utilization_pct >= 60 ? "#22C55E" : "#F97316" },
        { l: "Committed Matches",  v: kpis.committed_recruiting_matches, c: "#22C55E" },
      ].map(s => (
        <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "10px 12px" }}>
          <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
        </div>
      ))}
    </div>
  );
}

function PartnersTab({ onSeed }: { onSeed: () => void }) {
  const [filter, setFilter] = useState("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [brief, setBrief] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const filterMap: Record<string, Record<string, string>> = {
    all: {}, active: { status: "active" }, renewal: { status: "renewal" },
    hs: { level: "high_school" }, college: { level: "university" },
  };
  const { data: partners = [] } = useQuery<Partner[]>({ queryKey: ["acad-partners", filter], queryFn: () => acadApi.partners(filterMap[filter]) });

  const selected = (partners as Partner[]).find((p: Partner) => p.id === selectedId);

  const generateBrief = async (id: string) => {
    setLoading(true); setBrief("");
    const result = await acadApi.partnerBrief(id);
    setBrief(result.brief);
    setLoading(false);
  };

  if (!partners.length && filter === "all") return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <GraduationCap size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>No academic partners yet</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed Academic Programs</button>
    </div>
  );

  return (
    <div style={{ display: "grid", gridTemplateColumns: selectedId ? "1fr 360px" : "1fr", gap: 20 }}>
      <div>
        <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
          {[["all","All"],["active","Active"],["renewal","Renewal Due"],["hs","High Schools"],["college","Universities"]].map(([k,l]) => (
            <button key={k} onClick={() => { setFilter(k); setSelectedId(null); setBrief(""); }} style={{ background: filter === k ? GOLD : "#0f2744", color: filter === k ? NAVY : "#8aa0bb", border: `1px solid ${filter === k ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>
          ))}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {(partners as Partner[]).map((p: Partner) => {
            const lc = LEVEL_COLORS[p.level] ?? GOLD;
            const sc = STATUS_COLORS[p.status] ?? "#6B7280";
            const isSelected = selectedId === p.id;
            return (
              <div key={p.id} onClick={() => { setSelectedId(isSelected ? null : p.id); setBrief(""); }}
                style={{ background: isSelected ? "#152f52" : "#0f2744", border: `1px solid ${isSelected ? GOLD : "rgba(201,168,76,0.12)"}`, borderRadius: 8, padding: "14px 16px", cursor: "pointer", transition: "all 0.15s" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                  <div>
                    <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 3 }}>{p.institution_name}</p>
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      <span style={{ fontSize: 10, fontWeight: 700, color: lc, background: `${lc}15`, border: `1px solid ${lc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(p.level)}</span>
                      <span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 6px" }}>{p.status.toUpperCase()}</span>
                      {p.is_renewal_due && <span style={{ fontSize: 10, fontWeight: 700, color: "#F97316", background: "rgba(249,115,22,0.15)", border: "1px solid rgba(249,115,22,0.3)", borderRadius: 3, padding: "1px 6px" }}>RENEWAL {p.days_until_expiry}d</span>}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{fmt(p.annual_contract_value)}<span style={{ fontSize: 10, color: "#4a6080" }}>/yr</span></p>
                    <p style={{ fontSize: 11, color: "#8aa0bb" }}>{p.student_athletes} athletes</p>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 14, fontSize: 11, color: "#8aa0bb" }}>
                  <span>📍 {p.city}, {p.state}</span>
                  <span>🎯 {p.sports.slice(0, 3).map(lbl).join(", ")}</span>
                  <span style={{ color: p.scholarship_utilization_pct >= 60 ? "#22C55E" : "#F97316" }}>
                    📚 {p.scholarship_hours_used}/{p.scholarship_hours_granted}h ({p.scholarship_utilization_pct}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {selected && (
        <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px", position: "sticky", top: 20, maxHeight: "80vh", overflowY: "auto" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F0F4FA", marginBottom: 2 }}>{selected.institution_name}</p>
          <p style={{ fontSize: 12, color: "#8aa0bb", marginBottom: 14 }}>{selected.primary_contact} · {selected.city}, {selected.state}</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 14 }}>
            {[
              { l: "Contract", v: fmt(selected.annual_contract_value), c: GOLD },
              { l: "Athletes", v: selected.student_athletes, c: "#60A5FA" },
              { l: "Sch Hrs Left", v: `${selected.scholarship_hours_remaining}h`, c: "#22C55E" },
              { l: "Utilization", v: `${selected.scholarship_utilization_pct}%`, c: selected.scholarship_utilization_pct >= 60 ? "#22C55E" : "#F97316" },
            ].map(s => (
              <div key={s.l} style={{ background: "#152f52", borderRadius: 5, padding: "8px 10px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 2 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
          <div style={{ marginBottom: 12 }}>
            <p style={{ fontSize: 11, color: "#4a6080", marginBottom: 4 }}>Sports</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
              {selected.sports.map(s => <span key={s} style={{ fontSize: 11, color: GOLD, background: "rgba(201,168,76,0.1)", border: "1px solid rgba(201,168,76,0.25)", borderRadius: 3, padding: "2px 7px" }}>{lbl(s)}</span>)}
            </div>
          </div>
          <button onClick={() => generateBrief(selected.id)} disabled={loading} style={{ width: "100%", background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px", fontWeight: 700, cursor: "pointer", fontSize: 13, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 12 }}>
            {loading ? <><RefreshCw size={13} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={13} />AI Partner Brief</>}
          </button>
          {brief && (
            <div style={{ background: "#152f52", borderRadius: 8, padding: "12px 14px" }}>
              <p style={{ fontSize: 12, color: "#d0dce8", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{brief}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SchedulingTab() {
  const today = new Date().toISOString().split("T")[0];
  const futureDate = new Date(Date.now() + 14 * 86400000).toISOString().split("T")[0];
  const { data: blocks = [] } = useQuery({ queryKey: ["acad-schedule"], queryFn: () => acadApi.schedule({ from_date: today, to_date: futureDate }) });
  const { data: partners = [] } = useQuery<Partner[]>({ queryKey: ["acad-partners", "all"], queryFn: () => acadApi.partners() });
  const partnerMap = Object.fromEntries((partners as Partner[]).map(p => [p.id, p.institution_name]));

  const SPORT_COLORS: Record<string, string> = {
    soccer: "#22C55E", basketball: "#F97316", volleyball: "#A855F7",
    ice_hockey: "#60A5FA", lacrosse: GOLD, softball: "#EF4444",
    flag_football: "#F97316", pickleball: "#22C55E", robotics: "#6B7280",
  };
  const AREA_ICONS: Record<string, string> = {
    "Large Dome": "🏟️", "Small Dome": "⛺", "Ice Rink": "🧊",
    "Outdoor Field 1": "🌿", "Outdoor Field 2": "🌿", "Health Center": "🏥",
    "Skill Shot Academy": "⛳", "PuttView AR": "⛳",
  };

  const grouped = (blocks as any[]).reduce((acc: Record<string, any[]>, b: any) => {
    acc[b.block_date] = [...(acc[b.block_date] || []), b];
    return acc;
  }, {});

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {Object.entries(grouped).map(([dateStr, dayBlocks]) => {
        const d = new Date(dateStr + "T12:00:00");
        const label = d.toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });
        const scholarshipBlocks = (dayBlocks as any[]).filter((b: any) => b.is_scholarship).length;
        const dayRev = (dayBlocks as any[]).reduce((s: number, b: any) => s + b.revenue, 0);
        return (
          <div key={dateStr} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 10, overflow: "hidden" }}>
            <div style={{ background: "#152f52", padding: "10px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, letterSpacing: 1, color: "#F0F4FA" }}>{label}</p>
              <div style={{ display: "flex", gap: 12 }}>
                {scholarshipBlocks > 0 && <span style={{ fontSize: 11, color: "#A855F7" }}>📚 {scholarshipBlocks} scholarship</span>}
                {dayRev > 0 && <span style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(dayRev)}</span>}
              </div>
            </div>
            <div style={{ padding: "8px 12px", display: "flex", flexDirection: "column", gap: 6 }}>
              {(dayBlocks as any[]).map((b: any) => {
                const sc = SPORT_COLORS[b.sport] ?? GOLD;
                return (
                  <div key={b.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", background: `${sc}08`, borderRadius: 6, borderLeft: `3px solid ${sc}` }}>
                    <span style={{ fontSize: 14 }}>{(AREA_ICONS as any)[b.facility_area] || "🏢"}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA" }}>{partnerMap[b.partner_id] || "Partner"}</p>
                        <span style={{ fontSize: 11, color: b.is_scholarship ? "#A855F7" : GOLD, fontWeight: 700 }}>
                          {b.is_scholarship ? "📚 Scholarship" : fmt(b.revenue)}
                        </span>
                      </div>
                      <div style={{ display: "flex", gap: 10, fontSize: 11, color: "#8aa0bb" }}>
                        <span>{b.start_time}–{b.end_time}</span>
                        <span style={{ color: sc }}>{lbl(b.sport)}</span>
                        <span>{b.facility_area}</span>
                        {b.attendees && <span>👥 {b.attendees}</span>}
                      </div>
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

function ScholarshipsTab() {
  const { data: sch } = useQuery({ queryKey: ["acad-scholarships"], queryFn: acadApi.scholarships });
  if (!sch) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10 }}>
        {[
          { l: "Hours Granted",     v: `${sch.total_hours_granted}h`, c: "#60A5FA" },
          { l: "Hours Used",        v: `${sch.total_hours_used}h`,    c: "#22C55E" },
          { l: "Hours Remaining",   v: `${sch.total_hours_remaining}h`, c: GOLD },
          { l: "Utilization",       v: `${sch.overall_utilization_pct}%`, c: sch.overall_utilization_pct >= 60 ? "#22C55E" : "#F97316" },
          { l: "Dollar Value",      v: fmt(sch.dollar_value_granted), c: "#A855F7" },
          { l: "Expiring ≤90d",    v: sch.partners_expiring_90d,      c: "#F97316" },
          { l: "Low Utilization",   v: sch.partners_low_utilization,  c: "#EF4444" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "10px 12px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      {/* Partner detail */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>SCHOLARSHIP HOURS BY PARTNER</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {sch.partner_detail.map((p: any) => {
            const barW = `${p.utilization_pct}%`;
            const barColor = p.utilization_pct >= 75 ? "#22C55E" : p.utilization_pct >= 40 ? GOLD : "#EF4444";
            return (
              <div key={p.id} style={{ background: "#152f52", borderRadius: 7, padding: "12px 14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                  <div>
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA" }}>{p.institution_name}</p>
                    <p style={{ fontSize: 11, color: "#8aa0bb" }}>{lbl(p.level)}{p.is_renewal_due ? ` · ⚠️ Renewal ${p.days_until_expiry}d` : ""}</p>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: barColor }}>{p.utilization_pct}%</p>
                    <p style={{ fontSize: 11, color: "#8aa0bb" }}>{p.hours_used}/{p.hours_granted}h</p>
                  </div>
                </div>
                <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
                  <div style={{ height: "100%", width: barW, background: barColor, borderRadius: 3, transition: "width 0.4s" }} />
                </div>
                <p style={{ fontSize: 11, color: "#4a6080", marginTop: 4 }}>{p.hours_remaining}h remaining · ${(p.hours_remaining * 150).toLocaleString()} value</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function RecruitingTab() {
  const [statusFilter, setStatusFilter] = useState("");
  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  const { data: matches = [] } = useQuery({ queryKey: ["acad-matches", statusFilter], queryFn: () => acadApi.matches(params) });
  const { data: partners = [] } = useQuery<Partner[]>({ queryKey: ["acad-partners", "all"], queryFn: () => acadApi.partners() });
  const partnerMap = Object.fromEntries((partners as Partner[]).map(p => [p.id, p.institution_name]));
  const STATUSES = ["pending","contacted","visited","committed","declined"];

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        <button onClick={() => setStatusFilter("")} style={{ background: !statusFilter ? GOLD : "#0f2744", color: !statusFilter ? NAVY : "#8aa0bb", border: `1px solid ${!statusFilter ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>All</button>
        {STATUSES.map(s => {
          const c = MATCH_COLORS[s] ?? GOLD;
          return <button key={s} onClick={() => setStatusFilter(s)} style={{ background: statusFilter === s ? c : "#0f2744", color: statusFilter === s ? "#071828" : "#8aa0bb", border: `1px solid ${statusFilter === s ? c : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{lbl(s)}</button>;
        })}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 10 }}>
        {(matches as any[]).map((m: any) => {
          const sc = MATCH_COLORS[m.status] ?? GOLD;
          const scoreColor = m.match_score >= 85 ? "#22C55E" : m.match_score >= 70 ? GOLD : "#F97316";
          return (
            <div key={m.id} style={{ background: "#0f2744", border: `1px solid ${sc}30`, borderRadius: 8, padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                <div>
                  <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 2 }}>{m.athlete_name}</p>
                  <p style={{ fontSize: 11, color: "#8aa0bb" }}>{m.athlete_school} · Class of {m.athlete_grad_year}</p>
                  <p style={{ fontSize: 11, color: "#8aa0bb" }}>{lbl(m.sport)} · GPA {m.gpa ?? "N/A"}</p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 26, color: scoreColor }}>{m.match_score}</p>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>match score</p>
                </div>
              </div>
              <p style={{ fontSize: 11, color: "#60A5FA", marginBottom: 6 }}>→ {partnerMap[m.partner_id] || "Partner"}</p>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "2px 8px" }}>{m.status.toUpperCase()}</span>
                {m.contacted_date && <span style={{ fontSize: 10, color: "#4a6080" }}>Contacted: {m.contacted_date}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AIBriefTab() {
  const { data: partners = [] } = useQuery<Partner[]>({ queryKey: ["acad-partners", "all"], queryFn: () => acadApi.partners({ status: "active" }) });
  const [selectedId, setSelectedId] = useState("program");
  const [briefType, setBriefType] = useState<"partner" | "program" | "recruiting">("program");
  const [brief, setBrief] = useState("");
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true); setBrief("");
    let result;
    if (briefType === "program") {
      result = await acadApi.programBrief();
      setBrief(result.brief);
    } else if (briefType === "partner" && selectedId !== "program") {
      result = await acadApi.partnerBrief(selectedId);
      setBrief(result.brief);
    } else if (briefType === "recruiting" && selectedId !== "program") {
      result = await acadApi.recruitingBrief(selectedId);
      setBrief(result.brief);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 20 }}>
      <div>
        <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Brief Type</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 }}>
          {[["program","Portfolio Brief","All partners + scholarship + pipeline"],["partner","Partner Brief","Selected institution"],["recruiting","Recruiting Brief","Selected institution's pipeline"]].map(([type, label, sub]) => (
            <div key={type} onClick={() => { setBriefType(type as any); setBrief(""); }} style={{ background: briefType === type ? "rgba(201,168,76,0.1)" : "#0f2744", border: `1px solid ${briefType === type ? GOLD : "rgba(201,168,76,0.15)"}`, borderRadius: 7, padding: "10px 12px", cursor: "pointer" }}>
              <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA" }}>{label}</p>
              <p style={{ fontSize: 11, color: "#8aa0bb" }}>{sub}</p>
            </div>
          ))}
        </div>
        {briefType !== "program" && (
          <>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>Select Partner</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, maxHeight: 240, overflowY: "auto" }}>
              {(partners as Partner[]).map((p: Partner) => (
                <div key={p.id} onClick={() => setSelectedId(p.id)} style={{ background: selectedId === p.id ? "rgba(201,168,76,0.1)" : "#0f2744", border: `1px solid ${selectedId === p.id ? GOLD : "rgba(201,168,76,0.1)"}`, borderRadius: 6, padding: "8px 10px", cursor: "pointer" }}>
                  <p style={{ fontSize: 12, fontWeight: 600, color: "#F0F4FA" }}>{p.institution_name}</p>
                  <p style={{ fontSize: 10, color: "#8aa0bb" }}>{lbl(p.level)}</p>
                </div>
              ))}
            </div>
          </>
        )}
        <button onClick={generate} disabled={loading || (briefType !== "program" && selectedId === "program")} style={{ width: "100%", background: GOLD, color: NAVY, border: "none", borderRadius: 7, padding: "10px", fontWeight: 700, cursor: "pointer", fontSize: 13, marginTop: 14, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
          {loading ? <><RefreshCw size={13} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={13} />Generate Brief</>}
        </button>
      </div>
      <div>
        {brief ? (
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "20px 24px" }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: GOLD, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>AI ACADEMIC BRIEF</p>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{brief}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "80px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
            <p style={{ fontSize: 14, color: "#8aa0bb" }}>Select brief type and generate</p>
            <p style={{ fontSize: 12, color: "#4a6080", marginTop: 4 }}>Portfolio · Partner · Recruiting pipeline</p>
          </div>
        )}
      </div>
    </div>
  );
}

const TABS = [
  { id: "partners",    label: "Partners",     icon: <GraduationCap size={14} /> },
  { id: "scheduling",  label: "Scheduling",   icon: <CalendarDays size={14} /> },
  { id: "scholarships",label: "Scholarships", icon: <BookOpen size={14} /> },
  { id: "recruiting",  label: "Recruiting",   icon: <Trophy size={14} /> },
  { id: "ai",          label: "AI Briefs",    icon: <Brain size={14} /> },
];

export default function AcademicPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("partners");
  const [seeding, setSeeding] = useState(false);
  const { data: kpis } = useQuery<KPIs>({ queryKey: ["acad-kpis"], queryFn: acadApi.kpis });

  const handleSeed = async () => {
    setSeeding(true);
    await acadApi.seed();
    ["acad-kpis","acad-partners","acad-schedule","acad-scholarships","acad-matches"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NXS NATIONAL COMPLEX","HS · COLLEGE · UNIVERSITY","SCHOLARSHIP HOURS","RECRUITING MATCH ENGINE"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>ACADEMIC PROGRAMS</h1>
          {kpis && <div style={{ display: "flex", gap: 16, marginBottom: 6, flexWrap: "wrap" }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Revenue: <strong style={{ color: GOLD }}>{fmt(kpis.annual_contract_revenue)}</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Athletes: <strong style={{ color: "#60A5FA" }}>{kpis.total_student_athletes}</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Scholarships: <strong style={{ color: "#A855F7" }}>{kpis.scholarship_utilization_pct}%</strong></span>
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
        {kpis && <KPIStrip kpis={kpis} />}
        {activeTab === "partners"     && <PartnersTab onSeed={handleSeed} />}
        {activeTab === "scheduling"   && <SchedulingTab />}
        {activeTab === "scholarships" && <ScholarshipsTab />}
        {activeTab === "recruiting"   && <RecruitingTab />}
        {activeTab === "ai"           && <AIBriefTab />}
      </div>
    </div>
  );
}
