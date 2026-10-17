# International readiness

What stands between LUXORA and selling in many countries, in the order to fix it. Each item says
what is true today, what "done" means, and how to verify it. Like the hard-coding audit, every
vocabulary a fix introduces is data (a seed file or a registry row), never a literal in code.

| # | Item | Status |
|---|---|---|
| 1 | Country and currency master | **Done** |
| 2 | Tax rules for every country | Open |
| 3 | Subdivisions for every country | Open |
| 4 | Address formats per country | Open |
| 5 | Money rounds to the currency's minor units | Open |
| 6 | Interface translation | Open |
| 7 | Right-to-left layout | Open |
| 8 | Time zones | Open |
| 9 | Payment and shipping coverage per country | Open |
| 10 | Data residency and regional deployment | Open |
| 11 | Country-specific legal requirements | Open |
| 12 | Clean the development database | Needs the owner's go-ahead |

## 1. Country and currency master (done)

**Before.** The country seed was a JavaScript literal of 13 countries. Providers named three
more (`SE`, `SA`, `CN`), and boot invented them: name "SE (auto-registered)", currency `SE`,
locale `en-SE`, which also created currencies called `SE`, `SA` and `CN` with a rate of 1.
Nothing checked a country or currency on the way in, so codes such as `XX` with currency `BAD`
could be saved. A country's decimals were `2` unless its currency was literally `"JPY"`.
The storefront was served disabled countries. The global country and currency endpoints were
broken: creating called a `newUid()` that does not exist, and every edit (including provider
and plan edits) stamped an `updated_at` column the tables do not have.

**Now.**
- `lib/seed/providers.json` `COUNTRIES` declares 49 countries (code, name, currency, symbol,
  locale) and `CURRENCIES` 40 currencies with their ISO 4217 minor units. A country's
  decimals are its currency's (JPY 0, KWD 3).
- A provider is linked only to declared countries; nothing is invented.
- Existing installs are repaired on boot: an auto-registered row takes the seed's geography
  and the invented currency is removed once nothing uses it. A row an operator renamed is
  never touched.
- A country the seed gains reaches an existing install once, **inactive**, with its currency
  inactive, so shoppers see nothing new until an operator switches it on. A country the
  operator deleted is not added back.
- Field declarations on the `country` and `currency` entities check every write, from Data
  Studio and the global API alike: `pattern` (ISO 3166-1 alpha-2, ISO 4217), `format: locale`
  (BCP 47) and bounds (`min`, `max`, `gt`). A country naming a currency nobody has still
  creates that currency and its FX row, as before; an operator then sets its rate.
- The storefront is served active countries only. Editing a country or currency needs the
  `geo` write permission, as creating one does.

**Verified by** `test/geo.js` (29 checks), in `npm test`.

## 2. Tax rules for every country

**Today.** `lib/seed/tax.json` has one rule for each of the original 13 countries. The 36
countries added in item 1 have none. A rule is one rate per country: US sales tax by state,
Canadian GST/HST/PST by province and similar regional taxes are not modelled, and there is no
tax-service provider (Avalara, TaxJar, Stripe Tax).

**Done when** every active country has a rule, rules can be scoped to a subdivision (the most
specific wins), and a tax provider can be declared like any other provider spec.
**Verify** with a test that quotes a cart in each active country, and for a US state and a
Canadian province.

## 3. Subdivisions for every country

**Today.** Subdivisions (states, provinces, prefectures) are seeded for the original 13
countries only. Address forms and regional rules for the new countries have nothing to pick.

**Done when** each declared country has its ISO 3166-2 subdivisions as seed data.

## 4. Address formats per country

**Today.** An address is always `address, city, state, zip, country`. Many countries order
fields differently, have no postcode, or need a district or building line (Japan, the UK,
Gulf countries, India's PIN plus landmark). Postcodes are not validated.

**Done when** a country row declares its address fields, their order, which are required and
the postcode pattern, and the checkout and console forms render from that declaration.

## 5. Money rounds to the currency's minor units

**Today.** Prices are converted with the currency's decimals (`money2`), but `lib/api.js`
still rounds 18 amounts with `toFixed(2)`, and the storefront's fallback formatter does too.
JPY (0) and KWD (3) amounts can round wrongly.

**Done when** every amount rounds with its currency's decimals, gated by a test.

## 6. Interface translation

**Today.** Product content can be localized (the `localization` entity), but the storefront
and consoles are English text in code, and every page is `<html lang="en">`.

**Done when** interface strings are message catalogues (data, per locale), the locale comes
from the shopper's choice, the store's default and `Accept-Language` in that order, and pages
set `lang` from it.

## 7. Right-to-left layout

**Today.** Nothing sets `dir="rtl"`. Arabic and Hebrew locales are now in the seed
(`ar-AE`, `ar-SA`, `ar-EG`, `ar-QA`, `ar-KW`, `he-IL`).

**Done when** the locale's direction (from `Intl.Locale` text info, or a declared flag)
sets `dir`, and the CSS uses logical properties. Verify in the browser check with an RTL store.

## 8. Time zones

**Today.** Times are stored and shown in UTC; a store has no time zone. Delivery promises,
cut-off times, scheduled offers and reports all assume one clock.

**Done when** a store (and each warehouse) declares an IANA time zone, and dates are shown
and scheduled in it.

## 9. Payment and shipping coverage per country

**Today.** Providers are linked to countries, but most of the 36 new countries only get the
global providers (Stripe, PayPal, DHL and the in-house carriers). Local methods (iDEAL is
there; Swish, BLIK, KakaoPay, GrabPay, Mada and others are not) and local carriers are
missing. Stripe and EasyPost themselves do not serve every country.

**Done when** each active country has at least one working payment method and carrier,
checked with real sandbox keys.

## 10. Data residency and regional deployment

**Today.** One server, one database. Some countries require personal data to stay in the
country or region (for example EU GDPR transfer rules, India's DPDP Act).

**Done when** a store can be placed in a region and its data stays there, and the platform
runs in more than one region.

## 11. Country-specific legal requirements

**Today.** There is a compliance module (consent, data-subject requests), but nothing
per country: tax-inclusive price display (EU, UK, AU), e-invoicing (India GST e-invoice,
EU), invoice numbering rules, cookie-consent rules and consumer-law return windows.

**Done when** each requirement is a rule scoped by country through the applicability-rules
engine, with the console showing which apply to a store.

## 12. Clean the development database

`data/luxora.db` holds test rows typed in by hand: `XX` and `XY` (currency `BAD`),
`ZA` "Zamunda" (currency `ZMD`; ZA is South Africa, ZAR), `ZN` "Zephyria Prime", and
`AQ` "Antarctica" (currency `ADC`). Item 1 stops new ones being saved but does not delete
existing rows an operator could own. They should be removed, and ZA restored from the seed,
once the owner agrees.
