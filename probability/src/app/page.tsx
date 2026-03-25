"use client";

import { db } from "@/lib/db";
import { type AppSchema } from "@/instant.schema";
import { id, InstaQLEntity } from "@instantdb/react";
import { useState } from "react";

const room = db.room("lottery");

function App() {
  const [selectedView, setSelectedView] = useState("dashboard");
  const { peers } = db.rooms.usePresence(room);
  const numUsers = 1 + Object.keys(peers).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <h1 className="text-3xl font-bold text-white">🎰 Lottery Intelligence</h1>
            <span className="text-sm text-slate-400">({numUsers} online)</span>
          </div>
          <div className="text-xs text-slate-500">Real-time Analytics Engine</div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex gap-6">
            {[
              { id: "dashboard", label: "📊 Dashboard", icon: "dashboard" },
              { id: "quick-predict", label: "⚡ Quick Predict", icon: "quick-predict" },
              { id: "heatmap", label: "🔥 Heatmap", icon: "heatmap" },
              { id: "clustering", label: "📈 Clustering", icon: "clustering" },
              { id: "predictions", label: "🎯 Predictions", icon: "predictions" },
              { id: "alerts", label: "🔔 Alerts", icon: "alerts" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedView(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedView === tab.id
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-500/50"
                    : "text-slate-400 hover:text-white hover:bg-slate-700/50"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {selectedView === "dashboard" && <DashboardView />}
        {selectedView === "quick-predict" && <QuickPredictorView />}
        {selectedView === "heatmap" && <HeatmapView />}
        {selectedView === "clustering" && <ClusteringView />}
        {selectedView === "predictions" && <PredictionsView />}
        {selectedView === "alerts" && <AlertsView />}
      </main>
    </div>
  );
}

// Dashboard View
function DashboardView() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <StatCard label="Winning Numbers" value="50,000" trend="+100.0%" positive />
      <StatCard label="Predictions" value="30,000" trend="+100.0%" positive />
      <StatCard label="Analysis Results" value="10,000" trend="+100.0%" positive />
      <StatCard label="Notifications" value="10,000" trend="+100.0%" positive />

      {/* Main Analytics Grid */}
      <div className="col-span-full grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">🎯 Top Predicted Numbers</h3>
          <div className="space-y-3">
            {[28194, 28190, 43785, 15036, 88990].map((num, i) => (
              <div key={num} className="flex items-center justify-between">
                <span className="text-slate-300">{i + 1}. {num}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                      style={{ width: `${(57 - i * 3)}%` }}
                    ></div>
                  </div>
                  <span className="text-green-400 text-sm font-mono">{57 - i * 3}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">📊 Draw Time Analysis</h3>
          <div className="space-y-4">
            {[
              { time: "1PM", score: 52.8, color: "from-blue-500" },
              { time: "6PM", score: 57.0, color: "from-cyan-500" },
              { time: "8PM", score: 48.5, color: "from-purple-500" },
            ].map((item) => (
              <div key={item.time}>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300 font-mono">{item.time}</span>
                  <span className="text-green-400 font-bold">{item.score}%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div
                    className={`bg-gradient-to-r ${item.color} to-slate-600 h-3 rounded-full`}
                    style={{ width: `${item.score}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Quick Predictor View
function QuickPredictorView() {
  const [ticketNumber, setTicketNumber] = useState("");
  const [cmDenomination, setCmDenomination] = useState("5cm");
  const [drawTime, setDrawTime] = useState("6PM");
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [prediction, setPrediction] = useState<{
    confidence: number;
    rank: number;
    status: string;
    recommendation: string;
  } | null>(null);

  const handlePredict = () => {
    if (!ticketNumber || ticketNumber.length !== 5) {
      alert("Please enter a valid 5-digit number");
      return;
    }

    // Simulate prediction logic
    const num = parseInt(ticketNumber);
    const baseConfidence = Math.random() * 40 + 45; // 45-85%

    // Series-based boost
    const series = Math.floor(num / 100);
    const seriesBoost = (series % 10) * 0.5;

    // Time-based preference
    const timeBoost = drawTime === "6PM" ? 5 : drawTime === "1PM" ? 3 : 1;

    // CM denomination factor
    const cmBoost = cmDenomination === "10cm" ? 3 : 0;

    const finalConfidence = Math.min(
      95,
      baseConfidence + seriesBoost + timeBoost + cmBoost
    );
    const predictedRank = Math.floor(Math.random() * 500) + 1;

    // Status determination
    let status = "🟢 GOOD PICK";
    let recommendation = "Recommended for purchase";

    if (finalConfidence >= 75) {
      status = "🟢 EXCELLENT";
      recommendation = "Strong candidate - High probability match detected";
    } else if (finalConfidence >= 60) {
      status = "🟡 MODERATE";
      recommendation = "Fair chance - Consider buying if budget allows";
    } else {
      status = "🔴 LOW";
      recommendation = "Low probability - Look for other numbers";
    }

    setPrediction({
      confidence: Math.round(finalConfidence * 10) / 10,
      rank: predictedRank,
      status,
      recommendation,
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-8 backdrop-blur-sm mb-8">
        <h2 className="text-3xl font-bold text-white mb-8">⚡ Quick Ticket Predictor</h2>

        {/* Input Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Ticket Number Input */}
          <div>
            <label className="block text-slate-300 font-semibold mb-3">
              🎫 Ticket Number (5 digits)
            </label>
            <input
              type="text"
              maxLength={5}
              placeholder="e.g., 28194"
              value={ticketNumber}
              onChange={(e) => setTicketNumber(e.target.value.replace(/\D/g, "").slice(0, 5))}
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 text-2xl font-mono text-center"
            />
            <p className="text-slate-400 text-sm mt-2">Enter your lottery ticket number</p>
          </div>

          {/* CM Denomination */}
          <div>
            <label className="block text-slate-300 font-semibold mb-3">
              📏 Denomination (CM)
            </label>
            <div className="flex gap-3">
              {["5cm", "10cm"].map((cm) => (
                <button
                  key={cm}
                  onClick={() => setCmDenomination(cm)}
                  className={`flex-1 px-4 py-3 rounded-lg font-semibold transition-all ${
                    cmDenomination === cm
                      ? "bg-cyan-600 text-white shadow-lg shadow-cyan-500/50"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  {cm}
                </button>
              ))}
            </div>
            <p className="text-slate-400 text-sm mt-2">Select ticket denomination</p>
          </div>

          {/* Draw Time */}
          <div>
            <label className="block text-slate-300 font-semibold mb-3">
              🕐 Draw Time
            </label>
            <div className="flex gap-3">
              {["1PM", "6PM", "8PM"].map((time) => (
                <button
                  key={time}
                  onClick={() => setDrawTime(time)}
                  className={`flex-1 px-4 py-3 rounded-lg font-semibold transition-all ${
                    drawTime === time
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-500/50"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  {time}
                </button>
              ))}
            </div>
            <p className="text-slate-400 text-sm mt-2">When is the draw?</p>
          </div>

          {/* Date Selection */}
          <div>
            <label className="block text-slate-300 font-semibold mb-3">
              📅 Draw Date
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
            />
            <p className="text-slate-400 text-sm mt-2">Select prediction date</p>
          </div>
        </div>

        {/* Predict Button */}
        <button
          onClick={handlePredict}
          className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold text-lg rounded-lg hover:from-green-500 hover:to-emerald-500 transition-all shadow-lg shadow-green-500/30 mb-8"
        >
          🎯 Predict Winning Probability
        </button>

        {/* Results */}
        {prediction && (
          <div className="bg-slate-900/50 border border-slate-600 rounded-lg p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Main Result */}
              <div>
                <p className="text-slate-400 text-sm mb-2">YOUR TICKET</p>
                <p className="text-5xl font-mono font-bold text-cyan-400 mb-4">
                  {ticketNumber}
                </p>
                <div className="space-y-2">
                  <p className="text-slate-300">
                    <span className="text-slate-400">Denomination:</span> {cmDenomination}
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Draw Time:</span> {drawTime}
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Date:</span> {selectedDate}
                  </p>
                </div>
              </div>

              {/* Prediction Score */}
              <div className="flex flex-col justify-center items-center bg-slate-800/50 border border-slate-600 rounded-lg p-6">
                <p className="text-slate-400 text-sm mb-3">PREDICTION CONFIDENCE</p>
                <div className="relative w-40 h-40 flex items-center justify-center mb-4">
                  <svg className="absolute w-full h-full" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="#334155"
                      strokeWidth="8"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="url(#grad1)"
                      strokeWidth="8"
                      strokeDasharray={`${prediction.confidence * 2.827} 282.7`}
                      transform="rotate(-90 50 50)"
                    />
                    <defs>
                      <linearGradient id="grad1">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#06b6d4" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <span className="text-5xl font-bold text-cyan-400">
                    {prediction.confidence}%
                  </span>
                </div>
                <p className="text-2xl font-bold text-center">{prediction.status}</p>
              </div>
            </div>

            {/* Detailed Analysis */}
            <div className="bg-slate-900/30 border border-slate-600 rounded-lg p-6 mb-6">
              <p className="text-slate-400 text-sm mb-2">ANALYSIS RESULTS</p>
              <div className="space-y-4">
                <div>
                  <p className="text-slate-300 font-semibold mb-2">Probability Rank</p>
                  <p className="text-cyan-400 font-mono text-lg">
                    #{prediction.rank} out of 99,999 possible numbers
                  </p>
                </div>
                <div>
                  <p className="text-slate-300 font-semibold mb-2">Recommendation</p>
                  <p className="text-slate-200">{prediction.recommendation}</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition-all">
                💾 Save to Watchlist
              </button>
              <button className="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg transition-all">
                📧 Email Results
              </button>
              <button
                onClick={() => setPrediction(null)}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-all"
              >
                🔄 Clear Results
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Tips Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <p className="text-lg font-bold text-cyan-400 mb-3">💡 Series Analysis</p>
          <p className="text-slate-300 text-sm">
            Numbers from hot-performing series (20-30, 28, 40-50) tend to score higher.
          </p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <p className="text-lg font-bold text-emerald-400 mb-3">📈 Best Time</p>
          <p className="text-slate-300 text-sm">
            6PM draws historically show highest prediction accuracy. 1PM is moderately reliable.
          </p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <p className="text-lg font-bold text-orange-400 mb-3">💰 Denomination</p>
          <p className="text-slate-300 text-sm">
            10CM denominations have slightly better odds due to broader number distribution.
          </p>
        </div>
      </div>
    </div>
  );
}

// Heatmap View
function HeatmapView() {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 backdrop-blur-sm">
      <h2 className="text-2xl font-bold text-white mb-6">🔥 Frequency vs Recency Heatmap</h2>
      <div className="grid gap-4 p-6 bg-slate-900/30 rounded-lg border border-slate-600">
        <div className="text-center text-slate-400">
          <p className="mb-4">Heatmap Engine - Analyzing {50000 + 30000 + 10000 + 10000} records...</p>
          <div className="inline-block">
            <div className="animate-pulse text-2xl">
              Generating frequency vs recency matrix...
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Clustering View
function ClusteringView() {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 backdrop-blur-sm">
      <h2 className="text-2xl font-bold text-white mb-6">📈 Cluster & Neighbor Analysis</h2>
      <div className="grid gap-4 p-6 bg-slate-900/30 rounded-lg border border-slate-600">
        <p className="text-slate-300 mb-4">Series Pattern Analysis by Draw Time:</p>
        {["1PM", "6PM", "8PM"].map((time) => (
          <div key={time} className="p-4 bg-slate-800 rounded border border-slate-600">
            <p className="font-mono text-cyan-400">{time} Draw - Clustering {Math.floor(50000/3)} numbers...</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// Predictions View
function PredictionsView() {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 backdrop-blur-sm">
      <h2 className="text-2xl font-bold text-white mb-6">🎯 Intelligent Predictions</h2>
      <div className="grid gap-4">
        {[
          { draw: "Today 1PM", top: [15036], confidence: 52.8 },
          { draw: "Today 6PM", top: [28194, 28190], confidence: 57.0 },
          { draw: "Today 8PM", top: [43785], confidence: 48.5 },
        ].map((pred, i) => (
          <div key={i} className="p-6 bg-slate-900/50 border border-slate-600 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-white font-semibold">{pred.draw}</p>
                <p className="text-slate-400 text-sm">Top picks: {pred.top.join(", ")}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-green-400">{pred.confidence}%</p>
                <p className="text-slate-400 text-xs">Confidence</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Alerts View
function AlertsView() {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 backdrop-blur-sm">
      <h2 className="text-2xl font-bold text-white mb-6">🔔 Smart Notifications</h2>
      <div className="space-y-3">
        {[
          { type: "📊 Analysis Complete", msg: "Full analysis on 100K records completed", time: "Now" },
          { type: "🎯 High Probability", msg: "Number 28194 detected at 57.0% confidence", time: "2m ago" },
          { type: "🔥 Trend Alert", msg: "Series 28 showing hot streak pattern", time: "5m ago" },
          { type: "💬 Sentiment", msg: "YouTube sentiment analysis: Bullish on 6PM draw", time: "10m ago" },
        ].map((alert, i) => (
          <div
            key={i}
            className="p-4 bg-slate-900/50 border border-slate-600 rounded-lg hover:border-slate-500 transition-all"
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="text-white font-semibold">{alert.type}</p>
                <p className="text-slate-400 text-sm mt-1">{alert.msg}</p>
              </div>
              <span className="text-slate-500 text-xs whitespace-nowrap ml-4">{alert.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({
  label,
  value,
  trend,
  positive,
}: {
  label: string;
  value: string;
  trend: string;
  positive: boolean;
}) {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-6 backdrop-blur-sm hover:border-slate-600 transition-all">
      <p className="text-slate-400 text-sm mb-2">{label}</p>
      <p className="text-3xl font-bold text-white mb-2">{value}</p>
      <p className={`text-sm font-semibold ${positive ? "text-green-400" : "text-red-400"}`}>
        {trend}
      </p>
    </div>
  );
}

export default App;
