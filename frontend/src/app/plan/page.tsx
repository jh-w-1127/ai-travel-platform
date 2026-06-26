"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import {
  Send, MapPin, Sparkles, Loader2, Hotel, UtensilsCrossed,
  Train, Camera, ChevronDown, ChevronUp, DollarSign, Clock, Map,
} from "lucide-react";

// Types
interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  toolCalls?: string[];
}

interface DayItem {
  time: string;
  poi_name_zh: string;
  poi_name_en: string;
  activity: string;
  transport: string;
  duration: string;
  cost_estimate: string;
  tips: string[];
}

interface DayPlan {
  day: number;
  date: string;
  title_zh: string;
  title_en: string;
  items: DayItem[];
}

interface ItineraryData {
  city: string;
  track: string;
  days: number;
  plan: DayPlan[];
  budget: {
    breakdown: Record<string, string>;
    total: string;
    total_usd: string;
    service_fee: string;
  } | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function PlanPage() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [itinerary, setItinerary] = useState<ItineraryData | null>(null);
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([1]));
  const [track, setTrack] = useState<"premium" | "budget" | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  // Auto-start with query param
  useEffect(() => {
    if (initialQuery) {
      handleSend(initialQuery);
    }
  }, [initialQuery]);

  const handleSend = useCallback(async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || isLoading) return;

    const userMsg: Message = { role: "user", content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setStreamingContent("");
    setItinerary(null);

    try {
      const response = await fetch(`${API_BASE}/api/planner/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [
            ...messages.map((m) => ({ role: m.role, content: m.content })),
            { role: "user", content: msg },
          ],
          track: track,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader");

      const decoder = new TextDecoder();
      let buffer = "";
      let content = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          if (line.startsWith("event: ")) {
            continue; // event type handled by data parsing
          }

          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (line.includes("event: message")) {
                content += data.content || "";
                setStreamingContent(content);
              } else if (line.includes("event: function_call")) {
                // Show tool call indicator
              } else if (line.includes("event: function_result")) {
                if (data.name === "generate_itinerary" && data.result?.plan) {
                  setItinerary(data.result);
                }
              } else if (line.includes("event: itinerary")) {
                if (data.plan) setItinerary(data);
              }
            } catch {
              // skip malformed JSON
            }
          }
        }
      }

      // Finalize message
      if (content) {
        setMessages((prev) => [...prev, { role: "assistant", content }]);
      }
      setStreamingContent("");
    } catch (err: any) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Sorry, something went wrong: ${err.message}. Make sure the planner API is running on ${API_BASE}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [input, messages, track, isLoading]);

  const toggleDay = (day: number) => {
    setExpandedDays((prev) => {
      const next = new Set(prev);
      if (next.has(day)) next.delete(day);
      else next.add(day);
      return next;
    });
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cq-red to-cq-gold flex items-center justify-center">
            <MapPin className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-gray-900">AI Travel Planner</h1>
            <p className="text-xs text-gray-500">Chongqing · MVP</p>
          </div>
        </div>
        {/* Track toggle */}
        <div className="flex gap-2">
          {(["premium", "budget"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTrack(track === t ? null : t)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                track === t
                  ? t === "premium"
                    ? "bg-cq-gold text-white shadow-lg shadow-cq-gold/25"
                    : "bg-green-600 text-white shadow-lg shadow-green-500/25"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {t === "premium" ? "✨ Premium" : "💰 Budget"}
            </button>
          ))}
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {/* Welcome */}
          {messages.length === 0 && !streamingContent && (
            <div className="text-center py-12 animate-fade-in">
              <Sparkles className="w-12 h-12 text-cq-gold mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">
                Plan Your Chongqing Adventure
              </h2>
              <p className="text-gray-500">
                Tell me about your travel style — I&apos;ll craft the perfect itinerary.
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-4">
                {[
                  "3天重庆经典行程，喜欢美食和夜景",
                  "4-day luxury trip, best hotels and fine dining",
                  "背包客穷游重庆，预算¥1500",
                ].map((p, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(p)}
                    className="px-4 py-2 rounded-full bg-white border border-gray-200
                               text-sm text-gray-600 hover:border-cq-gold hover:text-cq-gold
                               transition-all"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-cq-dark text-white rounded-br-md"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}

          {/* Streaming */}
          {streamingContent && (
            <div className="flex justify-start">
              <div className="max-w-[80%] bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                <p className="text-sm whitespace-pre-wrap leading-relaxed typing-cursor">
                  {streamingContent}
                </p>
              </div>
            </div>
          )}

          {/* Loading */}
          {isLoading && !streamingContent && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
                <Loader2 className="w-5 h-5 text-cq-gold animate-spin" />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Itinerary Display */}
        {itinerary && itinerary.plan && (
          <div className="max-w-3xl mx-auto mt-8 animate-slide-up">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {itinerary.track === "premium" ? "✨ Premium" : "💰 Budget"} Itinerary
                  </h2>
                  <p className="text-sm text-gray-500">
                    {itinerary.days} Days in {itinerary.city === "chongqing" ? "Chongqing 重庆" : itinerary.city}
                  </p>
                </div>
                {itinerary.budget && (
                  <div className="text-right">
                    <div className="text-2xl font-bold text-cq-red">{itinerary.budget.total}</div>
                    <div className="text-xs text-gray-500">{itinerary.budget.total_usd}</div>
                  </div>
                )}
              </div>

              {/* Day cards */}
              <div className="space-y-3">
                {itinerary.plan.map((day) => (
                  <div
                    key={day.day}
                    className="border border-gray-200 rounded-xl overflow-hidden"
                  >
                    <button
                      onClick={() => toggleDay(day.day)}
                      className="w-full flex items-center justify-between p-4
                                 bg-gray-50 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 rounded-full bg-cq-dark text-white flex items-center justify-center text-sm font-bold">
                          {day.day}
                        </span>
                        <div className="text-left">
                          <h3 className="font-semibold text-gray-900">{day.title_en}</h3>
                          <p className="text-xs text-gray-500">{day.title_zh}</p>
                        </div>
                      </div>
                      {expandedDays.has(day.day) ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </button>

                    {expandedDays.has(day.day) && (
                      <div className="p-4 space-y-3">
                        {day.items.map((item, j) => (
                          <div
                            key={j}
                            className="flex gap-4 p-3 rounded-lg bg-white border border-gray-100
                                       hover:border-cq-gold/30 transition-colors"
                          >
                            {/* Time */}
                            <div className="flex-shrink-0 w-20 text-right">
                              <div className="text-xs font-semibold text-cq-red">{item.time}</div>
                              <div className="text-xs text-gray-400 flex items-center justify-end gap-1 mt-1">
                                <Clock className="w-3 h-3" /> {item.duration}
                              </div>
                            </div>
                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-gray-900 text-sm">
                                {item.poi_name_en}
                              </h4>
                              <p className="text-xs text-gray-500 mt-0.5">{item.poi_name_zh}</p>
                              <p className="text-xs text-gray-600 mt-1">{item.activity}</p>
                              {item.tips.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1">
                                  {item.tips.slice(0, 2).map((tip, k) => (
                                    <span
                                      key={k}
                                      className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-xs"
                                    >
                                      💡 {tip}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                            {/* Meta */}
                            <div className="flex-shrink-0 flex flex-col items-end gap-1">
                              <div className="flex items-center gap-1 text-xs text-gray-500">
                                <Train className="w-3 h-3" />
                                {item.transport}
                              </div>
                              {item.cost_estimate && (
                                <div className="flex items-center gap-1 text-xs font-medium text-green-600">
                                  <DollarSign className="w-3 h-3" />
                                  {item.cost_estimate}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Budget Breakdown */}
              {itinerary.budget?.breakdown && (
                <div className="mt-6 p-4 rounded-xl bg-gray-50 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-cq-gold" />
                    Budget Breakdown
                  </h4>
                  <div className="space-y-1.5">
                    {Object.entries(itinerary.budget.breakdown).map(([key, val]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-600 capitalize">{key.replace(/_/g, " ")}</span>
                        <span className="text-gray-900 font-medium">{val}</span>
                      </div>
                    ))}
                    <div className="border-t border-gray-200 pt-1.5 mt-1.5 flex justify-between text-sm">
                      <span className="text-gray-600">Service Fee</span>
                      <span className="text-gray-900">{itinerary.budget!.service_fee}</span>
                    </div>
                    <div className="border-t-2 border-gray-300 pt-1.5 flex justify-between text-base font-bold">
                      <span className="text-gray-900">Total</span>
                      <span className="text-cq-red">{itinerary.budget!.total}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div className="border-t border-gray-200 bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Tell me about your dream trip..."
            className="flex-1 px-4 py-3 rounded-xl border border-gray-200
                       focus:border-cq-gold focus:ring-2 focus:ring-cq-gold/20
                       outline-none text-sm transition-all"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="p-3 rounded-xl bg-gradient-to-r from-cq-red to-orange-600 text-white
                       disabled:opacity-50 disabled:cursor-not-allowed
                       hover:shadow-lg hover:shadow-orange-500/25 transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
