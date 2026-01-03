import type { KpiItem } from '../data/types';
import { t } from '../i18n';

type KpiBarProps = {
  items: KpiItem[];
  comuneName: string;
};

const iconMap: Record<KpiItem['icon'], string> = {
  population: '👥',
  businesses: '🏭',
  incentives: '💶',
};

const KpiBar = ({ items, comuneName }: KpiBarProps) => {
  return (
    <div className="oma-kpi-bar">
      {items.map((item) => (
        <div className="oma-kpi-card" key={item.id}>
          <span className="oma-kpi-card__icon" aria-hidden="true">
            {iconMap[item.icon]}
          </span>
          <div className="oma-kpi-card__content">
            <div className="oma-kpi-card__value">{item.value}</div>
            <div className="oma-kpi-card__title">{t(item.labelKey)}</div>
            <div className="oma-kpi-card__desc">
              {t(item.descriptionKey, { comune: comuneName })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default KpiBar;
