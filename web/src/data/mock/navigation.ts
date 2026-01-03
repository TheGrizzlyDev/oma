import type { FooterLink, NavItem } from '../types';

export const navItems: NavItem[] = [
  { id: 'data', labelKey: 'nav.data' },
  { id: 'incentives', labelKey: 'nav.incentives' },
  { id: 'guide', labelKey: 'nav.guide' },
  { id: 'info', labelKey: 'nav.info' },
];

export const footerLinks: FooterLink[] = [
  { id: 'methodology', labelKey: 'footer.methodology' },
  { id: 'download', labelKey: 'footer.downloadData' },
  { id: 'provenance', labelKey: 'footer.dataProvenance' },
];
