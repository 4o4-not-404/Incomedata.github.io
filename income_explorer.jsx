import { useState, useMemo, useCallback } from "react";

// ═══════════════════════════════════════════════════════════════════════
// PASTE YOUR income_percentiles.json DATA HERE
// After running process_income.py, copy the contents of
// income_percentiles.json and replace the DEMO_DATA below.
//
// The structure is:
// { metadata: {...}, data: { "2024": { "29": { p50: 55000, ... }, ... }, ... } }
// ═══════════════════════════════════════════════════════════════════════

const DEMO_DATA = null; // Replace with: import data from './income_percentiles.json'

// If no real data loaded, show instructions
const CPI_U = {
  1990:130.7,1991:136.2,1992:140.3,1993:144.5,1994:148.2,1995:152.4,
  1996:156.9,1997:160.5,1998:163.0,1999:166.6,2000:172.2,2001:177.1,
  2002:179.9,2003:184.0,2004:188.9,2005:195.3,2006:201.6,2007:207.3,
  2008:215.3,2009:214.5,2010:218.1,2011:224.9,2012:229.6,2013:233.0,
  2014:236.7,2015:237.0,2016:240.0,2017:245.1,2018:251.1,2019:255.7,
  2020:258.8,2021:270.9,2022:292.7,2023:304.7,2024:313.0,2025:320.0,
};

const BASE_CPI_YEAR = 2024;
const BASE_CPI = CPI_U[BASE_CPI_YEAR];

const PKEYS = ["p1","p5","p10","p25","p50","p75","p90","p95","p99"];
const PKEYS_DEFAULT = ["p25","p50","p75","p90"];
const PLABELS = {
  p1:"1st",p5:"5th",p10:"10th",p25:"25th",p50:"Median",
  p75:"75th",p90:"90th",p95:"95th",p99:"Top 1%"
};
const PCOLORS = {
  p1:"#3a5a8a",p5:"#4a6fa5",p10:"#5b84b8",p25:"#6fa8c7",
  p50:"#f0c040",p75:"#e8883a",p90:"#d04535",p95:"#b82830",p99:"#8b1525"
};

function fmt(n){if(n==null)return"—";if(n>=1e6)return"$"+(n/1e6).toFixed(1)+"M";if(n>=1e3)return"$"+Math.round(n/1e3)+"k";return"$"+Math.round(n)}
function fmtFull(n){if(n==null)return"—";return"$"+Math.round(n).toLocaleString()}

function inflate(val, fromYear, toYear=BASE_CPI_YEAR){
  if(val==null)return null;
  const from=CPI_U[fromYear], to=CPI_U[toYear];
  if(!from||!to)return val;
  return val*(to/from);
}

export default function IncomeExplorer() {
  const [data, setData] = useState(DEMO_DATA);
  const [mode, setMode] = useState("age");     // "age" or "time"
  const [selAge, setSelAge] = useState(29);
  const [selYear, setSelYear] = useState(null); // auto-detect latest
  const [cmpYear, setCmpYear] = useState(null); // auto-detect earliest
  const [selPerc, setSelPerc] = useState(PKEYS_DEFAULT);
  const [real, setReal] = useState(true);
  const [showTable, setShowTable] = useState(false);

  // Handle JSON file upload
  const handleFile = useCallback(async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const text = await file.text();
      const parsed = JSON.parse(text);
      setData(parsed);
      const years = Object.keys(parsed.data).map(Number).sort((a,b)=>a-b);
      setSelYear(years[years.length-1]);
      setCmpYear(years[0]);
    } catch(err) {
      alert("Error parsing JSON: " + err.message);
    }
  }, []);

  const toggle = useCallback(p => {
    setSelPerc(prev => prev.includes(p) ? prev.filter(x=>x!==p) : [...prev, p]);
  }, []);

  // Derived values
  const years = useMemo(() => data ? Object.keys(data.data).map(Number).sort((a,b)=>a-b) : [], [data]);
  const ages = useMemo(() => {
    if (!data || !selYear) return [];
    const yd = data.data[String(selYear)];
    return yd ? Object.keys(yd).map(Number).sort((a,b)=>a-b) : [];
  }, [data, selYear]);

  const availPerc = useMemo(() => {
    if (!data || !years.length) return PKEYS;
    // Check which percentiles exist in the data
    const sample = data.data[String(years[years.length-1])];
    if (!sample) return PKEYS;
    const sampleAge = Object.values(sample)[0];
    return PKEYS.filter(p => sampleAge && p in sampleAge);
  }, [data, years]);

  // ── Chart dimensions ──
  const W=820, H=400, M={t:30,r:68,b:48,l:68};
  const cW=W-M.l-M.r, cH=H-M.t-M.b;

  // ── AGE PROFILE VIEW ──
  const renderAgeChart = () => {
    if (!data || !selYear) return null;
    const yd = data.data[String(selYear)] || {};
    const cd = cmpYear ? (data.data[String(cmpYear)] || {}) : {};
    const ageList = Object.keys(yd).map(Number).sort((a,b)=>a-b);
    if (!ageList.length) return null;

    // Collect values for y-scale
    const vals = [];
    ageList.forEach(age => {
      const d = yd[String(age)];
      selPerc.forEach(p => {
        if(d && d[p]!=null) vals.push(real ? inflate(d[p], selYear) : d[p]);
      });
      if(cmpYear && cd[String(age)]) {
        selPerc.forEach(p => {
          const v = cd[String(age)]?.[p];
          if(v!=null) vals.push(real ? inflate(v, cmpYear) : v);
        });
      }
    });
    if(!vals.length) return null;

    const yMax = Math.max(...vals)*1.08;
    const xS = a => M.l+((a-ageList[0])/(ageList[ageList.length-1]-ageList[0]))*cW;
    const yS = v => M.t+cH-(v/yMax)*cH;
    const step = yMax>500000?100000:yMax>200000?50000:yMax>100000?25000:10000;
    const yTicks = [];for(let t=0;t<=yMax;t+=step)yTicks.push(t);

    return (
      <svg width={W} height={H} style={{display:"block"}}>
        <rect x={M.l} y={M.t} width={cW} height={cH} fill="#13151d" rx={2}/>
        {yTicks.map(t=>(
          <g key={t}>
            <line x1={M.l} x2={W-M.r} y1={yS(t)} y2={yS(t)} stroke="#222530" strokeWidth={0.5}/>
            <text x={M.l-8} y={yS(t)+4} textAnchor="end" fill="#4a5060" fontSize={10}
              style={{fontFamily:"monospace"}}>{fmt(t)}</text>
          </g>
        ))}
        {ageList.filter(a=>a%5===0).map(a=>(
          <text key={a} x={xS(a)} y={H-8} textAnchor="middle" fill="#4a5060" fontSize={10}
            style={{fontFamily:"monospace"}}>{a}</text>
        ))}
        {/* Selected age line */}
        <line x1={xS(selAge)} x2={xS(selAge)} y1={M.t} y2={M.t+cH}
          stroke="#f0c040" strokeWidth={1.5} opacity={0.5}/>
        <text x={xS(selAge)} y={M.t-6} textAnchor="middle" fill="#f0c040" fontSize={10}
          fontWeight={700} style={{fontFamily:"monospace"}}>▼{selAge}</text>

        {/* Comparison year (dashed) */}
        {cmpYear && selPerc.map(p => {
          const pts = ageList.filter(a=>cd[String(a)]?.[p]!=null).map(a=>({
            a, v: real ? inflate(cd[String(a)][p], cmpYear) : cd[String(a)][p]
          }));
          if(!pts.length) return null;
          return <path key={p+"c"} fill="none" stroke={PCOLORS[p]} strokeWidth={1.2}
            strokeDasharray="4,4" opacity={0.35}
            d={pts.map((d,i)=>`${i?'L':'M'}${xS(d.a)},${yS(d.v)}`).join(" ")}/>;
        })}

        {/* Current year (solid) */}
        {selPerc.map(p => {
          const pts = ageList.filter(a=>yd[String(a)]?.[p]!=null).map(a=>({
            a, v: real ? inflate(yd[String(a)][p], selYear) : yd[String(a)][p]
          }));
          if(!pts.length) return null;
          return (
            <g key={p}>
              <path fill="none" stroke={PCOLORS[p]} strokeWidth={2.5} strokeLinejoin="round"
                d={pts.map((d,i)=>`${i?'L':'M'}${xS(d.a)},${yS(d.v)}`).join(" ")}/>
              <text x={W-M.r+5} y={yS(pts[pts.length-1].v)+4} fill={PCOLORS[p]} fontSize={9}
                style={{fontFamily:"monospace"}}>{PLABELS[p]}</text>
            </g>
          );
        })}
        {/* Dots at selected age */}
        {selPerc.map(p => {
          const d = yd[String(selAge)];
          if(!d||d[p]==null) return null;
          const v = real ? inflate(d[p], selYear) : d[p];
          return <circle key={p+"d"} cx={xS(selAge)} cy={yS(v)} r={4}
            fill={PCOLORS[p]} stroke="#0e1017" strokeWidth={2}/>;
        })}
      </svg>
    );
  };

  // ── TIME SERIES VIEW ──
  const renderTimeChart = () => {
    if (!data || !years.length) return null;

    const vals = [];
    years.forEach(yr => {
      const d = data.data[String(yr)]?.[String(selAge)];
      if(!d) return;
      selPerc.forEach(p => {
        if(d[p]!=null) vals.push(real ? inflate(d[p], yr) : d[p]);
      });
    });
    if(!vals.length) return null;

    const yMax = Math.max(...vals)*1.08;
    const xS = yr => M.l+((yr-years[0])/(years[years.length-1]-years[0]))*cW;
    const yS = v => M.t+cH-(v/yMax)*cH;
    const step = yMax>500000?100000:yMax>200000?50000:yMax>100000?25000:10000;
    const yTicks = [];for(let t=0;t<=yMax;t+=step)yTicks.push(t);

    return (
      <svg width={W} height={H} style={{display:"block"}}>
        <rect x={M.l} y={M.t} width={cW} height={cH} fill="#13151d" rx={2}/>
        {yTicks.map(t=>(
          <g key={t}>
            <line x1={M.l} x2={W-M.r} y1={yS(t)} y2={yS(t)} stroke="#222530" strokeWidth={0.5}/>
            <text x={M.l-8} y={yS(t)+4} textAnchor="end" fill="#4a5060" fontSize={10}
              style={{fontFamily:"monospace"}}>{fmt(t)}</text>
          </g>
        ))}
        {years.filter(y=>y%5===0||(years.length<15)).map(y=>(
          <text key={y} x={xS(y)} y={H-8} textAnchor="middle" fill="#4a5060" fontSize={10}
            style={{fontFamily:"monospace"}}>{y}</text>
        ))}
        {/* Recession bands */}
        {[[2001,2001],[2007,2009],[2020,2020]].map(([s,e])=>{
          if(s<years[0]||e>years[years.length-1])return null;
          return <rect key={s} x={xS(s)-2} y={M.t} width={Math.max(xS(e)-xS(s)+4,6)}
            height={cH} fill="#ff3333" opacity={0.04}/>;
        })}
        {selPerc.map(p => {
          const pts = years.filter(yr=>{
            const d=data.data[String(yr)]?.[String(selAge)];
            return d&&d[p]!=null;
          }).map(yr=>({
            yr, v: real ? inflate(data.data[String(yr)][String(selAge)][p], yr) : data.data[String(yr)][String(selAge)][p]
          }));
          if(!pts.length) return null;
          return (
            <g key={p}>
              <path fill="none" stroke={PCOLORS[p]} strokeWidth={2.5} strokeLinejoin="round"
                d={pts.map((d,i)=>`${i?'L':'M'}${xS(d.yr)},${yS(d.v)}`).join(" ")}/>
              {pts.map(d=>(
                <circle key={d.yr} cx={xS(d.yr)} cy={yS(d.v)} r={2.5}
                  fill={PCOLORS[p]} stroke="#0e1017" strokeWidth={1}/>
              ))}
              <text x={W-M.r+5} y={yS(pts[pts.length-1].v)+4} fill={PCOLORS[p]} fontSize={9}
                style={{fontFamily:"monospace"}}>{PLABELS[p]}</text>
            </g>
          );
        })}
      </svg>
    );
  };

  // ── NO DATA STATE ──
  if (!data) {
    return (
      <div style={{background:"#0e1017",color:"#c8cdd5",minHeight:"100vh",
        fontFamily:"'IBM Plex Sans',sans-serif",padding:"40px 20px",display:"flex",
        justifyContent:"center",alignItems:"center"}}>
        <div style={{maxWidth:600,textAlign:"center"}}>
          <h1 style={{fontSize:22,fontWeight:700,color:"#e0e2e8",marginBottom:16}}>
            Income Percentile Explorer
          </h1>
          <p style={{fontSize:14,color:"#888e9a",lineHeight:1.7,marginBottom:24}}>
            Load your <code style={{background:"#1a1d26",padding:"2px 6px",borderRadius:3}}>
            income_percentiles.json</code> file generated by the processing script.
          </p>
          <label style={{
            display:"inline-block",padding:"12px 28px",background:"#f0c040",color:"#0e1017",
            fontWeight:700,fontSize:14,borderRadius:6,cursor:"pointer",
          }}>
            Load JSON Data
            <input type="file" accept=".json" onChange={handleFile}
              style={{display:"none"}}/>
          </label>
          <p style={{fontSize:11,color:"#444a55",marginTop:20,lineHeight:1.7}}>
            See README.md for instructions on downloading IPUMS-CPS data
            and running process_income.py to generate this file.
          </p>
        </div>
      </div>
    );
  }

  // ── MAIN UI ──
  const latestYear = selYear || years[years.length-1];
  const compareYear = cmpYear || years[0];
  const yd = data.data[String(latestYear)] || {};
  const focusStats = yd[String(selAge)];

  return (
    <div style={{background:"#0e1017",color:"#c8cdd5",minHeight:"100vh",
      fontFamily:"'IBM Plex Sans','Segoe UI',sans-serif",padding:"20px 16px"}}>
      <div style={{maxWidth:880,margin:"0 auto"}}>

        <div style={{marginBottom:20,borderBottom:"1px solid #1e2230",paddingBottom:14}}>
          <h1 style={{fontSize:20,fontWeight:700,color:"#e0e2e8",margin:0}}>
            U.S. Individual Income by Age & Percentile
          </h1>
          <p style={{fontSize:11,color:"#4a5060",margin:"5px 0 0",lineHeight:1.6}}>
            {data.metadata?.source || "IPUMS-CPS"} ·
            {years.length} years ({years[0]}–{years[years.length-1]}) ·
            {real ? ` ${BASE_CPI_YEAR} dollars (CPI-U adjusted)` : " Nominal dollars"} ·
            {mode==="age" ? ` Solid=${latestYear}, Dashed=${compareYear}` : ` Age ${selAge}`}
          </p>
        </div>

        {/* Controls */}
        <div style={{display:"flex",flexWrap:"wrap",gap:8,marginBottom:14,alignItems:"center"}}>
          <div style={{display:"flex",gap:2,background:"#13151d",borderRadius:6,padding:2}}>
            {[["age","By Age"],["time","Over Time"]].map(([v,l])=>(
              <button key={v} onClick={()=>setMode(v)} style={{
                padding:"5px 14px",fontSize:12,fontWeight:600,border:"none",borderRadius:5,cursor:"pointer",
                background:mode===v?"#f0c040":"transparent",color:mode===v?"#0e1017":"#4a5060"
              }}>{l}</button>
            ))}
          </div>

          <div style={{display:"flex",alignItems:"center",gap:6,background:"#13151d",padding:"4px 12px",borderRadius:6}}>
            <span style={{fontSize:10,color:"#4a5060",textTransform:"uppercase"}}>Age</span>
            <input type="range" min={ages[0]||18} max={ages[ages.length-1]||65} value={selAge}
              onChange={e=>setSelAge(+e.target.value)} style={{width:120,accentColor:"#f0c040"}}/>
            <span style={{fontSize:15,fontWeight:700,color:"#f0c040",fontFamily:"monospace",minWidth:24}}>{selAge}</span>
          </div>

          {mode==="age" && (
            <>
              <select value={latestYear} onChange={e=>setSelYear(+e.target.value)}
                style={{background:"#13151d",color:"#c8cdd5",border:"1px solid #222530",borderRadius:4,padding:"4px 8px",fontSize:11,fontFamily:"monospace"}}>
                {years.map(y=><option key={y} value={y}>{y}</option>)}
              </select>
              <span style={{fontSize:10,color:"#4a5060"}}>vs</span>
              <select value={compareYear} onChange={e=>setCmpYear(+e.target.value)}
                style={{background:"#13151d",color:"#888e9a",border:"1px solid #222530",borderRadius:4,padding:"4px 8px",fontSize:11,fontFamily:"monospace"}}>
                {years.map(y=><option key={y} value={y}>{y}</option>)}
              </select>
            </>
          )}

          <button onClick={()=>setReal(!real)} style={{
            padding:"5px 12px",fontSize:11,fontWeight:600,border:"1px solid #222530",borderRadius:5,cursor:"pointer",
            background:real?"#1a2e1a":"#13151d",color:real?"#7ec87e":"#4a5060"
          }}>{real?`✓ Real ${BASE_CPI_YEAR}$`:"Nominal $"}</button>

          {focusStats && (
            <span style={{marginLeft:"auto",fontSize:10,color:"#3a4050",fontFamily:"monospace"}}>
              n={focusStats.n_samples?.toLocaleString()} · {((focusStats.est_workforce||0)/1e6).toFixed(1)}M workers
            </span>
          )}
        </div>

        {/* Percentile toggles */}
        <div style={{display:"flex",flexWrap:"wrap",gap:4,marginBottom:12}}>
          {availPerc.map(p=>(
            <button key={p} onClick={()=>toggle(p)} style={{
              padding:"4px 12px",fontSize:10,fontWeight:600,border:"none",borderRadius:3,cursor:"pointer",
              fontFamily:"monospace",
              background:selPerc.includes(p)?PCOLORS[p]:"#13151d",
              color:selPerc.includes(p)?"#fff":"#4a5060",
              opacity:selPerc.includes(p)?1:0.5
            }}>{PLABELS[p]}</button>
          ))}
        </div>

        {/* Chart */}
        <div style={{background:"#11131b",borderRadius:8,padding:"8px 4px 4px",border:"1px solid #1e2230",marginBottom:16,overflowX:"auto"}}>
          <div style={{minWidth:W}}>
            {mode==="age" ? renderAgeChart() : renderTimeChart()}
          </div>
        </div>

        {/* Stats cards for selected age */}
        {focusStats && (
          <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(130px,1fr))",gap:7,marginBottom:16}}>
            {selPerc.filter(p=>focusStats[p]!=null).map(p => {
              const v = real ? inflate(focusStats[p], latestYear) : focusStats[p];
              const cmpD = cmpYear ? data.data[String(compareYear)]?.[String(selAge)] : null;
              const cmpV = cmpD?.[p] != null ? (real ? inflate(cmpD[p], compareYear) : cmpD[p]) : null;
              const chg = (v && cmpV) ? ((v-cmpV)/cmpV*100) : null;
              return (
                <div key={p} style={{background:"#11131b",borderRadius:5,padding:"8px 10px",borderLeft:`3px solid ${PCOLORS[p]}`}}>
                  <div style={{fontSize:9,color:"#4a5060",textTransform:"uppercase",letterSpacing:"0.05em"}}>{PLABELS[p]}</div>
                  <div style={{fontSize:16,fontWeight:700,color:"#e0e2e8",fontFamily:"monospace"}}>{fmtFull(v)}</div>
                  {cmpV!=null && <div style={{fontSize:9,color:"#4a5060"}}>was {fmtFull(cmpV)}</div>}
                  {chg!=null && <div style={{fontSize:10,fontWeight:600,color:chg>0?"#7ec87e":"#d04535"}}>{chg>0?"+":""}{chg.toFixed(1)}%</div>}
                </div>
              );
            })}
          </div>
        )}

        {/* Data table */}
        <details>
          <summary style={{fontSize:12,color:"#4a5060",cursor:"pointer",padding:"8px 0",borderTop:"1px solid #1e2230"}}>
            Full data table
          </summary>
          <div style={{overflowX:"auto",marginTop:6}}>
            <table style={{width:"100%",borderCollapse:"collapse",fontSize:10,fontFamily:"monospace"}}>
              <thead>
                <tr style={{borderBottom:"1px solid #222530"}}>
                  <th style={{textAlign:"left",padding:"4px 6px",color:"#4a5060"}}>Age</th>
                  <th style={{textAlign:"right",padding:"4px 6px",color:"#4a5060"}}>n</th>
                  {selPerc.map(p=>(
                    <th key={p} style={{textAlign:"right",padding:"4px 6px",color:PCOLORS[p]}}>{PLABELS[p]}</th>
                  ))}
                  <th style={{textAlign:"right",padding:"4px 6px",color:"#5a6070"}}>Mean</th>
                </tr>
              </thead>
              <tbody>
                {ages.map((age,i)=>{
                  const d = yd[String(age)];
                  if(!d) return null;
                  return (
                    <tr key={age} onClick={()=>setSelAge(age)} style={{
                      cursor:"pointer",borderBottom:"1px solid #161820",
                      background:age===selAge?"#181c28":i%2===0?"transparent":"#0f1118"
                    }}>
                      <td style={{padding:"3px 6px",color:age===selAge?"#f0c040":"#6a7080",fontWeight:age===selAge?700:400}}>{age}</td>
                      <td style={{textAlign:"right",padding:"3px 6px",color:"#3a4050"}}>{d.n_samples}</td>
                      {selPerc.map(p=>(
                        <td key={p} style={{textAlign:"right",padding:"3px 6px",color:"#c0c5d0"}}>
                          {fmtFull(real ? inflate(d[p], latestYear) : d[p])}
                        </td>
                      ))}
                      <td style={{textAlign:"right",padding:"3px 6px",color:"#5a6070"}}>
                        {fmtFull(real ? inflate(d.mean, latestYear) : d.mean)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </details>

        {/* Methodology */}
        <div style={{fontSize:10,color:"#3a4050",lineHeight:1.7,padding:"12px",background:"#11131b",
          borderRadius:6,border:"1px solid #1e2230",marginTop:16}}>
          <strong style={{color:"#6a7080"}}>Source</strong><br/>
          {data.metadata?.citation || "IPUMS-CPS"}<br/><br/>
          <strong style={{color:"#6a7080"}}>Methodology</strong><br/>
          {data.metadata?.methodology?.income_variable || "INCTOT"} ·
          Weight: {data.metadata?.methodology?.weight_variable || "ASECWT"} ·
          {data.metadata?.methodology?.population || "Workers"} ·
          {data.metadata?.methodology?.percentile_method || "Weighted percentiles"}<br/>
          CPI-U adjustment base: {BASE_CPI_YEAR} · Generated: {data.metadata?.generated_at || "—"}
        </div>
      </div>
    </div>
  );
}
