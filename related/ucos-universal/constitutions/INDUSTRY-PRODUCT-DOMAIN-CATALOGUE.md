# UCOS Ω∞ — Standards-Mapped Industry, Product, Service & Domain Catalogue

| Field | Value |
|---|---|
| Document ID | `UCOS-STD-CATALOGUE` |
| Version | 1.0.0 |
| Authority | Normative companion to `COVERAGE-REGISTER.md` (L1, L3, L20) |
| Purpose | Prove completeness **against international standards** instead of hand-made lists: **every ISIC Rev.4 division** (all industries), **every UN CPC v2.1 division** (all goods and services), and **every APQC PCF category and process group** (all business domains). Each is mapped to an owner: universe(s), an industry pack, or an explicit, approved out-of-scope decision. |

**How completeness is computed.** The code lists live in U08 (Appendix D). Each code has a `CoverageMapping { standard, code, owners: [universe | pack], phase, rationale }`. Lower levels (ISIC classes, CPC subclasses, APQC processes and activities) inherit their parent's mapping unless overridden. `ucos coverage --standard isic4|cpc21|apqc-pcf` reports the percentage mapped at every level, and unmapped codes are gaps (§5). **Target: 100% at every level. This document is at 100% for ISIC divisions, CPC divisions and APQC level-1/level-2.**

Universe ids are as in `COVERAGE-REGISTER.md`. Pack ids are written `family.name`. ⓡ marks regulated activity that needs licence rules (U67) and, where relevant, regulated-goods profiles (U18 App. E.2).

---

## 1. Industries — ISIC Rev.4, all 21 sections and 88 divisions

| Div | ISIC division | Pack | Key universes composed | Notes |
|---|---|---|---|---|
| **A** | **Agriculture, forestry and fishing** | | | |
| 01 | Crop and animal production, hunting | `agri.farming` | U18 (living, perishable, bulk), U91 (mandi/auctions), U82 (farm services), U92 (sensors), U100 (crop credit and insurance) | subsidies via gov pack |
| 02 | Forestry and logging | `agri.forestry` | U18 bulk commodity, U98 (certifications, carbon), U90 (timber legality), U101 | ⓡ EUDR due diligence |
| 03 | Fishing and aquaculture | `agri.fisheries` | U18 perishable/cold chain, U92, U90, U67 quotas (right-permit nature) | ⓡ catch quotas |
| **B** | **Mining and quarrying** | | | |
| 05 | Coal and lignite | `mining.extractives` | U79 (heavy equipment), U101 (EHS), U92, U98, U90, U91 (offtake) | ⓡ |
| 06 | Crude petroleum and natural gas | `energy.upstream` | same as 05, plus U100 (hedging) | ⓡ |
| 07 | Metal ores | `mining.extractives` | as 05 | ⓡ conflict minerals |
| 08 | Other mining and quarrying | `mining.extractives` | as 05 | ⓡ |
| 09 | Mining support services | `mining.services` | U82, U19, U101 | |
| **C** | **Manufacturing** (all use `mfg.core` = U47 + U108 + U101 + U45 + U34 + U79 + U92) | | | |
| 10 | Food products | `mfg.food` | + lots/FEFO, perishable, recall (U18), HACCP (U101) | ⓡ FSSAI, FDA |
| 11 | Beverages | `mfg.beverages` | + excise (U31), regulated goods (alcohol) | ⓡ |
| 12 | Tobacco products | `mfg.tobacco` | + track-and-trace, excise | ⓡ |
| 13 | Textiles | `mfg.textiles` | + U98 (chemicals, water) | |
| 14 | Wearing apparel | `mfg.apparel` | + U78 (made-to-measure) | |
| 15 | Leather and related products | `mfg.leather` | + U90 (CITES for exotic leathers) | ⓡ |
| 16 | Wood and cork products | `mfg.wood` | + U98 | |
| 17 | Paper and paper products | `mfg.paper` | + U98 EPR | |
| 18 | Printing and reproduction of media | `mfg.print` | + U78 (print-on-demand), U104 (copyright) | |
| 19 | Coke and refined petroleum | `mfg.refining` | + U101 process safety, U31 excise | ⓡ |
| 20 | Chemicals | `mfg.chemicals` | + SDS documents (U18), U90 precursors | ⓡ REACH |
| 21 | Pharmaceuticals | `mfg.pharma` | + GMP (U101), design control (U108), serialisation | ⓡ |
| 22 | Rubber and plastics | `mfg.plastics` | + U98 EPR | |
| 23 | Other non-metallic minerals | `mfg.minerals` | core | |
| 24 | Basic metals | `mfg.metals` | + bulk commodity | |
| 25 | Fabricated metal products | `mfg.fabrication` | + U78 (job shop, configure-price-quote) | |
| 26 | Computer, electronic and optical products | `mfg.electronics` | + serials (U79), e-waste (U98) | |
| 27 | Electrical equipment | `mfg.electrical` | + certifications (BIS, CE) | ⓡ |
| 28 | Machinery and equipment n.e.c. | `mfg.machinery` | + U80 (after-sales), U82 | |
| 29 | Motor vehicles | `mfg.automotive` | + IATF (U101), VIN (U79), recalls | ⓡ |
| 30 | Other transport equipment | `mfg.aerospace-marine-rail` | + AS9100, U90 dual-use | ⓡ |
| 31 | Furniture | `mfg.furniture` | + U78 (configurable) | |
| 32 | Other manufacturing (jewellery, toys, medical devices, sports goods) | `mfg.other` | + hallmarking, toy safety, med-device design control | ⓡ some |
| 33 | Repair and installation of machinery | `services.industrial-repair` | U82, U80, U79 | |
| **D** | **Electricity, gas, steam and air-conditioning supply** | | | |
| 35 | Electricity, gas, steam supply | `utilities.energy` | U92 meters, U27 (rating), U23 time-of-use pricing, U82, U98, U100 (trading) | ⓡ |
| **E** | **Water supply, sewerage, waste management and remediation** | | | |
| 36 | Water collection, treatment and supply | `utilities.water` | U92, U27, U82, U101 | ⓡ |
| 37 | Sewerage | `utilities.sewerage` | U82, U101 environmental permits | ⓡ |
| 38 | Waste collection, treatment, disposal; materials recovery | `environment.waste-recycling` | U82 (pickups, routes via U36), U79 (disposal), U98 (EPR, credits), U91 (scrap auctions) | ⓡ |
| 39 | Remediation and other waste management | `environment.remediation` | U101, U98, U108 (projects) | ⓡ |
| **F** | **Construction** | | | |
| 41 | Construction of buildings | `construction.building` | U96 (projects), U108 (design), U45 (procurement), U101 (site safety, permits to work), U89 (contracts), U105 (handover), U30 (progress billing) | ⓡ building permits |
| 42 | Civil engineering | `construction.civil` | as 41, plus U79 (plant) | ⓡ |
| 43 | Specialised construction (electrical, plumbing, finishing) | `construction.trades` | U82 (jobs), U19 (credentials), U78 (quotes) | ⓡ licensed trades |
| **G** | **Wholesale and retail trade; repair of motor vehicles** | | | |
| 45 | Motor-vehicle trade and repair | `auto.dealer-service` | U18 fitment, U79, U80, U82, U100 (vehicle finance) | ⓡ |
| 46 | Wholesale trade | `retail.b2b-distribution` | U23 contract prices, U107 (distributors), U45, U89 | |
| 47 | Retail trade | `retail.*` (D2C, marketplace, grocery, quick commerce, fashion, electronics, pharmacy ⓡ) | Phase 1 core + U25, U78, U84 | |
| **H** | **Transportation and storage** | | | |
| 49 | Land transport and pipelines | `mobility.*`, `logistics.road`, `transit.public` | U37, U36, U81 (seats), U92 (telematics) | ⓡ |
| 50 | Water transport | `logistics.maritime`, `travel.ferries` | U36, U90, U81, U79 (vessels) | ⓡ |
| 51 | Air transport | `travel.airline`, `logistics.air-cargo` | U81 seats/fares, U36, U90, U101 (aviation safety), U79 | ⓡ |
| 52 | Warehousing and transport support | `logistics.warehousing-3pl` | U34, U35, U36, U90 | |
| 53 | Postal and courier | `logistics.courier` | U35, U36, U12 | ⓡ postal |
| **I** | **Accommodation and food service** | | | |
| 55 | Accommodation | `hospitality.stays` | U13 (nightly inventory), U17, U83, U23 (rate plans), U81 | ⓡ local registration |
| 56 | Food and beverage service | `food.restaurants`, `food.delivery`, `food.catering` | U78 modifiers, U35, U37, U13, U101 (hygiene) | ⓡ licences |
| **J** | **Information and communication** | | | |
| 58 | Publishing (books, periodicals, software) | `media.publishing`, `software.saas-vendor` | U41, U27, U28, U104 (copyright), U99 (passports optional) | |
| 59 | Motion picture, video, TV, sound recording, music | `media.studio-music` | U41, U104, U107 (royalties), U81 (premieres) | |
| 60 | Programming and broadcasting | `media.broadcast-ott` | U41 (live, DRM), U27, U33 (ads) | ⓡ broadcasting |
| 61 | Telecommunications | `telecom.operator` | U27, U28, U79 (SIMs/CPE), U82 (installs), U92 | ⓡ |
| 62 | Computer programming and consultancy | `software.services`, `software.saas-vendor` | U19, U96 (timesheets), U27, U89 | |
| 63 | Information services (portals, data, hosting) | `data.providers`, `platform.portals` | U93 (data products), U28, U44 | |
| **K** | **Financial and insurance activities** | | | |
| 64 | Financial services (banking, lending, holding) | `fin.banking`, `fin.lending` | U100, U30, U99, U69, U09 KYC | ⓡ |
| 65 | Insurance, reinsurance, pensions | `fin.insurance`, `fin.pensions` | U100 (policies, claims), U80 (embedded) | ⓡ |
| 66 | Auxiliary financial (brokerage, exchanges, advisory) | `fin.brokerage`, `fin.exchange`, `fin.payments` | U100 (trading), U91, U29 | ⓡ |
| **L** | **Real estate** | | | |
| 68 | Real estate activities | `realestate.*` (sales, rentals, property management) | U18 real-property nature, U83, U89, U82, U105 | ⓡ RERA |
| **M** | **Professional, scientific and technical** | | | |
| 69 | Legal and accounting | `pro-services.legal-accounting` | U104, U19, U96, U89, U30 | ⓡ |
| 70 | Head offices; management consultancy | `pro-services.consulting`, `enterprise.hq` | U102, U103, U96 | |
| 71 | Architecture, engineering, technical testing | `pro-services.aec`, `labs.testing` | U108, U96, U101 (accreditation ISO 17025) | ⓡ |
| 72 | Scientific research and development | `labs.research` | U108 (ELN/LIMS-lite), U93, U104, U79 (instruments) | ⓡ biosafety |
| 73 | Advertising and market research | `marketing.agency`, `research.panels` | U33, U86, U97 (surveys), U85 | |
| 74 | Other professional (design, photography, translation) | `pro-services.creative` | U19, U43, U15 (translation services) | |
| 75 | Veterinary activities | `health.veterinary`, `pets.*` | U19, U13 (appointments), U18 (pharma ⓡ), U11 (animal as subject via role profile) | ⓡ |
| **N** | **Administrative and support services** | | | |
| 77 | Rental and leasing | `rental.*` | U83 | |
| 78 | Employment activities (staffing, recruitment) | `staffing.*` | U46, U18 labour-time nature, U17, U91 (bidding for gigs), U19 credentials | ⓡ labour law |
| 79 | Travel agencies, tour operators, reservations | `travel.agency-ota` | U81, U13, U100 (travel insurance), U90 | ⓡ |
| 80 | Security and investigation | `services.security` | U82 (patrols), U105, U92 (CCTV/access), U19 credentials | ⓡ |
| 81 | Services to buildings and landscaping | `services.facilities` | U82, U105, U79 | |
| 82 | Office admin and business support (call centres, BPO, events) | `services.bpo`, `events.organiser` | U39, U40, U81 | |
| **O** | **Public administration and defence** | | | |
| 84 | Public administration, defence, social security | `gov.*`, `defence.*` (restricted) | U82 (citizen service requests), U97, U89, U67, U90 (dual-use), U09 (national ID) | ⓡ; defence needs sovereign cells |
| **P** | **Education** | | | |
| 85 | Education | `education.*` (schools, higher-ed, LMS, coaching, exams) | U19, U41, U27, U97, U96, U13 (academic calendars) | ⓡ minors |
| **Q** | **Human health and social work** | | | |
| 86 | Human health | `health.*` (clinics, hospitals, telemedicine, pharmacy, labs) | U19, U13, U11 (patient role), U66 health data, FHIR via U05 | ⓡ |
| 87 | Residential care | `care.residential` | U13, U17, U82, U11 (guardian relationships), U101 | ⓡ |
| 88 | Social work without accommodation (elder care, disability, childcare) | `care.community` | U82 (visits), U19, U46, U97 | ⓡ |
| **R** | **Arts, entertainment and recreation** | | | |
| 90 | Creative, arts and entertainment | `arts.*` | U81, U41, U104, U107 (royalties) | |
| 91 | Libraries, archives, museums | `culture.institutions` | U81 (admission), U41, U43, U18 (cultural property ⓡ) | |
| 92 | Gambling and betting | `gaming.real-money`, `lottery.*` | U100-like wallets (U84), U09 (KYC, age), U69, U67 (responsible-gambling controls), U77 virtual realities | ⓡ strict licensing; geo-fencing |
| 93 | Sports, amusement and recreation | `sports.clubs-fitness`, `leisure.parks` | U27 (memberships), U13 (classes, courts), U81, U17 | |
| **S** | **Other service activities** | | | |
| 94 | Membership organisations (associations, unions, religious, political) | `nonprofit.membership`, `faith.communities` | U27, U88, U86, U29 (donations), U103 (governance) | ⓡ political finance rules |
| 95 | Repair of computers and personal goods | `services.repair` | U80, U82, U79 | |
| 96 | Other personal services (beauty, wellness, laundry, funeral, pet care) | `personal-services.*` | U13 (appointments), U19, U82, U84 (packages) | ⓡ some |
| **T** | **Households as employers; own-use production** | | | |
| 97 | Households as employers of domestic personnel | `staffing.domestic` | U46 (light payroll), U19, U09 (verification) | ⓡ domestic-work laws |
| 98 | Undifferentiated own-use production by households | **Out of scope (approved)**: non-market activity. Personal-productivity uses run on U96 and U13. | — | rationale recorded as a DecisionRecord |
| **U** | **Extraterritorial organisations** | | | |
| 99 | Extraterritorial organisations (UN, embassies, treaty bodies) | `gov.international` | U77 authorities, U12 jurisdictions, U89, U67 | sovereign or immunity considerations |

**Beyond ISIC (future and non-terrestrial):** `space.*` (orbital services, launch, satellite data, off-world operations), `metaverse.*` (virtual-world economies). Both are composed via U77 (and §Z of the Coverage Register).

---

## 2. Goods and services — UN CPC v2.1, all 10 sections and 71 divisions

| CPC div | Description | Product or service nature (U18 E.1 / U19) | Owners |
|---|---|---|---|
| **0** | **Agriculture, forestry and fishery products** | | |
| 01 | Products of agriculture, horticulture, market gardening | perishable / bulk-commodity | U18, U34, U91 |
| 02 | Live animals and animal products | living / perishable | U18, U90 |
| 03 | Forestry and logging products | bulk-commodity, environmental-credit | U18, U98 |
| 04 | Fish and other fishing products | perishable, living | U18 (cold chain) |
| **1** | **Ores and minerals; electricity, gas and water** | | |
| 11–16 | Coal, petroleum, gas, uranium/thorium ⓡ, metal ores, stone/sand/clay, other minerals | bulk-commodity | U18, U90, U91, U100 |
| 17 | Electricity, town gas, steam, hot water | energy | U92 meters, U27 |
| 18 | Natural water | water-utility | utilities pack |
| **2** | **Food, beverages, tobacco; textiles, apparel, leather** | | |
| 21–23 | Meat, fish, fruit, oils, dairy, grain mill and other food products | perishable / physical-consumable | U18, U34 (lots) |
| 24 | Beverages ⓡ (alcohol) | physical-consumable + regulated profile | U18 E.2 |
| 25 | Tobacco products ⓡ | regulated | U18 E.2 |
| 26–29 | Yarn, fabrics, textile articles, apparel, leather, footwear | physical | U18, U78 |
| **3** | **Other transportable goods** | | |
| 31 | Wood, cork, straw products | physical | U18 |
| 32 | Pulp, paper, printed matter (books, newspapers) | physical / digital-download | U18, U41 |
| 33 | Coke oven, refined petroleum, nuclear fuel ⓡ | bulk-commodity | U18, U90 |
| 34–35 | Basic chemicals ⓡ, other chemical products (pharma ⓡ, cosmetics) | physical + SDS + regulated | U18 E.2 |
| 36 | Rubber and plastics products | physical | U18, U98 |
| 37 | Glass and other non-metallic mineral products | physical | U18 |
| 38 | Furniture; other transportable goods (jewellery, instruments, toys, sports goods) | physical-durable | U18, U78 |
| 39 | Wastes and scraps | bulk-commodity (secondary materials) | U18, U91, U98 |
| **4** | **Metal products, machinery and equipment** | | |
| 41–42 | Basic metals; fabricated metal products | physical / bulk | U18, U78 |
| 43–44 | General and special-purpose machinery | physical-durable | U18, U79, U80 |
| 45 | Office, accounting and computing machinery | physical-durable | U18, U79 |
| 46–47 | Electrical machinery; radio, TV and communication equipment | physical-durable | U18, U79, U92 |
| 48 | Medical ⓡ, precision and optical instruments; watches | physical-durable + regulated | U18 E.2, U108 |
| 49 | Transport equipment (vehicles, aircraft, ships) | vehicle | U18, U79, U100 |
| **5** | **Constructions and construction services** | | |
| 53 | Constructions (buildings, civil works) | real-property | U18, U89 |
| 54 | Construction services | service (project) | U19, U82, U96, construction pack |
| **6** | **Distributive trade, accommodation, food, transport, utility distribution services** | | |
| 61–62 | Wholesale and retail trade services | service (commerce itself) | Phase 1 commerce core, U25, U107 |
| 63 | Accommodation, food and beverage services | service + experience | hospitality and food packs, U13 |
| 64 | Passenger transport services | service (transport) | U37, U81 |
| 65 | Freight transport services | service | U36 |
| 66 | Rental of transport vehicles with operators | service | U37, U83 |
| 67 | Supporting transport services (cargo handling, storage, terminals) | service | U36, U34 |
| 68 | Postal and courier services | service | U35, U36 |
| 69 | Electricity, gas and water distribution services | service (metered) | utilities packs |
| **7** | **Financial, real estate, rental and leasing services** | | |
| 71 | Financial and related services ⓡ | financial-instrument / service | U100, U29, U84 |
| 72 | Real estate services | service | realestate pack, U89 |
| 73 | Leasing or rental without operator | service | U83 |
| **8** | **Business and production services** | | |
| 81 | Research and development services | service | U108, U19 |
| 82 | Legal and accounting services | service ⓡ | U104, U19 |
| 83 | Other professional, technical and business services (consulting, architecture, advertising, research, design) | service | U19, U96, U33, U97 |
| 84 | Telecommunications, broadcasting, information supply (incl. online content, data) | service / streaming-right / data-product | U27, U41, U93 |
| 85 | Support services (employment, security, cleaning, travel arrangement, call centres) | service, labour-time | U46, U82, staffing pack |
| 86 | Support services to agriculture, mining and utilities | service | U82 |
| 87 | Maintenance, repair and installation | service | U80, U82 |
| 88 | Manufacturing services on inputs owned by others (contract manufacturing) | service | U47, U89 |
| 89 | Other manufacturing services; publishing, printing, reproduction; materials recovery | service | U47, U41, U98 |
| **9** | **Community, social and personal services** | | |
| 91 | Public administration and compulsory social security services | public service | gov pack, U82 |
| 92 | Education services | service | education pack, U19 |
| 93 | Human health and social care services ⓡ | service | health and care packs |
| 94 | Sewage, waste collection, treatment, environmental protection | service | environment pack, U98 |
| 95 | Services of membership organisations | service | nonprofit pack |
| 96 | Recreational, cultural and sporting services (incl. gambling ⓡ) | service / experience-admission | U81, sports and gaming packs |
| 97 | Other services (personal care, laundry, funeral) | service | personal-services pack |
| 98 | Domestic services | labour-time | staffing.domestic |
| 99 | Services of extraterritorial organisations | public service | gov.international |

**Digital and new-economy goods not separated in CPC v2.1** (covered explicitly): software licences and SaaS (U28, U27), data products (U93), virtual items and metaverse land (U77), tokens and NFTs (U99), carbon and environmental credits (U98), AI services and model access (U49 + U19), API access (U63 API products).

---

## 3. Business domains — APQC PCF (cross-industry v7.x), 13 categories and their process groups

> Level-2 group names follow APQC PCF v7.x wording, condensed. Exact numbering is imported with the `apqc-pcf` code list. Every level-3/4 process inherits its group's owners unless overridden.

| # | Category → process groups | Owners |
|---|---|---|
| 1 | **Develop Vision and Strategy:** define the business concept and vision; develop business strategy; execute and measure strategic initiatives; develop and manage innovation | U102, U54, U72, U108 (innovation) |
| 2 | **Develop and Manage Products and Services:** govern and manage the product/service development programme; generate and define new product/service ideas; develop products and services | U108, U18, U19, U78, U20 |
| 3 | **Market and Sell Products and Services:** understand markets, customers and capabilities; develop marketing strategy; develop sales strategy; develop and manage marketing plans; develop and manage sales plans | U85, U86, U33, U87, U88, U38, U22, U23, U24, U107, U97 |
| 4 | **Manage Supply Chain for Physical Products:** plan for and align supply-chain resources; procure materials and services; produce/manufacture/deliver product; manage logistics and warehousing | U45, U47, U34, U35, U36, U90, U94 (planning), U101 (quality) |
| 5 | **Deliver Services:** establish service delivery governance and strategies; manage service delivery resources; deliver service to customer | U19, U82, U17, U13, U96 |
| 6 | **Manage Customer Service:** develop customer care/service strategy; plan and manage customer service contacts; service products after sales; manage product recalls and regulatory audits; evaluate customer service operations and satisfaction | U39, U40, U80, U18 (recalls), U70, U97 |
| 7 | **Develop and Manage Human Capital:** develop and manage HR planning, policies and strategies; recruit, source and select; manage employee onboarding, development and counselling; manage employee relations; reward and retain; redeploy and retire; manage employee information and analytics; manage employee communication | U46, U96, U105, U106, U40, U72 |
| 8 | **Manage Information Technology:** develop and manage the IT customer relationship; develop and manage IT business strategy; develop and manage IT resilience and risk; manage enterprise information; develop and maintain IT solutions; deploy IT solutions; deliver and support IT services | U95, U73, U65, U93, U63, `itsm.*` (U82, U39), U57 |
| 9 | **Manage Financial Resources:** perform planning and management accounting; perform revenue accounting; perform general accounting and reporting; manage fixed-asset projects; process payroll; process accounts payable and expense reimbursement; manage treasury operations; manage internal controls; manage taxes; manage international funds/consolidation | U30, U102 (planning), U106, U46 (payroll), U31, U29, U100 (treasury instruments), U67 (internal controls), U79 (fixed assets) |
| 10 | **Acquire, Construct and Manage Assets:** plan and acquire assets; design and construct productive assets; maintain productive assets; dispose of assets | U79, U45, construction packs, U82, U105, U108 |
| 11 | **Manage Enterprise Risk, Compliance, Remediation and Resiliency:** manage enterprise risk; manage compliance; manage remediation efforts; manage business resiliency | U69, U67, U65, U101, U104, U73 (continuity and disaster recovery), U66 |
| 12 | **Manage External Relationships:** build investor relationships; manage government and industry relationships; manage relations with the board of directors; manage legal and ethical issues; manage public relations programmes | U103 (investors, board), U67 (regulators), U104 (legal, ethics), U86 + U88 (public relations, media; see note), U98 (community and sustainability), U107 (industry partners) |
| 13 | **Develop and Manage Business Capabilities:** manage business processes; manage portfolios, programmes and projects; manage enterprise quality; manage change; develop and manage enterprise-wide knowledge management; measure and benchmark | U60 + U02 (process), U96 (portfolio, programme, project), U101 (quality), U76 (change), U07 + U39 (knowledge), U72 + U20 (benchmarks), U93 |

**Note (A-58):** public relations (press releases, media lists, coverage tracking) is added to **U86 Marketing Automation** scope as a `pr` campaign kind, with media monitoring via U88 social listening connectors.

**Industry-specific frameworks** are mapped by their packs: BIAN (banking) → `fin.*`; TM Forum eTOM (telecom) → `telecom.*`; HL7 FHIR resources (health) → `health.*`; ISA-95 (manufacturing operations) → `mfg.*`; ACORD (insurance) → `fin.insurance`.

---

## 4. Out-of-scope register (must be explicit and approved)
| Code | Item | Decision | Rationale |
|---|---|---|---|
| ISIC 98 | Own-use household production | Out of scope | Non-market. Personal-productivity use is served by U96 and U13 without a dedicated pack. |
| — | Direct operation of nuclear facilities, weapons manufacture control systems | Out of scope for the runtime (OT safety systems); commerce and administration of those industries is in scope as restricted packs | Safety-critical control systems need certified OT platforms. UCOS integrates via U92 without controlling them. |

Every other ISIC division, CPC division and APQC group is in scope with an owner.

---

## 5. Completeness enforcement (gap rules and reports)
```prolog
coverage_owner(Std, Code, O) :- coverage_mapping(Std, Code, O).
coverage_owner(Std, Code, O) :- parent_code(Std, Code, P), coverage_owner(Std, P, O), not overridden(Std, Code).
gap(standard_code_unmapped, Std, Code)   :- standard(Std), code(Std, Code), not coverage_owner(Std, Code, _), not out_of_scope(Std, Code).
gap(owner_unspecified_for_phase, Code, U) :- coverage_owner(_, Code, U), universe(U), needed_by_phase(Code, Ph), current_phase(Ph), not specified(U).
gap(pack_missing_for_active_industry, T, Code) :- tenant(T), tenant_industry(T, Code), coverage_owner(isic4, Code, Pack), pack(Pack), not available(Pack).
gap(out_of_scope_without_decision, Code) :- out_of_scope(_, Code), not decision_record_for(Code).
```
`ucos coverage` output (CI artefact, published to the Console's Architecture menu):

```text
standard   level        codes   mapped   out-of-scope   unmapped   coverage
isic4      section         21       21          0            0       100.0%
isic4      division        88       87          1            0       100.0%
isic4      class          419      419*         4            0       100.0%   (*inherited unless overridden)
cpc21      section         10       10          0            0       100.0%
cpc21      division        71       71          0            0       100.0%
cpc21      subclass      2887     2887*         0            0       100.0%
apqc-pcf   category        13       13          0            0       100.0%
apqc-pcf   process group   ~70      ~70          0            0       100.0%
```
New standard versions (ISIC Rev.5, CPC v3, new APQC releases) arrive as U08 releases. Any new or changed codes appear immediately as `standard_code_unmapped` gaps until an owner is assigned. This is how completeness is maintained over time.
