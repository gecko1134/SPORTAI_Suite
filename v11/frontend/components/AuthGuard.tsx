"use client";
/**
 * AuthGuard — wraps every protected page
 * Checks localStorage for a valid token, redirects to /login if missing
 */

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getStoredUser, type AuthUser } from "../lib/auth";

interface Props {
  children: (user: AuthUser) => React.ReactNode;
}

export default function AuthGuard({ children }: Props) {
  const router   = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const stored = getStoredUser();
    if (!stored) {
      router.replace("/login");
    } else {
      setUser(stored);
    }
    setChecking(false);
  }, [pathname]);

  if (checking) return (
    <div style={{
      minHeight: "100vh", background: "#071828",
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{ textAlign: "center" }}>
        <div style={{
          width: 40, height: 40, border: "3px solid rgba(201,168,76,0.2)",
          borderTop: "3px solid #C9A84C", borderRadius: "50%",
          animation: "spin 0.8s linear infinite", margin: "0 auto 12px",
        }} />
        <p style={{ fontFamily: "'Bebas Neue'", fontSize: 14, color: "#4a6080", letterSpacing: 2 }}>
          LOADING SPORTAI
        </p>
      </div>
    </div>
  );

  if (!user) return null;
  return <>{children(user)}</>;
}
