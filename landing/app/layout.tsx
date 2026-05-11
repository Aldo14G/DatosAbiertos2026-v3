import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DatosAbiertos NL 2026 — Calidad de Datos del Gobierno de Nuevo León",
  description:
    "Evaluación independiente de calidad de datos abiertos del Portal de Datos del Gobierno de Nuevo León, bajo estándares ISO/IEC 25012. Proyecto de LABNL.",
  keywords: [
    "datos abiertos",
    "Nuevo León",
    "calidad de datos",
    "ISO 25012",
    "transparencia",
    "gobierno abierto",
    "LABNL",
    "open data",
    "Mexico",
    "Monterrey",
    "gobierno digital",
  ],
  authors: [{ name: "LABNL — Laboratorio para la Ciudad de Nuevo León" }],
  openGraph: {
    type: "website",
    locale: "es_MX",
    alternateLocale: "en_US",
    title: "DatosAbiertos NL 2026 — Calidad de Datos Abiertos",
    description:
      "290 datasets evaluados bajo ISO/IEC 25012. 65% alcanzan Gold. Proyecto de LABNL — Laboratorio para la Ciudad de Nuevo León.",
    siteName: "DatosAbiertos NL 2026",
  },
  twitter: {
    card: "summary_large_image",
    title: "DatosAbiertos NL 2026 — Calidad de Datos Abiertos",
    description:
      "290 datasets del gobierno de Nuevo León evaluados bajo estándares ISO/IEC 25012. Un proyecto de LABNL.",
  },
  icons: {
    icon: "/cerebro.png",
    shortcut: "/cerebro.png",
    apple: "/cerebro.png",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="scroll-smooth">
      <head>
        <link rel="icon" href="/cerebro.png" type="image/png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body className="antialiased min-h-screen bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
