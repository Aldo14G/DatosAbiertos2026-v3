"use client";

import { useEffect, useRef, useState } from "react";
import { Menu, X } from "lucide-react";
import { useLang } from "./LangProvider";

const DASHBOARD_URL =
  process.env.NEXT_PUBLIC_DASHBOARD_URL ?? "http://localhost:8501";

const NAV_LINKS = [
  { href: "hallazgos", labelEs: "Hallazgos", labelEn: "Findings" },
  { href: "dimensions", labelEs: "Dimensiones", labelEn: "Dimensions" },
  { href: "methodology", labelEs: "Metodología", labelEn: "Methodology" },
  { href: "rankings", labelEs: "Dependencias", labelEn: "Agencies" },
  { href: "credits", labelEs: "Créditos", labelEn: "Credits" },
] as const;

export function Navbar() {
  const { lang, toggle, t } = useLang();
  const [open, setOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("");
  const [scrolled, setScrolled] = useState(false);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    const ids = NAV_LINKS.map((l) => l.href);

    function update() {
      const scrollY = window.scrollY;
      setScrolled(scrollY > 12);

      const offset = 80;
      let current = "";
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= offset) {
          current = id;
        }
      }
      setActiveSection(current);
    }

    function onScroll() {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      rafRef.current = requestAnimationFrame(update);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    update();
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <header
      data-nav
      className={`fixed top-0 left-0 right-0 z-50 border-b transition-all duration-300 ${
        scrolled
          ? "border-border bg-background/95 backdrop-blur-sm shadow-sm"
          : "border-transparent bg-background/80 backdrop-blur-sm"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Logo */}
        <a
          href="#hero"
          className="flex flex-col leading-tight transition-opacity hover:opacity-80 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-2 rounded"
        >
          <span
            className="font-mono text-xs font-medium tracking-widest text-muted-foreground uppercase"
            aria-hidden="true"
          >
            LABNL · ISO/IEC 25012
          </span>
          <span className="font-serif text-base font-bold text-foreground">
            DatosAbiertos NL 2026
          </span>
        </a>

        {/* Desktop nav */}
        <nav
          className="hidden items-center gap-1 md:flex"
          aria-label={t("Navegación principal", "Main navigation")}
        >
          {NAV_LINKS.map((link) => {
            const isActive = activeSection === link.href;
            return (
              <a
                key={link.href}
                href={`#${link.href}`}
                className={`relative rounded px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-2 ${
                  isActive
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                aria-current={isActive ? "location" : undefined}
              >
                {t(link.labelEs, link.labelEn)}
                {isActive && (
                  <span
                    className="absolute inset-x-2 -bottom-[13px] h-[2px] rounded-full bg-teal"
                    aria-hidden="true"
                  />
                )}
              </a>
            );
          })}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            aria-label={t("Cambiar a inglés", "Switch to Spanish")}
            className="rounded border border-border px-2.5 py-1 font-mono text-xs font-medium text-muted-foreground transition-colors hover:border-foreground hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring cursor-pointer"
          >
            {lang === "es" ? "EN" : "ES"}
          </button>

          <a
            href={DASHBOARD_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden rounded bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-2 md:inline-flex items-center gap-1.5"
          >
            {t("Ver dashboard", "Open dashboard")}
          </a>

          <button
            onClick={() => setOpen((o) => !o)}
            aria-label={open ? t("Cerrar menú", "Close menu") : t("Abrir menú", "Open menu")}
            aria-expanded={open}
            className="rounded p-1.5 text-muted-foreground hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring cursor-pointer md:hidden"
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <nav
          className="border-t border-border bg-background px-4 pb-4 pt-3 md:hidden"
          aria-label={t("Menú móvil", "Mobile menu")}
        >
          <ul className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => {
              const isActive = activeSection === link.href;
              return (
                <li key={link.href}>
                  <a
                    href={`#${link.href}`}
                    onClick={() => setOpen(false)}
                    aria-current={isActive ? "location" : undefined}
                    className={`flex items-center gap-2 rounded px-3 py-2 text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-muted text-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    {isActive && (
                      <span className="size-1.5 rounded-full bg-teal shrink-0" aria-hidden="true" />
                    )}
                    {t(link.labelEs, link.labelEn)}
                  </a>
                </li>
              );
            })}
            <li className="mt-2 pt-2 border-t border-border">
              <a
                href={DASHBOARD_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="block rounded bg-primary px-3 py-2 text-center text-sm font-medium text-primary-foreground"
              >
                {t("Ver dashboard", "Open dashboard")}
              </a>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
}
