/**
 * Quality Metrics Collector
 *
 * Persists and aggregates CLI quality-gate metrics in .aiox/data.
 *
 * @module quality/metrics-collector
 * @version 1.0.0
 * @story 3.11a - Quality Gates Metrics Collector
 */

const fs = require('fs').promises;
const path = require('path');

const DEFAULT_RETENTION_DAYS = 30;

function toPositiveInteger(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

function createEmptyLayerMetrics(layerNumber) {
  const base = {
    totalRuns: 0,
    passRate: 0,
    avgTimeMs: 0,
    findingsCount: 0,
    lastRun: null,
  };

  if (layerNumber !== 2) {
    return base;
  }

  return {
    ...base,
    autoCatchRate: 0,
    coderabbit: {
      active: false,
      findingsCount: 0,
      severityBreakdown: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
    },
    quinn: {
      findingsCount: 0,
      topCategories: [],
    },
  };
}

function createEmptyMetrics(retentionDays = DEFAULT_RETENTION_DAYS) {
  return {
    lastUpdated: null,
    retentionDays,
    history: [],
    layers: {
      layer1: createEmptyLayerMetrics(1),
      layer2: createEmptyLayerMetrics(2),
      layer3: createEmptyLayerMetrics(3),
    },
    trends: {
      passRates: [],
      autoCatchRate: [],
    },
  };
}

class MetricsCollector {
  constructor(options = {}) {
    this.projectRoot = options.projectRoot || process.cwd();
    this.retentionDays = toPositiveInteger(options.retentionDays, DEFAULT_RETENTION_DAYS);
    this.dataPath = options.dataPath || path.join(this.projectRoot, '.aiox', 'data', 'quality-metrics.json');
  }

  async getMetrics() {
    const rawMetrics = await this.readMetricsFile();
    const metrics = this.recomputeMetrics(rawMetrics.history || [], rawMetrics.retentionDays || this.retentionDays);
    await this.saveMetrics(metrics);
    return metrics;
  }

  async recordRun(layer, result = {}) {
    const layerNumber = Number.parseInt(layer, 10);
    if (![1, 2, 3].includes(layerNumber)) {
      throw new Error(`Invalid layer "${layer}". Expected 1, 2, or 3.`);
    }

    const metrics = await this.getMetrics();
    const run = this.normalizeRun(layerNumber, result);
    metrics.history.push(run);

    const recomputed = this.recomputeMetrics(metrics.history, metrics.retentionDays);
    await this.saveMetrics(recomputed);

    return run;
  }

  async recordPRReview(result = {}) {
    return this.recordRun(2, result);
  }

  async cleanup() {
    const metrics = await this.getMetrics();
    const cutoff = Date.now() - metrics.retentionDays * 24 * 60 * 60 * 1000;
    const filteredHistory = metrics.history.filter((run) => new Date(run.timestamp).getTime() > cutoff);
    const removedCount = metrics.history.length - filteredHistory.length;

    const recomputed = this.recomputeMetrics(filteredHistory, metrics.retentionDays);
    await this.saveMetrics(recomputed);

    return removedCount;
  }

  async export(format = 'json') {
    const metrics = await this.getMetrics();

    if (format === 'csv') {
      return this.toCsv(metrics.history);
    }

    return JSON.stringify(metrics, null, 2);
  }

  recomputeMetrics(history = [], retentionDays = this.retentionDays) {
    const metrics = createEmptyMetrics(toPositiveInteger(retentionDays, this.retentionDays));
    const normalizedHistory = history
      .map((run) => this.normalizeStoredRun(run))
      .sort((left, right) => new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime());

    metrics.history = normalizedHistory;
    metrics.lastUpdated = new Date().toISOString();

    for (const layerNumber of [1, 2, 3]) {
      const layerRuns = normalizedHistory.filter((run) => run.layer === layerNumber);
      metrics.layers[`layer${layerNumber}`] = this.buildLayerMetrics(layerNumber, layerRuns);
    }

    metrics.trends = this.buildTrends(normalizedHistory);
    return metrics;
  }

  async saveMetrics(metrics) {
    await fs.mkdir(path.dirname(this.dataPath), { recursive: true });
    await fs.writeFile(this.dataPath, JSON.stringify(metrics, null, 2), 'utf8');
    return metrics;
  }

  async readMetricsFile() {
    try {
      const content = await fs.readFile(this.dataPath, 'utf8');
      const parsed = JSON.parse(content);
      if (!parsed || typeof parsed !== 'object') {
        return createEmptyMetrics(this.retentionDays);
      }
      return parsed;
    } catch (error) {
      if (error.code === 'ENOENT') {
        return createEmptyMetrics(this.retentionDays);
      }
      throw error;
    }
  }

  normalizeRun(layer, result = {}) {
    return {
      timestamp: new Date().toISOString(),
      layer,
      passed: Boolean(result.passed),
      durationMs: Math.max(0, Number.parseInt(result.durationMs, 10) || 0),
      findingsCount: Math.max(0, Number.parseInt(result.findingsCount, 10) || 0),
      metadata: result.metadata && typeof result.metadata === 'object' ? result.metadata : {},
      coderabbit: result.coderabbit || null,
      quinn: result.quinn || null,
    };
  }

  normalizeStoredRun(run = {}) {
    const timestamp = run.timestamp && !Number.isNaN(new Date(run.timestamp).getTime())
      ? run.timestamp
      : new Date().toISOString();

    return {
      timestamp,
      layer: Number.parseInt(run.layer, 10) || 1,
      passed: Boolean(run.passed),
      durationMs: Math.max(0, Number.parseInt(run.durationMs, 10) || 0),
      findingsCount: Math.max(0, Number.parseInt(run.findingsCount, 10) || 0),
      metadata: run.metadata && typeof run.metadata === 'object' ? run.metadata : {},
      coderabbit: run.coderabbit || null,
      quinn: run.quinn || null,
    };
  }

  buildLayerMetrics(layerNumber, layerRuns) {
    const metrics = createEmptyLayerMetrics(layerNumber);

    if (layerRuns.length === 0) {
      return metrics;
    }

    const passedRuns = layerRuns.filter((run) => run.passed).length;
    const totalDuration = layerRuns.reduce((sum, run) => sum + run.durationMs, 0);
    const totalFindings = layerRuns.reduce((sum, run) => sum + run.findingsCount, 0);

    metrics.totalRuns = layerRuns.length;
    metrics.passRate = passedRuns / layerRuns.length;
    metrics.avgTimeMs = Math.round(totalDuration / layerRuns.length);
    metrics.findingsCount = totalFindings;
    metrics.lastRun = layerRuns[layerRuns.length - 1].timestamp;

    if (layerNumber !== 2) {
      return metrics;
    }

    const autoCaughtRuns = layerRuns.filter((run) => {
      const codeRabbitFindings = run.coderabbit?.findingsCount || 0;
      const quinnFindings = run.quinn?.findingsCount || 0;
      return codeRabbitFindings + quinnFindings > 0 || run.findingsCount > 0;
    }).length;

    metrics.autoCatchRate = autoCaughtRuns / layerRuns.length;
    metrics.coderabbit = this.buildCodeRabbitMetrics(layerRuns);
    metrics.quinn = this.buildQuinnMetrics(layerRuns);

    return metrics;
  }

  buildCodeRabbitMetrics(layerRuns) {
    const summary = {
      active: false,
      findingsCount: 0,
      severityBreakdown: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
    };

    for (const run of layerRuns) {
      if (!run.coderabbit) {
        continue;
      }

      summary.active = true;
      summary.findingsCount += Number.parseInt(run.coderabbit.findingsCount, 10) || 0;

      const severityBreakdown = run.coderabbit.severityBreakdown || {};
      for (const severity of ['critical', 'high', 'medium', 'low']) {
        summary.severityBreakdown[severity] += Number.parseInt(severityBreakdown[severity], 10) || 0;
      }
    }

    return summary;
  }

  buildQuinnMetrics(layerRuns) {
    const categoryCounts = new Map();
    let findingsCount = 0;

    for (const run of layerRuns) {
      if (!run.quinn) {
        continue;
      }

      findingsCount += Number.parseInt(run.quinn.findingsCount, 10) || 0;
      const categories = Array.isArray(run.quinn.topCategories) ? run.quinn.topCategories : [];
      for (const category of categories) {
        categoryCounts.set(category, (categoryCounts.get(category) || 0) + 1);
      }
    }

    const topCategories = [...categoryCounts.entries()]
      .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
      .slice(0, 5)
      .map(([category]) => category);

    return {
      findingsCount,
      topCategories,
    };
  }

  buildTrends(history) {
    const dailyPassRate = new Map();
    const dailyAutoCatch = new Map();

    for (const run of history) {
      const date = run.timestamp.slice(0, 10);

      const passBucket = dailyPassRate.get(date) || { total: 0, passed: 0 };
      passBucket.total += 1;
      passBucket.passed += run.passed ? 1 : 0;
      dailyPassRate.set(date, passBucket);

      if (run.layer === 2) {
        const autoCatchBucket = dailyAutoCatch.get(date) || { total: 0, autoCaught: 0 };
        autoCatchBucket.total += 1;
        const codeRabbitFindings = run.coderabbit?.findingsCount || 0;
        const quinnFindings = run.quinn?.findingsCount || 0;
        if (codeRabbitFindings + quinnFindings > 0 || run.findingsCount > 0) {
          autoCatchBucket.autoCaught += 1;
        }
        dailyAutoCatch.set(date, autoCatchBucket);
      }
    }

    return {
      passRates: [...dailyPassRate.entries()]
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([date, values]) => ({
          date,
          value: values.total === 0 ? 0 : values.passed / values.total,
        })),
      autoCatchRate: [...dailyAutoCatch.entries()]
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([date, values]) => ({
          date,
          value: values.total === 0 ? 0 : values.autoCaught / values.total,
        })),
    };
  }

  toCsv(history) {
    const header = [
      'timestamp',
      'layer',
      'passed',
      'durationMs',
      'findingsCount',
      'coderabbitFindings',
      'quinnFindings',
    ];

    const rows = history.map((run) => [
      run.timestamp,
      run.layer,
      run.passed,
      run.durationMs,
      run.findingsCount,
      run.coderabbit?.findingsCount || 0,
      run.quinn?.findingsCount || 0,
    ]);

    return [header, ...rows]
      .map((row) => row.map((value) => JSON.stringify(value)).join(','))
      .join('\n');
  }
}

module.exports = {
  DEFAULT_RETENTION_DAYS,
  MetricsCollector,
  createEmptyMetrics,
};
