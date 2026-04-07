import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>OpenNemesis Chat</title>
      </head>
      <body className="m-0 font-[ui-sans-serif,system-ui]">
        {children}
      </body>
    </html>
  );
}
