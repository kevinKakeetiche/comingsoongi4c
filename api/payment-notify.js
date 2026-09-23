export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  // Monetbil sends the final transaction status here. In production, connect this
  // endpoint to GI4C's database/CRM before marking a donation as received.
  console.log('GI4C Monetbil notification:', req.body || {});
  return res.status(200).json({ received: true });
}
