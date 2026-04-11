"use client";
/**
 * SportAI Suite — Capital Stack Tracker
 * /app/capital-stack/page.tsx · Sprint 8 · NGP Development
 * Tabs: Sources · Disbursements · IRR Model · TID · AI Investor Brief
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { DollarSign, BarChart2, TrendingUp, Waves, Brain, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const capApi = {
  sources:   (p?) => fetch(`${API}/api/capital/sources${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  disbs:     (p?) => fetch(`${API}/api/capital/disbursements${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  irr:       () => fetch(`${API}/api/capital/irr-model`).then(r => r.json()),
  tid:       () => fetch(`${API}/api/capital/tid-model`).then(r => r.json()),
  reports:   () => fetch(`${API}/api/capital/investor-reports`).then(r => r.json()),
  seed:      () => fetch(`${API}/api/capital/seed`, { method: "POST" }).then(r => r.json()),
  aiBrief:   () => fetch(`${API}/api/capital/ai-investor-brief`, { method: "POST" }).then(r => r.json()),
  aiGapClose:() => fetch(`${API}/api/capital/ai-gap-close-brief`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const PHASE_COLORS: Record<string, string> = { phase1: "#22C55E", phase2: GOLD, bridge: "#60A5FA" };
const STATUS_COLORS: Record<string, string> = {
  planning: "#6B7280", application: "#60A5FA", committed: GOLD,
  received: "#F97316", deployed: "#22C55E", closed: "#4ade80",
};
const SOURCE_COLORS: Record<string, string> = {
  community_bonds: "#60A5FA", bank_loan: "#6B7280", sba_504: "#60A5FA",
  naming_rights: GOLD, state_grant: "#22C55E", crowdfunding: "#F97316",
  equity: "#A855F7", irrrb_grant: "#22C55E", mn_deed_grant: "#22C55E",
};
const CAT_COLORS: Record<string, string> = {
  land: "#60A5FA", construction: "#F97316", equipment: GOLD,
  ff_and_e: "#A855F7", soft_costs: "#6B7280", working_capital: "#22C55E",
  contingency: "#EF4444", debt_service: "#F97316",
};

function WaterfallBar({ label, committed, target, color, subtitle }: any) {
  const pct = Math.min(Math.round(committed / target * 100), 100);
  const gap = target - committed;
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <div>
          <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA" }}>{label}</p>
          {subtitle && <p style={{ fontSize: 11, color: "#8aa0bb" }}>{subtitle}</p>}
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color }}>{fmt(committed)}</p>
          <p style={{ fontSize: 10, color: "#4a6080" }}>of {fmt(target)} · {pct}%</p>
        </div>
      </div>
      <div style={{ height: 8, background: "rgba(255,255,255,0.06)", borderRadius: 4, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: `linear-gradient(90deg, ${color}88, ${color})`, borderRadius: 4, transition: "width 0.5s" }} />
      </div>
      {gap > 0 && <p style={{ fontSize: 11, color: "#EF4444", marginTop: 3 }}>Gap: {fmt(gap)}</p>}
    </div>
  );
}

function SourcesTab({ onSeed }: { onSeed: () => void }) {
  const [phaseFilter, setPhaseFilter] = useState("");
  const params: Record<string, string> = {};
  if (phaseFilter) params.phase = phaseFilter;
  const { data: sources = [] } = useQuery({ queryKey: ["cap-sources", phaseFilter], queryFn: () => capApi.sources(params) });
  const { data: irr } = useQuery({ queryKey: ["cap-irr"], queryFn: capApi.irr });

  if (!sources.length && !phaseFilter) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <DollarSign size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Capital Stack not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed $9.85M Capital Stack</button>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {irr && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 10 }}>
          {[
            { l: "Total Target",  v: fmt(irr.total_target),    c: "#F0F4FA" },
            { l: "Committed",     v: `${irr.committed_pct}%`,  c: irr.committed_pct >= 80 ? "#22C55E" : GOLD },
            { l: "Total Gap",     v: fmt(irr.total_gap),        c: "#EF4444" },
            { l: "Proj. IRR",     v: `${irr.projected_irr}%`,  c: GOLD },
            { l: "Payback",       v: `${irr.projected_payback_yrs}yr`, c: "#60A5FA" },
          ].map(s => (
            <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "10px 12px" }}>
              <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
            </div>
          ))}
        </div>
      )}

      {/* Phase waterfall */}
      {irr && (
        <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 16 }}>CAPITAL WATERFALL — $9.85M PIPELINE</p>
          <WaterfallBar label="Phase 1 — Campus Build ($5.2M)" committed={irr.phase1_committed} target={irr.phase1_target} color="#22C55E" subtitle="Community bonds + IRRRB + Bank loan + DEED + Equity" />
          <WaterfallBar label="Phase 2 — Skill Shot + PuttView ($4.65M)" committed={irr.phase2_committed} target={irr.phase2_target} color={GOLD} subtitle="SBA 504 + Naming Rights + State Grants + Crowdfunding" />
          <WaterfallBar label="TOTAL CAPITAL PIPELINE" committed={irr.total_committed} target={irr.total_target} color="#60A5FA" />
        </div>
      )}

      {/* Phase filter */}
      <div style={{ display: "flex", gap: 8 }}>
        {[["","All Phases"],["phase1","Phase 1"],["phase2","Phase 2"]].map(([k,l]) => (
          <button key={k} onClick={() => setPhaseFilter(k)} style={{ background: phaseFilter === k ? GOLD : "#0f2744", color: phaseFilter === k ? NAVY : "#8aa0bb", border: `1px solid ${phaseFilter === k ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>
        ))}
      </div>

      {/* Source cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {(sources as any[]).map((s: any) => {
          const pc = PHASE_COLORS[s.phase] ?? GOLD;
          const sc = STATUS_COLORS[s.status] ?? "#6B7280";
          const tc = SOURCE_COLORS[s.source_type] ?? GOLD;
          return (
            <div key={s.id} style={{ background: "#0f2744", border: `1px solid ${s.gap > 0 ? "rgba(249,115,22,0.25)" : "rgba(201,168,76,0.12)"}`, borderRadius: 8, padding: "14px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 5 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: pc, background: `${pc}15`, border: `1px solid ${pc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.phase)}</span>
                    <span style={{ fontSize: 10, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.source_type)}</span>
                    <span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(s.status)}</span>
                  </div>
                  <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 3 }}>{s.label}</p>
                  {s.lender_investor && <p style={{ fontSize: 12, color: "#8aa0bb" }}>{s.lender_investor}</p>}
                  {s.notes && <p style={{ fontSize: 11, color: "#4a6080", marginTop: 3 }}>{s.notes}</p>}
                </div>
                <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 14 }}>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: GOLD }}>{fmt(s.committed_amount)}</p>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>of {fmt(s.target_amount)}</p>
                  {s.gap > 0 && <p style={{ fontSize: 12, color: "#EF4444", fontWeight: 700 }}>Gap: {fmt(s.gap)}</p>}
                  {s.interest_rate && <p style={{ fontSize: 11, color: "#8aa0bb", marginTop: 4 }}>{s.interest_rate}% / {s.term_years}yr</p>}
                  {s.annual_debt_service > 0 && <p style={{ fontSize: 11, color: "#F97316" }}>{fmt(s.annual_debt_service)}/yr debt svc</p>}
                </div>
              </div>
              <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
                <div style={{ height: "100%", width: `${s.committed_pct}%`, background: `linear-gradient(90deg, ${pc}88, ${pc})`, borderRadius: 3 }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function DisbursementsTab() {
  const { data: disbs = [] } = useQuery({ queryKey: ["cap-disbs"], queryFn: () => capApi.disbs() });
  const byCategory = (disbs as any[]).reduce((acc: Record<string, number>, d: any) => {
    acc[d.category] = (acc[d.category] || 0) + d.amount;
    return acc;
  }, {});
  const totalDeployed = (disbs as any[]).reduce((s: number, d: any) => s + d.amount, 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Category summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        {Object.entries(byCategory).map(([cat, total]: [string, any]) => {
          const cc = CAT_COLORS[cat] ?? GOLD;
          return (
            <div key={cat} style={{ background: `${cc}08`, border: `1px solid ${cc}30`, borderRadius: 8, padding: "12px 14px" }}>
              <p style={{ fontSize: 11, color: cc, fontWeight: 700, marginBottom: 4 }}>{lbl(cat)}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: "#F0F4FA" }}>{fmt(total)}</p>
            </div>
          );
        })}
        <div style={{ background: "rgba(201,168,76,0.08)", border: `1px solid ${GOLD}30`, borderRadius: 8, padding: "12px 14px" }}>
          <p style={{ fontSize: 11, color: GOLD, fontWeight: 700, marginBottom: 4 }}>TOTAL DEPLOYED</p>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: GOLD }}>{fmt(totalDeployed)}</p>
        </div>
      </div>

      {/* Disbursement table */}
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Phase","Category","Description","Amount","Date","Vendor"].map(h => (
                <th key={h} style={{ padding: "8px 10px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(disbs as any[]).map((d: any) => {
              const pc = PHASE_COLORS[d.phase] ?? GOLD;
              const cc = CAT_COLORS[d.category] ?? GOLD;
              return (
                <tr key={d.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "8px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: pc, background: `${pc}15`, borderRadius: 3, padding: "1px 6px" }}>{lbl(d.phase)}</span></td>
                  <td style={{ padding: "8px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: cc, background: `${cc}15`, borderRadius: 3, padding: "1px 6px" }}>{lbl(d.category)}</span></td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#F0F4FA" }}>{d.description}</td>
                  <td style={{ padding: "8px 10px", fontFamily: "'Bebas Neue'", fontSize: 16, color: GOLD }}>{fmt(d.amount)}</td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#8aa0bb" }}>{d.disbursed_date || "—"}</td>
                  <td style={{ padding: "8px 10px", fontSize: 12, color: "#8aa0bb" }}>{d.vendor || "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function IRRTab() {
  const { data: irr } = useQuery({ queryKey: ["cap-irr"], queryFn: capApi.irr });
  if (!irr) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  const maxRev = Math.max(...irr.five_year_cashflow_model.map((cf: any) => cf.revenue));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10 }}>
        {[
          { l: "Total Committed",  v: `${irr.committed_pct}%`,   c: irr.committed_pct >= 80 ? "#22C55E" : GOLD },
          { l: "Projected IRR",    v: `${irr.projected_irr}%`,   c: irr.projected_irr >= irr.target_irr ? "#22C55E" : "#F97316" },
          { l: "Target IRR",       v: `${irr.target_irr}%`,      c: "#4a6080" },
          { l: "Payback",          v: `${irr.projected_payback_yrs}yr`, c: GOLD },
          { l: "5-Year Target",    v: fmt(irr.five_year_revenue_target), c: "#22C55E" },
          { l: "Annual Debt Svc",  v: fmt(irr.annual_debt_service), c: "#F97316" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 24, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      {/* 5-year cash flow */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 16 }}>5-YEAR CASH FLOW MODEL</p>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 12, height: 100, marginBottom: 10 }}>
          {irr.five_year_cashflow_model.map((cf: any) => {
            const barH = Math.round((cf.revenue / maxRev) * 85);
            const netColor = cf.net >= 0 ? "#22C55E" : "#EF4444";
            return (
              <div key={cf.year} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <p style={{ fontSize: 10, color: netColor }}>Net: {fmt(cf.net)}</p>
                <div style={{ width: "70%", background: `linear-gradient(180deg, ${GOLD}, #7a612e)`, borderRadius: "3px 3px 0 0", height: `${barH}%`, minHeight: 4 }} />
                <p style={{ fontSize: 11, color: "#8aa0bb" }}>Yr {cf.year}</p>
                <p style={{ fontSize: 10, color: GOLD }}>{fmt(cf.revenue)}</p>
              </div>
            );
          })}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, marginTop: 8 }}>
          {irr.five_year_cashflow_model.map((cf: any) => (
            <div key={cf.year} style={{ background: "#152f52", borderRadius: 5, padding: "8px 10px" }}>
              <p style={{ fontSize: 10, color: "#4a6080" }}>Year {cf.year}</p>
              <p style={{ fontSize: 12, color: GOLD }}>{fmt(cf.revenue)}</p>
              <p style={{ fontSize: 12, color: cf.net >= 0 ? "#22C55E" : "#EF4444" }}>Net: {fmt(cf.net)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TIDTab() {
  const { data: tid } = useQuery({ queryKey: ["cap-tid"], queryFn: capApi.tid });
  if (!tid) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  const maxAssess = Math.max(...tid.monthly_detail.map((l: any) => l.tid_assessment));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        {[
          { l: "TID Assessed (12mo)", v: fmt(tid.total_tid_assessed_12mo),    c: GOLD },
          { l: "Hotel Revenue (12mo)",v: fmt(tid.total_hotel_revenue_12mo),  c: "#22C55E" },
          { l: "Annual TID Rate",     v: fmt(tid.annual_tid_rate_est),         c: GOLD },
          { l: "TID Bond Capacity",   v: fmt(tid.tid_bond_capacity),           c: "#60A5FA" },
          { l: "Avg Occupancy",       v: `${tid.avg_occupancy_pct}%`,          c: "#F97316" },
          { l: "Tourists Served",     v: tid.total_tourists_12mo.toLocaleString(), c: "#F0F4FA" },
          { l: "Assessment Rate",     v: tid.tid_assessment_rate,              c: "#4a6080" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>MONTHLY TID ASSESSMENT TREND</p>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 80, marginBottom: 10 }}>
          {tid.monthly_detail.map((l: any) => {
            const h = Math.round((l.tid_assessment / maxAssess) * 70);
            return (
              <div key={l.month} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 3 }}>
                <div style={{ width: "80%", background: `linear-gradient(180deg, ${GOLD}, #7a612e)`, borderRadius: "2px 2px 0 0", height: `${h}%`, minHeight: 3 }} title={`${l.month}: ${fmt(l.tid_assessment)}`} />
                <span style={{ fontSize: 9, color: "#4a6080", transform: "rotate(-30deg)", whiteSpace: "nowrap" }}>{l.month.slice(5)}</span>
              </div>
            );
          })}
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
            <thead><tr>{["Month","Hotel Rev","TID","Cumulative TID","Occ%","Tourists"].map(h => <th key={h} style={{ padding: "5px 8px", color: "#4a6080", textAlign: "left", fontWeight: 700 }}>{h}</th>)}</tr></thead>
            <tbody>
              {tid.monthly_detail.map((l: any) => (
                <tr key={l.month} style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "5px 8px", color: "#F0F4FA", fontWeight: 600 }}>{l.month}</td>
                  <td style={{ padding: "5px 8px", color: GOLD }}>{fmt(l.hotel_revenue)}</td>
                  <td style={{ padding: "5px 8px", color: "#22C55E" }}>{fmt(l.tid_assessment)}</td>
                  <td style={{ padding: "5px 8px", color: "#60A5FA" }}>{fmt(l.tid_cumulative)}</td>
                  <td style={{ padding: "5px 8px", color: "#F97316" }}>{l.occupancy_pct}%</td>
                  <td style={{ padding: "5px 8px", color: "#8aa0bb" }}>{l.tourism_visitors.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function AIBriefTab() {
  const [investorBrief, setInvestorBrief] = useState<any>(null);
  const [gapBrief, setGapBrief] = useState<any>(null);
  const [loadingInvestor, setLoadingInvestor] = useState(false);
  const [loadingGap, setLoadingGap] = useState(false);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      {[
        { title: "INVESTOR BRIEF", btn: "Generate Investor Brief", loading: loadingInvestor, result: investorBrief, field: "brief",
          run: async () => { setLoadingInvestor(true); setInvestorBrief(await capApi.aiBrief()); setLoadingInvestor(false); },
          extra: (r: any) => (
            <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
              {[["Committed", `${r.irr_summary.committed_pct}%`, "#22C55E"], ["IRR", `${r.irr_summary.projected_irr}%`, GOLD], ["Gap", fmt(r.irr_summary.total_gap), "#EF4444"]].map(([l, v, c]) => (
                <div key={l} style={{ background: "#152f52", borderRadius: 5, padding: "6px 12px" }}>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>{l}</p>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: c as string }}>{v}</p>
                </div>
              ))}
            </div>
          )},
        { title: "GAP CLOSE BRIEF", btn: "Gap Close Strategy", loading: loadingGap, result: gapBrief, field: "brief",
          run: async () => { setLoadingGap(true); setGapBrief(await capApi.aiGapClose()); setLoadingGap(false); },
          extra: (r: any) => r.total_gap > 0 && (
            <div style={{ marginTop: 10 }}>
              <p style={{ fontSize: 12, color: "#EF4444" }}>Total gap to close: <strong>{fmt(r.total_gap)}</strong></p>
            </div>
          )},
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
  { id: "sources", label: "Sources",        icon: <DollarSign size={14} /> },
  { id: "disbs",   label: "Disbursements",  icon: <BarChart2 size={14} /> },
  { id: "irr",     label: "IRR Model",      icon: <TrendingUp size={14} /> },
  { id: "tid",     label: "TID",            icon: <Waves size={14} /> },
  { id: "ai",      label: "AI Investor",    icon: <Brain size={14} /> },
];

export default function CapitalStackPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("sources");
  const [seeding, setSeeding] = useState(false);
  const { data: irr } = useQuery({ queryKey: ["cap-irr"], queryFn: capApi.irr });

  const handleSeed = async () => {
    setSeeding(true);
    await capApi.seed();
    ["cap-sources","cap-disbs","cap-irr","cap-tid"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["NGP DEVELOPMENT","$9.85M PIPELINE","IRR 36.8%","PAYBACK 3.1YR","5-YR $35.6M"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>CAPITAL STACK TRACKER</h1>
          {irr && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Committed: <strong style={{ color: GOLD }}>{irr.committed_pct}%</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>IRR: <strong style={{ color: irr.projected_irr >= irr.target_irr ? "#22C55E" : "#F97316" }}>{irr.projected_irr}%</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Gap: <strong style={{ color: "#EF4444" }}>{fmt(irr.total_gap)}</strong></span>
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
        {activeTab === "sources" && <SourcesTab onSeed={handleSeed} />}
        {activeTab === "disbs"   && <DisbursementsTab />}
        {activeTab === "irr"     && <IRRTab />}
        {activeTab === "tid"     && <TIDTab />}
        {activeTab === "ai"      && <AIBriefTab />}
      </div>
    </div>
  );
}
