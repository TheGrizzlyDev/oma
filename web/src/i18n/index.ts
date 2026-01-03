import it from './it';

export const strings = it;
export type Strings = typeof it;

type Interpolations = Record<string, string | number>;

const getValueByPath = (path: string, source: Record<string, unknown>): unknown => {
  return path.split('.').reduce<unknown>((acc, key) => {
    if (acc && typeof acc === 'object' && key in acc) {
      return (acc as Record<string, unknown>)[key];
    }
    return undefined;
  }, source);
};

export const t = (key: string, vars?: Interpolations): string => {
  const value = getValueByPath(key, strings as Record<string, unknown>);
  if (typeof value !== 'string') {
    return key;
  }
  if (!vars) {
    return value;
  }
  return Object.entries(vars).reduce((acc, [varKey, varValue]) => {
    return acc.replaceAll(`{${varKey}}`, String(varValue));
  }, value);
};
