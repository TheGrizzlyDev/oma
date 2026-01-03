import type { ComuneSummary, DatasetTab, KpiItem, NavItem, SidebarAction, FooterLink } from './types';
import { datasetTabs } from './mock/datasets';
import { comuneAvezzano } from './mock/comune';
import { sidebarActions } from './mock/sidebar';
import { navItems, footerLinks } from './mock/navigation';
import { formatEur, formatInt } from '../utils/format';

export const getDatasetTabs = (): DatasetTab[] => datasetTabs;

export const getInitialSelectedComune = (): ComuneSummary => comuneAvezzano;

export const getKpisForComune = (
  comune: ComuneSummary,
  _datasetId: string,
): KpiItem[] => [
  {
    id: 'population',
    labelKey: 'kpis.population.title',
    descriptionKey: 'kpis.population.description',
    value: formatInt(comune.population),
    icon: 'population',
  },
  {
    id: 'businesses',
    labelKey: 'kpis.businesses.title',
    descriptionKey: 'kpis.businesses.description',
    value: formatInt(comune.businesses),
    icon: 'businesses',
  },
  {
    id: 'incentives',
    labelKey: 'kpis.incentives.title',
    descriptionKey: 'kpis.incentives.description',
    value: formatEur(comune.incentivesEur),
    icon: 'incentives',
  },
];

export const getSidebarActions = (): SidebarAction[] => sidebarActions;

export const getNavItems = (): NavItem[] => navItems;

export const getFooterLinks = (): FooterLink[] => footerLinks;
