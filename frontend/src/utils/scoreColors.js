export function getLabelColor(label) {
  switch (label) {
    case 'EXPLOSIVE': return '#00C853';
    case 'HIGH': return '#64DD17';
    case 'WORTH_TEST': return '#FFD600';
    case 'NICHE': return '#FF6D00';
    case 'LOW': return '#757575';
    default: return '#757575';
  }
}

export function getScoreGradient(score) {
  const numScore = Number(score) || 0;
  if (numScore >= 80) return 'linear-gradient(90deg, #00C853, #64DD17)';
  if (numScore >= 60) return 'linear-gradient(90deg, #FFD600, #FF6D00)';
  return 'linear-gradient(90deg, #757575, #9E9E9E)';
}

export function getAccelerationIcon(acceleration_bonus) {
  const bonus = Number(acceleration_bonus) || 1.0;
  if (bonus > 1.3) return '🚀';
  if (bonus > 1.1) return '📈';
  if (bonus === 1.0) return '➡️';
  return '📉';
}

export function getClassificationColor(classification) {
  switch (classification) {
    case 'EXPLOSIVE': return '#FF0050';
    case 'HIGH': return '#00C853';
    case 'WORTH_TEST': return '#FFD600';
    case 'NICHE': return '#FF6D00';
    case 'LOW': return '#757575';
    default: return '#9E9E9E';
  }
}

export function getClassificationLabel(classification) {
  switch (classification) {
    case 'EXPLOSIVE': return 'Explosivo';
    case 'HIGH': return 'Alto Potencial';
    case 'WORTH_TEST': return 'Vale Testar';
    case 'NICHE': return 'Nicho';
    case 'LOW': return 'Baixo';
    default: return classification || 'N/A';
  }
}

export function getRiskFlagIcon(flag) {
  switch (flag) {
    case 'high_saturation': return 'warning';
    case 'weak_evidence': return 'help_outline';
    case 'price_volatility': return 'currency_exchange';
    case 'low_creator_count': return 'person_off';
    case 'declining_trend': return 'trending_down';
    case 'short_history': return 'schedule';
    default: return 'flag';
  }
}
