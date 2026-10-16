export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const serviceKey = process.env.MONETBIL_SERVICE_KEY;
  if (!serviceKey) {
    return res.status(503).json({ error: 'Le paiement n’est pas encore activé. Ajoutez MONETBIL_SERVICE_KEY dans les variables d’environnement du site.' });
  }

  try {
    const { amount, phone, firstName, lastName, email } = req.body || {};
    const value = Number(amount);
    if (!Number.isInteger(value) || value < 100 || value > 1000000) {
      return res.status(400).json({ error: 'Montant invalide. Utilisez un montant entre 100 et 1 000 000 FCFA.' });
    }

    const origin = `${req.headers['x-forwarded-proto'] || 'https'}://${req.headers.host}`;
    const paymentRef = `GI4C-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
    const payload = {
      amount: value,
      phone: phone || '',
      phone_lock: false,
      locale: 'fr',
      operator: 'CM_ORANGEMONEY',
      country: 'CM',
      currency: 'XAF',
      item_ref: 'GI4C-DONATION',
      payment_ref: paymentRef,
      user: email || paymentRef,
      first_name: firstName || '',
      last_name: lastName || '',
      email: email || '',
      return_url: `${origin}/payment-success.html?ref=${encodeURIComponent(paymentRef)}`,
      notify_url: `${origin}/api/payment-notify`,
      logo: `${origin}/assets/gi4c-logo.jpg`
    };

    const response = await fetch(`https://api.monetbil.com/widget/v2.1/${serviceKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok || !data.success || !data.payment_url) {
      return res.status(502).json({ error: 'Monetbil n’a pas pu créer la session de paiement.', details: data });
    }

    return res.status(200).json({ success: true, payment_url: data.payment_url, payment_ref: paymentRef });
  } catch (error) {
    return res.status(500).json({ error: 'Erreur serveur pendant la préparation du paiement.' });
  }
}
