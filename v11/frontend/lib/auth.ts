/**
 * SportAI Suite v11 — Auth Helper
 * Token storage, login/logout, current user
 */

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface AuthUser {
  username: string;
  role: string;
  full_name?: string;
  access_token: string;
}

export async function login(username: string, password: string): Promise<AuthUser> {
  const form = new URLSearchParams({ username, password });
  const res = await fetch(`${API}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Invalid username or password");
  }

  const data = await res.json();
  const user: AuthUser = {
    username: data.username,
    role: data.role,
    full_name: data.full_name,
    access_token: data.access_token,
  };

  if (typeof window !== "undefined") {
    localStorage.setItem("sportai_user", JSON.stringify(user));
  }
  return user;
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("sportai_user");
    window.location.href = "/login";
  }
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("sportai_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function authHeaders(): Record<string, string> {
  const user = getStoredUser();
  return user ? { Authorization: `Bearer ${user.access_token}` } : {};
}
