import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Главная", end: true },
  { to: "/details", label: "Детали" },
  { to: "/categories", label: "Категории" },
  { to: "/suppliers", label: "Поставщики" },
  { to: "/warehouses", label: "Склады" },
];

export default function Navigation() {
  return (
    <nav className="navigation" aria-label="Основная навигация">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) =>
            isActive ? "navigation-link active" : "navigation-link"
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
