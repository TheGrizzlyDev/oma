import type { ReactNode } from 'react';
import { strings } from '../i18n';

type MapPanelProps = {
  children?: ReactNode;
  onComuneSelect?: (istatCode: string) => void;
};

const MapPanel = ({ children, onComuneSelect }: MapPanelProps) => {
  return (
    <div className="oma-map-panel">
      <div className="oma-map-panel__controls">
        <button type="button" className="oma-chip">
          {strings.map.controls.filters}
        </button>
        <button type="button" className="oma-chip">
          {strings.map.controls.layers}
        </button>
        <button type="button" className="oma-chip">
          {strings.map.controls.legend}
        </button>
      </div>
      <div
        id="oma-map"
        className="oma-map-panel__canvas"
        aria-label={strings.map.ariaLabel}
        role="region"
        onClick={() => onComuneSelect?.('066006')}
      />
      {children}
    </div>
  );
};

export default MapPanel;
