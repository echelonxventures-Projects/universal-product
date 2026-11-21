// Universe-default policy for the Phase 0 sample pack (U57 appendix, layer: universe-default). Members of a tenant
// may use sample.notes inside their own tenant. Finer rules (only editors publish, only the author edits, only
// services send reminders) stay in the pack and return SAMPLE_FORBIDDEN or SAMPLE_NOT_AUTHOR.
// The kernel's enforcement point gives every operation's action two parents: Action::"group:write" (commands) or
// Action::"group:read" (queries), and Action::"group:capability:<capability id>".

@id("sample.notes.tenant-members")
permit (principal, action in Action::"group:capability:sample.notes", resource)
when { principal has tenant && resource has tenant && principal.tenant == resource.tenant };
