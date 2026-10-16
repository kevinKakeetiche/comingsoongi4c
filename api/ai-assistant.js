const GI4C_KNOWLEDGE = `
GI4C (Global Impact for Communities) is a Community Intelligence & Systems Strengthening Hub.
Mission: To leverage technology, data, and localized research to strengthen public systems and empower communities by translating real-time intelligence into informed decisions and coordinated action that advance healthy people, resilient systems, and sustainable communities
Motto: Intelligence for Action & Systems for Impact.
Slogan: Connecting Community Intelligence to Decisions, Resources & Action for Coordinated Interventions.
Logic: Community Intelligence -> Informed Decisions -> Mobilized Resources -> Coordinated Action -> Stronger Systems -> Sustainable Impact.
Values C.I.R.C.L.E.: Community-Centred, Integrity, Responsibility, Collaboration, Learning & Evidence, Equity & Inclusion.
Principles R.E.C.I.P.E.: Responsibility, Empathy, Compassion, Integrity, Purpose, Ethics.
Thematic areas: Health Systems & Community Well-being; Socio-economic Development & Livelihoods; Climate & Environmental Resilience; Data Intelligence, Research & Systems Strengthening.
Operation 20K Trees: Project duration 2023-2028; geographic focus Machatoum Community, Cameroon; overall target 20,000 trees; current status 2,300 trees planted (11.5%); remaining 17,700. GI4C is technical implementer and project coordinator. A GIS/GPS tree registry is planned for planting locations, species, dates, survival and growth.
Key portals: portal.gi4c.org, learn.gi4c.org, library.gi4c.org, report.gi4c.org.
Contact: Yaoundé, Cameroon; info@gi4c.org; www.gi4c.org.
`;

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(body));
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return json(res, 405, { error: 'Method not allowed' });
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const message = String(body.message || '').trim();
    if (!message) return json(res, 400, { error: 'Message is required' });
    if (message.length > 4000) return json(res, 400, { error: 'Message is too long' });

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return json(res, 503, { error: 'The GI4C assistant is not configured yet. Please contact info@gi4c.org for verified information.' });
    }

    const wantWeb = body.realtime === true;
    const tools = wantWeb ? [{ type: 'web_search' }] : [];
    const prompt = `You are an experimental GI4C website assistant. Answer in the user's language.\n\nRULES:\n- Use the GI4C website knowledge summary below for GI4C facts.\n- Never invent GI4C metrics, projects, staff, donors, beneficiaries or results.\n- If a fact is not in the summary, say that it is not confirmed by the current GI4C website knowledge.\n- When realtime mode is enabled, use web search for current external information and clearly label external facts as external.\n- Give concise, useful answers.\n- Do not claim that the summary is a formally verified or complete source.\n\nGI4C WEBSITE KNOWLEDGE SUMMARY:\n${GI4C_KNOWLEDGE}\n\nUSER QUESTION:\n${message}`;

    const response = await fetch('https://api.openai.com/v1/responses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(8000),
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'gpt-4.1-mini',
        tools,
        input: prompt,
        max_output_tokens: 700
      })
    });

    const data = await response.json();
    if (!response.ok) {
      return json(res, 502, { error: 'AI provider error', detail: data?.error?.message || 'Unknown provider error' });
    }

    const answer = data.output_text || 'Je n’ai pas pu produire une réponse.';
    const sources = [];
    for (const item of (data.output || [])) {
      if (item.type === 'web_search_call') sources.push({ title: 'Web search', type: 'web' });
    }
    sources.unshift({ title: 'GI4C website knowledge summary', type: 'internal' });
    return json(res, 200, { answer, sources, mode: wantWeb ? 'realtime' : 'gi4c-only' });
  } catch (error) {
    console.error('GI4C assistant request failed:', error);
    return json(res, 500, { error: 'The assistant is temporarily unavailable. Please try again or contact info@gi4c.org.' });
  }
}
