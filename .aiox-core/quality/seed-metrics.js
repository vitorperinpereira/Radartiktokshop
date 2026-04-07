/**
 * Seed quality metrics data for local testing.
 *
 * @module quality/seed-metrics
 * @version 1.0.0
 * @story 3.11a - Quality Gates Metrics Collector
 */

const { MetricsCollector } = require('./metrics-collector');

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickLayer() {
  const roll = Math.random();
  if (roll < 0.45) return 1;
  if (roll < 0.8) return 2;
  return 3;
}

function generateLayerRun(timestamp, layer) {
  const passRate = {
    1: 0.9,
    2: 0.78,
    3: 0.86,
  };

  const passed = Math.random() < passRate[layer];
  const findingsCount = passed ? randomInt(0, 2) : randomInt(2, 8);
  const durationByLayer = {
    1: [400, 4500],
    2: [2000, 14000],
    3: [3000, 18000],
  };
  const [minDuration, maxDuration] = durationByLayer[layer];

  const run = {
    timestamp,
    layer,
    passed,
    durationMs: randomInt(minDuration, maxDuration),
    findingsCount,
    metadata: {
      triggeredBy: 'seed',
    },
    coderabbit: null,
    quinn: null,
  };

  if (layer === 2) {
    const codeRabbitFindings = randomInt(0, findingsCount + 1);
    const quinnFindings = Math.max(0, findingsCount - codeRabbitFindings);

    run.coderabbit = {
      findingsCount: codeRabbitFindings,
      severityBreakdown: {
        critical: Math.min(codeRabbitFindings, randomInt(0, 1)),
        high: Math.min(codeRabbitFindings, randomInt(0, 2)),
        medium: Math.min(codeRabbitFindings, randomInt(0, 3)),
        low: Math.max(0, codeRabbitFindings - randomInt(0, 3)),
      },
    };

    run.quinn = {
      findingsCount: quinnFindings,
      topCategories: quinnFindings > 0
        ? ['security', 'tests', 'performance', 'types'].slice(0, randomInt(1, 3))
        : [],
    };
  }

  return run;
}

function generateSeedData(options = {}) {
  const days = Number.parseInt(options.days, 10) || 30;
  const runsPerDay = Number.parseInt(options.runsPerDay, 10) || 8;
  const weekendReduction = options.weekendReduction !== false;
  const collector = new MetricsCollector({ retentionDays: days });
  const history = [];

  for (let offset = days - 1; offset >= 0; offset -= 1) {
    const day = new Date();
    day.setHours(0, 0, 0, 0);
    day.setDate(day.getDate() - offset);

    const isWeekend = day.getDay() === 0 || day.getDay() === 6;
    const dailyRuns = weekendReduction && isWeekend
      ? Math.max(1, Math.floor(runsPerDay / 2))
      : runsPerDay;

    for (let index = 0; index < dailyRuns; index += 1) {
      const timestamp = new Date(day);
      timestamp.setHours(randomInt(8, 22), randomInt(0, 59), randomInt(0, 59), 0);
      history.push(generateLayerRun(timestamp.toISOString(), pickLayer()));
    }
  }

  return collector.recomputeMetrics(history, days);
}

async function seedMetrics(options = {}) {
  const metrics = generateSeedData(options);
  const collector = new MetricsCollector({ retentionDays: metrics.retentionDays });
  await collector.saveMetrics(metrics);
  return metrics;
}

module.exports = {
  generateSeedData,
  seedMetrics,
};
