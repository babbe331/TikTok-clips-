/* ============================================================
   Farmlind Produce — Slack connector
   A tiny always-on service that listens to a Slack channel,
   parses order messages, and holds them in a queue that the
   Farmlind web app pulls from automatically.

   Endpoints:
     POST /slack/events   <- Slack sends new messages here
     GET  /pending?key=   -> app fetches new parsed orders
     POST /ack            -> app confirms it imported them
     GET  /health         -> simple status check

   Env vars (set these on your host):
     SLACK_SIGNING_SECRET   (from your Slack app -> Basic Information)
     APP_KEY                (any secret string; also entered in the app)
     SLACK_CHANNEL          (optional: only accept messages from this channel ID)
     PORT                   (host usually sets this automatically)
   ============================================================ */
const express = require("express");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const app = express();
const SIGNING_SECRET = process.env.SLACK_SIGNING_SECRET || "";
const APP_KEY = process.env.APP_KEY || "";
const ONLY_CHANNEL = process.env.SLACK_CHANNEL || "";
const STORE = path.join(__dirname, "orders.json");

/* ---------- tiny JSON-file queue (persists across restarts) ---------- */
function loadQueue(){ try{ return JSON.parse(fs.readFileSync(STORE,"utf8")); }catch(e){ return []; } }
function saveQueue(q){ try{ fs.writeFileSync(STORE, JSON.stringify(q)); }catch(e){ console.error("save failed",e); } }
let queue = loadQueue();

/* ---------- CORS so the GitHub Pages app can read /pending ---------- */
app.use((req,res,next)=>{
  res.header("Access-Control-Allow-Origin","*");
  res.header("Access-Control-Allow-Headers","Content-Type");
  res.header("Access-Control-Allow-Methods","GET,POST,OPTIONS");
  if(req.method==="OPTIONS") return res.sendStatus(200);
  next();
});

/* ---------- order parser (matches the app's parser) ---------- */
const NUM_WORDS={zero:0,a:1,an:1,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,
 eleven:11,twelve:12,thirteen:13,fourteen:14,fifteen:15,sixteen:16,seventeen:17,eighteen:18,nineteen:19,
 twenty:20,thirty:30,forty:40,fifty:50,sixty:60,seventy:70,eighty:80,ninety:90,couple:2,few:3};
const NUM_MULT={dozen:12,hundred:100};
const UNIT_WORDS=new Set(["case","cases","box","boxes","flat","flats","bag","bags","lb","lbs","pound","pounds",
 "crown","crowns","bunch","bunches","head","heads","carton","cartons","piece","pieces","ct","count","of","x"]);
const cw=w=>w.toLowerCase().replace(/[^a-z]/g,"");
function parseQtyLine(line){
  line=line.trim(); let qty=1, rest=line;
  const m=line.match(/^(\d+(?:\.\d+)?)\s*(?:x|\*)?\s+(.*)$/i);
  if(m){ qty=parseFloat(m[1]); rest=m[2]; }
  else{
    const t=line.split(/\s+/); let i=0,cur=0,used=false;
    while(i<t.length && i<3){ const w=cw(t[i]);
      if(NUM_WORDS[w]!==undefined){ cur+=NUM_WORDS[w]; used=true; i++; }
      else if(NUM_MULT[w]!==undefined){ cur=(cur||1)*NUM_MULT[w]; used=true; i++; }
      else break; }
    if(used){ qty=cur||1; rest=t.slice(i).join(" "); }
  }
  let nt=rest.split(/\s+/);
  while(nt.length>1 && UNIT_WORDS.has(cw(nt[0]))) nt.shift();
  return { qty, name:nt.join(" ").trim() };
}
function parseOrder(text){
  const lines=String(text||"").split(/\r?\n/).map(l=>l.trim()).filter(Boolean);
  if(lines.length<2) return null;                       // need a name + at least one item
  const items=lines.slice(1).map(parseQtyLine).filter(it=>it.name);
  if(items.length===0) return null;
  return { customerName:lines[0], items };
}

/* ---------- Slack signature verification (needs the raw body) ---------- */
app.use("/slack/events", express.raw({ type:"*/*" }));
function verifySlack(req){
  if(!SIGNING_SECRET) return true;                      // allow if not configured (dev)
  const ts=req.header("X-Slack-Request-Timestamp");
  const sig=req.header("X-Slack-Signature");
  if(!ts || !sig) return false;
  if(Math.abs(Date.now()/1000 - Number(ts)) > 300) return false;  // 5-min replay window
  const base=`v0:${ts}:${req.body.toString("utf8")}`;
  const mine="v0="+crypto.createHmac("sha256",SIGNING_SECRET).update(base).digest("hex");
  try{ return crypto.timingSafeEqual(Buffer.from(mine),Buffer.from(sig)); }catch(e){ return false; }
}

app.post("/slack/events",(req,res)=>{
  let body;
  try{ body=JSON.parse(req.body.toString("utf8")); }catch(e){ return res.sendStatus(400); }
  if(body.type==="url_verification") return res.json({ challenge: body.challenge });   // Slack handshake
  if(!verifySlack(req)) return res.sendStatus(401);

  const ev=body.event;
  if(ev && ev.type==="message" && !ev.bot_id && !ev.subtype){
    if(!ONLY_CHANNEL || ev.channel===ONLY_CHANNEL){
      const parsed=parseOrder(ev.text);
      if(parsed){
        const id=(ev.channel||"")+":"+(ev.ts||Date.now());
        if(!queue.some(o=>o.id===id)){
          queue.push({ id, customerName:parsed.customerName, items:parsed.items, ts:Date.now(), channel:ev.channel });
          saveQueue(queue);
          console.log("queued order from",parsed.customerName,"(",parsed.items.length,"items )");
        }
      }
    }
  }
  res.sendStatus(200);   // always 200 fast so Slack doesn't retry
});

/* ---------- app pulls new orders ---------- */
function checkKey(req){ return !APP_KEY || (req.query.key===APP_KEY) || (req.body && req.body.key===APP_KEY); }
app.get("/pending",(req,res)=>{
  if(!checkKey(req)) return res.status(401).json({error:"bad key"});
  res.json({ orders: queue });
});
app.use(express.json());
app.post("/ack",(req,res)=>{
  if(!checkKey(req)) return res.status(401).json({error:"bad key"});
  const ids=new Set((req.body && req.body.ids)||[]);
  queue=queue.filter(o=>!ids.has(o.id));
  saveQueue(queue);
  res.json({ ok:true, remaining:queue.length });
});

app.get("/health",(req,res)=>res.json({ ok:true, queued:queue.length }));
app.get("/",(req,res)=>res.send("Farmlind Slack connector is running."));

const PORT=process.env.PORT||3000;
app.listen(PORT,()=>console.log("Farmlind Slack connector listening on "+PORT));
