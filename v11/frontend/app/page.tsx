"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser } from "../lib/auth";

export default function RootPage() {
  const router = useRouter();
  useEffect(() => {
    const user = getStoredUser();
    router.replace(user ? "/command-center" : "/login");
  }, []);

  return (
    <div style={{
      minHeight: "100vh", background: "#071828",
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{
        width: 36, height: 36, border: "3px solid rgba(201,168,76,0.2)",
        borderTop: "3px solid #C9A84C", borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
      }} />
    </div>
  );
}
