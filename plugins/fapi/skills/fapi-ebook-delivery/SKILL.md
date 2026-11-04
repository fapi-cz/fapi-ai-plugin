---
name: fapi-ebook-delivery
description: Připrav prodej e-booku nebo jiného elektronického souboru a jeho automatické zpřístupnění po zaplacení. Použij pro doručení PDF, materiály u produktu a kontrolu, zda je potřeba další odesílací akce.
---

# Prodej a doručení e-booku

Při onboardingu po jasném zadání názvu, ceny a měny rovnou vytvoř produkt a navázaný formulář pomocí `fapi-product-create` a `fapi-sales-form-create`. Výslovný požadavek jen na produkt respektuj. Již vyjasněný záměr nepotvrzuj znovu; doptávej se pouze na skutečně chybějící nebo rozporný údaj. E-book je obvykle `electronic-publication`, jiné digitální materiály mohou být `electronic-service` podle skutečného obsahu. Výslovně sdělený daňový režim ulož před vytvořením přes postup `fapi-billing-setup`.

## Materiál přímo u produktu

Výchozí cesta je nahrát soubor v Prodej → Produkty → úprava produktu. FAPI jej po zaplacení nestornované objednávky zpřístupní na jejím přehledu a přes odkazy v HTML e-mailu. Použij `notification_reference_show` k ověření zástupných symbolů: odkazy mohou být součástí `{items}` / `{itemsList}`, samostatný seznam materiálů poskytuje `{downloads}` / `{downloadsList}`.

Pokud materiál již doručuje e-mail po zaplacení, nepřidávej další akci pro stejné doručení. Nevyžaduj externí odkaz ani soubor připojený k e-mailové šabloně. Jiný odesílací scénář připrav pouze na výslovné zadání; při změně existujících šablon nebo akcí zachovej ostatní konfiguraci.

## Co ověřit a co zbývá ručně

Současné produktové MCP neumí nahrát ani vypsat připojené soubory. Neoznamuj úspěšný upload či otestované doručení bez důkazu. Vytvoření produktu a formuláře neblokuj chybějícím souborem; dej zákazníkovi konkrétní krok pro jeho nahrání a před prodejem ověření doručení.

Načti `item_templates_show` a `forms_show`, ověř ceny a propojení produktu a formuláře. Rovnou vrať skutečný `form.url` k prohlédnutí. Při vlastní e-mailové šabloně ověř odpovídající zástupný symbol i přiřazení sady k formuláři. Rozlišuj kontrolu konfigurace od skutečné testovací objednávky a doručení; objednávku ani platbu nevytvářej automaticky.
