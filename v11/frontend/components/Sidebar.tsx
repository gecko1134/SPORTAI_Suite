"use client";
/**
 * SportAI Suite v11 — Sidebar Navigation
 * All 17 modules organized by entity with active state, user badge, logout
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logout, type AuthUser } from "../lib/auth";
import {
  LayoutDashboard, Users, Star, DollarSign, Building2,
  GraduationCap, Snowflake, Utensils, Map, Zap,
  Target, Shield, Dumbbell, Trophy, Layers, BookOpen,
  LogOut, ChevronDown, ChevronRight, Settings,
  TrendingUp, Waves, Key,
} from "lucide-react";
import { useState } from "react";

const GOLD  = "#C9A84C";
const NAVY  = "#0A2240";

interface NavItem {
  label: string;
  href:  string;
  icon:  React.ReactNode;
  badge?: string;
}

interface NavGroup {
  entity:    string;
  color:     string;
  icon:      string;
  items:     NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    entity: "Command Center",
    color:  GOLD,
    icon:   "🎯",
    items: [
      { label: "CEO Dashboard",     href: "/command-center",  icon: <LayoutDashboard size={14} />, badge: "CEO" },
      { label: "Revenue Maximizer", href: "/revenue-ai",      icon: <Zap size={14} />,             badge: "AI" },
      { label: "Layout Optimizer",  href: "/layout-ai",       icon: <Map size={14} />,             badge: "AI" },
    ],
  },
  {
    entity: "NXS National Complex",
    color:  "#60A5FA",
    icon:   "🏟️",
    items: [
      { label: "Hotel",       href: "/hotel",   icon: <Building2 size={14} /> },
      { label: "Lodging",     href: "/lodging", icon: <Layers size={14} /> },
      { label: "Ice Rink",    href: "/rink",    icon: <Snowflake size={14} /> },
      { label: "F&B",         href: "/fnb",     icon: <Utensils size={14} /> },
      { label: "Academic",    href: "/academic",icon: <GraduationCap size={14} /> },
    ],
  },
  {
    entity: "Nexus Domes Inc.",
    color:  GOLD,
    icon:   "🏢",
    items: [
      { label: "Membership Predictor", href: "/membership-predictor", icon: <Star size={14} />,       badge: "AI" },
      { label: "Foundation Card",      href: "/foundation-card",      icon: <Shield size={14} /> },
    ],
  },
  {
    entity: "LPF Foundation",
    color:  "#22C55E",
    icon:   "🎯",
    items: [
      { label: "NIL Program",        href: "/nil",       icon: <Trophy size={14} /> },
      { label: "Equipment Exchange", href: "/equipment", icon: <Dumbbell size={14} /> },
      { label: "Grant Tracker",      href: "/grants",    icon: <BookOpen size={14} /> },
    ],
  },
  {
    entity: "NGP Development",
    color:  "#F97316",
    icon:   "🏗️",
    items: [
      { label: "Capital Stack", href: "/capital-stack", icon: <DollarSign size={14} /> },
      { label: "Skill Shot",    href: "/skill-shot",    icon: <Target size={14} /> },
      { label: "PuttView AR",   href: "/puttview",      icon: <Waves size={14} /> },
    ],
  },
  {
    entity: "Platform Admin",
    color:  "#A855F7",
    icon:   "⚙️",
    items: [
      { label: "SaaS Admin", href: "/saas-admin", icon: <Key size={14} />, badge: "ADMIN" },
    ],
  },
];

export default function Sidebar({ user }: { user: AuthUser }) {
  const pathname  = usePathname();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const toggleGroup = (entity: string) => {
    setCollapsed(prev => ({ ...prev, [entity]: !prev[entity] }));
  };

  return (
    <nav style={{
      width: 220, flexShrink: 0,
      background: NAVY,
      borderRight: "1px solid rgba(201,168,76,0.15)",
      display: "flex", flexDirection: "column",
      height: "100vh", position: "sticky", top: 0,
      overflowY: "auto", overflowX: "hidden",
    }}>
      {/* Brand */}
      <div style={{
        padding: "18px 16px 14px",
        borderBottom: "1px solid rgba(201,168,76,0.15)",
        flexShrink: 0,
      }}>
        <div style={{ marginBottom: 4 }}>
          <span style={{ fontFamily: "'Bebas Neue'", fontSize: 22, letterSpacing: 2, color: "#F0F4FA" }}>
            SPORT<span style={{ color: GOLD }}>AI</span>
          </span>
          <span style={{
            marginLeft: 6, fontSize: 9, fontWeight: 700, color: GOLD,
            background: "rgba(201,168,76,0.12)", border: "1px solid rgba(201,168,76,0.3)",
            borderRadius: 3, padding: "1px 5px", letterSpacing: 1, verticalAlign: "middle",
          }}>v11</span>
        </div>
        <p style={{ fontSize: 10, color: "#4a6080", letterSpacing: "0.05em" }}>
          NXS NATIONAL COMPLEX
        </p>
      </div>

      {/* Nav groups */}
      <div style={{ flex: 1, padding: "10px 0", overflowY: "auto" }}>
        {NAV_GROUPS.map(group => {
          const isOpen = !collapsed[group.entity];
          const hasActive = group.items.some(i => pathname === i.href);

          return (
            <div key={group.entity} style={{ marginBottom: 2 }}>
              {/* Group header */}
              <button
                onClick={() => toggleGroup(group.entity)}
                style={{
                  width: "100%", display: "flex", alignItems: "center",
                  gap: 6, padding: "7px 14px",
                  background: hasActive ? `${group.color}10` : "none",
                  border: "none", cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <span style={{ fontSize: 13 }}>{group.icon}</span>
                <span style={{
                  fontSize: 10, fontWeight: 700, color: hasActive ? group.color : "#4a6080",
                  textTransform: "uppercase", letterSpacing: "0.08em", flex: 1,
                }}>
                  {group.entity}
                </span>
                {isOpen
                  ? <ChevronDown size={11} style={{ color: "#4a6080" }} />
                  : <ChevronRight size={11} style={{ color: "#4a6080" }} />
                }
              </button>

              {/* Nav items */}
              {isOpen && (
                <div>
                  {group.items.map(item => {
                    const active = pathname === item.href;
                    return (
                      <Link key={item.href} href={item.href} style={{ textDecoration: "none" }}>
                        <div style={{
                          display: "flex", alignItems: "center", gap: 8,
                          padding: "7px 14px 7px 28px",
                          background: active ? `${group.color}18` : "none",
                          borderRight: active ? `2px solid ${group.color}` : "2px solid transparent",
                          transition: "all 0.15s",
                          cursor: "pointer",
                        }}
                        onMouseEnter={e => { if (!active) (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)"; }}
                        onMouseLeave={e => { if (!active) (e.currentTarget as HTMLElement).style.background = "none"; }}
                        >
                          <span style={{ color: active ? group.color : "#4a6080", flexShrink: 0 }}>
                            {item.icon}
                          </span>
                          <span style={{
                            fontSize: 13, fontWeight: active ? 700 : 400,
                            color: active ? "#F0F4FA" : "#8aa0bb",
                            flex: 1, letterSpacing: "0.02em",
                          }}>
                            {item.label}
                          </span>
                          {item.badge && (
                            <span style={{
                              fontSize: 8, fontWeight: 700,
                              color: active ? group.color : "#4a6080",
                              background: active ? `${group.color}20` : "rgba(255,255,255,0.04)",
                              border: `1px solid ${active ? group.color + "40" : "rgba(255,255,255,0.06)"}`,
                              borderRadius: 3, padding: "1px 4px", letterSpacing: 0.5,
                            }}>
                              {item.badge}
                            </span>
                          )}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* User bar */}
      <div style={{
        padding: "12px 14px",
        borderTop: "1px solid rgba(201,168,76,0.12)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <div style={{
            width: 30, height: 30, borderRadius: "50%",
            background: `${GOLD}20`, border: `1px solid ${GOLD}40`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'Bebas Neue'", fontSize: 13, color: GOLD, flexShrink: 0,
          }}>
            {user.username[0].toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{ fontSize: 12, fontWeight: 700, color: "#F0F4FA", lineHeight: 1.2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user.full_name ?? user.username}
            </p>
            <p style={{ fontSize: 10, color: GOLD, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              {user.role}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          style={{
            width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
            background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
            borderRadius: 6, padding: "7px", color: "#EF4444",
            fontSize: 12, fontWeight: 700, cursor: "pointer",
            letterSpacing: "0.05em", transition: "all 0.15s",
          }}
          onMouseEnter={e => (e.currentTarget.style.background = "rgba(239,68,68,0.15)")}
          onMouseLeave={e => (e.currentTarget.style.background = "rgba(239,68,68,0.08)")}
        >
          <LogOut size={12} />
          SIGN OUT
        </button>
      </div>
    </nav>
  );
}
