const astroEntry = new URL("./node_modules/astro/astro.js", import.meta.url);
await import(astroEntry.href);
