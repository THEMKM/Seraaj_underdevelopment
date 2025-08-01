"use client";

import { useState } from "react";
import { PxButton, PxCard, PxInput, PxChip } from "../../../components/ui";
import { useAuth } from "../../../contexts/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"volunteer" | "org_admin">("volunteer");
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const result = await register({
        email,
        password,
        role
      });
      
      if (result.success) {
        // Redirect to onboarding
        router.push('/onboarding');
      } else {
        alert(result.error || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/">
            <h1 className="text-3xl font-pixel text-ink mb-4">SERAAJ</h1>
          </Link>
          <h2 className="text-xl font-pixel text-ink mb-2">SIGN UP</h2>
          <p className="text-ink">Join our volunteer community</p>
        </div>

        <PxCard className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-pixel text-ink mb-3">
                I AM A
              </label>
              <div className="flex gap-2">
                <PxChip
                  variant={role === "volunteer" ? "selected" : "default"}
                  onClick={() => setRole("volunteer")}
                >
                  VOLUNTEER
                </PxChip>
                <PxChip
                  variant={role === "org_admin" ? "selected" : "default"}
                  onClick={() => setRole("org_admin")}
                >
                  NGO ADMIN
                </PxChip>
              </div>
            </div>

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
              disabled={isLoading}
            >
              {isLoading ? "CREATING ACCOUNT..." : "CREATE ACCOUNT"}
            </PxButton>
          </form>

          <div className="mt-6 text-center">
            <p className="text-ink">
              Already have an account?{" "}
              <Link href="/auth/login" className="text-pixel-coral font-pixel text-sm">
                LOG IN
              </Link>
            </p>
          </div>
        </PxCard>
      </div>
    </div>
  );
}