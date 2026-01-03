import type { SidebarAction } from '../types';

export const sidebarActions: SidebarAction[] = [
  {
    id: 'start-business',
    titleKey: 'sidebar.actions.startBusiness.title',
    descriptionKey: 'sidebar.actions.startBusiness.description',
    icon: 'pin',
  },
  {
    id: 'incentives',
    titleKey: 'sidebar.actions.incentives.title',
    descriptionKey: 'sidebar.actions.incentives.description',
    icon: 'euro',
  },
  {
    id: 'services',
    titleKey: 'sidebar.actions.services.title',
    descriptionKey: 'sidebar.actions.services.description',
    icon: 'factory',
  },
  {
    id: 'download',
    titleKey: 'sidebar.actions.download.title',
    descriptionKey: 'sidebar.actions.download.description',
    icon: 'download',
  },
];
