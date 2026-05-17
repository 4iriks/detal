export default function HomePage() {
  return (
    <section className="page-section">
      <div className="page-heading">
        <p className="eyebrow">Курсовая работа</p>
        <h1>Главная</h1>
      </div>
      <p className="lead">
        Информационная система для учета деталей на складе предприятия.
      </p>
      <div className="summary-grid">
        <div className="summary-item">
          <span>Детали</span>
          <strong>Номенклатура и остатки</strong>
        </div>
        <div className="summary-item">
          <span>Категории</span>
          <strong>Группировка деталей</strong>
        </div>
        <div className="summary-item">
          <span>Поставщики</span>
          <strong>Контакты и поставки</strong>
        </div>
        <div className="summary-item">
          <span>Склады</span>
          <strong>Места хранения</strong>
        </div>
      </div>
    </section>
  );
}
