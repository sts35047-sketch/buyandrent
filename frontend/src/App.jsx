import React, { useState, useMemo, useRef } from 'react';

const icons = {
  Dashboard: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>,
  Insights: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>,
  Spending: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>,
  Payments: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
};

const mockTransactions = [
  { name: "Figma Annual", category: "Software", date: "Today, 9:42 AM", amount: -144, dot: "#111" },
  { name: "Chase • Checking", category: "Transfer in", date: "Yesterday", amount: 2400, dot: "#5B5CFF" },
  { name: "Whole Foods", category: "Groceries", date: "Dec 11", amount: -86.32, dot: "#D4C5B2" },
  { name: "United • SFO → JFK", category: "Travel", date: "Dec 10", amount: -412, dot: "#B8B8B8" },
  { name: "Stripe Payout", category: "Income", date: "Dec 09", amount: 1240, dot: "#5B5CFF" }
];

function generateMockBalanceData() {
  let e = [], n = 4280;
  for (let t = 0; t < 90; t++) {
    let r = Math.sin(t / 12) * 180,
      l = t > 25 && t < 45 ? -(Math.sin((t - 25) / 20 * Math.PI) * 900) : 0,
      u = -t * 6;
    n = 4280 + r + l + u + (Math.random() - 0.5) * 40;
    e.push({ day: t, balance: Math.round(n) });
  }
  return e;
}

export default function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [paymentPlan, setPaymentPlan] = useState("split");
  const [hoverIndex, setHoverIndex] = useState(null);
  
  const balanceData = useMemo(() => generateMockBalanceData(), []);
  
  const minBal = Math.min(...balanceData.map(d => d.balance));
  const maxBal = Math.max(...balanceData.map(d => d.balance)) - minBal || 1;
  const getX = (i) => 20 + (i / (balanceData.length - 1)) * 860;
  const getY = (bal) => 232 - ((bal - minBal) / maxBal) * 208;
  
  const pathD = useMemo(() => {
    let d = `M ${getX(0)} ${getY(balanceData[0].balance)}`;
    for (let i = 1; i < balanceData.length; i++) {
      let px = getX(i - 1), py = getY(balanceData[i - 1].balance);
      let cx = getX(i), cy = getY(balanceData[i].balance);
      let mx = (px + cx) / 2;
      d += ` Q ${mx} ${py} ${cx} ${cy}`;
    }
    return d;
  }, [balanceData]);
  
  const fillD = `${pathD} L ${getX(balanceData.length - 1)} 232 L ${getX(0)} 232 Z`;

  return (
    <div className="min-h-screen w-full flex max-w-[100vw] overflow-hidden font-sans">
      <aside className="hidden lg:flex w-[268px] shrink-0 bg-[#0A0A0B] text-[#F6F5F2] flex-col relative z-20 overflow-hidden">
        <div className="absolute inset-0 paper pointer-events-none" />
        <div className="absolute -top-20 -right-20 w-[300px] h-[300px] rounded-full bg-[#5B5CFF]/[0.18] blur-[60px] pointer-events-none" />
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/[0.08] to-transparent" />
        <div className="relative p-[22px] flex flex-col h-full">
          <div className="flex items-start gap-3">
            <div className="w-[32px] h-[32px] rounded-[9px] bg-[#F6F5F2] text-[#0A0A0B] grid place-items-center shadow-[0_1px_0_rgba(255,255,255,0.6)_inset,0_8px_20px_rgba(0,0,0,0.4)]">
              <span className="font-fraunces font-bold text-[17px] tracking-[-0.03em] leading-none translate-y-[1px]">B</span>
            </div>
            <div className="leading-[1.05]">
              <div className="font-fraunces text-[15.5px] font-[600] tracking-[-0.02em]">Buy or Wait?</div>
              <div className="text-[11px] text-white/45 font-[500] tracking-[0.02em] mt-[2px]">Personal • Astra</div>
            </div>
          </div>
          
          <button className="mt-7 w-full group flex items-center gap-2.5 rounded-[12px] bg-white/[0.06] border border-white/[0.07] px-3 h-[40px] hover:bg-white/[0.09] spring">
            <div className="w-6 h-6 rounded-full bg-[#F6F5F2] text-[#0A0A0B] grid place-items-center text-[11px] font-bold">A</div>
            <div className="text-left">
              <div className="text-[13px] font-[600] tracking-[-0.01em] leading-none">Alex M.</div>
              <div className="text-[11px] text-white/45 leading-none mt-[3px]">alex@linear... • Pro</div>
            </div>
          </button>
          
          <nav className="mt-8 space-y-0.5">
            <div className="font-mono text-[10px] tracking-[0.14em] text-white/30 px-2 mb-3">MAIN</div>
            {["Dashboard", "Insights", "Spending", "Payments"].map(item => {
               let active = activeTab === item;
               return (
                 <button key={item} onClick={() => setActiveTab(item)} className={`relative w-full flex items-center gap-3 px-2.5 h-[36px] rounded-[10px] text-[13.5px] font-[500] tracking-[-0.01em] text-left spring ${active ? "bg-white/[0.10] text-white" : "text-white/55 hover:text-white/90 hover:bg-white/[0.05]"}`}>
                   <div style={{ opacity: active ? 1 : 0.7 }}>{icons[item]}</div>
                   <span>{item}</span>
                   {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[#5B5CFF] shadow-[0_0_10px_#5B5CFF]" />}
                 </button>
               )
            })}
          </nav>
          
          <div className="mt-auto pt-6">
            <div className="rounded-[16px] bg-white/[0.06] border border-white/[0.08] p-4 relative overflow-hidden spring hover:bg-white/[0.08] hover:-translate-y-[1px]">
              <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-[#5B5CFF]/0 via-[#5B5CFF]/40 to-transparent" />
              <div className="relative">
                <div className="font-mono text-[10px] tracking-[0.12em] text-white/40">CURRENT PLAN</div>
                <div className="mt-2 font-fraunces text-[16px] leading-[1.1] font-[600] tracking-[-0.02em]">
                  You're good to wait<br/>13 days.
                </div>
                <div className="mt-2 text-[11.5px] leading-[1.5] text-white/55 font-[450]">
                  That MacBook won't dip below $3.2k buffer if you wait til May 3. Earns $23.
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-[11px] font-[600] px-2 py-1 rounded-full bg-[#5B5CFF] text-white">Astra • 94%</span>
                  <span className="text-[11px] text-white/40">May 3 • 9:00 AM</span>
                </div>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 px-1 text-[11px] text-white/30">
              <span className="w-1.5 h-1.5 rounded-full bg-[#5B5CFF] animate-pulse" /> Encrypted • Linear-grade sync
            </div>
          </div>
        </div>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col max-h-screen overflow-auto bg-[#F6F5F2]">
        <div className="sticky top-0 z-10 bg-[#F6F5F2]/85 backdrop-blur-[18px] border-b border-[#0A0A0B]/[0.06]">
          <div className="h-[64px] px-5 md:px-8 lg:px-10 flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 text-[13px]">
              <span className="font-[600] tracking-[-0.01em]">Alex's Vault</span>
              <span className="text-[#0A0A0B]/20">/</span>
              <span className="text-[#0A0A0B]/50">MacBook Pro decision</span>
            </div>
            <div className="flex-1 flex justify-center">
              <button className="group w-full max-w-[440px] h-[36px] rounded-full bg-white border border-[#0A0A0B]/[0.08] shadow-sm flex items-center gap-2.5 px-4 text-left spring">
                <span className="text-[13px] text-[#0A0A0B]/45 font-[500] flex-1 text-center font-fraunces">Ask Astra...</span>
                <span className="text-[11px] font-[500] px-1.5 py-0.5 rounded-[6px] bg-[#F6F5F2] border border-[#0A0A0B]/[0.08] text-[#0A0A0B]/50">⌘K</span>
              </button>
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden md:flex items-center gap-2 px-3 h-[30px] rounded-full bg-[#0A0A0B] text-white text-[11.5px] font-[600]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#5B5CFF] shadow-[0_0_8px_#5B5CFF]" /> Live • 12ms
              </div>
            </div>
          </div>
        </div>

        <main className="px-5 md:px-8 lg:px-10 py-7 md:py-8 pb-32">
          <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8">
            <div className="min-w-0">
              <div className="flex items-center gap-3">
                <span className="font-mono text-[10.5px] tracking-[0.14em] text-[#0A0A0B]/40">DECISION • MAY 2026</span>
                <span className="h-px w-12 bg-[#0A0A0B]/15 hidden md:block" />
                <span className="text-[12px] font-[500] text-[#0A0A0B]/60">Chase • Amex synced 2 min ago</span>
              </div>
              <h1 className="mt-4 font-fraunces text-[36px] md:text-[48px] leading-[0.95] tracking-[-0.04em] font-[600]">
                Good morning, <span className="italic font-normal">Alex.</span>
              </h1>
              <div className="mt-4 flex flex-wrap items-center gap-3 text-[14px]">
                <span className="inline-flex items-center gap-2 px-3 h-[30px] rounded-full bg-white border border-[#0A0A0B]/10 shadow-sm">
                  <span className="font-[600]">MacBook Pro 14"</span>
                  <span className="text-[#0A0A0B]/40">• $899</span>
                </span>
                <span className="text-[#0A0A0B]/55">We ran the numbers — you can wait a bit.</span>
              </div>
            </div>

            <div className="relative shrink-0 xl:w-[300px]">
              <div className="flex items-baseline gap-3">
                <div className="font-fraunces text-[88px] leading-[0.85] tracking-[-0.06em] font-[700]">84</div>
                <div className="pb-2">
                  <div className="text-[12px] font-[700] tracking-[0.08em] uppercase text-[#0A0A0B]/40">Affordability</div>
                  <div className="mt-1 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#5B5CFF]" />
                    <span className="text-[13px] font-[600] tracking-[-0.01em]">Strong</span>
                    <span className="text-[12px] text-[#0A0A0B]/50">— you're in good shape</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 h-px w-full bg-gradient-to-r from-[#0A0A0B]/15 to-transparent" />
              <div className="mt-3 grid grid-cols-2 gap-4 text-[12px]">
                <div><span className="text-[#0A0A0B]/45">Cash flow</span><span className="ml-2 font-[600]">78 • good</span></div>
                <div><span className="text-[#0A0A0B]/45">Buffer</span><span className="ml-2 font-[600]">42 • low</span></div>
              </div>
            </div>
          </div>

          <div className="mt-10 grid grid-cols-12 gap-6 lg:gap-8 items-start">
            <div className="col-span-12 lg:col-span-8">
              <div className="rounded-[28px] bg-white border border-[#0A0A0B]/[0.07] shadow-xl overflow-hidden relative">
                <div className="relative p-7 md:p-8 pb-4 flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h2 className="font-mono text-[11px] tracking-[0.12em] text-[#0A0A0B]/40">90-DAY BALANCE • ASTRA FORECAST</h2>
                      <span className="text-[10px] font-bold tracking-widest px-2 py-0.5 rounded-full bg-[#0A0A0B] text-white">INK</span>
                    </div>
                    <div className="mt-4 flex items-baseline gap-4">
                      <span className="font-fraunces text-[32px] font-semibold tracking-tight">$3,842</span>
                      <span className="text-[12.5px] font-medium text-[#0A0A0B]/50">after rent + this purchase on {paymentPlan === "split" ? "split" : "pay now"}</span>
                    </div>
                  </div>
                  <div className="hidden md:flex items-center gap-1.5 rounded-full bg-[#F6F5F2] border border-[#0A0A0B]/[0.06] p-1">
                    {["90D", "60D", "30D"].map(n => (
                      <button key={n} className={`h-[26px] px-3 rounded-full text-[11.5px] font-semibold ${n === "90D" ? "bg-[#0A0A0B] text-white" : "text-[#0A0A0B]/50"}`}>{n}</button>
                    ))}
                  </div>
                </div>

                <div className="relative px-3 md:px-6 pb-2 h-[250px] md:h-[280px]">
                  <svg viewBox="0 0 900 260" className="w-full h-full select-none">
                    <defs>
                      <linearGradient id="wash" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#5B5CFF" stopOpacity="0.18" />
                        <stop offset="55%" stopColor="#0A0A0B" stopOpacity="0.06" />
                        <stop offset="100%" stopColor="#0A0A0B" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                    {[0,1,2].map(n => (
                      <line key={n} x1="20" x2="880" y1={24 + n * 69.3} y2={24 + n * 69.3} stroke="#0A0A0B" strokeOpacity="0.06" strokeDasharray="2 8" />
                    ))}
                    <path d={fillD} fill="url(#wash)" />
                    <path d={pathD} fill="none" stroke="#0A0A0B" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" opacity="0.92" />
                    
                    <rect x={getX(26)} y="24" width={getX(44) - getX(26)} height="208" rx="14" fill="#FF4D3E" fillOpacity="0.05" stroke="#FF4D3E" strokeOpacity="0.12" strokeDasharray="4 6" />
                    <text x={getX(35)} y="40" className="font-mono" fontSize="10" fill="#FF4D3E" opacity="0.7" textAnchor="middle">RENT WEEK RISK</text>
                    
                    <g transform={`translate(${getX(16)}, ${getY(balanceData[16].balance - 40)})`}>
                      <rect x="-48" y="-22" width="96" height="20" rx="10" fill="#0A0A0B" />
                      <text x="0" y="-9" textAnchor="middle" fontSize="10.5" fontWeight="600" fill="white" className="font-mono">SALARY HITS HERE</text>
                    </g>
                    <path d={`M ${getX(16)} ${getY(balanceData[16].balance - 25)} Q ${getX(16) + 8} ${getY(balanceData[16].balance - 12)} ${getX(16) + 2} ${getY(balanceData[16].balance)}`} stroke="#0A0A0B" strokeWidth="1.2" fill="none" strokeLinecap="round" />
                    <circle cx={getX(16)} cy={getY(balanceData[16].balance)} r="4" fill="#5B5CFF" stroke="white" strokeWidth="2" />
                  </svg>
                </div>
                <div className="mx-7 mt-2 mb-6 rounded-[14px] bg-[#F6F5F2] border border-[#0A0A0B]/[0.06] px-4 h-[44px] flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-[#0A0A0B] text-white flex items-center justify-center text-[12px]">↗</span>
                  <span className="text-[12.5px] font-medium text-[#0A0A0B]/70">Lowest point <span className="font-bold text-[#0A0A0B]">${minBal.toLocaleString()}</span> on rent week. Split plan avoids it completely.</span>
                </div>
              </div>
            </div>

            <div className="col-span-12 lg:col-span-4 space-y-5">
              <div className="relative rounded-[24px] bg-[#0A0A0B] text-[#F6F5F2] p-6 md:p-7 border border-white/[0.08] shadow-2xl">
                <div className="absolute top-0 right-0 w-[180px] h-[180px] rounded-full bg-[#5B5CFF]/20 blur-[30px]" />
                <h3 className="font-mono text-[10px] tracking-widest text-white/40">ASTRA SAYS</h3>
                <h2 className="mt-4 font-fraunces text-[42px] leading-none tracking-tight">You're good to<br/>wait 13 days.</h2>
                <p className="mt-3 text-[14px] text-white/70">Until May 3 • earns $23 in interest</p>
                <button className="mt-6 w-full h-[48px] rounded-[16px] bg-white text-[#0A0A0B] font-bold text-[14px] hover:bg-[#F6F5F2] transition-colors">Remind me May 3</button>
              </div>

              <div className="rounded-[24px] bg-white border border-[#0A0A0B]/[0.06] shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <h3 className="font-fraunces font-bold text-[17px]">How to pay</h3>
                  <span className="font-mono text-[10px] text-[#0A0A0B]/40 tracking-widest">APPLE STORE • 6% APR</span>
                </div>
                
                <div className="mt-5 space-y-3">
                  <button onClick={() => setPaymentPlan("now")} className={`w-full text-left p-4 rounded-[16px] border ${paymentPlan === "now" ? "border-[#5B5CFF] shadow-[0_0_0_1px_#5B5CFF]" : "border-[#0A0A0B]/[0.08]"} transition-colors relative`}>
                    <div className="font-mono text-[11px] text-[#0A0A0B]/50 tracking-wider">PAY NOW</div>
                    <div className="mt-2 flex items-baseline gap-2">
                      <span className="text-[22px] font-bold font-fraunces">$899</span>
                      <span className="text-[13px] text-[#0A0A0B]/50">one-time today</span>
                    </div>
                    <div className="mt-1 text-[12px] text-[#0A0A0B]/50">Balance dips to $3,183</div>
                    {paymentPlan === "now" && <div className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-[#0A0A0B] text-white flex items-center justify-center">✓</div>}
                  </button>

                  <button onClick={() => setPaymentPlan("split")} className={`w-full text-left p-4 rounded-[16px] border ${paymentPlan === "split" ? "border-[#5B5CFF] shadow-[0_0_0_1px_#5B5CFF]" : "border-[#0A0A0B]/[0.08]"} transition-colors relative`}>
                    <div className="absolute -top-3 right-4 bg-[#5B5CFF] text-white text-[10px] font-bold px-2 py-1 rounded-full">RECOMMENDED</div>
                    <div className="flex items-center gap-2">
                      <div className="font-mono text-[11px] text-[#0A0A0B]/50 tracking-wider">SPLIT INTO 3</div>
                      <span className="text-[10px] bg-[#5B5CFF]/10 text-[#5B5CFF] px-1.5 py-0.5 rounded font-bold">0% APR</span>
                    </div>
                    <div className="mt-2 flex items-baseline gap-2">
                      <span className="text-[22px] font-bold font-fraunces">$306</span>
                      <span className="text-[13px] text-[#0A0A0B]/50">/mo</span>
                    </div>
                    <div className="mt-1 text-[12px] text-[#5B5CFF] font-medium">Keeps buffer above $3.2k</div>
                    {paymentPlan === "split" && <div className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-[#0A0A0B] text-white flex items-center justify-center">✓</div>}
                  </button>
                </div>
              </div>
              
              <div className="rounded-[24px] bg-white border border-[#0A0A0B]/[0.06] shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-mono text-[11px] text-[#0A0A0B]/40 tracking-widest">RECENT</h3>
                  <span className="text-[12px] text-[#0A0A0B]/50 cursor-pointer">View all →</span>
                </div>
                <div className="space-y-4">
                  {mockTransactions.map((tx, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full flex items-center justify-center border border-[#0A0A0B]/[0.06]">
                        <span className="w-1.5 h-1.5 rounded-full" style={{backgroundColor: tx.dot}} />
                      </div>
                      <div>
                        <div className="text-[13px] font-semibold">{tx.name}</div>
                        <div className="text-[11px] text-[#0A0A0B]/40">{tx.category} • {tx.date}</div>
                      </div>
                      <div className={`ml-auto font-mono text-[13px] ${tx.amount > 0 ? "text-[#5B5CFF]" : "text-[#0A0A0B]"}`}>
                        {tx.amount > 0 ? "+" : ""}{tx.amount < 0 ? `-$${Math.abs(tx.amount)}` : `$${tx.amount.toLocaleString()}`}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
