"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MapPin, Sparkles, Compass, ChevronRight, Mountain, Waves, UtensilsCrossed } from "lucide-react";

const QUICK_STARTS = [
  { icon: Compass, label: "3-Day Classic", prompt: "我想规划一个3天重庆经典行程，喜欢美食和夜景" },
  { icon: Mountain, label: "Nature & Culture", prompt: "I want a 4-day trip mixing nature and culture in Chongqing" },
  { icon: UtensilsCrossed, label: "Foodie Tour", prompt: "我是吃货！3天重庆美食之旅，从早吃到晚" },
  { icon: Waves, label: "River & Night", prompt: "想看最美的重庆江景和夜景，悠闲2-3天" },
];

export default function HomePage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [isHovered, setIsHovered] = useState(false);

  const handleStart = (prompt?: string) => {
    const q = prompt || input.trim();
    if (!q) return;
    router.push(`/plan?q=${encodeURIComponent(q)}`);
  };

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Hero Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-cq-dark via-gray-900 to-cq-river">
        <div className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `radial-gradient(circle at 20% 80%, #D4A017 0%, transparent 50%),
                              radial-gradient(circle at 80% 20%, #C0392B 0%, transparent 50%)`,
          }}
        />
        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      <div className="relative z-10">
        {/* Nav */}
        <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cq-red to-cq-gold flex items-center justify-center">
              <MapPin className="w-5 h-5 text-white" />
            </div>
            <span className="text-white font-bold text-lg">Chongqing Travel</span>
          </div>
        </nav>

        {/* Hero */}
        <section className="flex flex-col items-center justify-center min-h-[85vh] px-4 text-center">
          {/* Badge */}
          <div className="animate-fade-in mb-6">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur border border-white/10 text-white/80 text-sm">
              <Sparkles className="w-4 h-4 text-cq-gold" />
              AI-Powered · Chongqing MVP
            </span>
          </div>

          {/* Title */}
          <h1 className="animate-slide-up text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight">
            Discover{" "}
            <span className="gradient-text">Chongqing</span>
            <br />
            <span className="text-3xl md:text-5xl font-medium text-white/70">
              The 8D Magical City
            </span>
          </h1>

          <p className="animate-slide-up text-lg md:text-xl text-white/60 max-w-2xl mb-12"
             style={{ animationDelay: "0.1s" }}>
            AI understands your travel style. From Michelin-star hotpot to hidden
            alleyway noodles — get a personalized Chongqing itinerary in seconds.
          </p>

          {/* Input Card */}
          <div
            className="animate-slide-up w-full max-w-2xl"
            style={{ animationDelay: "0.2s" }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            <div className={`glass-card p-2 transition-all duration-500 ${
              isHovered ? "shadow-xl shadow-cq-gold/10 scale-[1.01]" : ""
            }`}>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleStart()}
                  placeholder="Describe your dream Chongqing trip..."
                  className="flex-1 px-4 py-4 bg-transparent text-gray-800 placeholder-gray-400
                             outline-none text-lg"
                />
                <button
                  onClick={() => handleStart()}
                  disabled={!input.trim()}
                  className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Plan My Trip
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Quick Starts */}
          <div
            className="animate-slide-up grid grid-cols-2 md:grid-cols-4 gap-3 mt-8 w-full max-w-2xl"
            style={{ animationDelay: "0.3s" }}
          >
            {QUICK_STARTS.map((qs, i) => (
              <button
                key={i}
                onClick={() => handleStart(qs.prompt)}
                className="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/5
                           border border-white/10 hover:bg-white/10 hover:border-white/20
                           transition-all duration-300 group"
              >
                <qs.icon className="w-5 h-5 text-cq-gold group-hover:scale-110 transition-transform" />
                <span className="text-white/70 text-sm font-medium group-hover:text-white/90">
                  {qs.label}
                </span>
              </button>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
