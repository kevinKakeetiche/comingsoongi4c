const GI4C_KNOWLEDGE = `
GI4C (Global Impact for Communities) is a Community Data Intelligence & Systems Strengthening Hub.
Mission: To make community needs, vulnerabilities, and opportunities visible through continuous community intelligence, and to work with governments, communities, donors, development partners, and other stakeholders to translate evidence into better decisions, targeted resource allocation, and coordinated interventions that strengthen systems and drive sustainable impact.
Motto: Intelligence for Action & Systems for Impact.
Slogan: Making Community Needs Visible for Coordinated Interventions.
Logic: Community intelligence -> Evidence -> Better decisions -> Targeted resources -> Coordinated interventions -> Stronger systems -> Sustainable impact.
Values C.I.R.C.L.E.: Community-Centred, Integrity, Responsibility, Collaboration, Learning & Evidence, Equity & Inclusion.
Principles R.E.C.I.P.E.: Responsibility, Empathy, Compassion, Integrity, Purpose, Ethics.
Thematic areas: Health Systems & Community Well-being; Socio-economic Development & Livelihoods; Climate & Environmental Resilience; Data Intelligence, Research & Systems Strengthening.
Operation 20K Trees: Project duration 2026-2032; geographic focus Machatoum Community, Cameroon; overall target 20,000 trees; current status 2,000 trees planted (10%); remaining 18,000. GI4C is technical implementer and project coordinator. A GIS/GPS tree registry is planned for planting locations, species, dates, survival and growth.
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
      return json(res, 200, {
        answer: 'Le moteur IA temps réel n’est pas encore activé. La clé OPENAI_API_KEY doit être ajoutée au backend. En attendant, voici la base GI4C disponible : Operation 20K Trees compte 2 000 arbres plantés sur 20 000 (10 %), avec 18 000 arbres restants.',
        sources: [{ title: 'GI4C internal knowledge base', type: 'internal' }],
        mode: 'knowledge-base'
      });
    }

    const wantWeb = body.realtime !== false;
    const tools = wantWeb ? [{ type: 'web_search' }] : [];
    const prompt = `You are the official GI4C AI Assistant. Answer in the user's language.\n\nRULES:\n- Prioritize the GI4C knowledge below for GI4C facts.\n- Never invent GI4C metrics, projects, staff, donors, beneficiaries or results.\n- If a fact is not in the GI4C knowledge base, say that it is not confirmed by the current GI4C source.\n- When realtime mode is enabled, use web search for current external information and clearly label external facts as external.\n- Give concise, useful answers.\n- For current data, always distinguish GI4C internal data from web information.\n\nGI4C KNOWLEDGE:\n${GI4C_KNOWLEDGE}\n\nUSER QUESTION:\n${message}`;

    const response = await fetch('https://api.openai.com/v1/responses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'gpt-5.6-luna',
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
    sources.unshift({ title: 'GI4C internal knowledge base', type: 'internal' });
    return json(res, 200, { answer, sources, mode: wantWeb ? 'realtime' : 'gi4c-only' });
  } catch (error) {
    return json(res, 500, { error: 'Internal server error', detail: error.message });
  }
}
