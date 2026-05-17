import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <section className="page-section">
      <div className="page-heading">
        <p className="eyebrow">404</p>
        <h1>Страница не найдена</h1>
      </div>
      <Link className="text-link" to="/">
        Вернуться на главную
      </Link>
    </section>
  );
}
