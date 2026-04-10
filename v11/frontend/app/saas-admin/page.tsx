"use client";
/**
 * SportAI Suite — SaaS Admin v11
 * /app/saas-admin/page.tsx · Sprint 9 · Final Integration Capstone
 * Tabs: MRR Dashboard · Tenants · API Keys · White-Label · v11 Changelog
 */

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { BarChart2, Users, Key, Palette, BookOpen, RefreshCw } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const saasApi = {
  mrr:       () => fetch(`${API}/api/saas-admin/mrr-dashboard`).then(r => r.json()),
  tenants:   (p?) => fetch(`${API}/api/saas-admin/tenants${p ? "?" + new URLSearchParams(p) : ""}`).then(r => r.json()),
  apiKeys:   () => fetch(`${API}/api/saas-admin/api-keys`).then(r => r.json()),
  whiteLbl:  () => fetch(`${API}/api/saas-admin/white-label-configs`).then(r => r.json()),
  changelog: () => fetch(`${API}/api/saas-admin/changelog`).then(r => r.json()),
  seed:      () => fetch(`${API}/api/saas-admin/seed`, { method: "POST" }).then(r => r.json()),
};

const GOLD = "#C9A84C"; const NAVY = "#0A2240";
const fmt  = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
const lbl  = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

const PLAN_COLORS: Record<string, string>   = { starter: "#60A5FA", professional: GOLD, enterprise: "#22C55E" };
const STATUS_COLORS: Record<string, string> = { trial: "#60A5FA", active: "#22C55E", paused: GOLD, churned: "#EF4444" };
const PLAN_PRICE: Record<string, number>    = { starter: 299, professional: 599, enterprise: 1499 };

function MRRTab({ onSeed }: { onSeed: () => void }) {
  const { data: mrr } = useQuery({ queryKey: ["saas-mrr"], queryFn: saasApi.mrr });

  if (!mrr || mrr.active_tenants === 0) return (
    <div style={{ textAlign: "center", padding: "48px", background: "#0f2744", borderRadius: 10, border: "1px solid rgba(201,168,76,0.15)" }}>
      <BarChart2 size={36} style={{ color: "rgba(201,168,76,0.3)", margin: "0 auto 12px" }} />
      <p style={{ color: "#F0F4FA", fontWeight: 600, marginBottom: 16 }}>SaaS Admin not seeded</p>
      <button onClick={onSeed} style={{ background: GOLD, color: NAVY, border: "none", borderRadius: 6, padding: "10px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }}>Seed 12 Tenants</button>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Key metrics */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 12 }}>
        {[
          { l: "MRR",              v: fmt(mrr.mrr),                      c: GOLD },
          { l: "ARR",              v: fmt(mrr.arr),                      c: "#22C55E" },
          { l: "Active Tenants",   v: mrr.active_tenants,                c: "#22C55E" },
          { l: "Trial",            v: mrr.trial_tenants,                 c: "#60A5FA" },
          { l: "Churned",          v: mrr.churned_tenants,               c: "#EF4444" },
          { l: "Churn Rate",       v: `${mrr.churn_rate_pct}%`,          c: mrr.churn_rate_pct < 10 ? "#22C55E" : "#F97316" },
          { l: "Avg MRR/Tenant",   v: fmt(mrr.avg_mrr_per_tenant),       c: GOLD },
          { l: "Enterprise",       v: mrr.enterprise_tenants,            c: "#22C55E" },
          { l: "White-Label",      v: mrr.white_label_deployments,       c: "#A855F7" },
          { l: "API Calls MTD",    v: mrr.total_api_calls_mtd.toLocaleString(), c: "#60A5FA" },
        ].map(s => (
          <div key={s.l} style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 8, padding: "12px 14px" }}>
            <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{s.l}</p>
            <p style={{ fontFamily: "'Bebas Neue'", fontSize: 24, color: s.c as string }}>{s.v}</p>
          </div>
        ))}
      </div>

      {/* Plan breakdown */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>MRR BY PLAN</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
          {Object.entries(mrr.plan_breakdown).map(([plan, data]: [string, any]) => {
            const pc = PLAN_COLORS[plan] ?? GOLD;
            const planPct = mrr.mrr > 0 ? Math.round(data.mrr / mrr.mrr * 100) : 0;
            return (
              <div key={plan} style={{ background: `${pc}08`, border: `1px solid ${pc}30`, borderRadius: 8, padding: "14px 16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                  <div>
                    <p style={{ fontFamily: "'Bebas Neue'", fontSize: 16, color: pc }}>{lbl(plan)}</p>
                    <p style={{ fontSize: 11, color: "#4a6080" }}>${PLAN_PRICE[plan]}/mo per seat</p>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <p style={{ fontFamily: "'Bebas Neue'", fontSize: 24, color: "#F0F4FA" }}>{data.count}</p>
                    <p style={{ fontSize: 10, color: "#4a6080" }}>tenants</p>
                  </div>
                </div>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 22, color: GOLD }}>{fmt(data.mrr)}<span style={{ fontSize: 11, color: "#4a6080" }}>/mo</span></p>
                <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2, marginTop: 8 }}>
                  <div style={{ height: "100%", width: `${planPct}%`, background: pc, borderRadius: 2 }} />
                </div>
                <p style={{ fontSize: 10, color: "#4a6080", marginTop: 4 }}>{planPct}% of MRR</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function TenantsTab() {
  const [statusFilter, setStatusFilter] = useState("");
  const [planFilter, setPlanFilter] = useState("");
  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (planFilter)   params.plan   = planFilter;
  const { data: tenants = [] } = useQuery({ queryKey: ["saas-tenants", statusFilter, planFilter], queryFn: () => saasApi.tenants(params) });

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {[["","All"],["active","Active"],["trial","Trial"],["paused","Paused"],["churned","Churned"]].map(([k,l]) => {
            const c = k ? STATUS_COLORS[k] : GOLD;
            return <button key={k} onClick={() => setStatusFilter(k)} style={{ background: statusFilter === k ? (k ? c : GOLD) : "#0f2744", color: statusFilter === k ? "#071828" : "#8aa0bb", border: `1px solid ${statusFilter === k ? (k ? c : GOLD) : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 10px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>;
          })}
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginLeft: 8 }}>
          {[["","All Plans"],["starter","Starter"],["professional","Pro"],["enterprise","Enterprise"]].map(([k,l]) => {
            const c = k ? PLAN_COLORS[k] : GOLD;
            return <button key={k} onClick={() => setPlanFilter(k)} style={{ background: planFilter === k ? c : "#0f2744", color: planFilter === k ? "#071828" : "#8aa0bb", border: `1px solid ${planFilter === k ? c : "rgba(201,168,76,0.2)"}`, borderRadius: 6, padding: "5px 10px", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow Condensed'" }}>{l}</button>;
          })}
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Tenant","Plan","Status","MRR","Location","API Calls MTD","Modules","WL"].map(h => (
                <th key={h} style={{ padding: "8px 10px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(tenants as any[]).map((t: any) => {
              const pc = PLAN_COLORS[t.plan] ?? GOLD;
              const sc = STATUS_COLORS[t.status] ?? "#6B7280";
              return (
                <tr key={t.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "9px 10px" }}>
                    <p style={{ fontWeight: 700, fontSize: 13, color: "#F0F4FA" }}>{t.name}</p>
                    <p style={{ fontSize: 10, color: "#4a6080" }}>{t.contact_name} · {t.contact_email}</p>
                    {t.trial_end && <p style={{ fontSize: 10, color: "#60A5FA" }}>Trial ends: {t.trial_end}</p>}
                  </td>
                  <td style={{ padding: "9px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: pc, background: `${pc}15`, border: `1px solid ${pc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(t.plan)}</span></td>
                  <td style={{ padding: "9px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(t.status)}</span></td>
                  <td style={{ padding: "9px 10px", fontFamily: "'Bebas Neue'", fontSize: 18, color: t.monthly_revenue > 0 ? GOLD : "#4a6080" }}>{t.monthly_revenue > 0 ? fmt(t.monthly_revenue) : "—"}</td>
                  <td style={{ padding: "9px 10px", fontSize: 12, color: "#8aa0bb" }}>{t.city}, {t.state}</td>
                  <td style={{ padding: "9px 10px", fontSize: 12, color: t.api_calls_mtd > 10000 ? "#22C55E" : "#F0F4FA" }}>{t.api_calls_mtd.toLocaleString()}</td>
                  <td style={{ padding: "9px 10px", fontSize: 12, color: "#8aa0bb" }}>{t.modules_enabled}</td>
                  <td style={{ padding: "9px 10px", fontSize: 14 }}>{t.white_label ? "✅" : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function APIKeysTab() {
  const { data: keys = [] } = useQuery({ queryKey: ["saas-keys"], queryFn: saasApi.apiKeys });
  const totalCalls = (keys as any[]).reduce((s: number, k: any) => s + k.calls_total, 0);

  return (
    <div>
      <div style={{ background: "rgba(96,165,250,0.08)", border: "1px solid rgba(96,165,250,0.25)", borderRadius: 8, padding: "12px 16px", marginBottom: 16, display: "flex", justifyContent: "space-between" }}>
        <p style={{ fontSize: 13, color: "#60A5FA" }}><strong>{(keys as any[]).length}</strong> active API keys</p>
        <p style={{ fontSize: 13, color: "#60A5FA" }}><strong>{totalCalls.toLocaleString()}</strong> total API calls</p>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(201,168,76,0.2)" }}>
              {["Key Prefix","Label","Status","Rate Limit","Total Calls","Last Used","Expires"].map(h => (
                <th key={h} style={{ padding: "8px 10px", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#4a6080", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(keys as any[]).map((k: any) => {
              const sc = k.status === "active" ? "#22C55E" : "#EF4444";
              return (
                <tr key={k.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={{ padding: "9px 10px", fontFamily: "monospace", fontSize: 12, color: GOLD }}>{k.key_prefix}_****</td>
                  <td style={{ padding: "9px 10px", fontSize: 12, color: "#F0F4FA" }}>{k.label}</td>
                  <td style={{ padding: "9px 10px" }}><span style={{ fontSize: 10, fontWeight: 700, color: sc, background: `${sc}15`, border: `1px solid ${sc}40`, borderRadius: 3, padding: "1px 6px" }}>{lbl(k.status)}</span></td>
                  <td style={{ padding: "9px 10px", fontSize: 12, color: "#8aa0bb" }}>{k.rate_limit_per_min}/min</td>
                  <td style={{ padding: "9px 10px", fontFamily: "'Bebas Neue'", fontSize: 16, color: "#60A5FA" }}>{k.calls_total.toLocaleString()}</td>
                  <td style={{ padding: "9px 10px", fontSize: 11, color: "#4a6080" }}>{k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : "Never"}</td>
                  <td style={{ padding: "9px 10px", fontSize: 11, color: k.expires_at ? "#F97316" : "#4a6080" }}>{k.expires_at || "No expiry"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function WhiteLabelTab() {
  const { data: configs = [] } = useQuery({ queryKey: ["saas-wl"], queryFn: saasApi.whiteLbl });

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <p style={{ fontSize: 13, color: "#8aa0bb" }}><strong style={{ color: "#A855F7" }}>{(configs as any[]).length}</strong> white-label deployments — Enterprise plan only</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 12 }}>
        {(configs as any[]).map((c: any) => (
          <div key={c.id} style={{ background: "#0f2744", border: "1px solid rgba(168,85,247,0.25)", borderRadius: 10, padding: "16px 18px" }}>
            <div style={{ display: "flex", gap: 10, marginBottom: 12, alignItems: "center" }}>
              <div style={{ width: 28, height: 28, background: c.primary_color, borderRadius: 6, border: "2px solid rgba(255,255,255,0.1)" }} />
              <div style={{ width: 28, height: 28, background: c.secondary_color, borderRadius: 6, border: "2px solid rgba(255,255,255,0.1)" }} />
              <div>
                <p style={{ fontWeight: 700, fontSize: 14, color: "#F0F4FA" }}>{c.platform_name}</p>
                {c.custom_domain && <p style={{ fontSize: 11, color: "#A855F7" }}>🌐 {c.custom_domain}</p>}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <span style={{ fontSize: 11, color: c.primary_color, background: `${c.primary_color}15`, border: `1px solid ${c.primary_color}40`, borderRadius: 3, padding: "1px 7px" }}>Primary: {c.primary_color}</span>
              {c.hide_powered_by && <span style={{ fontSize: 11, color: "#A855F7", background: "rgba(168,85,247,0.1)", border: "1px solid rgba(168,85,247,0.3)", borderRadius: 3, padding: "1px 7px" }}>White-glove</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ChangelogTab() {
  const { data: cl } = useQuery({ queryKey: ["saas-changelog"], queryFn: saasApi.changelog });
  if (!cl) return <p style={{ color: "#8aa0bb" }}>Loading…</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Header */}
      <div style={{ background: `${GOLD}08`, border: `1px solid ${GOLD}30`, borderRadius: 10, padding: "18px 22px" }}>
        <div style={{ display: "flex", gap: 10, alignItems: "baseline", marginBottom: 8 }}>
          <p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: GOLD }}>v{cl.version}</p>
          <p style={{ fontSize: 13, color: "#8aa0bb" }}>Released {cl.release_date}</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
          {[["New Modules", cl.total_new_modules, "#22C55E"], ["New DB Tables", cl.total_new_db_tables, "#60A5FA"], ["New Endpoints", cl.total_new_endpoints, GOLD]].map(([l, v, c]) => (
            <div key={l} style={{ background: "rgba(0,0,0,0.2)", borderRadius: 6, padding: "10px 14px" }}>
              <p style={{ fontSize: 10, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>{l}</p>
              <p style={{ fontFamily: "'Bebas Neue'", fontSize: 28, color: c as string }}>{v}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Highlights */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>v11 HIGHLIGHTS</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {cl.highlights.map((h: string, i: number) => (
            <div key={i} style={{ display: "flex", gap: 8, fontSize: 13 }}>
              <span style={{ color: GOLD, flexShrink: 0 }}>✦</span>
              <p style={{ color: "#d0dce8" }}>{h}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Sprint breakdown */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 14 }}>SPRINT-BY-SPRINT DELIVERY</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {cl.sprints.map((s: any) => (
            <div key={s.sprint} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "10px 12px", background: "#152f52", borderRadius: 7 }}>
              <div style={{ background: `${GOLD}20`, border: `1px solid ${GOLD}40`, borderRadius: 5, padding: "3px 10px", flexShrink: 0 }}>
                <p style={{ fontFamily: "'Bebas Neue'", fontSize: 14, color: GOLD }}>S{s.sprint}</p>
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: 13, fontWeight: 700, color: "#F0F4FA", marginBottom: 3 }}>{s.theme}</p>
                <p style={{ fontSize: 11, color: "#8aa0bb" }}>{s.modules.join(" · ")}</p>
              </div>
              <div style={{ textAlign: "right", flexShrink: 0 }}>
                <p style={{ fontSize: 11, color: "#60A5FA" }}>{s.tables} tables</p>
                <p style={{ fontSize: 11, color: GOLD }}>{s.endpoints} endpoints</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* All seed commands */}
      <div style={{ background: "#0f2744", border: "1px solid rgba(201,168,76,0.15)", borderRadius: 10, padding: "16px 20px" }}>
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 18, letterSpacing: 1, color: "#F0F4FA", marginBottom: 12 }}>ALL SEED COMMANDS</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 6 }}>
          {cl.seed_commands.map((cmd: string) => (
            <code key={cmd} style={{ background: "#071828", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 5, padding: "5px 10px", fontSize: 12, color: "#22C55E", fontFamily: "monospace" }}>{cmd}</code>
          ))}
        </div>
      </div>
    </div>
  );
}

const TABS = [
  { id: "mrr",       label: "MRR Dashboard",  icon: <BarChart2 size={14} /> },
  { id: "tenants",   label: "Tenants",        icon: <Users size={14} /> },
  { id: "api-keys",  label: "API Keys",       icon: <Key size={14} /> },
  { id: "white-label",label:"White-Label",    icon: <Palette size={14} /> },
  { id: "changelog", label: "v11 Changelog",  icon: <BookOpen size={14} /> },
];

export default function SaaSAdminPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("mrr");
  const [seeding, setSeeding] = useState(false);
  const { data: mrr } = useQuery({ queryKey: ["saas-mrr"], queryFn: saasApi.mrr });

  const handleSeed = async () => {
    setSeeding(true);
    await saasApi.seed();
    ["saas-mrr","saas-tenants","saas-keys","saas-wl"].forEach(k => qc.invalidateQueries({ queryKey: [k] }));
    setSeeding(false);
  };

  return (
    <div style={{ background: "#071828", minHeight: "100vh", fontFamily: "'Barlow Condensed', sans-serif", color: "#F0F4FA" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap'); @keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ background: NAVY, borderBottom: "1px solid rgba(201,168,76,0.2)", padding: "16px 28px 0" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
          {["SPORTAI PLATFORM","SAAS v11","MULTI-TENANT","WHITE-LABEL"].map(l => (
            <div key={l} style={{ background: "rgba(201,168,76,0.12)", borderRadius: 3, padding: "1px 8px" }}><span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 2 }}>{l}</span></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <h1 style={{ fontFamily: "'Bebas Neue'", fontSize: 30, letterSpacing: 2 }}>SAAS ADMIN — v11</h1>
          {mrr && mrr.active_tenants > 0 && (
            <div style={{ display: "flex", gap: 16, marginBottom: 6, flexWrap: "wrap" }}>
              <span style={{ fontSize: 13, color: "#8aa0bb" }}>MRR: <strong style={{ color: GOLD }}>{fmt(mrr.mrr)}</strong></span>
              <span style={{ fontSize: 13, color: "#8aa0bb" }}>ARR: <strong style={{ color: "#22C55E" }}>{fmt(mrr.arr)}</strong></span>
              <span style={{ fontSize: 13, color: "#8aa0bb" }}>Active: <strong style={{ color: "#22C55E" }}>{mrr.active_tenants}</strong></span>
            </div>
          )}
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
        {activeTab === "mrr"         && <MRRTab onSeed={handleSeed} />}
        {activeTab === "tenants"     && <TenantsTab />}
        {activeTab === "api-keys"    && <APIKeysTab />}
        {activeTab === "white-label" && <WhiteLabelTab />}
        {activeTab === "changelog"   && <ChangelogTab />}
      </div>
    </div>
  );
}
