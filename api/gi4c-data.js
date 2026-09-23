export default function handler(req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({
    updatedAt: new Date().toISOString(),
    operation20KTrees: { target: 20000, planted: 2000, remaining: 18000, progressPercent: 10, duration: '2026-2032', location: 'Machatoum Community, Cameroon' },
    sources: ['GI4C internal data']
  });
}
