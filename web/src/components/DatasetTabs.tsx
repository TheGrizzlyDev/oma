import type { DatasetTab } from '../data/types';
import { t } from '../i18n';

const iconMap: Record<DatasetTab['icon'], string> = {
  population: '👥',
  businesses: '🏢',
  incentives: '💶',
};

type DatasetTabsProps = {
  tabs: DatasetTab[];
  activeId: string;
  onSelect: (tab: DatasetTab) => void;
};

const DatasetTabs = ({ tabs, activeId, onSelect }: DatasetTabsProps) => {
  return (
    <div className="oma-tabs" role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={tab.id === activeId}
          className={`oma-tab ${tab.id === activeId ? 'oma-tab--active' : ''}`}
          onClick={() => onSelect(tab)}
        >
          <span className="oma-tab__icon" aria-hidden="true">
            {iconMap[tab.icon]}
          </span>
          <span>{t(tab.labelKey)}</span>
        </button>
      ))}
    </div>
  );
};

export default DatasetTabs;
