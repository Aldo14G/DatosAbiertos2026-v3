"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";
import { useLang } from "./LangProvider";

const DASHBOARD_URL = "https://catalogodatos.nl.gob.mx";

export function Navbar() {
  const { lang, toggle, t } = useLang();
  const [open, setOpen] = useState(false);

  const navLinks = [
    { href: "#dimensions", label: t("Dimensiones", "Dimensions") },
    { href: "#rankings", label: t("Dependencias", "Agencies") },
    { href: "#methodology", label: t("Metodología", "Methodology") },
    { href: "#credits", label: t("Créditos", "Credits") },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
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
        <nav className="hidden items-center gap-6 md:flex" aria-label={t("Navegación principal", "Main navigation")}>
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-2 rounded"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Language toggle */}
          <button
            onClick={toggle}
            aria-label={t("Cambiar a inglés", "Switch to Spanish")}
            className="rounded border border-border px-2.5 py-1 font-mono text-xs font-medium text-muted-foreground transition-colors hover:border-foreground hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring cursor-pointer"
          >
            {lang === "es" ? "EN" : "ES"}
          </button>

          {/* CTA — desktop only */}
          <a
            href={DASHBOARD_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden rounded bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-2 md:inline-flex items-center gap-1.5"
          >
            {t("Ver dashboard", "Open dashboard")}
          </a>

          {/* Mobile hamburger */}
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
            {navLinks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block rounded px-2 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  {link.label}
                </a>
              </li>
            ))}
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
