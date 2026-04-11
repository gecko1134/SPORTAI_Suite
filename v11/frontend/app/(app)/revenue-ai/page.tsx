"use client";
/**
 * SportAI Suite — AI Revenue Maximizer
 * /app/revenue-ai/page.tsx · Sprint 7
 * Tabs: Score · Opportunities · Pricing Gaps · Cross-Sell · Weekly Brief
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Zap, Target, TrendingUp, ArrowRightLeft, Brain, RefreshCw, CheckCircle, AlertCircle } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const revApi = {
  score:       () => fetch(`${API}/api/revenue-ai/score`).then(r => r.json()),
  opps:        (p?) => fetch(`${API}/api/revenue-ai/opportunities${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  gaps:        () => fetch(`${API}/api/revenue-ai/pricing-gaps`).then(r => r.json()),
  crossSell:   () => fetch(`${API}/api/revenue-ai/cross-sell`).then(r => r.json()),
  actions:     () => fetch(`${API}/api/revenue-ai/actions`).then(r => r.json()),
  seed:        () => fetch(`${API}/api/revenue-ai/seed`, { method: "POST" }).then(r => r.json()),
  weeklyBrief: () => fetch(`${API}/api/revenue-ai/weekly-brief`, { method: "POST" }).then(r => r.json()),
  deepDive:    (mod: string) => fetch(`${API}/api/revenue-ai/ai-module-deep-dive?module=${mod}`, { method: "POST" }).then(r => r.json()),
  updateOpp:   (id: string, status: string) => fetch(`${API}/api/revenue-ai/opportunities/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const PRIORITY_COLORS: Record<string, string> = { critical: "#EF4444", high: "#F97316", medium: GOLD, low: "#6B7280" };
const TYPE_COLORS: Record<string, string> = {
  idle_capacity: "#60A5FA", pricing_gap: "#F97316", cross_sell: "#22C55E",
  retention_risk: "#EF4444", underutilized_asset: GOLD, revenue_leak: "#EF4444",
  upsell: "#A855F7", new_program: "#22C55E",
};
const EFFORT_COLORS: Record<string, string> = { low: "#22C55E", medium: GOLD, high: "#F97316" };

function ScoreGauge({ score, band }: { score: number; band: string }) {
  const r = 70; const circ = 2 * Math.PI * r;
  const color = score >= 80 ? "#22C55E" : score >= 60 ? GOLD : "#EF4444";
  return (
    <div style={{ textAlign: "center" }}>
      <svg width={170} height={170} viewBox="0 0 170 170">
        <circle cx={85} cy={85} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={14} />
        <circle cx={85} cy={85} r={r} fill="none" stroke={color} strokeWidth={14}
          strokeDasharray={circ} strokeDashoffset={circ - (score / 100) * circ}
          strokeLinecap="round" transform="rotate(-90 85 85)" style={{ transition: "stroke-dashoffset 0.8s" }} />
        <text x={85} y={78} textAnchor="middle" fill="#F0F4FA" fontSize={34} fontFamily="'Bebas Neue'" letterSpacing={1}>{score}</text>
        <text x={85} y={98} textAnchor="middle" fill={color} fontSize={13} fontFamily="'Barlow Condensed'" fontWeight={700}>{band}</text>
        <text x={85} y={112} textAnchor="middle" fill="#4a6080" fontSize={10} fontFamily="'Barlow Condensed'">REVENUE SCORE</text>
      </svg>
    </div>
  );
}

function ScoreTab({ onSeed }: { onSeed: () => void }) {
  const { data: score } = useQuery({ queryKey: ["rev-score"], queryFn: revApi.score });

  if (!score || score.open_opportunities === 0) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <Zap size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>Revenue Maximizer not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed 13 Opportunities</button>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ background: "#0f2744", border: `1px solid ${GOLD}40`, borderRadius: 10, padding: "24px 28px", display: "grid", gridTemplateColumns: "auto 1fr", gap: 28, alignItems: "start" }}>
        <ScoreGauge score={score.revenue_score} band={score.score_band} />
        <div>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 13, color: "#4a6080", letterSpacing: 2, marginBottom: 8 }}>CROSS-PLATFORM HEALTH SCORE</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            {[
              { l: "Open Opportunities", v: score.open_opportunities, c: "#F0F4FA" },
              { l: "Critical",           v: score.critical_open,       c: "#EF4444" },
              { l: "High Priority",      v: score.high_open,           c: "#F97316" },
              { l: "Impact at Stake",    v: fmt(score.total_impact_at_stake), c: GOLD },
            ].map(s => (
              <div key={s.l} style={{ background: "#152f52", borderRadius: 6, padding: "8px 12px" }}>
                <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 2 }}>{s.l}</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: s.c as string }}>{s.v}</p>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 11, color: "#4a6080", fontFamily: "monospace", background: "#152f52", borderRadius: 5, padding: "6px 10px" }}>{score.score_calculation}</p>
        </div>
      </div>

      {/* Module health */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>MODULE HEALTH SNAPSHOT</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 }}>
          {Object.entries(score.module_health).map(([key, val]: [string, any]) => {
            const pct = val as number;
            const color = pct >= 80 ? "#22C55E" : pct >= 60 ? GOLD : "#F97316";
            return (
              <div key={key} style={{ background: "#152f52", borderRadius: 7, padding: "10px 12px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                  <p style={{ fontSize: 12, color: "#8aa0bb" }}>{lbl(key)}</p>
                  <p style={{ fontSize: 13, fontWeight: 700, color }}>{pct}%</p>
                </div>
                <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                  <div style={{ height: "100%", width: `${pct}%`, background: color, borderRadius: 2, transition: "width 0.4s" }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function OpportunitiesTab() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState("all");
  const filterMap: Record<string, Record<string, string>> = {
    all: {}, critical: { priority: "critical" }, high: { priority: "high" },
    idle: { opp_type: "idle_capacity" }, pricing: { opp_type: "pricing_gap" },
  };
  const { data: opps = [] } = useQuery({ queryKey: ["rev-opps", filter], queryFn: () => revApi.opps(filterMap[filter]) });

  const totalImpact = (opps as any[]).reduce((s: number, o: any) => s + o.estimated_annual_impact, 0);

  const resolve = async (id: string) => {
    await revApi.updateOpp(id, "resolved");
    qc.invalidateQueries({ queryKey: ["rev-opps"] });
    qc.invalidateQueries({ queryKey: ["rev-score"] });
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {[["all","All"],["critical","🔴 Critical"],["high","🟠 High"],["idle","Idle Capacity"],["pricing","Pricing Gap"]].map(([k,l]) => (
            <button key={k} onClick={() => setFilter(k)} style={{ background: filter === k ? GOLD : "#0f2744", color: filter === k ? NAVY : "#8aa0bb", border: `1px solid ${filter === k ? GOLD : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>
          ))}
        </div>
        <span style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: GOLD }}>{fmt(totalImpact)} total impact</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {(opps as any[]).map((o: any) => {
          const pc = PRIORITY_COLORS[o.priority] ?? GOLD;
          const tc = TYPE_COLORS[o.opportunity_type] ?? GOLD;
          const ec = EFFORT_COLORS[o.effort_level] ?? GOLD;
          return (
            <div key={o.id} style={{ background: "#0f2744", border: `1px solid ${pc}30`, borderRadius: 8, padding: "16px 18px" }}>
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 10, marginBottom: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 6 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: pc, background: `${pc}15`, border: `1px solid ${pc}40`, borderRadius: 3, padding: "1px 7px" }}>{o.priority.toUpperCase()}</span>
                    <span style={{ fontSize: 10, fontWeight: 700, color: tc, background: `${tc}15`, border: `1px solid ${tc}40`, borderRadius: 3, padding: "1px 7px" }}>{lbl(o.opportunity_type)}</span>
                    <span style={{ fontSize: 10, color: "#8aa0bb", background: "#152f52", borderRadius: 3, padding: "1px 7px" }}>{o.module}</span>
                    <span style={{ fontSize: 10, color: ec, background: `${ec}15`, border: `1px solid ${ec}40`, borderRadius: 3, padding: "1px 7px" }}>{o.effort_level} effort</span>
                  </div>
                  <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 4 }}>{o.title}</p>
                  <p style={{ fontSize: 12, color: "#8aa0bb", lineHeight: 1.5, marginBottom: 8 }}>{o.description}</p>
                  <div style={{ background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 5, padding: "8px 12px" }}>
                    <p style={{ fontSize: 11, fontWeight: 700, color: "#22C55E", marginBottom: 3 }}>→ RECOMMENDED ACTION</p>
                    <p style={{ fontSize: 12, color: "#d0dce8" }}>{o.recommended_action}</p>
                  </div>
                </div>
                <div style={{ textAlign: "right", flexShrink: 0 }}>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 24, color: GOLD }}>{fmt(o.estimated_annual_impact)}</p>
                  <p style={{ fontSize: 10, color: "#4a6080", marginBottom: 8 }}>annual impact</p>
                  <button onClick={() => resolve(o.id)} style={{ background: "rgba(34,197,94,0.1)", color: "#22C55E", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 5, padding: "5px 10px", fontSize: 11, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
                    <CheckCircle size={11} />Resolve
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PricingGapsTab() {
  const { data: gaps = [] } = useQuery({ queryKey: ["rev-gaps"], queryFn: revApi.gaps });
  const totalGap = (gaps as any[]).reduce((s: number, g: any) => s + g.annual_impact, 0);

  return (
    <div>
      <div style={{ background: "rgba(249,115,22,0.08)", border: "1px solid rgba(249,115,22,0.25)", borderRadius: 8, padding: "12px 16px", marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p style={{ fontSize: 13, color: "#F97316" }}><strong>{(gaps as any[]).length} pricing gaps</strong> identified across modules</p>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: "#F97316" }}>{fmt(totalGap)} total annual gap</p>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {(gaps as any[]).map((g: any, i: number) => {
          const gapPct = g.gap_pct;
          const barColor = gapPct >= 50 ? "#EF4444" : gapPct >= 25 ? "#F97316" : GOLD;
          return (
            <div key={i} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.12)", borderRadius: 8, padding: "14px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                <div>
                  <div style={{ display: "flex", gap: 6, marginBottom: 4 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: "#8aa0bb", background: "#152f52", borderRadius: 3, padding: "1px 7px" }}>{g.module}</span>
                    <span style={{ fontSize: 10, fontWeight: 700, color: "#F97316", background: "rgba(249,115,22,0.1)", border: "1px solid rgba(249,115,22,0.3)", borderRadius: 3, padding: "1px 7px" }}>{gapPct.toFixed(1)}% gap</span>
                  </div>
                  <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA", marginBottom: 3 }}>{g.gap_type}</p>
                  <p style={{ fontSize: 12, color: "#8aa0bb" }}>Current: <span style={{ color: "#EF4444" }}>${g.current_rate}</span> → Optimal: <span style={{ color: "#22C55E" }}>${g.optimal_rate}</span> · {g.sessions_affected} sessions affected</p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: "#F97316" }}>{fmt(g.annual_impact)}</p>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>annual gap</p>
                </div>
              </div>
              <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3, marginBottom: 8 }}>
                <div style={{ height: "100%", width: `${Math.min(gapPct, 100)}%`, background: barColor, borderRadius: 3 }} />
              </div>
              <p style={{ fontSize: 12, color: "#22C55E" }}>→ {g.action}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CrossSellTab() {
  const { data: crossSells = [] } = useQuery({ queryKey: ["rev-cross"], queryFn: revApi.crossSell });
  const totalPotential = (crossSells as any[]).reduce((s: number, c: any) => s + c.potential_annual_revenue, 0);

  return (
    <div>
      <div style={{ background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.25)", borderRadius: 8, padding: "12px 16px", marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p style={{ fontSize: 13, color: "#22C55E" }}><strong>{(crossSells as any[]).length} cross-sell pairs</strong> mapped across modules</p>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: "#22C55E" }}>{fmt(totalPotential)} annual potential</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 12 }}>
        {(crossSells as any[]).map((c: any, i: number) => (
          <div key={i} style={{ background: "#0f2744", border: "1px solid rgba(34,197,94,0.18)", borderRadius: 8, padding: "14px 16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: GOLD, background: "rgba(201,168,76,0.1)", border: "1px solid rgba(201,168,76,0.25)", borderRadius: 3, padding: "2px 7px" }}>{c.source_module}</span>
              <ArrowRightLeft size={12} style={{ color: "#22C55E" }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: "#22C55E", background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 3, padding: "2px 7px" }}>{c.target_module}</span>
            </div>
            <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA", marginBottom: 4 }}>{c.offer}</p>
            <p style={{ fontSize: 12, color: "#8aa0bb", marginBottom: 8 }}>Trigger: {c.trigger}</p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 8 }}>
              <div style={{ background: "#152f52", borderRadius: 5, padding: "6px 10px" }}>
                <p style={{ fontSize: 10, color: "#4a6080" }}>Annual Revenue</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: "#22C55E" }}>{fmt(c.potential_annual_revenue)}</p>
              </div>
              <div style={{ background: "#152f52", borderRadius: 5, padding: "6px 10px" }}>
                <p style={{ fontSize: 10, color: "#4a6080" }}>Conversion Target</p>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: GOLD }}>{c.conversion_target_pct}%</p>
              </div>
            </div>
            <p style={{ fontSize: 11, color: "#22C55E" }}>→ {c.activation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function WeeklyBriefTab() {
  const [brief, setBrief] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [deepDive, setDeepDive] = useState<any>(null);
  const [ddModule, setDdModule] = useState("hotel");
  const [ddLoading, setDdLoading] = useState(false);

  const MODULES = ["hotel","rink","fnb","puttview","skill_shot","academic","campground","nil","foundation_card"];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA" }}>WEEKLY REVENUE BRIEF</p>
          <button onClick={async () => { setLoading(true); setBrief(await revApi.weeklyBrief()); setLoading(false); }} disabled={loading}
            style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "8px 16px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 6 }}>
            {loading ? <><RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />Generating…</> : <><Brain size={12} />Generate Brief</>}
          </button>
        </div>
        {brief ? (
          <div style={{ background: "#0f2744", border: `1px solid ${GOLD}`, borderRadius: 10, padding: "18px 20px" }}>
            <div style={{ display: "flex", gap: 12, marginBottom: 14, flexWrap: "wrap" }}>
              {[
                { l: "Revenue Score",    v: `${brief.revenue_score}/100`, c: GOLD },
                { l: "Impact at Stake", v: fmt(brief.total_impact_at_stake), c: "#EF4444" },
                { l: "Cross-Sell",      v: fmt(brief.cross_sell_potential), c: "#22C55E" },
                { l: "Pricing Gaps",   v: fmt(brief.pricing_gap_total),   c: "#F97316" },
              ].map(s => (
                <div key={s.l} style={{ background: "#152f52", borderRadius: 5, padding: "6px 12px" }}>
                  <p style={{ fontSize: 10, color: "#4a6080" }}>{s.l}</p>
                  <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, color: s.c as string }}>{s.v}</p>
                </div>
              ))}
            </div>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{brief.brief}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "60px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Brain size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Generate weekly cross-platform revenue brief</p>
          </div>
        )}
      </div>

      <div>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>MODULE DEEP DIVE</p>
        <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
          <select value={ddModule} onChange={e => setDdModule(e.target.value)} style={{ flex: 1, background: "#0f2744", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 6, color: "#F0F4FA", padding: "8px 10px", fontSize: 13, fontFamily: "'Barlow Condensed'" }}>
            {MODULES.map(m => <option key={m} value={m}>{lbl(m)}</option>)}
          </select>
          <button onClick={async () => { setDdLoading(true); setDeepDive(await revApi.deepDive(ddModule)); setDdLoading(false); }} disabled={ddLoading}
            style={{ background: "#0f2744", color: GOLD, border: `1px solid ${GOLD}`, borderRadius: 6, padding: "8px 14px", fontWeight: 700, cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", gap: 5 }}>
            {ddLoading ? <RefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} /> : <Brain size={12} />}
          </button>
        </div>
        {deepDive ? (
          <div style={{ background: "#0f2744", border: `1px solid rgba(201,168,76,0.3)`, borderRadius: 10, padding: "18px 20px" }}>
            <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
              <div><p style={{ fontSize: 10, color: "#4a6080" }}>MODULE</p><p style={{ fontSize: 14, fontWeight: 700, color: GOLD }}>{lbl(deepDive.module)}</p></div>
              <div><p style={{ fontSize: 10, color: "#4a6080" }}>OPEN OPPS</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F0F4FA" }}>{deepDive.opportunities}</p></div>
              <div><p style={{ fontSize: 10, color: "#4a6080" }}>TOTAL IMPACT</p><p style={{ fontFamily: "'Bebas Neue'", fontSize: 20, color: "#F97316" }}>{fmt(deepDive.total_module_impact)}</p></div>
            </div>
            <p style={{ fontSize: 13, color: "#d0dce8", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>{deepDive.brief}</p>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "60px 24px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.1)" }}>
            <Target size={32} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 10px" }} />
            <p style={{ fontSize: 13, color: "#8aa0bb" }}>Select a module and run deep-dive analysis</p>
          </div>
        )}
      </div>
    </div>
  );
}

const TABS = [
  { id: "score",   label: "Revenue Score",   icon: <Zap size={14} /> },
  { id: "opps",    label: "Opportunities",   icon: <Target size={14} /> },
  { id: "gaps",    label: "Pricing Gaps",    icon: <AlertCircle size={14} /> },
  { id: "cross",   label: "Cross-Sell",      icon: <ArrowRightLeft size={14} /> },
  { id: "brief",   label: "Weekly Brief",    icon: <Brain size={14} /> },
];

export default function RevenueAIPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("score");
  const [seeding, setSeeding] = useState(false);
  const { data: score } = useQuery({ queryKey: ["rev-score"], queryFn: revApi.score });

  const handleSeed = async () => {
    setSeeding(true);
    await revApi.seed();
    ["rev-score","rev-opps"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["CROSS-MODULE ENGINE","13 OPPORTUNITIES","PRICING GAPS","CROSS-SELL MAP"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>AI REVENUE MAXIMIZER</h1>
          {score && <div style={{ display: "flex", gap: 16, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>Score: <strong style={{ color: score.revenue_score >= 80 ? "#22C55E" : GOLD }}>{score.revenue_score}/100</strong></span>
            <span style={{ fontSize: 13, color: "#8aa0bb" }}>At Stake: <strong style={{ color: "#F97316" }}>{fmt(score.total_impact_at_stake)}</strong></span>
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
        {activeTab === "score" && <ScoreTab onSeed={handleSeed} />}
        {activeTab === "opps"  && <OpportunitiesTab />}
        {activeTab === "gaps"  && <PricingGapsTab />}
        {activeTab === "cross" && <CrossSellTab />}
        {activeTab === "brief" && <WeeklyBriefTab />}
      </div>
    </div>
  );
}
