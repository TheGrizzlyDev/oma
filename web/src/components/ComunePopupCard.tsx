import { strings } from '../i18n';

type ComunePopupCardProps = {
  name: string;
  population: string;
  businesses: string;
  incentives: string;
};

const ComunePopupCard = ({ name, population, businesses, incentives }: ComunePopupCardProps) => {
  return (
    <div className="oma-popup">
      <div className="oma-popup__header">
        <span>{strings.map.popup.titlePrefix} {name}</span>
        <span aria-hidden="true">›</span>
      </div>
      <div className="oma-popup__body">
        <div className="oma-popup__row">
          <span>{strings.map.popup.population}:</span>
          <strong>{population}</strong>
        </div>
        <div className="oma-popup__row">
          <span>{strings.map.popup.businesses}:</span>
          <strong>{businesses}</strong>
        </div>
        <div className="oma-popup__row">
          <span>{strings.map.popup.incentives}:</span>
          <strong>{incentives}</strong>
        </div>
        <a className="oma-link" href="#">{strings.map.popup.detail}</a>
      </div>
    </div>
  );
};

export default ComunePopupCard;
