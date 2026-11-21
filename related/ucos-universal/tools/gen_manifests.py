#!/usr/bin/env python3
"""gen_manifests — source of truth for spec/capabilities/packs/*.yaml.

Part 1 (hand-authored): every capability of the Phase 0–1 universes, communication and contact centre, with adapters,
ports, simulators, decisions, controls and views.
Part 2 (derived): one `<slug>.core` manifest for each specified universe that has no hand-authored capability. It is parsed
from the constitution (objects, commands, queries, events, Depends on, Delivery phase) and from
TEMPORAL-BINDING-MATRIX.md (temporal kind and uses). Derived manifests have maturity `experimental` until a steward
replaces them with hand-authored ones.

Usage: python3 tools/gen_manifests.py   then   python3 tools/gen_registries.py && python3 tools/ucos_check.py
"""
import glob, os, re
import yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'spec', 'capabilities', 'packs')

def ev(slug, obj, *verbs):
    return [f'{slug}.{obj}.{v}' for v in verbs]

P = []  # list of dicts

TM = {  # universe -> threat model (docs/threat-models/); everything else uses the kernel baseline
    'U09': 'identity', 'U11': 'party-and-privacy', 'U66': 'party-and-privacy',
    'U12': 'geo-and-fulfillment', 'U35': 'geo-and-fulfillment', 'U36': 'geo-and-fulfillment',
    'U20': 'commerce-checkout-order', 'U22': 'commerce-checkout-order', 'U23': 'commerce-checkout-order',
    'U24': 'commerce-checkout-order', 'U26': 'commerce-checkout-order', 'U29': 'payment',
    'U31': 'tax-and-documents', 'U42': 'tax-and-documents', 'U40': 'communication', 'U109': 'communication',
    'U62': 'integration-webhooks', 'U43': 'storefront-and-admin-ui', 'U64': 'storefront-and-admin-ui',
    'U87': 'storefront-and-admin-ui'}
def threat_model_for(universe):
    return f"docs/threat-models/{TM.get(universe.split('-')[0], 'kernel-and-tenancy')}.md"
def pack(id, universe, kind, phase, purpose, scope='tenant', types=(), commands=(), queries=(), events=(),
         consumes=(), requires=(), optional=(), implements=(), ports=(), decisions=(), selection=None,
         temporal=('S', ['TP']), classes=(), controls=(), views=()):
    m = {
        'apiVersion': 'ucos.io/v1', 'kind': 'Capability',
        'metadata': {'id': id, 'version': '1.0.0', 'universe': universe, 'steward': f'ucos:org:steward-{universe.split("-",1)[1]}',
                     'purpose': purpose, 'capabilityKind': kind, 'maturity': 'beta', 'phase': phase, 'scope': scope},
        'spec': {}
    }
    s = m['spec']
    if implements: s['implements'] = list(implements)
    prov = {}
    if types: prov['objectTypes'] = list(types)
    if commands: prov['commands'] = list(commands)
    if queries: prov['queries'] = list(queries)
    if events: prov['events'] = list(events)
    if decisions: prov['decisions'] = list(decisions)
    if ports: prov['ports'] = list(ports)
    if prov: s['provides'] = prov
    if consumes: s['consumes'] = {'events': list(consumes)}
    if requires: s['requires'] = [{'capability': r, 'version': '>=1 <2'} for r in requires]
    if optional: s['optional'] = [{'capability': o} for o in optional]
    if selection: s['selection'] = selection
    s['temporal'] = {'kind': temporal[0], 'uses': temporal[1]}
    if classes: s['security'] = {'dataClasses': list(classes), 'threatModel': threat_model_for(universe)}
    if controls: s['compliance'] = {'controls': list(controls)}
    if views: s['ui'] = {'views': list(views)}
    s['certification'] = {'gates': ['ARCH-*', 'SEC-*', 'TEST-*', 'DOC-*', 'OBS-*'] + (['A11Y-*'] if views else [])}
    P.append(m)

T = lambda *xs: [f'ucos.{x}' for x in xs]

# ---------------- Platform-scope (control plane / global registries) ----------------
pack('meta.core','U04-meta','core',0,'Registry of object types, field types, value types, relationship types and lifecycles.','platform',
     T('meta.ObjectType','meta.FieldType','meta.ValueType','meta.RelationshipType','meta.LifecycleModel','meta.ExtensionSchema'),
     ['ProposeObjectType','ValidateObjectType','ApproveObjectType','PublishObjectType','DeprecateObjectType','CreateExtensionSchema'],
     ['GetObjectType','ResolveSchema','CheckCompatibility'], ev('meta','object-type','published','deprecated')+ev('meta','extension','created'),
     temporal=('V',['TP','TR','ASOF']))
pack('refdata.core','U08-reference-data','core',0,'Authoritative standard code lists (ISO, IANA, UN, ISIC, CPC, HS, APQC…) and crosswalks.','platform',
     T('refdata.CodeList','refdata.CodeValue','refdata.CodeMapping','refdata.CodeListRelease'),['StageRelease','PublishRelease','CreateCodeList','SetTenantAlias'],
     ['GetCode','ListCodes','MapCode'], ev('refdata','release','published')+ev('refdata','code','deprecated'), requires=['meta.core'], temporal=('V',['TR']))
pack('frame.core','U77-existence-reality-frame','core',0,'Frames of reference: realities, bodies, spatial frames, time scales, calendar/monetary/unit/language systems, authorities.','platform',
     T('frame.Reality','frame.Body','frame.SpatialReferenceFrame','frame.TimeScale','frame.CalendarSystem','frame.MonetarySystem','frame.UnitSystem','frame.LanguageSystem','frame.GoverningAuthority','frame.Frame','frame.RealityLink','frame.FrameConversion'),
     ['RegisterReality','RegisterBody','DefineFrame','RegisterConversion','LinkRealities','SetTenantDefaultFrame'],['ResolveFrame','Convert'],
     ev('frame','frame','defined')+ev('frame','reality','registered'), requires=['meta.core','refdata.core'], temporal=('V',['TS']))
pack('authority.core','U01-authority','core',0,'Authorities, delegations and immutable decision records for every governed decision.','platform',
     T('authority.Authority','authority.DecisionRecord'),['CreateAuthority','DelegateAuthority','RevokeAuthority','RecordDecision','AddApproval','Ratify','Annul','BreakGlass'],
     ['WhoCanDecide','CheckAuthority','DecisionHistory'], ev('authority','decision','recorded','ratified')+ev('authority','authority','revoked'), requires=['meta.core','temporal.core'], temporal=('S',['TR','TRG','REM']))
pack('policy.core','U03-policy','core',0,'Cedar policy sets, layered PDP, policy analysis and tests.','platform',
     T('policy.Policy','policy.PolicySet','policy.PolicyTest'),['ProposePolicy','ActivatePolicySet','AddPolicyTest'],['IsAuthorized','PartialEvaluate','AnalysePolicySet'],
     ev('policy','policyset','activated'), requires=['meta.core','temporal.core'], temporal=('S',['TR','POL','ASOF']))
pack('governance.core','U02-governance','core',0,'Change proposals, classification, impact analysis, waivers and progressive release plans.','platform',
     T('governance.ChangeProposal','governance.Waiver','governance.ReleasePlan','governance.ChangeWindow','governance.ChangeTemplate'),
     ['CreateProposal','SubmitProposal','ScheduleProposal','ActivateProposal','WithdrawProposal','RequestWaiver','GrantWaiver','RevokeWaiver'],['ChangeCalendar','ProposalTimeline'],
     ev('governance','proposal','submitted','approved','completed','rolled-back')+ev('governance','waiver','granted','expired'),
     requires=['authority.core','temporal.core','policy.core'], temporal=('S',['POL','TRG','TR','D']))
pack('ontology.core','U05-ontology','core',0,'Concepts, relations, external mappings and duplicate-concept detection.','platform',
     T('ontology.Concept','ontology.ExternalMapping','ontology.DuplicateCase'),['ProposeConcept','RelateConcepts','MapExternal','ResolveDuplicate'],['FindSimilar','ResolveTerm'],
     ev('ontology','concept','proposed','merged'), requires=['meta.core'], temporal=('V',['TR']))
pack('taxonomy.core','U06-taxonomy','core',0,'Classification schemes, nodes, attribute templates, mappings and classifications.','platform',
     T('taxonomy.Taxonomy','taxonomy.TaxonomyNode','taxonomy.TaxonomyMapping','taxonomy.Classification'),
     ['CreateTaxonomy','AddNode','MoveNode','DeprecateNode','MapNodes','Classify','BulkReclassify'],['Tree','EffectiveAttributes','Suggest'],
     ev('taxonomy','node','changed')+ev('taxonomy','classification','changed'), requires=['ontology.core','refdata.core'], temporal=('V',['TR']))
pack('knowledge.graph','U07-knowledge-graph','core',1,'Knowledge graph projections, assertions with trust, traceability and grounding.','platform',
     T('knowledge.KnowledgeObject','knowledge.Assertion','knowledge.Contradiction'),['ProposeAssertion','AcceptAssertion','RetractAssertion','ResolveContradiction','RebuildProjection'],
     ['Trace','ImpactOf','Ground'], ev('knowledge','assertion','accepted')+ev('knowledge','contradiction','opened'), requires=['ontology.core','event.core','temporal.core'], temporal=('S',['TR','D','R']))
pack('product.intelligence','U18-product-intelligence','core',1,'Global product master (GPID), attributes, variants, brands, provenance, matching and recalls.','platform',
     T('product.GlobalProduct','product.ProductModel','product.Attribute','product.Brand','product.ProductFact','product.MatchCase','product.Recall','product.ProductDocument','product.RegulatedGoodsProfile'),
     ['IngestBatch','ContributeFromTenant','Match','ResolveMatch','MergeProducts','PublishProduct','RegisterAttribute','RecordRecall'],['GetGlobalProduct','SearchGlobal','ByIdentifier','Compatible'],
     ev('product','global','published','updated','merged')+ev('product','recall','published'), requires=['taxonomy.core','currency.core','asset.core','l10n.core'], temporal=('S',['TP','TR','TRG']))
pack('service.intelligence','U19-service-intelligence','core',1,'Global service master (GSID), service plans, SLA templates and credential requirements.','platform',
     T('service.GlobalService','service.ServicePlan','service.SLADefinitionTemplate','service.CredentialType'),['ProposeGlobalService','PublishGlobalService','RegisterCredentialType'],
     ['GetGlobalService','RequirementsFor'], ev('service','global','published'), requires=['taxonomy.core','temporal.core'], temporal=('S',['D','SLA','AV']))
pack('industry.registry','U20-industry','core',1,'Industry classification and certified industry templates that pre-fill platform definitions.','platform',
     T('industry.IndustryTemplate','industry.Standard','industry.Benchmark'),['PublishTemplate','DeprecateTemplate'],['TemplatesFor','ExpandTemplate'],
     ev('industry','template','published'), requires=['taxonomy.core','refdata.core'], temporal=('V',['TR']))
pack('capability.registry','U57-capability','core',0,'Capability definitions, packs, adapters, extension points, marketplace and revocation.','platform',
     T('capability.CapabilityDefinition','capability.CapabilityPack','capability.CapabilityBundle','capability.MarketplaceListing'),
     ['RegisterCapability','PublishPack','RevokePackVersion','DeprecateCapability'],['GetCapability','Implementations','Dependents'],
     ev('capability','pack','published','revoked'), requires=['meta.core','certification.core'], temporal=('S',['TP','TRG','SLA']))
pack('composition.core','U58-composition','core',0,'Deterministic composition of platform definitions into blueprints with traces and gap reports.','platform',
     T('composition.PlatformDefinition','composition.Blueprint','composition.ResolutionTrace','composition.RuleModule','composition.RegistrySnapshot'),
     ['Compose','Recompose','PromoteCandidate','ApplyFix','CreateSnapshot'],['Why','WhyNot','Diff','EstimateCost'],
     ev('composition','run','completed')+ev('composition','recompose','required'), requires=['capability.registry','gap.core','governance.core'], temporal=('S',['R','D']))
pack('event.core','U61-event','core',0,'Event types, schemas, topics, subscriptions, replay and dead letters.','platform',
     T('event.EventType','event.EventSchema','event.Subscription'),['RegisterEventType','PublishSchema','CreateSubscription','Replay','RedriveDeadLetters'],['EventCatalog'],
     ev('event','schema','published'), requires=['meta.core','temporal.core'], temporal=('S',['TP','D','TR']))
pack('security.core','U65-security','core',0,'Classification, keys, secrets, security controls, findings and incidents.','platform',
     T('security.Key','security.SecretRef','security.SecurityControl','security.ThreatModel','security.Finding','security.SecurityIncident'),
     ['CreateKey','RotateKey','DestroyKey','RecordFinding','TriageFinding','AcceptRisk','DeclareIncident','SetSecurityProfile'],['Posture'],
     ev('security','key','rotated')+ev('security','incident','declared'), requires=['authority.core','temporal.core'], temporal=('S',['R','TRG','SLA']))
pack('audit.core','U68-audit-evidence','core',0,'Hash-chained audit records, evidence, collectors, evidence packs and legal holds.','platform',
     T('audit.AuditRecord','audit.ChainAnchor','audit.Evidence','audit.EvidenceCollector','audit.EvidencePack','audit.AuditorAccessGrant'),
     ['AnchorChains','VerifyChain','CollectEvidence','AssembleEvidencePack','PlaceLegalHold'],['SearchAudit','EvidenceFor'],
     ev('audit','chain','anchored')+ev('audit','evidence','collected'), requires=['security.core','temporal.core'], temporal=('S',['R','TR']))
pack('infra.core','U73-infrastructure-deployment','core',0,'Cells, placement, deployments, blueprint activation, backups and disaster recovery.','platform',
     T('infra.Cell','infra.Placement','infra.Deployment','infra.Activation','infra.BackupPolicy','infra.DRPlan','infra.Environment'),
     ['ProvisionCell','PlaceTenant','MigrateShard','Deploy','ActivateBlueprint','RollbackActivation','FailoverCell'],['TenantPlacement','DriftReport'],
     ev('infra','activation','completed','rolled-back')+ev('infra','cell','failed-over'), requires=['security.core','temporal.core'], temporal=('S',['R','POL','D','TRG']))
pack('certification.core','U74-certification','core',0,'Certification gates, profiles, runs and signed attestations.','platform',
     T('certification.CertificationGate','certification.CertificationProfile','certification.CertificationRun','certification.Certification'),
     ['DefineGate','StartRun','IssueCertification','Invalidate','Revoke'],['StatusOf'],
     ev('certification','run','completed')+ev('certification','certification','issued','invalidated'), requires=['audit.core','temporal.core'], temporal=('S',['TP','TRG','D']))
pack('gap.core','U75-discovery-gap','core',0,'Gap model, rule library, scans, fix catalogue and discovery questions.','platform',
     T('gap.Gap','gap.GapRule','gap.Fix','gap.GapReport','gap.DiscoveryFinding'),['Scan','ApplyFix','AssignGap','RequestWaiver'],['OpenGaps','Why'],
     ev('gap','scan','completed'), requires=['meta.core','temporal.core'], temporal=('S',['TP','TRG','R']))
pack('sdlc.core','U95-software-delivery-source-control','core',0,'Repositories, change requests, pipelines, artifacts with provenance, definitions-as-code sync.','platform',
     T('sdlc.Repository','sdlc.ChangeRequest','sdlc.PipelineRun','sdlc.Artifact','sdlc.DefinitionsRepoMapping'),['RegisterRepository','OpenChangeRequest','SyncDefinitions','RunPipeline'],['ProvenanceOf'],
     ev('sdlc','pr','merged')+ev('sdlc','artifact','published'), requires=['governance.core','certification.core'], temporal=('S',['R','D']))

# ---------------- Tenant-scope foundation ----------------
pack('identity.core','U09-identity','core',0,'Identities, credentials, sessions, roles, grants, delegations, federation and verification records.',
     types=T('identity.Identity','identity.Credential','identity.Session','identity.Role','identity.RoleGrant','identity.Delegation','identity.FederatedProvider','identity.VerificationRecord'),
     commands=['RegisterIdentity','VerifyIdentifier','EnrollCredential','RevokeCredential','EndSession','DefineRole','GrantRole','RevokeRole','ElevateJIT','CreateDelegation','ConfigureFederation','SuspendIdentity'],
     queries=['WhoAmI','GetEffectiveRoles'], events=ev('identity','identity','registered','suspended')+ev('identity','session','started','ended')+ev('identity','role','granted','revoked')+ev('identity','delegation','created'),
     requires=['authority.core','policy.core','party.core','temporal.core'], optional=['identity.social-login'], temporal=('S',['TP','D','TR','TRG','R']), classes=['PII','CREDENTIAL'],
     controls=['ucos.ctrl.mfa-business-users','ucos.ctrl.access-review'], views=['identity.login','identity.account.security'])
pack('identity.federation-provider','U09-identity','abstract',1,'Port for external identity providers (OIDC/SAML/social).', ports=['identity.federation-provider@1'], temporal=('V',[]))
pack('identity.social-login','U09-identity','adapter',1,'Social identity providers (Google, Apple…) via OIDC federation.', implements=['identity.federation-provider'],
     requires=['integration.core'], selection={'jurisdictions':['*']}, temporal=('V',['TP']))
pack('party.core','U11-person-party','core',0,'Persons, organisations as parties, roles, contact points, preferences, merge and erasure.',
     types=T('party.Party','party.Person','party.PartyRole','party.ContactPoint','party.Preference','party.PartyRelationship'),
     commands=['CreatePerson','UpdatePerson','AssignRole','EndRole','AddContactPoint','VerifyContactPoint','MergeParties','ErasePerson'],
     queries=['GetPerson','FindCandidates','ListReferences','ContactFor'], events=ev('party','person','created','merged','erased')+ev('party','role','assigned')+ev('party','contact','verified'),
     requires=['geo.core','l10n.core','meta.core'], temporal=('E',['TR','TP']), classes=['PII','SPI'])
pack('org.core','U10-organization-tenant','core',0,'Tenants, organisations, org units, workspaces, brands, stores and tenant links.',
     types=T('org.Tenant','org.Organization','org.OrgUnit','org.Workspace','org.Brand','org.Store','org.TenantLink'),
     commands=['ProvisionTenant','ChangeIsolationTier','SuspendTenant','OffboardTenant','CreateOrganization','SetOrganizationStanding','CreateStore','ChangeStoreStatus','CreateBrand','VerifyDomain','CreateWorkspace','CreateTenantLink'],
     queries=['ResolveTenantByHost','OrgTree','StoresNear'], events=ev('org','tenant','provisioned','suspended')+ev('org','organization','created','standing-changed')+ev('org','store','status-changed')+ev('org','domain','verified'),
     requires=['identity.core','geo.core','entitlement.core','temporal.core'], temporal=('S',['POL','TP','TRG','CAL']), views=['org.store.editor','org.domain.setup'])
pack('geo.core','U12-geography','core',0,'Places, addresses, jurisdictions, zones, geofences, service areas and address formats.',
     types=T('geo.Place','geo.Address','geo.Jurisdiction','geo.Zone','geo.Geofence','geo.ServiceArea','geo.AddressFormat'),
     commands=['CreateAddress','UpdateAddress','VerifyAddress','UpsertPlace','UpsertJurisdiction','DefineZone','DefineGeofence','DefineServiceArea'],
     queries=['ResolveJurisdictions','PointInZones','IsServiceable','Geocode','ValidateAddress','FormatAddress'],
     events=ev('geo','address','created','updated','verified')+ev('geo','zone','changed')+ev('geo','jurisdiction','changed'),
     requires=['refdata.core','frame.core','maps.provider'], temporal=('E',['TR','POL']), classes=['PII','LOCATION'], views=['geo.address.form'])
pack('maps.provider','U12-geography','abstract',0,'Port for geocoding, reverse geocoding, autocomplete and static maps.', ports=['maps.provider@1'], temporal=('V',[]))
pack('maps.google','U12-geography','adapter',1,'Google Maps Platform adapter for maps.provider.', implements=['maps.provider'], requires=['integration.core'], selection={'jurisdictions':['*']}, temporal=('V',[]))
pack('maps.simulator','U12-geography','simulator',0,'Deterministic maps simulator for simulation and test realities.', implements=['maps.provider'], selection={'jurisdictions':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))
pack('temporal.core','U13-temporal','core',0,'Calendars, temporal policies, availability, slots, reservations, SLA clocks, triggers, schedules, waitlists, queues, feeds and reminders.',
     types=T('temporal.Calendar','temporal.CalendarEntry','temporal.TemporalPolicy','temporal.AvailabilityWindow','temporal.Slot','temporal.Reservation','temporal.SLADefinition','temporal.SLAClock','temporal.Trigger','temporal.Schedule','temporal.Waitlist','temporal.QueueToken','temporal.CalendarFeed','temporal.ExternalCalendarLink','temporal.Invitation','temporal.Reminder','temporal.TimezoneRelease'),
     commands=['CreateCalendar','UpsertCalendarEntries','CreateTemporalPolicy','DefineAvailability','HoldReservation','ConfirmReservation','ReleaseReservation','RescheduleReservation','StartSLAClock','PauseSLAClock','ResumeSLAClock','StopSLAClock','CreateTrigger','CancelTrigger','JoinWaitlist','IssueQueueToken','PublishFeed','LinkExternalCalendar','SendInvitation','UpgradeTimezoneRelease'],
     queries=['EvaluatePolicy','ExpandPolicy','IsWorkingTime','AddBusinessDuration','QueryAvailability','FindCommonAvailability','NextOccurrences','FiscalPeriodOf','SettlementDate','Timeline'],
     events=ev('temporal','trigger','fired','misfired')+ev('temporal','policy','changed','activated','deactivated')+ev('temporal','calendar','changed')+ev('temporal','reservation','held','confirmed','released','expired','rescheduled')+ev('temporal','sla','started','paused','warning','breached','met')+ev('temporal','waitlist','promoted')+ev('temporal','queue','called')+ev('temporal','tz','upgraded'),
     requires=['refdata.core','frame.core','geo.core'], temporal=('S',['TP','TR','D','BD','R','POL','CAL','AV','FCA','SLA','TRG','REM','WL','FEED','ASOF','TS']), views=['temporal.policy.editor','temporal.calendar.month','temporal.slot-picker'])
pack('currency.core','U14-currency-unit','core',0,'Money, currencies, FX rates and rate policies, rounding, allocation, units and conversions.',
     types=T('currency.Currency','currency.ExchangeRate','currency.RateSource','currency.RatePolicy','currency.RoundingRule','currency.Unit','currency.UnitConversion','currency.PackagingUnit'),
     commands=['IngestRates','PublishRate','DefineRatePolicy','DefineRoundingRule','RegisterUnit','RegisterConversion'],
     queries=['Convert','GetRate','Round','Allocate','ConvertQuantity','FormatMoney'], events=ev('currency','rates','updated')+ev('currency','policy','changed'),
     requires=['refdata.core','temporal.core','frame.core'], optional=['fx.provider'], temporal=('S',['TR','R','D','CAL']))
pack('fx.provider','U14-currency-unit','abstract',0,'Port for FX reference-rate feeds.', ports=['fx.provider@1'], temporal=('V',[]))
pack('fx.simulator','U14-currency-unit','simulator',0,'Deterministic FX simulator for simulation/test realities.', implements=['fx.provider'], selection={'jurisdictions':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))
pack('fx.reference-rates','U14-currency-unit','adapter',1,'Reference FX rate feed adapter (central-bank and commercial sources).', implements=['fx.provider'], requires=['integration.core'], selection={'jurisdictions':['*']}, temporal=('S',['R']))
pack('l10n.core','U15-localization','core',0,'Locales, message bundles, translations, glossaries and format profiles.',
     types=T('l10n.Locale','l10n.MessageKey','l10n.MessageBundle','l10n.Translation','l10n.FormatProfile','l10n.Glossary'),
     commands=['RegisterBundle','RequestTranslation','SubmitTranslation','ApproveTranslation','SetTenantOverride','EnableLocale'],
     queries=['Resolve','GetBundle','Coverage','Format'], events=ev('l10n','bundle','registered')+ev('l10n','translation','approved','stale')+ev('l10n','locale','enabled'),
     requires=['refdata.core','frame.core'], temporal=('E',['D']), views=['l10n.translation.editor','l10n.locale.switcher'])
pack('context.core','U16-context','core',0,'Context profiles and rules; resolver configuration for the gateway.',
     types=T('context.ContextProfile','context.ContextRule'), commands=['DefineContextProfile','DefineContextRule'], queries=['ResolveContext'],
     events=ev('context','profile','changed'), requires=['org.core','geo.core','temporal.core','currency.core','l10n.core','identity.core','frame.core'], temporal=('E',['TP','ASOF','D']))
pack('entitlement.core','U28-entitlement','core',0,'Plans, features, quotas, entitlements and metering with real-time check/consume.',
     types=T('entitlement.Feature','entitlement.Quota','entitlement.Plan','entitlement.Entitlement','entitlement.UsageCounter'),
     commands=['DefinePlan','DefineFeature','DefineQuota','Grant','Revoke','ChangePlan','Consume','ResetCounters'],
     queries=['Check','Remaining','EffectiveEntitlements','Usage'], events=ev('entitlement','entitlement','granted','revoked','expired')+ev('entitlement','quota','threshold','exceeded'),
     requires=['temporal.core','currency.core'], temporal=('S',['TR','R','D']), views=['billing.plan-and-usage'])

# ---------------- Platform services exposed to tenants ----------------
pack('integration.core','U62-integration','core',1,'Connector runtime, webhook ingress, resilient outbound calls, sandboxes, tenant webhooks.',
     types=T('integration.ConnectorInstance','integration.InboundWebhook','integration.SyncJob','integration.TenantWebhookSubscription','integration.TenantWebhookDelivery'),
     commands=['CreateConnectorInstance','VerifyConnectorInstance','RotateCredentials','DisableInstance','ReplayInboundWebhook','RunSyncJob','SubscribeTenantWebhook','RedeliverWebhook'],
     queries=['InstanceHealth','CallLog','WebhookLog'], events=ev('integration','instance','activated','degraded','disabled')+ev('integration','webhook','received','failed')+ev('integration','tenant-webhook','disabled'),
     requires=['temporal.core'], temporal=('S',['R','D','TP']), views=['integration.instances','integration.webhooks'])
pack('decision.core','U53-decision','core',1,'Decision tables and models with tenant versions, bounds, tests and decision logs.',
     types=T('decision.DecisionDefinition','decision.TenantDecisionVersion','decision.DecisionLog'),
     commands=['RegisterDecision','ProposeTenantVersion','PublishTenantVersion','AddDecisionTest','RollbackTenantVersion'],
     queries=['Evaluate','Explain','Simulate','Coverage'], events=ev('decision','version','published'), requires=['temporal.core'], temporal=('S',['POL','TR','TRG','ASOF']), views=['decision.table.editor'])
pack('workflow.core','U60-workflow','core',1,'Durable workflow definitions, instances, human tasks, escalations and sagas.',
     types=T('workflow.WorkflowDefinition','workflow.WorkflowInstance','workflow.HumanTask','workflow.EscalationPolicy','workflow.Migration'),
     commands=['StartWorkflow','Signal','CancelWorkflow','SuspendWorkflow','ResumeWorkflow','MigrateInstances','ClaimTask','CompleteTask','ReassignTask','DelegateTask'],
     queries=['GetInstance','InstancesFor','TaskInbox','StuckInstances'], events=ev('workflow','instance','started','transitioned','completed','failed','compensated')+ev('workflow','task','created','completed','escalated'),
     requires=['temporal.core','decision.core'], temporal=('S',['TRG','SLA','BD']), views=['task.inbox'])
pack('asset.core','U43-asset','core',1,'Binary assets with scanning, renditions, rights and signed delivery.',
     types=T('asset.BinaryAsset','asset.Rendition','asset.AssetRights'), commands=['InitiateUpload','FinalizeUpload','RequestRendition','SetRights','DeleteAsset','ShredAsset'],
     queries=['GetAsset','SignedUrl','UsagesOf'], events=ev('asset','asset','available','quarantined','deleted')+ev('asset','rights','expiring','expired'),
     requires=['temporal.core'], temporal=('S',['TR','TRG','D']), views=['asset.library','asset.uploader'])
pack('document.core','U42-document','core',1,'Document templates, deterministic rendering, immutable issued documents and signatures.',
     types=T('document.DocumentTemplate','document.Document','document.RenderRecord'),
     commands=['PublishTemplate','RenderDocument','IssueDocument','SupersedeDocument','VoidDocument','DeliverDocument'],
     queries=['DocumentsFor','Download','VerifyDocument'], events=ev('document','document','issued','superseded','voided','delivered'),
     requires=['asset.core','l10n.core','currency.core','temporal.core'], temporal=('S',['TP','TR']), views=['document.template.editor','document.viewer'])
pack('search.core','U44-search','core',1,'Search indexes, query understanding, ranking profiles, merchandising and search analytics.',
     types=T('search.IndexDefinition','search.Synonym','search.QueryRule','search.RankingProfile'),
     commands=['DefineIndex','Reindex','UpsertSynonyms','DefineQueryRule','DefineRankingProfile','PinResult'],
     queries=['Search','Suggest','AdminSearch','ExplainResult'], events=ev('search','index','rebuilt'),
     consumes=['catalog.listing.published','catalog.listing.unpublished','catalog.listing.updated','pricing.price.changed','inventory.stock.depleted','inventory.stock.restocked'],
     requires=['taxonomy.core','temporal.core','catalog.listing'], temporal=('S',['POL','TR','D','R']), views=['search.results','search.autocomplete','search.merchandising.console'])
pack('api.core','U63-api','core',1,'Generated REST/GraphQL/MCP surfaces, API products, clients, rate limits and deprecations.',
     types=T('api.APIDefinition','api.APIProduct','api.APIClient','api.RateLimitPolicy'),
     commands=['GenerateAPI','PublishAPIProduct','RegisterClient','RotateClientSecret','DeprecateOperation'],
     queries=['GetOpenAPI','GetGraphQLSchema','UsageFor'], events=ev('api','definition','generated')+ev('api','client','registered')+ev('api','quota','exceeded'),
     requires=['entitlement.core','integration.core','temporal.core'], temporal=('S',['TP','TRG','D','R']), views=['developer.portal'])
pack('ui.core','U64-ui-app-channel','core',1,'UI meta-model: views, components, journeys, portals, themes and channel profiles; web renderer.',
     types=T('ui.ViewDefinition','ui.Component','ui.Journey','ui.Portal','ui.Theme','ui.ChannelProfile'),
     commands=['ProposeView','PublishView','DefineJourney','DefinePortal','PublishTheme','RegisterComponent'],
     queries=['CompiledView','PortalManifest','PreviewAs'], events=ev('ui','view','published')+ev('ui','theme','published'),
     requires=['l10n.core','temporal.core'], temporal=('S',['ASOF','D']), controls=['ucos.ctrl.wcag-2.2-aa'])
pack('ui.storefront-web','U64-ui-app-channel','ui-pack',1,'Storefront web views (home, listing, product, search, cart, checkout, account, orders, returns, pages).',
     requires=['ui.core','catalog.listing','commerce.cart','commerce.checkout','order.core','search.core','seo.core'],
     temporal=('S',['AV','POL']), controls=['ucos.ctrl.in-ecom-disclosures','ucos.ctrl.honest-design'],
     views=['storefront.home','storefront.plp','storefront.pdp','storefront.search','storefront.cart','storefront.checkout','storefront.account','storefront.orders','storefront.order-tracking','storefront.returns','storefront.page'])
pack('ui.tenant-admin','U64-ui-app-channel','ui-pack',1,'Tenant admin portal views (catalog, pricing, offers, orders, inventory, settings, users, compliance).',
     requires=['ui.core','org.core','identity.core'], temporal=('S',['ASOF']),
     views=['admin.dashboard','admin.catalog','admin.pricing','admin.offers','admin.orders','admin.inventory','admin.settings','admin.users','admin.compliance'])
pack('seo.core','U87-web-presence-seo','core',1,'Routes, slugs, redirects, metadata, structured data, sitemaps and robots/AI-crawler policy.',
     types=T('seo.Route','seo.Slug','seo.Redirect','seo.MetaTemplate','seo.StructuredDataMapping','seo.Sitemap','seo.SiteSettings'),
     commands=['DefineRoute','SetSlug','CreateRedirect','DefineMetaTemplate','MapStructuredData','RegenerateSitemaps','UpdateSiteSettings'],
     queries=['ResolveUrl','SeoAudit','PreviewSnippet'], events=ev('seo','slug','changed')+ev('seo','redirect','created')+ev('seo','sitemap','regenerated'),
     consumes=['catalog.listing.published','catalog.listing.unpublished'], requires=['ui.core','temporal.core'], temporal=('S',['R','TP','TRG']), views=['seo.audit.dashboard'])
pack('observability.core','U72-observability-analytics','core',1,'Signals, SLOs, alerts, dashboards, certified metrics, reports, feature flags and experiments.',
     types=T('obs.SignalDefinition','obs.SLO','obs.AlertRule','obs.Dashboard','obs.MetricDefinition','obs.Report','obs.FeatureFlag','obs.Experiment'),
     commands=['DefineSLO','DefineAlertRule','PublishDashboard','DefineMetric','ScheduleReport','CreateFlag','StartExperiment','StopExperiment'],
     queries=['SLOStatus','QueryMetric','EvaluateFlag','ExperimentResults'], events=ev('observability','slo','burning','breached')+ev('observability','alert','fired')+ev('analytics','report','delivered'),
     requires=['temporal.core'], temporal=('S',['D','POL','R','TP','TRG']), views=['analytics.dashboard'])
pack('privacy.consent','U66-privacy-consent','core',1,'Purposes, notices, consent records and cookie consent.',
     types=T('privacy.Purpose','privacy.Notice','privacy.Consent','privacy.CookieConsent'), commands=['DefinePurpose','PublishNotice','RecordConsent','WithdrawConsent'],
     queries=['ConsentSnapshot','HasConsent'], events=ev('privacy','consent','granted','withdrawn')+ev('privacy','notice','published'),
     requires=['party.core','temporal.core','l10n.core'], temporal=('S',['TR','TP']), classes=['PII'], controls=['ucos.ctrl.consent-notice'], views=['privacy.center','cookie.banner'])
pack('privacy.dsr','U66-privacy-consent','core',1,'Data subject requests (access, rectification, erasure, portability, grievance) across universes.',
     types=T('privacy.DataSubjectRequest'), commands=['SubmitDSR','VerifyDSRIdentity','CompleteDSR'], queries=['DSRStatus'],
     events=ev('privacy','dsr','received','completed','overdue'), requires=['party.core','workflow.core','temporal.core','identity.core'], temporal=('S',['SLA','TRG']),
     classes=['PII'], controls=['ucos.ctrl.dsr-erasure','ucos.ctrl.dsr-access'], views=['privacy.dsr.console'])
pack('privacy.retention','U66-privacy-consent','core',1,'Retention rules, legal-hold-aware deletion, anonymisation and crypto-shredding.',
     types=T('privacy.RetentionRule','privacy.TransferRecord','privacy.ProcessingActivity'), commands=['DefineRetentionRule','RunRetention','RecordTransfer'], queries=['RetentionDue','RoPA'],
     events=ev('privacy','retention','executed'), requires=['temporal.core'], temporal=('S',['D','R']), controls=['ucos.ctrl.retention','ucos.ctrl.ropa'])
pack('compliance.core','U67-compliance','core',1,'Regulations, clauses, obligations, controls, mappings, posture and regulatory change.',
     types=T('compliance.Regulation','compliance.Clause','compliance.Obligation','compliance.Control','compliance.Interpretation','compliance.ControlStatus','compliance.ComplianceAssessment','compliance.RegulatoryChange'),
     commands=['PublishRegulationVersion','DefineControl','MapControl','RecordInterpretation','StartAssessment','RecordRegulatoryChange','ComputeStatus'],
     queries=['ApplicableRegulations','ControlsFor','Posture','TraceClause'], events=ev('compliance','control','failed','recovered')+ev('compliance','regulation','published')+ev('compliance','change','effective-soon'),
     requires=['temporal.core','audit.core'], temporal=('S',['TP','TRG','R','D','TR']), views=['compliance.posture'])

# ---------------- Commerce core (P1) ----------------
pack('catalog.listing','U21-catalog','core',1,'Tenant listings referencing global products/services, sellable units, catalogues and collections.',
     types=T('catalog.Listing','catalog.SellableUnit','catalog.Catalog','catalog.Collection'),
     commands=['CreateListing','UpdateListing','SubmitForReview','ApproveListing','RejectListing','PublishListing','PauseListing','SuppressListing','ArchiveListing','AddSellableUnit','UpdateSellableUnit','BulkImport','DefineCatalog','DefineCollection'],
     queries=['GetListing','ResolveCatalog','ListingsInCatalog','QualityReport'],
     events=ev('catalog','listing','created','published','unpublished','updated','approved','rejected','suppressed')+ev('catalog','unit','changed')+ev('catalog','import','completed'),
     consumes=['product.global.updated','product.recall.published'],
     requires=['product.intelligence','taxonomy.core','org.core','asset.core','l10n.core','temporal.core','decision.core'],
     temporal=('S',['POL','TRG','AV']), controls=['ucos.ctrl.in-legal-metrology-attributes'], views=['catalog.listing.edit','catalog.import.wizard'])
pack('offer.engine','U22-offer','core',1,'Offers, promotions, coupons, campaigns, stacking, funding, budgets and redemptions.',
     types=T('offer.Offer','offer.Campaign','offer.Coupon','offer.CouponBatch','offer.Redemption'),
     commands=['CreateOffer','UpdateOffer','PublishOffer','PauseOffer','CancelOffer','CreateCampaign','GenerateCoupons','ReserveRedemption','ConfirmRedemption','ReverseRedemption','SimulateOffer'],
     queries=['EvaluateOffers','ActiveOffersFor','CouponStatus','CampaignPerformance'],
     events=ev('offer','offer','created','published','paused','cancelled','activated','expired')+ev('offer','coupons','generated')+ev('offer','redemption','reserved','confirmed','reversed'),
     consumes=['temporal.policy.activated','temporal.policy.deactivated'],
     requires=['temporal.core','decision.core','catalog.listing','currency.core','party.core'], temporal=('S',['POL','TRG','D']), views=['offer.builder','offer.badge'])
pack('pricing.engine','U23-pricing','core',1,'Price lists, price rules, fees, waterfall quotes, price history and B2B quotes.',
     types=T('pricing.PriceList','pricing.PriceEntry','pricing.PriceRule','pricing.Fee','pricing.PriceQuote','pricing.B2BQuote'),
     commands=['UpsertPriceEntries','SchedulePriceChange','DefinePriceList','DefinePriceRule','DefineFee','CreateB2BQuote','SendB2BQuote','AcceptB2BQuote'],
     queries=['Quote','DisplayPrice','PriceHistory','LowestPrice','ResolvePriceList'], events=ev('pricing','price','changed')+ev('pricing','pricelist','changed')+ev('pricing','b2b-quote','accepted'),
     requires=['currency.core','temporal.core','catalog.listing','decision.core','tax.core'], optional=['offer.engine'], temporal=('S',['TR','POL','TRG','TP','ASOF']),
     controls=['ucos.ctrl.fee-transparency','ucos.ctrl.reference-price'], views=['pricing.pricelist.grid'])
pack('commerce.cart','U24-commerce-cart-checkout','core',1,'Carts with lines, coupons, estimates, merge and abandonment.',
     types=T('commerce.Cart','commerce.CartLine'),
     commands=['CreateCart','AddLine','UpdateLineQuantity','RemoveLine','ApplyCoupon','RemoveCoupon','MergeCarts','SaveForLater','EstimateCart'],
     queries=['GetCart','GetCartByBuyer'], events=ev('commerce','cart','created','line-added','line-removed','coupon-applied','abandoned','converted','merged'),
     consumes=['catalog.listing.unpublished','pricing.price.changed','inventory.stock.depleted'],
     requires=['catalog.listing','pricing.engine','identity.core','temporal.core'], optional=['offer.engine','inventory.core','tax.core'], temporal=('S',['D','TRG']), views=['cart.mini','cart.page'])
pack('commerce.checkout','U24-commerce-cart-checkout','core',1,'Checkout orchestration: details, fulfilment options and slots, final signed quote, payment, order placement.',
     types=T('commerce.Checkout'),
     commands=['StartCheckout','SetContact','SetShippingAddress','SetBillingDetails','SelectFulfilmentOption','SelectSlot','ApplyCode','ConfirmAndPay','RetryPayment','CancelCheckout'],
     queries=['GetCheckout'], events=ev('commerce','checkout','started','priced','payment-pending','completed','expired','failed'),
     consumes=['payment.payment-intent.authorized','payment.payment-intent.failed','temporal.trigger.fired'],
     requires=['commerce.cart','pricing.engine','inventory.core','fulfillment.core','payment.core','tax.core','geo.core','party.core','workflow.core','privacy.consent','order.core'],
     optional=['offer.engine'], temporal=('S',['D','TRG','TP','AV']), classes=['PII'], controls=['ucos.ctrl.honest-design','ucos.ctrl.terms-acceptance'], views=['checkout.onepage','checkout.review'])
pack('order.core','U26-order','core',1,'Orders, seller orders, lines, adjustments, cancellations and returns with immutable commercial terms.',
     types=T('order.Order','order.SellerOrder','order.OrderLine','order.OrderAdjustment','order.ReturnRequest'),
     commands=['PlaceOrder','ConfirmOrder','CancelOrder','CancelSellerOrder','AmendOrder','AdjustOrder','RequestReturn','ApproveReturn','RejectReturn','ReceiveReturn','CompleteReturn','CompleteOrder'],
     queries=['GetOrder','OrdersForBuyer','OrdersForSeller','OrderTimeline','CancellationOptions','ReturnOptions'],
     events=ev('order','order','placed','confirmed','cancelled','amended','completed')+ev('order','line','cancelled')+ev('order','return','requested','approved','completed')+ev('order','adjustment','created'),
     consumes=['payment.payment-intent.captured','fulfillment.shipment.delivered','fulfillment.shipment.dispatched','temporal.trigger.fired'],
     requires=['workflow.core','payment.core','fulfillment.core','tax.core','document.core','temporal.core','decision.core'], temporal=('S',['TP','D','TRG']), classes=['PII','FINANCIAL'],
     views=['order.list','order.detail','return.request'])
pack('payment.core','U29-payment','core',1,'Payment intents, attempts, tokenised methods, refunds, COD and reconciliation.',
     types=T('payment.PaymentIntent','payment.PaymentAttempt','payment.PaymentMethod','payment.Refund'),
     commands=['CreateIntent','ConfirmIntent','HandleAction','Capture','Void','Refund','SaveMethod','RemoveMethod','CreateMandate','RecordCodCollection','Reconcile'],
     queries=['GetIntent','ReconciliationReport'], events=ev('payment','payment-intent','created','requires-action','authorized','captured','failed','canceled')+ev('payment','refund','issued','failed')+ev('payment','reconciliation','mismatch'),
     requires=['payment.provider','currency.core','integration.core','temporal.core','identity.core'], temporal=('S',['TP','TRG','CAL','R','TR','SLA']), classes=['FINANCIAL'],
     controls=['ucos.ctrl.pci-hosted-fields','ucos.ctrl.card-tokenization'], views=['checkout.payment'])
pack('payment.provider','U29-payment','abstract',1,'Port for payment service providers (create/authorize/capture/void/refund/status/webhooks/methods).', ports=['payment.provider@2'], temporal=('V',[]))
pack('payment.provider.razorpay','U29-payment','adapter',1,'Razorpay adapter: cards, UPI, net banking, wallets, EMI (India).', implements=['payment.provider'],
     requires=['integration.core'], selection={'jurisdictions':['ucos:jur:IN'],'methods':['card','upi','netbanking','wallet','emi']}, temporal=('V',['TP']))
pack('payment.provider.network-intl','U29-payment','adapter',1,'Network International (N-Genius) adapter: cards, Apple Pay, Google Pay (UAE).', implements=['payment.provider'],
     requires=['integration.core'], selection={'jurisdictions':['ucos:jur:AE'],'methods':['card','apple-pay','google-pay']}, temporal=('V',['TP']))
pack('payment.provider.cod','U29-payment','adapter',1,'Cash-on-delivery internal provider with remittance reconciliation.', implements=['payment.provider'],
     requires=['temporal.core'], selection={'jurisdictions':['ucos:jur:IN','ucos:jur:AE'],'methods':['cod']}, temporal=('S',['TRG']))
pack('payment.provider.simulator','U29-payment','simulator',0,'Contract-faithful payment simulator for simulation/test realities.', implements=['payment.provider'],
     selection={'jurisdictions':['*'],'methods':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))
pack('tax.core','U31-tax','core',1,'Tax regimes, categories, rules, registrations, determinations and tax documents with numbering.',
     types=T('tax.TaxRegime','tax.TaxCategory','tax.TaxRule','tax.TaxRegistration','tax.Exemption','tax.TaxDetermination','tax.TaxDocument','tax.Withholding'),
     commands=['Determine','CommitDetermination','IssueTaxDocument','CancelTaxDocument','RegisterEInvoice','RecordRegistration','RecordExemption','ImportRegimePack'],
     queries=['TaxCategories','DocumentsForOrder'], events=ev('tax','determination','committed')+ev('tax','document','issued','cancelled')+ev('tax','einvoice','registered','failed'),
     requires=['tax.determination','document.core','geo.core','temporal.core','currency.core'], temporal=('S',['TR','CAL','D','TRG']), classes=['FINANCIAL'], controls=['ucos.ctrl.tax-invoice'])
pack('tax.determination','U31-tax','abstract',1,'Port for tax determination engines and regime packs.', ports=['tax.determination@1'], temporal=('V',[]))
pack('tax.gst-india','U31-tax','adapter',1,'India GST regime pack (CGST/SGST/IGST/cess, HSN/SAC, place of supply, TCS).', implements=['tax.determination'],
     selection={'jurisdictions':['ucos:jur:IN']}, temporal=('E',['TR']))
pack('tax.vat-uae','U31-tax','adapter',1,'UAE VAT regime pack (standard/zero/exempt, designated zones, TRN).', implements=['tax.determination'],
     selection={'jurisdictions':['ucos:jur:AE']}, temporal=('E',['TR']))
pack('tax.einvoice-india','U31-tax','adapter',1,'India e-invoicing (IRP via GSP): IRN, signed QR, cancellation window.', implements=['tax.einvoice'],
     requires=['integration.core','tax.core'], selection={'jurisdictions':['ucos:jur:IN']}, temporal=('S',['TRG','D']))
pack('tax.einvoice-simulator','U31-tax','simulator',1,'E-invoice portal simulator (IRN/QR generation, cancellation window) for tests.', implements=['tax.einvoice'], selection={'jurisdictions':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))
pack('tax.einvoice','U31-tax','abstract',1,'Port for government e-invoicing portals.', ports=['tax.einvoice@1'], temporal=('V',[]))
pack('inventory.core','U34-inventory','core',1,'Stock locations, items, balances, movements, reservations, allocations and lots.',
     types=T('inventory.StockLocation','inventory.StockItem','inventory.StockBalance','inventory.StockMovement','inventory.StockReservation','inventory.Allocation','inventory.Lot'),
     commands=['ReceiveStock','AdjustStock','Reserve','ReleaseReservation','ConvertReservation','Allocate','Deallocate','RecordPick','RecordShip','RecordReturn','TransferStock','SetSafetyStock','QuarantineLot','RecallLot'],
     queries=['Availability','Balances','MovementHistory'], events=ev('inventory','stock','adjusted','received','reserved','released','allocated','shipped','depleted','restocked')+ev('inventory','lot','expired','recalled')+ev('inventory','balance','low'),
     requires=['catalog.listing','org.core','currency.core','temporal.core'], temporal=('S',['D','TRG','TP','R','POL']), views=['inventory.balances.grid'])
pack('fulfillment.core','U35-fulfillment','core',1,'Fulfilment profiles, options and promises, sourcing, fulfilment orders, shipments, pickup and digital delivery.',
     types=T('fulfillment.FulfilmentProfile','fulfillment.FulfillmentOrder','fulfillment.Shipment','fulfillment.PickupOrder','fulfillment.DigitalDelivery','fulfillment.ReturnShipment'),
     commands=['PlanFulfilment','CreateFulfillmentOrders','StartPick','ConfirmPack','CreateLabel','Dispatch','RecordTrackingEvent','RecordDelivery','RecordDeliveryFailure','ScheduleReattempt','InitiateRTO','CreatePickupOrder','ConfirmPickup','CreateReturnShipment','ReceiveReturnShipment'],
     queries=['FulfilmentOptions','Tracking'], events=ev('fulfillment','order','created','allocated','packed')+ev('fulfillment','shipment','created','dispatched','in-transit','out-for-delivery','delivered','failed','rto')+ev('fulfillment','pickup','ready','completed','expired')+ev('fulfillment','digital','delivered'),
     consumes=['order.order.confirmed','order.return.approved'],
     requires=['inventory.core','logistics.carrier','temporal.core','geo.core','document.core','integration.core'], temporal=('S',['CAL','BD','D','AV','TRG','SLA','TR']), classes=['PII','LOCATION'],
     views=['delivery.promise','order.tracking','fulfillment.queue'])
pack('logistics.carrier','U35-fulfillment','abstract',1,'Port for carriers (rates, shipments, labels, tracking, pickups, webhooks).', ports=['logistics.carrier@1'], temporal=('V',[]))
pack('carrier.shiprocket','U35-fulfillment','adapter',1,'India carrier aggregator adapter.', implements=['logistics.carrier'], requires=['integration.core'], selection={'jurisdictions':['ucos:jur:IN']}, temporal=('V',['TP']))
pack('carrier.aramex','U35-fulfillment','adapter',1,'UAE/GCC carrier adapter.', implements=['logistics.carrier'], requires=['integration.core'], selection={'jurisdictions':['ucos:jur:AE']}, temporal=('V',['TP']))
pack('carrier.simulator','U35-fulfillment','simulator',0,'Carrier simulator with deterministic tracking timelines.', implements=['logistics.carrier'], selection={'jurisdictions':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))
pack('communication.core','U40-communication','core',1,'Templates, notification rules, consent-aware sending, delivery tracking and conversations (P3).',
     types=T('comm.Channel','comm.Template','comm.NotificationRule','comm.Message','comm.ProxyContact'),
     commands=['DefineTemplate','PublishTemplate','DefineNotificationRule','SendDirect','CreateProxyContact','Unsubscribe'],
     queries=['MessagesFor','DeliveryStats','PreviewTemplate'], events=ev('communication','message','sent','delivered','failed','bounced')+ev('communication','unsubscribed','recorded'),
     consumes=['order.order.confirmed','fulfillment.shipment.dispatched','fulfillment.shipment.delivered','payment.refund.issued','identity.identity.registered'],
     requires=['messaging.provider','party.core','privacy.consent','l10n.core','temporal.core','integration.core'], temporal=('S',['POL','TRG','D']),
     controls=['ucos.ctrl.marketing-consent','ucos.ctrl.unsubscribe'], views=['comm.template.editor','comm.preference.center'])
pack('messaging.provider','U40-communication','abstract',1,'Port for messaging providers (email, SMS, WhatsApp, push, voice).', ports=['messaging.provider@1'], temporal=('V',[]))
pack('messaging.email','U40-communication','adapter',1,'Transactional email adapter (SES/SendGrid class) with domain authentication.', implements=['messaging.provider'],
     requires=['integration.core'], selection={'jurisdictions':['*'],'methods':['email']}, temporal=('V',[]))
pack('messaging.sms-in-dlt','U40-communication','adapter',1,'India SMS adapter with TRAI DLT template and header registration.', implements=['messaging.provider'],
     requires=['integration.core'], selection={'jurisdictions':['ucos:jur:IN'],'methods':['sms']}, temporal=('V',[]), controls=['ucos.ctrl.in-trai-dlt'])
pack('messaging.sms-ae','U40-communication','adapter',1,'UAE SMS adapter with sender-ID registration (TDRA).', implements=['messaging.provider'],
     requires=['integration.core'], selection={'jurisdictions':['ucos:jur:AE'],'methods':['sms']}, temporal=('V',[]))
pack('messaging.whatsapp','U40-communication','adapter',1,'WhatsApp Business Platform adapter via BSP (templates, sessions).', implements=['messaging.provider'],
     requires=['integration.core'], selection={'jurisdictions':['*'],'methods':['whatsapp']}, temporal=('V',[]))
pack('messaging.simulator','U40-communication','simulator',0,'Messaging simulator capturing messages for tests and simulation realities.', implements=['messaging.provider'],
     selection={'jurisdictions':['*'],'methods':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))

# ---------------- Communication completeness (A-64, A-65) ----------------
pack('communication.inapp','U40-communication','core',1,'In-app notification centre: notifications with categories, actions, read state and live unread counts.',
     types=T('comm.Notification'), commands=['MarkRead','MarkAllRead','ArchiveNotification','PerformNotificationAction'], queries=['Inbox','UnreadCounts'],
     events=ev('communication','notification','created','read'), implements=['messaging.provider'], selection={'jurisdictions':['*'],'methods':['in-app']},
     requires=['communication.core','temporal.core','privacy.retention'], temporal=('S',['TP','TRG']), views=['notification.center','notification.bell'])
pack('communication.inbound','U40-communication','core',1,'Inbound message intake (email/SMS/WhatsApp/social replies), opt-out keywords first, intent routing to conversations, cases, orders or bots.',
     types=T('comm.InboundMessage'), commands=['RouteInbound','ReprocessInbound'], queries=['InboundLog'],
     events=ev('communication','inbound','received','routed'), consumes=['integration.webhook.received'], decisions=['communication.inbound-routing'],
     requires=['communication.core','decision.core','integration.core','temporal.core'], temporal=('S',['TP','CAL']), classes=['PII'], controls=['ucos.ctrl.unsubscribe'])
pack('communication.realtime','U40-communication','core',3,'Real-time conversations: WebSocket gateway, presence, typing, delivery/read receipts, rich message types, masked parties.',
     types=T('comm.Conversation','comm.ConversationMessage','comm.Presence'), commands=['StartConversation','PostMessage','MarkDelivered','MarkSeen','SetTyping','CloseConversation'],
     queries=['ConversationHistory','ActiveConversations'], events=ev('communication','conversation','started','message-posted','closed'),
     requires=['communication.core','asset.core','temporal.core','privacy.retention'], temporal=('S',['TP','D']), classes=['PII'], views=['chat.thread','chat.widget'])
pack('communication.broadcast','U40-communication','core',4,'Broadcast and emergency alerts with severity-based approvals, acknowledgement tracking and escalation.',
     types=T('comm.Broadcast','comm.BroadcastAcknowledgement'), commands=['CreateBroadcast','ApproveBroadcast','SendBroadcast','Acknowledge'],
     queries=['BroadcastStatus'], events=ev('communication','broadcast','sent','escalated','acknowledged'),
     requires=['communication.core','authority.core','temporal.core','geo.core'], temporal=('S',['POL','TRG','D']), views=['broadcast.console'])
pack('communication.agent-protocol','U40-communication','core',3,'Signed agent-to-agent message exchange (internal bus and external A2A/MCP transports) with mandates and audit.',
     types=T('comm.AgentMessage'), commands=['SendAgentMessage','AcknowledgeAgentMessage'], queries=['AgentMessageLog'],
     events=ev('communication','agent-message','sent','acknowledged'), requires=['communication.core','temporal.core','integration.core'], temporal=('S',['TP','D']))
for mid, ph, meth, purpose in [
    ('messaging.web-push',1,'web-push','Web Push (VAPID) adapter for browser notifications.'),
    ('messaging.push-fcm',3,'push-android','Firebase Cloud Messaging adapter (Android and cross-platform push).'),
    ('messaging.push-apns',3,'push-ios','Apple Push Notification service adapter.'),
    ('messaging.voice-tts',3,'voice','Voice notification adapter (text-to-speech calls, OTP by voice) via CPaaS.'),
    ('messaging.rcs',4,'rcs','RCS Business Messaging adapter with SMS fallback.'),
    ('messaging.telegram',4,'telegram','Telegram Bot API adapter (opt-in threads).'),
    ('messaging.line',4,'line','LINE Messaging API adapter.'),
    ('messaging.wechat',4,'wechat','WeChat Official Account messaging adapter.'),
    ('messaging.viber',4,'viber','Viber Business Messages adapter.'),
    ('messaging.messenger',4,'messenger','Facebook Messenger Platform adapter.'),
    ('messaging.instagram',4,'instagram','Instagram Messaging API adapter.'),
    ('messaging.postal',4,'postal','Print-and-mail adapter for postal letters (documents from U42).')]:
    pack(mid,'U40-communication','adapter',ph,purpose, implements=['messaging.provider'], requires=['integration.core'],
         selection={'jurisdictions':['*'],'methods':[meth]}, temporal=('V',[]))
pack('rtc.provider','U109-realtime-comms-contact-center','abstract',3,'Port for voice (PSTN/SIP/WebRTC, IVR, masked calling) and video (rooms, tokens, recording) providers.', ports=['rtc.provider@1'], temporal=('V',[]))
pack('rtc.voice-cpaas','U109-realtime-comms-contact-center','adapter',3,'CPaaS voice adapter: calls, IVR media, DTMF/speech gather, recording, masked proxy numbers.', implements=['rtc.provider'],
     requires=['integration.core'], selection={'jurisdictions':['*'],'methods':['voice']}, temporal=('V',[]))
pack('rtc.video-sfu','U109-realtime-comms-contact-center','adapter',3,'WebRTC SFU adapter: rooms, participant tokens, recording/egress, screen share.', implements=['rtc.provider'],
     requires=['integration.core'], selection={'jurisdictions':['*'],'methods':['video']}, temporal=('V',[]))
pack('rtc.simulator','U109-realtime-comms-contact-center','simulator',3,'Voice/video simulator with scripted call flows for tests and simulation realities.', implements=['rtc.provider'],
     selection={'jurisdictions':['*'],'methods':['*'],'realities':['simulated','hypothetical']}, temporal=('V',[]))
pack('contactcenter.core','U109-realtime-comms-contact-center','core',3,'Contact centre: queues, skills routing, agent states, IVR and bot flows with human hand-off, call-backs, recordings with consent, supervision.',
     types=T('rtc.Queue','rtc.AgentProfile','rtc.Interaction','rtc.IvrFlow','rtc.BotFlow','rtc.Callback','rtc.Recording'),
     commands=['DefineQueue','SetAgentState','StartInteraction','RouteInteraction','AcceptInteraction','TransferInteraction','ConferenceIn','EndInteraction','WrapUp','RequestCallback','StartRecording','PauseRecording','PublishIvrFlow','PublishBotFlow','Monitor','Whisper','Barge'],
     queries=['QueueStats','AgentBoard','InteractionHistory','EstimatedWait'],
     events=ev('rtc','interaction','started','answered','transferred','ended')+ev('rtc','queue','sla-breached')+ev('rtc','callback','requested','completed')+ev('rtc','recording','available'),
     consumes=['communication.inbound.routed'], decisions=['rtc.routing'],
     requires=['rtc.provider','communication.core','communication.realtime','decision.core','workflow.core','temporal.core','privacy.consent','privacy.retention','asset.core','identity.core'],
     temporal=('S',['CAL','SLA','D','TRG','POL']), classes=['PII'], controls=['ucos.ctrl.recording-consent','ucos.ctrl.bot-disclosure','ucos.ctrl.pci-hosted-fields'],
     views=['agent.desktop','supervisor.wallboard','ivr.flow.designer'])
pack('rtc.sessions','U109-realtime-comms-contact-center','core',3,'Video sessions (consults, meetings, classes, video-KYC, support) with scheduling, lobby, recording consent and captions.',
     types=T('rtc.VideoSession'), commands=['CreateVideoSession','JoinVideoSession','IssueSessionToken','EndVideoSession'], queries=['SessionStatus'],
     events=ev('rtc','session','started','ended'), requires=['rtc.provider','temporal.core','identity.core','privacy.consent','asset.core'],
     temporal=('S',['AV','TP','TR']), classes=['PII','BIOMETRIC'], controls=['ucos.ctrl.recording-consent'], views=['video.room'])


# ---------------- Phase 0 exit-test sample pack (A-74; U57 Appendix S) ----------------
pack('sample.notes','U57-capability','core',0,'Sample pack for the Phase 0 exit test: an object type defined only in spec/, composed, certified, activated and exercised end to end.',
     types=T('sample.Note'), commands=['CreateNote','EditNote','PublishNote','ArchiveNote','ScheduleNoteReminder','RemindNote'], queries=['GetNote','ListNotes'],
     events=ev('sample','note','created','published','archived','reminded'), consumes=['temporal.trigger.fired'],
     requires=['meta.core','temporal.core','policy.core','audit.core','event.core','identity.core'],
     temporal=('S',['TP','TRG']), classes=['PII'], views=['sample.note.list','sample.note.editor'])
P[-1]['metadata']['maturity'] = 'experimental'

# ---------------- Phase 2 core (hand-authored, replaces derived manifests; A-73) ----------------
pack('ledger.core','U30-ledger-finance','core',2,'Double-entry ledger: charts of accounts, posting rules from events, settlements, revenue schedules, period close, reconciliation.',
     types=T('ledger.LedgerEntity','ledger.Account','ledger.JournalEntry','ledger.PostingRule','ledger.Settlement','ledger.RevenueSchedule','ledger.Period','ledger.Reconciliation','ledger.Invoice'),
     commands=['CreateLedgerEntity','DefineAccount','PublishPostingRule','PostManualJournal','ReverseEntry','ClosePeriod','ReopenPeriod','ImportStatement','Reconcile','ScheduleRevenue','RunReplay'],
     queries=['TrialBalance','AccountActivity','Balance','FinancialStatements','Aging'],
     events=ev('ledger','journal','posted')+ev('ledger','period','closed','reopened')+ev('ledger','settlement','completed')+ev('ledger','reconciliation','break'),
     consumes=['payment.payment-intent.captured','payment.refund.issued','order.order.confirmed','fulfillment.shipment.delivered',
               'marketplace.commission.accrued','marketplace.payout.paid','stored-value.instrument.issued','stored-value.instrument.redeemed'],
     decisions=['ledger.account-resolution','ledger.revenue-recognition'],
     requires=['currency.core','temporal.core','org.core','tax.core','event.core','audit.core','decision.core','workflow.core'],
     temporal=('S',['CAL','R','D','BD']), classes=['FINANCIAL'], controls=['ucos.ctrl.books-retention','ucos.ctrl.manual-journal-sod'],
     views=['ledger.journal-explorer','ledger.period-close','ledger.reconciliation','ledger.statements'])
pack('marketplace.core','U25-marketplace','core',2,'Multi-sided marketplace: seller onboarding and standing, commission plans, payouts with holds, statements, seller performance.',
     types=T('marketplace.SellerAccount','marketplace.CommissionPlan','marketplace.PayoutSchedule','marketplace.SellerStatement','marketplace.SellerPerformance','marketplace.MarketplacePolicy'),
     commands=['ApplyAsSeller','CompleteKYB','ApproveSeller','RejectSeller','SignSellerAgreement','ApproveCategory','SetSellerStanding','DefineCommissionPlan','AccrueCommission','ComputePayout','ReleasePayout','HoldPayout','IssueStatement'],
     queries=['SellerDashboard','PayableBalance','PerformanceScorecard','NextPayout'],
     events=ev('marketplace','seller','approved','suspended','reinstated')+ev('marketplace','commission','accrued')+ev('marketplace','payout','scheduled','paid','held')+ev('marketplace','statement','issued'),
     consumes=['order.order.confirmed','order.return.completed','fulfillment.shipment.delivered','payment.refund.issued'],
     decisions=['marketplace.commission-plan','marketplace.payout-hold'],
     requires=['org.core','identity.core','catalog.listing','order.core','payment.core','tax.core','decision.core','temporal.core','entitlement.core','ledger.core','risk.core','document.core'],
     optional=['trust.core','contract.core'],
     temporal=('S',['POL','CAL','R','TR','SLA']), classes=['PII','FINANCIAL'],
     controls=['ucos.ctrl.seller-kyb','ucos.ctrl.in-ecom-seller-disclosure'],
     views=['marketplace.seller-onboarding','marketplace.seller-hub','marketplace.payout-run','marketplace.commission-plans'])
pack('subscription.core','U27-subscription','core',2,'Recurring plans, subscriptions, proration, usage rating, billing runs, dunning and recurring payment mandates.',
     types=T('subscription.SubscriptionPlan','subscription.Subscription','subscription.UsageRecord','subscription.RatedCharge','subscription.BillingRun','subscription.DunningPlan'),
     commands=['CreatePlan','Subscribe','StartTrial','ChangePlan','UpdateQuantity','Pause','Resume','Cancel','ReportUsage','RunBilling','RetryPayment','ApplyCredit'],
     queries=['PreviewChange','UpcomingInvoice','UsageSummary'],
     events=ev('subscription','subscription','created','activated','renewed','past-due','paused','canceled','plan-changed')+ev('subscription','usage','rated')+ev('subscription','invoice','issued')+ev('subscription','dunning','step'),
     consumes=['payment.payment-intent.captured','payment.payment-intent.failed'],
     decisions=['subscription.renewal-notice','subscription.dunning-plan'],
     requires=['temporal.core','pricing.engine','entitlement.core','payment.core','ledger.core','tax.core','document.core','communication.core','decision.core','currency.core'],
     temporal=('S',['TR','R','TRG','D','BD']), classes=['PII','FINANCIAL'],
     controls=['ucos.ctrl.renewal-notice','ucos.ctrl.easy-cancellation','ucos.ctrl.in-emandate'],
     views=['subscription.manage','subscription.plan-builder','subscription.billing-run'])
pack('logistics.core','U36-logistics','core',2,'Multi-carrier rating and selection, manifests and pickups, normalised tracking, NDR and RTO handling, transport documents.',
     types=T('logistics.Carrier','logistics.RateQuote','logistics.CarrierSelection','logistics.Manifest','logistics.TrackingEvent','logistics.DeliveryException','logistics.Route','logistics.TransportDocument'),
     commands=['RegisterCarrier','RateShop','SelectCarrier','CreateManifest','SchedulePickup','IngestTracking','RaiseNDR','ResolveNDR','PlanRoutes','GenerateTransportDocument'],
     queries=['Rates','TransitTime','CarrierScorecard','RouteStatus'],
     events=ev('logistics','tracking','updated')+ev('logistics','ndr','raised','resolved')+ev('logistics','pickup','completed','missed')+ev('logistics','route','planned'),
     consumes=['fulfillment.shipment.created'],
     decisions=['logistics.carrier-selection'],
     requires=['fulfillment.core','geo.core','temporal.core','integration.core','currency.core','pricing.engine','decision.core','workflow.core','tax.core'],
     optional=['resource.core'],
     temporal=('S',['R','D','AV','CAL']), classes=['PII','LOCATION'], controls=['ucos.ctrl.in-eway-bill'],
     views=['logistics.rate-shop','logistics.ndr-queue','logistics.carrier-scorecard'])
pack('risk.core','U69-risk','core',2,'Real-time risk scoring with explainable reasons, velocity checks, review queues and block/allow lists; unknown band on failure.',
     types=T('risk.RiskModel','risk.RiskAssessment','risk.VelocityCounter','risk.ReviewCase','risk.ListEntry','risk.AMLAlert','risk.RiskRegisterItem'),
     commands=['Score','RecordOutcome','OpenReview','DecideReview','AddListEntry','PublishRiskModel','RaiseAMLAlert','FileReport'],
     events=ev('risk','assessment','high')+ev('risk','review','decided')+ev('risk','label','recorded')+ev('risk','aml','alert-raised'),
     consumes=['order.order.placed','commerce.checkout.started','identity.session.started','payment.refund.issued'],
     decisions=['risk.checkout-thresholds','risk.login-thresholds'],
     requires=['decision.core','context.core','event.core','identity.core','temporal.core','workflow.core','observability.core'],
     optional=['ml.core'],
     temporal=('S',['D']), classes=['PII'], controls=['ucos.ctrl.automated-decision-contest'],
     views=['risk.cockpit','risk.review-queue','risk.rule-editor'])
pack('trust.core','U70-trust-reputation','core',2,'Reviews and ratings with verified-experience badges, moderation, published aggregation method and trust badges.',
     types=T('trust.Review','trust.ReviewResponse','trust.Aggregate','trust.TrustScore','trust.Badge'),
     commands=['RequestReview','SubmitReview','ModerateReview','RespondToReview','ReportReview','RecomputeAggregates','AwardBadge','RevokeBadge'],
     events=ev('trust','review','published','removed')+ev('trust','aggregate','updated')+ev('trust','badge','awarded','revoked'),
     consumes=['fulfillment.shipment.delivered'],
     decisions=['trust.review-moderation'],
     requires=['order.core','party.core','risk.core','temporal.core','privacy.consent','compliance.core','asset.core'],
     optional=['marketplace.core','product.intelligence'],
     temporal=('S',['TRG','D']), classes=['PII'], controls=['ucos.ctrl.authentic-reviews'],
     views=['trust.pdp-reviews','trust.write-review','trust.moderation-queue'])
pack('resource.core','U17-resource','core',2,'Resources that provide capacity over time (people, vehicles, rooms, machines), skills and credentials, pools and capacity plans.',
     types=T('resource.ResourceType','resource.Resource','resource.ResourcePool','resource.CapacityPlan'),
     commands=['DefineResourceType','RegisterResource','AssignSkill','AttachCredential','SetResourceCalendar','DefinePool','RetireResource'],
     queries=['EligibleResources','PoolCapacity','Utilisation'],
     events=ev('resource','resource','registered','retired')+ev('resource','skill','expiring'),
     requires=['temporal.core','geo.core','party.core','identity.core'],
     optional=['service.intelligence'],
     temporal=('S',['CAL','AV','R']), classes=['PII'], views=['resource.directory','resource.pool-editor'])
pack('generation.core','U59-generation','core',2,'Deterministic generators for SDKs, API and event docs, migrations, dashboards, tests and diagrams; AI-assisted drafts as proposals only.','platform',
     types=T('generation.GeneratorDefinition','generation.GenerationRun'),
     commands=['RegisterGenerator','RunGenerator','PublishArtifacts','VerifyReproducibility'],
     events=ev('generation','run','completed','failed')+ev('generation','artifact','published'),
     requires=['composition.core','capability.registry','meta.core','api.core','event.core','certification.core','temporal.core'],
     temporal=('S',['R']))

# ================================================================ Part 2: derived core manifests
def _section(text, title_re):
    m = re.search(r'^#{2,3} [^\n]*' + title_re + r'[^\n]*$', text, re.M)
    if not m:
        return ''
    nxt = re.search(r'^#{2,3} ', text[m.end():], re.M)
    return text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]

def _expand_alt(tok):
    parts = tok.split('|')
    out = [parts[0]]
    for alt in parts[1:]:
        if len(re.findall(r'[A-Z]', alt)) >= 2:
            out.append(alt)
        else:
            mm = re.match(r'^(.*?)([A-Z][a-z0-9]*)$', parts[0])
            out.append((mm.group(1) if mm else '') + alt)
    return out

def _names(line):
    toks = re.findall(r'`([A-Z][A-Za-z0-9|/]*)', line)
    out = []
    for t in toks:
        for piece in t.split('/'):
            if piece:
                out.extend(_expand_alt(piece))
    return [x for x in out if re.fullmatch(r'[A-Z][A-Za-z0-9]+', x)]

def _events(text):
    out = []
    for t in re.findall(r'`([a-z][a-z0-9-]*\.[a-z0-9-]+\.[a-z0-9|-]+)`', text):
        base, verbs = t.rsplit('.', 1)
        out += [f'{base}.{v}' for v in verbs.split('|') if v]
    return list(dict.fromkeys(out))

matrix = {}
for line in open(os.path.join(ROOT, 'constitutions', 'TEMPORAL-BINDING-MATRIX.md'), encoding='utf-8'):
    mm = re.match(r'^\| (U\d+) [^|]*\|[^|]*\|([^|]*)\| ([VES]) \|', line)
    if mm:
        allowed = {'TP','TR','D','BD','R','POL','CAL','AV','FCA','SLA','TRG','REM','WL','FEED','ASOF','TS'}
        uses = [re.sub(r'\(.*?\)', '', u).strip() for u in mm.group(2).split(',')]
        matrix[mm.group(1)] = (mm.group(3), [u for u in uses if u in allowed])

PLATFORM_SCOPE = {'U48', 'U54', 'U59', 'U76'}
have = {m['metadata']['universe'].split('-')[0] for m in P}
derived = []
for doc in sorted(glob.glob(os.path.join(ROOT, 'constitutions', 'U*', 'constitution.md'))):
    folder = os.path.basename(os.path.dirname(doc))
    uid = folder.split('-')[0]
    if uid in have:
        continue
    text = open(doc, encoding='utf-8').read()
    slug = re.search(r'\| Universe ID \| `U\d+-([a-z0-9-]+)`', text).group(1)
    phase = int(re.search(r'\| Delivery phase \| P(\d)', text).group(1))
    deps = re.search(r'^\| Depends on \|([^\n]*)', text, re.M)
    dep_uids = list(dict.fromkeys(re.findall(r'\b(U\d{2,3})\b', deps.group(1)))) if deps else []
    purpose = re.search(r'^> (.*)$', text, re.M)
    purpose = re.sub(r'[*`]', '', purpose.group(1)) if purpose else f'{folder} core capability.'
    purpose = (purpose.split(':')[0] if ':' in purpose[:200] else purpose.split('. ')[0][:200]).strip().rstrip('.') + '.'
    objs = _section(text, r'Objects')
    types = list(dict.fromkeys(re.findall(r'`([A-Z][A-Za-z0-9]+)(?:\s*\([^)`]*\))?\s*\{', objs)
                               + re.findall(r'`([A-Z][A-Za-z0-9]+)`\s*\([^)]*\)\s*`\{', objs)
                               + re.findall(r'\*\*`([A-Z][A-Za-z0-9]+)`\*\*', objs)))
    cmds = qrys = []
    evline = ''
    for line in text.splitlines():
        if line.startswith('Commands:'):
            cmds = _names(line[len('Commands:'):])
        elif line.startswith('Queries:'):
            qrys = _names(line[len('Queries:'):])
        elif line.startswith('Events:') or 'Events:' in line[:40]:
            evline += line
    kind_t, uses = matrix.get(uid, ('V', []))
    derived.append(dict(uid=uid, folder=folder, slug=slug, phase=phase, deps=dep_uids, purpose=purpose, types=types,
                        cmds=list(dict.fromkeys(cmds)), qrys=list(dict.fromkeys(qrys)), events=_events(evline), tk=kind_t, uses=uses))

def _core_of(uid):
    cands = [m for m in P if m['metadata']['universe'].startswith(uid + '-') and m['metadata']['capabilityKind'] == 'core']
    cands += [{'metadata': {'id': d['slug'] + '.core', 'phase': d['phase']}} for d in derived if d['uid'] == uid]
    return min(cands, key=lambda m: m['metadata']['phase'])['metadata'] if cands else None

for d in derived:
    cap_id = d['slug'] + '.core'
    req, opt = [], []
    for u in d['deps']:
        c = _core_of(u)
        if not c or c['id'] == cap_id:
            continue
        (req if c['phase'] <= d['phase'] else opt).append(c['id'])
    if d['tk'] == 'S' and 'temporal.core' not in req:
        req.append('temporal.core')
    ns = d['slug']
    pack(cap_id, d['folder'], 'core', d['phase'], d['purpose'], 'platform' if d['uid'] in PLATFORM_SCOPE else 'tenant',
         types=T(*[f'{ns}.{t}' for t in d['types']]), commands=d['cmds'], queries=d['qrys'], events=d['events'],
         requires=list(dict.fromkeys(req)), optional=list(dict.fromkeys(o for o in opt if o not in req)),
         temporal=(d['tk'], d['uses']))
    P[-1]['metadata']['maturity'] = 'experimental'

hand_events = {e for m in P if m['metadata'].get('maturity') != 'experimental' for e in m['spec'].get('provides', {}).get('events', [])}
for m in P:
    if m['metadata'].get('maturity') == 'experimental' and 'events' in m['spec'].get('provides', {}):
        m['spec']['provides']['events'] = [e for e in m['spec']['provides']['events'] if e not in hand_events]

def _reqs(cid):
    m = next((x for x in P if x['metadata']['id'] == cid), None)
    return [r['capability'] for r in m['spec'].get('requires', [])] if m else []
def _closure(start):
    seen, stack = set(), list(start)
    while stack:
        x = stack.pop()
        if x not in seen:
            seen.add(x); stack.extend(_reqs(x))
    return seen
for m in P:  # derived manifests must not close a requires-cycle; such edges become optional
    if m['metadata'].get('maturity') != 'experimental':
        continue
    cid, keep = m['metadata']['id'], []
    for r in m['spec'].get('requires', []):
        if cid in _closure([r['capability']]):
            m['spec'].setdefault('optional', []).append({'capability': r['capability']})
        else:
            keep.append(r)
    m['spec']['requires'] = keep

wanted = {}
for m in P:
    wanted[m['metadata']['id'] + '.yaml'] = yaml.safe_dump(m, sort_keys=False, width=140)
import sys
stale_files = sorted([n for n, c in wanted.items() if not os.path.exists(os.path.join(OUT, n)) or open(os.path.join(OUT, n)).read() != c]
                     + [f for f in os.listdir(OUT) if f.endswith('.yaml') and f not in wanted])
if '--check' in sys.argv:
    for n in stale_files:
        print('out of date: spec/capabilities/packs/' + n)
    sys.exit(1 if stale_files else 0)
for f in os.listdir(OUT):                 # remove manifests no longer generated
    if f.endswith('.yaml') and f not in wanted:
        os.remove(os.path.join(OUT, f))
for name, content in wanted.items():      # rewrite only what changed (avoids churn on synced folders)
    path = os.path.join(OUT, name)
    if not os.path.exists(path) or open(path).read() != content:
        open(path, 'w').write(content)
print(len(P), 'manifests', f'({len(derived)} derived from specs)')
