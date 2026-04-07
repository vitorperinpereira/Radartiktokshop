export function formatNumber(n) {
  if (n === null || n === undefined) return '';
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  return n.toString();
}

export function formatCurrency(n) {
  if (n === null || n === undefined) return '';
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(n);
}

export function formatScore(n) {
  if (n === null || n === undefined) return '0.0';
  return Number(n).toFixed(1);
}

export function formatDate(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  const formatter = new Intl.DateTimeFormat('pt-BR', { month: 'short', day: 'numeric', year: 'numeric' });
  return formatter.format(d).toLowerCase().replace(' de ', ' ');
}

export function formatDaysAgo(days) {
  if (days === null || days === undefined) return '';
  if (days === 0) return "Hoje";
  if (days === 1) return "1 dia atrás";
  return `${days} dias atrás`;
}
