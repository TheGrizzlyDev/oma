export const formatInt = (value: number): string => {
  return new Intl.NumberFormat('it-IT').format(value);
};

export const formatEur = (value: number): string => {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value);
};
