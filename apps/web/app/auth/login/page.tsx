"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { PxButton, PxCard, PxInput } from "../../../components/ui";
import { useAuth } from "../../../contexts/AuthContext";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, loading } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    const result = await login({ email, password });
    
    if (result.success) {
      // Redirect based on user role or to dashboard
      router.push("/feed");
    } else {
      setError(result.error || "Login failed");
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/">
            <h1 className="text-3xl font-pixel text-ink mb-4">SERAAJ</h1>
          </Link>
          <h2 className="text-xl font-pixel text-ink mb-2">LOG IN</h2>
          <p className="text-ink">Welcome back to the platform</p>
        </div>

        <PxCard className="p-8">
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <PxInput
              label="EMAIL"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />

            <PxInput
              label="PASSWORD"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />

            <PxButton
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={loading}
            >
              {loading ? "LOGGING IN..." : "LOG IN"}
            </PxButton>
          </form>
          
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">Demo Accounts (Password: Demo123!):</p>
            <div className="text-xs text-gray-500 space-y-1 mt-2">
              <p><strong>Volunteers:</strong></p>
              <p>Layla: layla@example.com</p>
              <p>Omar: omar@example.com</p>
              <p>Fatima: fatima@example.com</p>
              <p><strong>Organizations:</strong></p>
              <p>Hope Education: contact@hopeeducation.org</p>
              <p>Cairo Health: info@cairohealthnetwork.org</p>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-ink">
              Don't have an account?{" "}
              <Link href="/auth/register" className="text-pixel-coral font-pixel text-sm">
                SIGN UP
              </Link>
            </p>
          </div>
        </PxCard>
      </div>
    </div>
  );
}