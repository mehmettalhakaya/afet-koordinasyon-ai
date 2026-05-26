import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Panel" },
  { to: "/harita", label: "Harita" },
  { to: "/cagrilar", label: "Çağrılar" },
  { to: "/yeni", label: "Yeni Çağrı" },
  { to: "/analiz", label: "Analiz" },
];

export default function Layout() {
  return (
    <div className="app">
      <nav className="topnav">
        <div className="topnav-inner">
          <NavLink to="/dashboard" className="nav-logo" aria-label="mtk afetkoordinasyon AI">
            mtk
            <span className="logo-product">
              afetkoordinasyon<em lang="en">AI</em>
            </span>
          </NavLink>
          <div className="nav-links">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  "nav-link" + (isActive ? " active" : "")
                }
              >
                {l.label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>
      <main className="main">
        <div className="disclaimer">
          <strong>DEMO:</strong> Bu uygulama gerçek acil durum sistemi değildir.
          Eğitim ve araştırma amaçlıdır. Acil durumda <strong>112</strong>'yi
          arayın, <strong>AFAD</strong> ve <strong>Kızılay</strong>'ı takip
          edin.
        </div>
        <Outlet />
      </main>
      <footer className="site-footer">
        <span>
          mtk · AfetKoordinasyon<span lang="en">AI</span> v0.2 — demo / portföy
        </span>
        <a href="https://mtkaya.me" target="_blank" rel="noopener noreferrer">
          mtkaya.me →
        </a>
      </footer>
    </div>
  );
}
