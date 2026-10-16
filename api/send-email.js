const RECIPIENT = 'info@gi4c.org';
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function clean(value) {
  return String(value || '').trim();
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[character]);
}

function reply(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(body));
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return reply(res, 405, { error: 'Method not allowed.' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const fromEmail = process.env.RESEND_FROM_EMAIL;
  if (!apiKey || !fromEmail || !EMAIL_PATTERN.test(fromEmail)) {
    return reply(res, 503, {
      error: 'Email delivery is not configured yet. Please email info@gi4c.org directly.'
    });
  }

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const type = clean(body.type);
    const email = clean(body.email);
    if (body.website) return reply(res, 400, { error: 'Request could not be accepted.' });
    if (email.length > 254 || !EMAIL_PATTERN.test(email)) {
      return reply(res, 400, { error: 'Enter a valid email address of no more than 254 characters.' });
    }

    let subject;
    let text;
    let html;
    let replyTo;

    if (type === 'contact') {
      const name = clean(body.name);
      const contactSubject = clean(body.subject).replace(/[\r\n]+/g, ' ');
      const message = clean(body.message);
      if (!name || !contactSubject || !message) {
        return reply(res, 400, { error: 'Complete all required contact fields.' });
      }
      if (name.length > 120 || contactSubject.length > 160 || message.length > 5000) {
        return reply(res, 400, { error: 'One or more fields exceed their permitted length.' });
      }

      subject = `Website contact: ${contactSubject}`;
      text = `Name: ${name}\nEmail: ${email}\n\n${message}`;
      html = `<p><strong>Name:</strong> ${escapeHtml(name)}</p><p><strong>Email:</strong> ${escapeHtml(email)}</p><p><strong>Subject:</strong> ${escapeHtml(contactSubject)}</p><p>${escapeHtml(message).replace(/\n/g, '<br>')}</p>`;
      replyTo = email;
    } else if (type === 'newsletter') {
      subject = 'Website newsletter subscription request';
      text = `Please add this address to GI4C's newsletter list, subject to the subscriber's consent: ${email}`;
      html = `<p>A visitor asked to receive GI4C updates at:</p><p><strong>${escapeHtml(email)}</strong></p><p>Please add the address to the mailing list only after confirming that GI4C's newsletter process is in place.</p>`;
      replyTo = email;
    } else {
      return reply(res, 400, { error: 'Unsupported email request.' });
    }

    const providerResponse = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      signal: AbortSignal.timeout(10000),
      body: JSON.stringify({
        from: `GI4C Website <${fromEmail}>`,
        to: [RECIPIENT],
        reply_to: replyTo,
        subject,
        text,
        html
      })
    });

    if (!providerResponse.ok) {
      console.error('Resend rejected GI4C website email:', providerResponse.status);
      return reply(res, 502, {
        error: 'GI4C could not accept the message for delivery. Please try again or email info@gi4c.org directly.'
      });
    }

    return reply(res, 200, { success: true });
  } catch (error) {
    console.error('GI4C website email request failed:', error);
    return reply(res, 500, {
      error: 'GI4C could not send the message. Please try again or email info@gi4c.org directly.'
    });
  }
}
