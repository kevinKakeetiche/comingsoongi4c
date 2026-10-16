export default function handler(req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({
    updatedAt: new Date().toISOString(),
    operation20KTrees: { target: 20000, planted: 2300, remaining: 17700, progressPercent: 11.5, duration: '2023-2028', location: 'Machatoum Community, Cameroon' },
    sources: ['GI4C internal data']
  });
}
