export type DatasetTab = {
  id: string;
  labelKey: string;
  icon: 'population' | 'businesses' | 'incentives';
};

export type ComuneSummary = {
  istatCode: string;
  name: string;
  population: number;
  businesses: number;
  incentivesEur: number;
};

export type KpiItem = {
  id: string;
  labelKey: string;
  descriptionKey: string;
  value: string;
  icon: 'population' | 'businesses' | 'incentives';
};

export type SidebarAction = {
  id: string;
  titleKey: string;
  descriptionKey: string;
  icon: 'pin' | 'euro' | 'factory' | 'download';
};

export type NavItem = {
  id: string;
  labelKey: string;
};

export type FooterLink = {
  id: string;
  labelKey: string;
};
