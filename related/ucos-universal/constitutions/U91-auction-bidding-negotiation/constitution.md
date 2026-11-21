# U91 — Auction, Bidding & Negotiation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U91-auction` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:commerce-price-discovery` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 (forward auctions, best-offer, B2B RFQ/tenders), P6 (reverse auctions, agent-to-agent negotiation) |
| Depends on | U13 Temporal (auction windows, soft-close extensions), U21 Catalog, U23 Pricing (reserve/ceiling), U29 Payment (bid deposits/holds), U09 Identity (bidder verification), U69 Risk (shill bidding), U51 Agents (negotiation agents), U89 Contract (award → agreement), U45 Procurement |
| Depended on by | marketplaces (eBay-like), B2B procurement (tenders), ad auctions? (no — ad auctions are U33 real-time), energy/commodity exchanges (packs), U25 Marketplace |
| Master references | Master Commerce models "Auction, Tender, Negotiated Pricing, Autonomous Bidding" (A-36) |

> Auction owns **price discovery by competition or negotiation**: forward auctions (English, Dutch, sealed-bid first/second price, buy-it-now), best-offer/counter-offer, reverse auctions and tenders/RFQ/RFP (sourcing), bid rules and increments, reserve prices, proxy bidding, soft-close, award and settlement handoff, and structured negotiations (human↔human, human↔agent, agent↔agent within delegated bounds).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| AUC-L1 | Bids are binding, timestamped by the server (Temporal), immutable and ordered deterministically. | Append-only bid log; server time only. |
| AUC-L2 | Auction rules (format, increments, reserve, soft-close, visibility) are fixed at start; changes void and restart. | Rule snapshot on open. |
| AUC-L3 | Sealed bids are encrypted until close; nobody (incl. operators) sees them early. | Envelope encryption with time-locked release (key released at close by service). |
| AUC-L4 | Agent negotiation operates within a signed mandate (limits, walk-away, concessions) and every offer is attributable. | Delegation (U09) + mandate object + audit. |

## 2. Objects
`Auction { id, kind: english|dutch|sealed-first|sealed-second|reverse|tender, item(s), window: TemporalPolicy, softClose: {extension Duration, trigger window}, increments (decision), reserve (sealed), startPrice, buyNow?, eligibility (verified bidders/deposit), visibility, status }` · `Bid { auction, bidder, amount: Money, proxyMax?, at (server), status }` · `RFQ/Tender { buyer, specs, documents, questions/clarifications, evaluation criteria (weighted), deadline: TimePoint, bidders invited/open, status }` · `Proposal { tender, supplier, price lines, technical response, score }` · `Negotiation { parties, subject, mandateRefs, offers: [{from, terms, at: TimePoint}], status: open|agreed|failed }` · `Mandate { principal, agent, limits (price/qty/terms), concessions strategy, expiry: TimePoint }` · `Award { auction|tender, winner(s), price, → order/contract }`.

## 3. Commands, Queries, Events, APIs
Commands: `CreateAuction`, `OpenAuction`, `PlaceBid`, `RetractBid` (rules-limited), `CloseAuction` (Temporal), `Award`, `IssueRFQ`, `SubmitProposal`, `EvaluateProposals`, `StartNegotiation`, `MakeOffer`, `AcceptOffer`.
Events: `auction.bid.placed|outbid`, `auction.closed|awarded`, `tender.proposal.submitted|awarded`, `negotiation.offer.made|agreed`.
```text
POST /v1/auction/auctions   POST /v1/auction/auctions/{id}/bids   GET /v1/auction/auctions/{id}/live (stream)
POST /v1/auction/rfqs       POST /v1/auction/negotiations/{id}/offers
```

## 4. Gaps & AI & Ops & UI & Scale
```prolog
gap(auction_without_bidder_verification, A) :- auction(A), high_value(A), not eligibility_rule(A).
gap(agent_negotiation_without_mandate, N) :- negotiation(N), agent_party(N, X), not mandate_for(X, N).
```
AI: shill-bid detection, bid recommendations, negotiation agents (bounded L4 within mandate; human approval to accept above thresholds), proposal scoring assistance. Signals: `bids_per_second`, `soft_close_extensions`, `sniping_rate`, `tender_cycle_days`. Views: live auction (WebSocket updates), bid history, RFQ workspace, proposal comparison matrix, negotiation thread. Scale: hot auctions 10k bids/min with ordered log per auction (single-partition); T1.

## Appendix
- **C.** 0.1.0.
