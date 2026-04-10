"use client";
/**
 * SportAI Suite v11 — Login Page
 * /app/login/page.tsx
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../lib/auth";

const GOLD = "#C9A84C";
const NAVY = "#0A2240";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      router.push("/command-center");
    } catch (err: any) {
      setError(err.message ?? "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh", background: NAVY,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "'Barlow Condensed', sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        input:-webkit-autofill { -webkit-box-shadow: 0 0 0 30px #0f2744 inset !important; -webkit-text-fill-color: #F0F4FA !important; }
      `}</style>

      <div style={{
        width: "100%", maxWidth: 420,
        background: "#071828",
        border: `1px solid ${GOLD}30`,
        borderRadius: 14,
        padding: "44px 40px",
        boxShadow: `0 0 60px rgba(201,168,76,0.08)`,
      }}>

        {/* Logo / Brand */}
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <div style={{
            display: "inline-block",
            background: `${GOLD}15`,
            border: `1px solid ${GOLD}40`,
            borderRadius: 8,
            padding: "6px 18px",
            marginBottom: 14,
          }}>
            <span style={{ fontFamily: "'Bebas Neue'", fontSize: 11, color: GOLD, letterSpacing: 3 }}>
              NXS NATIONAL COMPLEX
            </span>
          </div>
          <h1 style={{
            fontFamily: "'Bebas Neue'",
            fontSize: 38,
            color: "#F0F4FA",
            letterSpacing: 2,
            lineHeight: 1,
          }}>
            SPORT<span style={{ color: GOLD }}>AI</span> SUITE
          </h1>
          <p style={{ fontSize: 13, color: "#4a6080", marginTop: 6, letterSpacing: "0.05em" }}>
            v11 · Enterprise Platform
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="admin"
              required
              autoComplete="username"
              style={{
                width: "100%", padding: "12px 14px",
                background: "#0f2744",
                border: `1px solid ${error ? "#EF4444" : "rgba(201,168,76,0.2)"}`,
                borderRadius: 7, color: "#F0F4FA",
                fontSize: 15, fontFamily: "'Barlow Condensed'",
                outline: "none",
                transition: "border-color 0.2s",
              }}
              onFocus={e => e.target.style.borderColor = GOLD}
              onBlur={e => e.target.style.borderColor = error ? "#EF4444" : "rgba(201,168,76,0.2)"}
            />
          </div>

          <div style={{ marginBottom: 24 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: "#4a6080", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              autoComplete="current-password"
              style={{
                width: "100%", padding: "12px 14px",
                background: "#0f2744",
                border: `1px solid ${error ? "#EF4444" : "rgba(201,168,76,0.2)"}`,
                borderRadius: 7, color: "#F0F4FA",
                fontSize: 15, fontFamily: "'Barlow Condensed'",
                outline: "none",
                transition: "border-color 0.2s",
              }}
              onFocus={e => e.target.style.borderColor = GOLD}
              onBlur={e => e.target.style.borderColor = error ? "#EF4444" : "rgba(201,168,76,0.2)"}
            />
          </div>

          {error && (
            <div style={{
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: 6, padding: "10px 14px", marginBottom: 16,
              fontSize: 13, color: "#EF4444",
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !username || !password}
            style={{
              width: "100%",
              background: loading ? "rgba(201,168,76,0.5)" : GOLD,
              color: NAVY,
              border: "none",
              borderRadius: 7,
              padding: "14px",
              fontSize: 16,
              fontFamily: "'Bebas Neue'",
              letterSpacing: 2,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "opacity 0.2s",
              opacity: (!username || !password) ? 0.5 : 1,
            }}
          >
            {loading ? "SIGNING IN…" : "SIGN IN"}
          </button>
        </form>

        {/* Footer */}
        <div style={{ textAlign: "center", marginTop: 28, borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: 20 }}>
          <p style={{ fontSize: 11, color: "#4a6080" }}>
            Nexus Domes Inc. · 704 Kirkus St, Proctor MN
          </p>
          <p style={{ fontSize: 11, color: "#4a6080", marginTop: 3 }}>
            Level Playing Field Foundation · #TimeToLevelUP
          </p>
        </div>
      </div>
    </div>
  );
}
