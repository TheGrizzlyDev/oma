import { useMemo, useState } from 'react';
import type { ComuneSummary, DatasetTab } from '../data/types';
import { getDatasetTabs, getInitialSelectedComune, getKpisForComune } from '../data/provider';
import { formatEur, formatInt } from '../utils/format';
import DatasetTabs from './DatasetTabs';
import MapPanel from './MapPanel';
import ComunePopupCard from './ComunePopupCard';
import KpiBar from './KpiBar';

const Dashboard = () => {
  const tabs = useMemo(() => getDatasetTabs(), []);
  const [activeDataset, setActiveDataset] = useState<DatasetTab>(tabs[0]);
  const [selectedComune, setSelectedComune] = useState<ComuneSummary>(getInitialSelectedComune());

  const kpis = useMemo(
    () => getKpisForComune(selectedComune, activeDataset.id),
    [selectedComune, activeDataset],
  );

  const popupValues = {
    population: formatInt(selectedComune.population),
    businesses: formatInt(selectedComune.businesses),
    incentives: formatEur(selectedComune.incentivesEur),
  };

  return (
    <section className="oma-dashboard">
      <DatasetTabs
        tabs={tabs}
        activeId={activeDataset.id}
        onSelect={(tab) => setActiveDataset(tab)}
      />
      <MapPanel
        onComuneSelect={(istatCode) =>
          setSelectedComune((current) =>
            current.istatCode === istatCode ? current : current,
          )
        }
      >
        <ComunePopupCard
          name={selectedComune.name}
          population={popupValues.population}
          businesses={popupValues.businesses}
          incentives={popupValues.incentives}
        />
      </MapPanel>
      <KpiBar items={kpis} comuneName={selectedComune.name} />
    </section>
  );
};

export default Dashboard;
