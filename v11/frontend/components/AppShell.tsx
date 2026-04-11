"use client";
/**
 * SportAI Suite v11 — App Shell
 * Authenticated layout: Sidebar + main content area
 * Used by every protected page via the (app) route group
 */

import AuthGuard from "./AuthGuard";
import Sidebar   from "./Sidebar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      {(user) => (
        <div style={{
          display: "flex",
          minHeight: "100vh",
          background: "#071828",
        }}>
          <Sidebar user={user} />
          <main style={{
            flex: 1,
            minWidth: 0,
            overflowY: "auto",
            overflowX: "hidden",
          }}>
            {children}
          </main>
        </div>
      )}
    </AuthGuard>
  );
}
