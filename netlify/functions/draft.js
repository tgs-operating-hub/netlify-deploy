exports.handler = async function(event){
  if(event.httpMethod !== "POST"){ return { statusCode:405, body:"Method not allowed" }; }
  var KEY = process.env.DRAFT_SHARED_KEY;
  if(KEY && (event.headers["x-tgs-key"] !== KEY)){ return { statusCode:401, body:"Unauthorized" }; }
  var apiKey = process.env.ANTHROPIC_API_KEY;
  if(!apiKey){ return { statusCode:500, body: JSON.stringify({ error:"ANTHROPIC_API_KEY not set in Netlify env" }) }; }
  var input;
  try{ input = JSON.parse(event.body || "{}"); }catch(e){ return { statusCode:400, body:"Bad JSON" }; }
  var subject = input.subject || "", who = input.who || "", company = input.company || "", context = input.context || "";
  var model = process.env.DRAFT_MODEL || "claude-sonnet-4-6";
  var rules = "You are drafting an email reply AS Peter Te Hau, Founder of TGS Media. Output ONLY the email body text, nothing else. No signature, no sign-off, no name, because Gmail auto-appends his signature. Never use em dashes. Warm, direct, concise New Zealand business tone. Open with 'Hey <first name>,' for someone he knows or 'Hi <first name>,' for a formal or first contact. ROUTING: if this is a sales inquiry or someone wanting services like ads, marketing, an AI receptionist or a voice bot, Peter never takes sales calls, so warmly hand them to his sales team and include this booking link for Keith or Ayla: https://api.leadconnectorhq.com/widget/bookings/ultimate-lead-conversion-call . If an existing client asks for a meeting with Peter, point them to the client WhatsApp group and note that Bernice (bernice@tgsmedia.org) arranges meetings. Otherwise reply normally and helpfully. If a price, number, date, or decision is needed that you cannot know, insert a clear [ FILL IN: ... ] placeholder. Keep it short unless it is a proposal.";
  var userMsg = "Reply to this email.\nFrom: " + who + " (" + company + ")\nSubject: " + subject + "\n\nTheir message:\n" + context;
  try{
    var resp = await fetch("https://api.anthropic.com/v1/messages", {
      method:"POST",
      headers:{ "x-api-key": apiKey, "anthropic-version":"2023-06-01", "content-type":"application/json" },
      body: JSON.stringify({ model: model, max_tokens: 800, system: rules, messages:[{ role:"user", content: userMsg }] })
    });
    var data = await resp.json();
    if(!resp.ok){ return { statusCode:502, body: JSON.stringify({ error: (data.error && data.error.message) || "Anthropic error" }) }; }
    var out = ((data.content && data.content[0] && data.content[0].text) || "").trim();
    return { statusCode:200, headers:{ "content-type":"application/json" }, body: JSON.stringify({ body: out }) };
  }catch(e){
    return { statusCode:500, body: JSON.stringify({ error: String(e) }) };
  }
};
